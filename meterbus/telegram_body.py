import json

from .core_objects import DataEncoding, FunctionType
from .telegram_field import TelegramField
from .telegram_variable_data_record import TelegramVariableDataRecord
from .value_information_block import ValueInformationBlock


class TelegramBodyPayload(object):
    def __init__(self, payload=None):
        self._body = TelegramField()
        if payload is not None:
            self._body = TelegramField(payload)

        self._records = []

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

        # self.body.debug_fields(startPos, 0)

        rec = TelegramVariableDataRecord()

        # Data Information Block
        rec.dib.parts.append(self.body.parts[
            startPos])

        if rec.dib.is_eoud:  # End of User Data
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
        rec.vib.parts.append(self.body.parts[
            startPos + len(rec.dib.parts)])

        if rec.vib.has_extension_bit:
            for count, part in enumerate(
                    self.body.parts[startPos + 1 + len(rec.dib.parts):]):
                rec.vib.parts.append(part)

                if not rec.vib.has_extension_bit:
                    break

        lowerBoundary = startPos + len(rec.dib.parts) + len(rec.vib.parts)

        length, encoding = rec.dib.length_encoding

        # if there exist a LVAR Byte at the beginning of the data field,
        # change the data field length
        if encoding == DataEncoding.ENCODING_VARIABLE_LENGTH:
            length = self.body.parts[lowerBoundary]
            lowerBoundary += 1

        upperBoundary = lowerBoundary + length

        if length == 0:
            return upperBoundary

        # Data Block
        if len(self.body.parts) >= upperBoundary:
            dataField = TelegramField()
            dataField.parts += \
                self.body.parts[lowerBoundary:upperBoundary]
            rec.dataField = dataField

        self.records.append(rec)

        return upperBoundary

    def to_JSON(self):
        d = [json.loads(r.to_JSON()) for r in self.records]
        return json.dumps(d, sort_keys=False, indent=4)


class TelegramBodyHeader(object):
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
        self.ci_field = bodyHeader[0]
        self.id_nr_field = bodyHeader[1:5]
        self.manufacturer_field = bodyHeader[5:7]
        self.version_field = bodyHeader[7]
        self.measure_medium_field = bodyHeader[8]
        self.acc_nr_field = bodyHeader[9]
        self.status_field = bodyHeader[10]
        self.sig_field = bodyHeader[11:13]

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

    def to_JSON(self):
        return json.dumps({
            'type': hex(self.ci_field.parts[0]),
            'identification': ", ".join(map(hex, self.id_nr)),
            'manufactorer': self.manufacturer_field.decodeManufacturer,
            'version': hex(self.version_field.parts[0]),
            'medium': hex(self.measure_medium_field.parts[0]),
            'access_no': self.acc_nr_field.parts[0],
            'status': hex(self.status_field.parts[0]),
            'sign': ", ".join(map(hex, self.sig_field.parts))
        }, sort_keys=False, indent=4)


class TelegramBody(object):
    def __init__(self):
        self._bodyHeader = TelegramBodyHeader()
        self._bodyPayload = TelegramBodyPayload()
        self._bodyHeaderLength = 13

    @property
    def bodyHeaderLength(self):
        return self._bodyHeaderLength

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
        self._bodyPayload = TelegramBodyPayload(val)

    def load(self, body):
        self.bodyHeader = body[0:self.bodyHeaderLength]
        self.bodyPayload.load(body[self.bodyHeaderLength:])

    def parse(self):
        self.bodyPayload.parse()  # Load from raw into records

    def debug(self):
        self.bodyHeader.debug()
        self.bodyPayload.debug()

    def to_JSON(self):
        return json.dumps({
            'header': json.loads(self.bodyHeader.to_JSON()),
            'records': json.loads(self.bodyPayload.to_JSON()),
        }, sort_keys=False, indent=4)
