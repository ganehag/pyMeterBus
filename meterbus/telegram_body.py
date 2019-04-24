import simplejson as json

from .core_objects import DataEncoding, FunctionType
from .telegram_field import TelegramField
from .telegram_variable_data_record import TelegramVariableDataRecord
from .value_information_block import ValueInformationBlock


class TelegramBodyPayload(object):
    def __init__(self, payload=None, parent=None):
        self._body = TelegramField()
        if payload is not None:
            self._body = TelegramField(payload)

        self._records = []
        self._parent = parent

    @property
    def records(self):
        return self._records

    @records.setter
    def records(self, value):
        self._records = value

    @property
    def body(self):
        return self._body

    @body.setter
    def body(self, value):
        self._body = TelegramField(value)

    @property
    def interpreted(self):
        return [r.interpreted for r in self.records]

    def load(self, payload):
        self.body = payload
        self.parse()

    def set_payload(self, payload):
        self.body = payload

    def parse(self):
        self.records = []
        recordPos = 0

        try:
            while recordPos < len(self.body.parts):
                recordPos = self._parse_variable_data_rec(recordPos)
        except IndexError:
            raise

    def _parse_variable_data_rec(self, startPos):
        lowerBoundary = 0
        upperBoundary = 0

        # self.body.debug_fields(startPos, 1)

        rec = TelegramVariableDataRecord()

        # Data Information Block
        rec.dib.parts.append(self.body.parts[startPos])

        if rec.dib.is_eoud:  # End of User Data
            if rec.dib.more_records_follow:
                self.records.append(rec)

            if rec.dib.is_manufacturer_specific:
                rec.dataField.parts = \
                self.body.parts[startPos + 1:]

                # Add remaining data
                self.records.append(rec)

            return len(self.body.parts)

        elif rec.dib.function_type == \
                FunctionType.SPECIAL_FUNCTION_FILL_BYTE:
            return startPos + 1

        if rec.dib.has_extension_bit:
            for count, part in enumerate(
                    self.body.parts[startPos + 1:]):
                rec.dib.parts.append(part)

                if not rec.dib.has_extension_bit:
                    break

        # Value Information Block
        try:
            rec.vib.parts.append(self.body.parts[
                startPos + len(rec.dib.parts)])
        except IndexError:
            pass  # Hmm

        if rec.vib.without_extension_bit:
            var_lvext_p = startPos + len(rec.dib.parts) + len(rec.vib.parts)
            var_vife_len = self.body.parts[var_lvext_p]

            rec.vib.customVIF.parts = self.body.parts[var_lvext_p + 1:
                                                      var_lvext_p + 1 +
                                                      var_vife_len]

        if rec.vib.has_extension_bit:
            for count, part in enumerate(
                    self.body.parts[startPos + 1 +
                                    rec.vib.without_extension_bit +
                                    len(rec.dib.parts) +
                                    len(rec.vib.customVIF):]):
                rec.vib.parts.append(part)

                if not rec.vib.has_extension_bit:
                    break

        lowerBoundary = (startPos +
                         rec.vib.without_extension_bit +
                         len(rec.dib.parts) +
                         len(rec.vib.customVIF) +
                         len(rec.vib.parts))

        length, encoding = rec.dib.length_encoding

        # if there exist a LVAR Byte at the beginning of the data field,
        # change the data field length
        if encoding == DataEncoding.ENCODING_VARIABLE_LENGTH:
            lp = self.body.parts[lowerBoundary]

            if lp <= 0xBF:
                length = lp
            elif 0xC0 <= lp <= 0xCF:
                length = (lp - 0xC0) * 2
            elif 0xD0 <= lp <= 0xDF:
                length = (lp - 0xD0) * 2
            elif 0xE0 <= lp <= 0xEF:
                length = (lp - 0xE0)
            elif 0xF0 <= lp <= 0xFA:
                length = (lp - 0xF0)

            lowerBoundary += 1

        upperBoundary = lowerBoundary + length

        if length == 0:
            return upperBoundary

        # Data Block
        if len(self.body.parts) >= upperBoundary:
            dataField = TelegramField()
            dataField.parts += \
                self.body.parts[lowerBoundary:upperBoundary]

            # MSB Order
            if not self._parent.bodyHeader.isLSBOrder:
                dataField.parts.reverse()

            rec.dataField = dataField

        self.records.append(rec)

        return upperBoundary

    def more_records_follow(self):
        for rec in self.records:
            if rec.more_records_follow:
                return True

        return False

    def to_JSON(self):
        return json.dumps(self.interpreted, sort_keys=False, indent=4, use_decimal=True)


