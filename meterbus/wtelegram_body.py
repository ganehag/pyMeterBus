from builtins import (bytes, str, open, super, range,
                      zip, round, input, int, pow, object)

import binascii

import simplejson as json
from Crypto.Cipher import AES

from .core_objects import DataEncoding, FunctionType
from .telegram_field import TelegramField
# from .telegram_variable_data_record import TelegramVariableDataRecord
from .value_information_block import ValueInformationBlock
from .telegram_body import TelegramBodyPayload


class WTelegramBaseDataHeader(object):
    BYTE_ORDER_MASK = 0x04    # 0000 0100
    PADDING_BYTE = 0x00

    def __init__(self, frame = None):
        if isinstance(frame, WTelegramBaseDataHeader):
            self._manufacturer_field = frame._manufacturer_field
            self._id_nr_field = frame._id_nr_field
            self._version_field = frame._version_field
            self._device_field = frame._device_field

            self._ci_field = frame._ci_field
            self._acc_nr_field = frame._acc_nr_field
            self._status_field = frame._status_field
            self._configuration_field = frame._configuration_field
            self._decryption_field = frame._decryption_field

        else:
            self._manufacturer_field = TelegramField()  # manufacturer
            self._id_nr_field = TelegramField()  # identification number field
            self._version_field = TelegramField()  # version
            self._device_field = TelegramField()  # device type field

            self._ci_field = TelegramField()  # control information field
            self._acc_nr_field = TelegramField()  # access number
            self._status_field = TelegramField()  # status
            self._configuration_field = TelegramField()  # configuration field
            self._decryption_field = TelegramField()  # decryption field


    def load(self, bdata):
        self.manufacturer_field = bdata[0:2]
        self.id_nr_field = bdata[2:6]
        self.version_field = bdata[6]
        self.device_field = bdata[7]
        self.ci_field = bdata[8]

        return self.length

    @property
    def length(self):
        return 9

    @property
    def isLSBOrder(self):
        return not (self._ci_field.parts[0] & self.BYTE_ORDER_MASK)

    @property
    def address(self):
        return self.id_nr_field.parts + self.version_field.parts + self.device_field.parts

    @property
    def ci_field(self):
        return self._ci_field

    @ci_field.setter
    def ci_field(self, value):
        self._ci_field = TelegramField(value)

    @property
    def id_nr(self):
        """ID number of telegram in reverse byte order"""
        return self._id_nr_field[::-1]

    @property
    def id_nr_field(self):
        return self._id_nr_field

    @id_nr_field.setter
    def id_nr_field(self, value):
        self._id_nr_field = TelegramField(value)

    @property
    def manufacturer_field(self):
        return self._manufacturer_field

    @manufacturer_field.setter
    def manufacturer_field(self, value):
        self._manufacturer_field = TelegramField(value)

    @property
    def version_field(self):
        return self._version_field

    @version_field.setter
    def version_field(self, value):
        self._version_field = TelegramField(value)

    @property
    def device_field(self):
        return self._device_field

    @device_field.setter
    def device_field(self, value):
        self._device_field = TelegramField(value)

    @property
    def acc_nr_field(self):
        return self._acc_nr_field

    @acc_nr_field.setter
    def acc_nr_field(self, value):
        self._acc_nr_field = TelegramField(value)

    @property
    def status_field(self):
        return self._status_field

    @status_field.setter
    def status_field(self, value):
        self._status_field = TelegramField(value)

    @property
    def decryption_field(self):
        return self._decryption_field

    @decryption_field.setter
    def decryption_field(self, value):
        self._decryption_field = TelegramField(value)

    @property
    def configuration_field(self):
        return self._configuration_field

    @configuration_field.setter
    def configuration_field(self, value):
        self._configuration_field = TelegramField(value)

    @property
    def without_tl(self):
        """ Returns True if the CI field indicates no transport layer
        """
        return self.ci_field[0] in (0x69, 0x70, 0x78, 0x79)

    @property
    def short_tl(self):
        """ Returns True if the CI field indicates short transport layer
        """
        return self.ci_field[0] in (0x61, 0x65, 0x6A, 0x6E, 0x74,
                                    0x7A, 0x7B, 0x7D, 0x7F, 0x8A)

    @property
    def long_tl(self):
        """ Returns True if the CI field indicates long transport layer
        """
        return self.ci_field[0] in (0x60, 0x64, 0x6B, 0x6F, 0x72, 0x73,
                                    0x75, 0x7C, 0x7E, 0x80, 0x8B)

    @property
    def manu_tl(self):
        """ Returns True if the CI field indicates manufacturer specific layer
        """
        return self.ci_field[0] in (0xAA, )

    @property
    def encryption_mode(self):
        """ Returns the mode number as defined in prEN 13575-3
        """
        return self.configuration_field[0] & 0x0F

    @property
    def encryption_name(self):
        """ Return speaking name for encryption mode (defined in prEN 13575-3)

        Note, that OMS Security Report and BSI TRs resp. OMS 4 define further 
        modes currently not covered here.

        0 No encryption used
        1 Reserved
        2 DES encryption with CBC; IV is zero (deprecated)
        3 DES encryption with CBC; IV is not zero (deprecated)
        4 AES encryption with CBC; IV is zero
        5 AES encryption with CBC; IV is not zero
        6 Reserved for new encryption
        7 - 15 Reserved
        """
        mode = self.configuration_field[0] & 0x0F

        if mode == 0:
            return "No encryption used"

        if mode == 1 or mode >= 6:
            return "Reserved"

        return {
            2: "DES encryption with CBC; IV is zero (deprecated)",
            3: "DES encryption with CBC; IV is not zero (deprecated)",
            4: "AES encryption with CBC; IV is zero",
            5: "AES encryption with CBC; IV is not zero"
        }.get(mode)

    @property
    def crypto_iv(self):
        """ Returns the IV in little endian
        The IV is derived from the manufacturer bytes, the device address and
        the access number from the data header. Note, that None is being 
        returned if the current mode does not specify an IV or the IV for that
        specific mode is not implemented.

        Currently implemented IVs are:
        - IV for mode 2 encryption
        - IV for mode 4 encryption
        - IV for mode 5 encryption
        """

        if self.encryption_mode == 2:
            return bytearray(b'\x00\x00\x00\x00\x00\x00\x00\x00')

        elif self.encryption_mode == 4:
            return bytearray(b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00')

        elif self.encryption_mode == 5:
            '''
            According to prEN 13757-3 the IV for mode 5 is setup as follows

            LSB 1   2   3   4   5   6   7   8   9   10  11  12  13  14  MSB
            Man Man ID  ..  ..  ID  Ver Med Acc ..  ..  ..  ..  ..  ..  Acc
            LSB MSB LSB         MSB sio ium
            '''

            iv = bytearray(
                 self.manufacturer_field.parts
               + self.id_nr_field.parts
               + self.version_field.parts
               + self.device_field.parts
               + self.acc_nr_field.parts * 8
            )

            return iv

        return None

    def decrypt(self, data):
        # FIXME: implement proper handling of KEYS
        keys = {
            '\x00\x00\x03\x11': b'\x00\x01\x02\x03\x04\x05\x06\x07\x08\x09\x0A\x0B\x0C\x0D\x0E\x0F'
        }

        devid = ''.join(chr(b) for b in self.id_nr_field[::-1])
        key = keys.get(devid, None)

        if key is None:
            return False

        if self.encryption_mode == 5:
            orig_len = len(data)

            spec = AES.new(key, AES.MODE_CBC, bytes(self.crypto_iv))
            data = data + ((16 - orig_len % 16) * [self.PADDING_BYTE])
            data = [ int(x) for x in bytearray(spec.decrypt(bytes(data))) ]

            if data[0:2] != [0x2F, 0x2F]:
                return False
            #     raise Exception("Decryption failed")
            return data[:orig_len]

        return None

    @property
    def interpreted(self):
        try:
            return {
                'manufacturer': self.manufacturer_field.decodeManufacturer,
                'identification': ", ".join(map(hex, self.id_nr)),
                'version': hex(self.version_field.parts[0]),
                'device_type': hex(self.device_field.parts[0]),
                'type': hex(self.ci_field.parts[0]),
                'access_no': self.acc_nr_field.parts[0],
                'status': hex(self.status_field.parts[0]),
                'configuration': ", ".join(map(hex,
                                               self.configuration_field)),
                'decryption': ", ".join(map(hex, self.decryption_field)),
            }
        except IndexError:
            return {
                'manufacturer': self.manufacturer_field.decodeManufacturer,
                'identification': ", ".join(map(hex, self.id_nr)),
                'version': hex(self.version_field.parts[0]),
                'device_type': hex(self.device_field.parts[0]),
                'type': hex(self.ci_field.parts[0]),
            }

    def to_JSON(self):
        return json.dumps(self.interpreted, sort_keys=False, indent=4, use_decimal=True)


class WTelegramManuSpecDataHeader(WTelegramBaseDataHeader):
    HEADER_LENGTH = 0

    def __init__(self, frame = None):
        super().__init__(frame)

    def load(self, bdata):
        if len(bdata) < self.length:
            return 0

        super().load(bdata)
        offset = super().length

        return self.length

    @property
    def length(self):
        return super().length + self.HEADER_LENGTH


class WTelegramShortDataHeader(WTelegramBaseDataHeader):
    HEADER_LENGTH = 6

    def __init__(self, frame = None):
        super().__init__(frame)

    def load(self, bdata):
        if len(bdata) < self.length:
            return 0

        super().load(bdata)
        offset = super().length

        if self.short_tl:
            ptr = bdata[offset:]

            self.acc_nr_field = ptr[0]
            self.status_field = ptr[1]
            self.configuration_field = ptr[2:4][::-1]  # swap configuration bytes as these arrive little endian
            self.decryption_field = ptr[4:6]

        return self.length

    @property
    def length(self):
        return super().length + self.HEADER_LENGTH


class WTelegramLongDataHeader(WTelegramBaseDataHeader):
    HEADER_LENGTH = 14

    def __init__(self, frame = None):
        super().__init__(frame)

    def load(self, bdata):
        if len(bdata) < self.length:
            return 0

        super().load(bdata)
        offset = super().length

        if self.long_tl:
            ptr = bdata[offset:]

            self.id_nr_field = ptr[0:4]
            self.manufacturer_field = ptr[4:6]
            self.version_field = ptr[6]
            self.device_field = ptr[7]

            self.acc_nr_field = ptr[8]
            self.status_field = ptr[9]
            # swap configuration bytes as these arrive little endian
            self.configuration_field = ptr[10:12][::-1]
            self.decryption_field = ptr[12:14]

        return self.length

    @property
    def length(self):
        return super().length + self.HEADER_LENGTH


class WTelegramDataHeader(object):
    @staticmethod
    def load(bdata):
        frame = WTelegramBaseDataHeader()
        frame.load(bdata)

        if frame.long_tl:
            frame = WTelegramLongDataHeader()

        elif frame.short_tl:
            frame = WTelegramShortDataHeader()

        elif frame.manu_tl:
            frame = WTelegramManuSpecDataHeader()

        if frame.load(bdata) == 0:
            return None

        return frame


class WTelegramFrame(object):
    def __init__(self):
        self._lField = TelegramField()
        self._cField = TelegramField()
        self._data_header = None
        self._payload = TelegramBodyPayload(parent=self)

    @property
    def lField(self):
        return self._lField

    @lField.setter
    def lField(self, value):
        self._lField = TelegramField(value)

    @property
    def cField(self):
        return self._cField

    @cField.setter
    def cField(self, value):
        self._cField = TelegramField(value)

    @property
    def bodyHeader(self):
        '''
        Hackish solution to be compatible with the remaining code/parser
        '''
        return self.dataHeader

    @property
    def dataHeader(self):
        return self._data_header

    @dataHeader.setter
    def dataHeader(self, value):
        self._data_header = value

    @property
    def records(self):
        return self._payload.records

#    @records.setter
#    def records(self, val):
#        self._records = TelegramBodyPayload(val).records

    @property
    def has_errors(self):
        """
        Returns true if the header status byte flags errors and alarms
        """
        if self.dataHeader.status_field[0] & 0xC0:
            return True

        return False

    @property
    def interpreted(self):
        return {
            'header': self.dataHeader.interpreted,
            'records': self._payload.interpreted,
            'length': int(self.lField.parts[0]),
            'c': hex(self.cField.parts[0]),
        }

    @property
    def is_encrypted(self):
        """ Returns False if the captured frame signals "No encryption"
        """
        try:
            if (self.dataHeader.configuration_field[0] & 0x0F != 0):
                return True
        except IndexError:
            pass

        return False

    def load(self, bdata):
        if isinstance(bdata, str):
            bdata = list(map(ord, bdata))

        self.lField = bdata[0]
        self.cField = bdata[1]

        self.dataHeader = WTelegramDataHeader.load(bdata[2:])
        if self.dataHeader is None:
            return None

        if self.is_encrypted:
            encrdata = bdata[2:]
            # self.dataHeader.length also contains the encryption bytes so we need
            # to step back two bytes... so -2
            d = self.dataHeader.decrypt(encrdata[(self.dataHeader.length - 2):])
            if d:
                bdata[(2 + self.dataHeader.length):] = d

        if not isinstance(self.dataHeader, WTelegramManuSpecDataHeader):
            try:
                self._payload.load(bdata[(2 + self.dataHeader.length):])
            except IndexError as e:
                return None
        else:
            # Insert manu specific record with data
            self._payload.load([0x0F] + bdata[(2 + self.dataHeader.length):])
            pass

        return True


    def to_JSON(self):
        return json.dumps(self.interpreted, sort_keys=False, indent=4, use_decimal=True)

