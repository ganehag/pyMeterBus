import simplejson as json

from .core_objects import DataEncoding, FunctionType
from .telegram_field import TelegramField
from .telegram_variable_data_record import TelegramVariableDataRecord
from .value_information_block import ValueInformationBlock
from .telegram_body import TelegramBodyPayload


class WTelegramBodyHeader(object):
    BYTE_ORDER_MASK = 0x04    # 0000 0100

    def __init__(self):
        self._manufacturer_field = TelegramField()  # manufacturer
        self._id_nr_field = TelegramField()       # identification number field
        self._version_field = TelegramField()       # version
        self._device_field = TelegramField()      # device type field
        self._ci_field = TelegramField()          # control information field
        self._acc_nr_field = TelegramField()      # access number
        self._status_field = TelegramField()      # status
        self._config_field = TelegramField()      # configuration field
        self._decryption_field = TelegramField()  # decryption field

    def load(self, bodyHeader):
        length = 15

        self.manufacturer_field = bodyHeader[0:2]
        self.id_nr_field = bodyHeader[2:6]
        self.version_field = bodyHeader[6]
        self.device_field = bodyHeader[7]
        self.ci_field = bodyHeader[8]

        ptr = bodyHeader[9:]

        if self.long_tl:
            self.id_nr_field = ptr[0:4]
            self.manufacturer_field = ptr[4:6]
            self.version_field = ptr[6]
            self.device_field = ptr[7]
            ptr = ptr[8:]
            length += 8

        if self.long_tl or self.short_tl:
            self.acc_nr_field = ptr[0]
            self.status_field = ptr[1]
            self.configuration_field = ptr[2:4][::-1]
            # swap configuration bytes as these arrive little endian
            self.decryption_field = ptr[4:6]

        return length


    @property
    def isLSBOrder(self):
        return not (self._ci_field.parts[0] & self.BYTE_ORDER_MASK)

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
    def id_nr(self):
        """ID number of telegram in reverse byte order"""
        return self._id_nr_field[::-1]

    @property
    def ci_field(self):
        return self._ci_field

    @ci_field.setter
    def ci_field(self, value):
        self._ci_field = TelegramField(value)

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
    def config_field(self):
        return self._config_field

    @config_field.setter
    def config_field(self, value):
        self._config_field = TelegramField(value)

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
    def interpreted(self):
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

    def to_JSON(self):
        return json.dumps(self.interpreted, sort_keys=False, indent=4, use_decimal=True)


class WTelegramBody(object):
    def __init__(self):
        self._bodyHeader = WTelegramBodyHeader()
        self._bodyPayload = TelegramBodyPayload(parent=self)
        self._bodyHeaderLength = 23

    @property
    def records(self):
        return self.bodyPayload.records

    @property
    def bodyHeaderLength(self):
        return self._bodyHeaderLength

    @property
    def bodyHeader(self):
        return self._bodyHeader

    @bodyHeader.setter
    def bodyHeader(self, val):
        self._bodyHeader = WTelegramBodyHeader()
        self._bodyHeaderLength = self._bodyHeader.load(val[0:self.bodyHeaderLength])

    @property
    def bodyPayload(self):
        return self._bodyPayload

    @bodyPayload.setter
    def bodyPayload(self, val):
        self._bodyPayload = TelegramBodyPayload(val)

    @property
    def interpreted(self):
        return {
            'header': self.bodyHeader.interpreted,
            'records': self.bodyPayload.interpreted,
        }

    def load(self, body):
        self.bodyHeader = body[0:self.bodyHeaderLength]
        self._bodyHeaderLength = self.bodyPayload.load(body[self.bodyHeaderLength:])

    def parse(self):
        self.bodyPayload.parse()  # Load from raw into records

    def debug(self):
        self.bodyHeader.debug()
        self.bodyPayload.debug()

    def to_JSON(self):
        return json.dumps(self.interpreted, sort_keys=False, indent=4, use_decimal=True)