class TelegramBodyHeader(object):
    MODE_BIT_MASK = 0x04  # 0000 0100 (6.1 CI-Field Mode bit)
    CI_VARIABLE_DATA = [0x72, 0x76, 0x78]
    CI_FIXED_DATA = [0x73, 0x77]

    def __init__(self):
        self._ci_field = TelegramField()        # control information field
        self._id_nr_field = TelegramField()     # identification number field
        self._manufacturer_field = TelegramField()     # manufacturer
        self._version_field = TelegramField()          # version
        self._measure_medium_field = TelegramField()   # measured medium
        self._acc_nr_field = TelegramField()           # access number
        self._status_field = TelegramField()           # status
        self._sig_field = TelegramField()              # signature field

    def load(self, bodyHeader):
        if len(bodyHeader) == 1:
            self.ci_field = bodyHeader[0]
        else:
            self.ci_field = bodyHeader[0]

            if self.noDataHeader:
                return

            if len(bodyHeader) >= 5:
                self.id_nr_field = bodyHeader[1:5]
            if len(bodyHeader) >= 7:
                self.manufacturer_field = bodyHeader[5:7]
            if len(bodyHeader) >= 8:
                self.version_field = bodyHeader[7]
            if len(bodyHeader) >= 9:
                self.measure_medium_field = bodyHeader[8]

            if len(bodyHeader) > 9:
                self.acc_nr_field = bodyHeader[9]
                self.status_field = bodyHeader[10]
                self.sig_field = bodyHeader[11:13]
                if not self.isLSBOrder:
                    self.id_nr_field.parts.reverse()
                    self.manufacturer_field.parts.reverse()
                    self.sig_field.parts.reverse()

    @property
    def id_nr(self):
        """ID number of telegram in reverse byte order"""
        return self._id_nr_field[::-1]

    @property
    def isLSBOrder(self):
        return not (self._ci_field.parts[0] & self.MODE_BIT_MASK)

    @property
    def noDataHeader(self):
        return (self._ci_field.parts and self._ci_field.parts[0] == 0x78)

    @property
    def isVariableData(self):
        return (self._ci_field.parts[0] in self.CI_VARIABLE_DATA)

    @property
    def isFixedData(self):
        return (self._ci_field.parts[0] in self.CI_FIXED_DATA)

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
    def measure_medium_field(self):
        return self._measure_medium_field

    @measure_medium_field.setter
    def measure_medium_field(self, value):
        self._measure_medium_field = TelegramField(value)

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
    def sig_field(self):
        return self._sig_field

    @sig_field.setter
    def sig_field(self, value):
        self._sig_field = TelegramField(value)

    @property
    def interpreted(self):
        if self.noDataHeader:
            return {
                'type': hex(self.ci_field.parts[0])
            }
        return {
            'type': hex(self.ci_field.parts[0]),
            'identification': ", ".join(map("0x{:02x}".format, self.id_nr)),
            'manufacturer': self.manufacturer_field.decodeManufacturer,
            'version': hex(self.version_field.parts[0]),
            'medium': hex(self.measure_medium_field.parts[0]),
            'access_no': self.acc_nr_field.parts[0],
            'status': hex(self.status_field.parts[0]),
            'sign': ", ".join(map(hex, self.sig_field.parts))
        }

    def to_JSON(self):
        return json.dumps(self.interpreted, sort_keys=False, indent=4, use_decimal=True)


class TelegramBody(object):
    def __init__(self):
        self._bodyHeader = TelegramBodyHeader()
        self._bodyPayload = TelegramBodyPayload(parent=self)
        self._bodyHeaderLength = 13

    @property
    def isVariableData(self):
        return self._bodyHeader.isVariableData

    @property
    def isFixedData(self):
        return self._bodyHeader.isFixedData

    @property
    def noDataHeader(self):
        return (self._bodyHeader.noDataHeader)

    @property
    def bodyHeaderLength(self):
        if self.noDataHeader:
            return 1  # need to offset with 1
        return self._bodyHeaderLength

    @bodyHeaderLength.setter
    def bodyHeaderLength(self, val):
        self._bodyHeaderLength = val

    @property
    def bodyHeader(self):
        return self._bodyHeader

    @bodyHeader.setter
    def bodyHeader(self, val):
        self._bodyHeader = TelegramBodyHeader()
        self._bodyHeader.load(val[0:self.bodyHeaderLength])

    @property
    def bodyPayload(self):
        return self._bodyPayload

    @bodyPayload.setter
    def bodyPayload(self, val):
        self._bodyPayload = TelegramBodyPayload(val, parent=self)

    @property
    def more_records_follow(self):
        return self._bodyPayload.more_records_follow

    @property
    def interpreted(self):
        return {
            'header': self.bodyHeader.interpreted,
            'records': self.bodyPayload.interpreted,
        }

    def load(self, body):
        self.bodyHeader = body[0:self.bodyHeaderLength]
        self.bodyPayload.load(body[self.bodyHeaderLength:])

    def parse(self):
        self.bodyPayload.parse()  # Load from raw into records

    def debug(self):
        self.bodyHeader.debug()
        self.bodyPayload.debug()

    def to_JSON(self):
        return json.dumps(self.interpreted, sort_keys=False, indent=4, use_decimal=True)
