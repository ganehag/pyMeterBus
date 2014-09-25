import struct
from mbus_protocol import DateCalculator


class TelegramField(object):
    def __init__(self, parts=None):
        self._field_parts = []
        self._parsed_value = None

        if parts is not None:
            if isinstance(parts, basestring):
                self.field_parts += map(ord, parts)

            elif isinstance(parts, (list, tuple)):
                self.field_parts += parts

            else:
                self.field_parts += [parts]

    @property
    def decodeInt(self):
        int_data = self.field_parts
        value = 0
        neg = int_data[-1] & 0x80

        i = len(int_data)
        while i > 0:
            if neg:
                value = (value << 8) + (int_data[i - 1] ^ 0xFF)
            else:
                value = (value << 8) + int_data[i - 1]

            i -= 1

        if neg:
            value = (value * -1) - 1

        return value

    @property
    def decodeBCD(self):
        bcd_data = self.field_parts
        val = 0
        i = len(bcd_data)
        while i > 0:
            val = (val * 10) + ((bcd_data[i-1] >> 4) & 0xF)
            val = (val * 10) + (bcd_data[i-1] & 0xF)

            i -= 1

        return val

    @property
    def decodeReal(self):
        real_data = self.field_parts
        return struct.unpack('f', "".join(map(chr, real_data)))[0]

    @property
    def decodeManufacturer(self):
        m_id = self.decodeInt
        return "{0}{1}{2}".format(
            chr(((m_id >> 10) & 0x001F) + 64),
            chr(((m_id >> 5) & 0x001F) + 64),
            chr(((m_id) & 0x001F) + 64))

    @property
    def decodeASCII(self):
        return "".join(map(chr, self.field_parts))

    @property
    def decodeDate(self):
        return DateCalculator.getDate(
            self.field_parts[0], self.field_parts[1], False)

    @property
    def decodeDateTime(self):
        return DateCalculator.getDateTime(
            self.field_parts[0], self.field_parts[1], self.field_parts[2],
            self.field_parts[3], False)

    @property
    def decodeTimeWithSeconds(self):
        return DateCalculator.getTimeWithSeconds(
            self.field_parts[0], self.field_parts[1], self.field_parts[2])

    @property
    def decodeDateTimeWithSeconds(self):
        return DateCalculator.getDateTimeWithSeconds(
            self.field_parts[0], self.field_parts[1], self.field_parts[2],
            self.field_parts[3], self.field_parts[4], False)

    @property
    def field_parts(self):
        return self._field_parts

    @field_parts.setter
    def field_parts(self, val):
        if isinstance(val, (list, tuple)):
            self._field_parts = list(val)
        else:
            self._field_parts = val

    @field_parts.deleter
    def field_parts(self):
        self._field_parts = []

    @property
    def field_parts_bytes(self):
        return map(ord, self._field_parts)
        # FIXME: ord? chr?

    @property
    def parsed_value(self):
        return self._parsed_value

    @parsed_value.setter
    def parsed_value(self, value):
        self._parsed_value = value

    def __str__(self):
        return " ".join(self.field_parts)

    def __getitem__(self, key):
        return self.field_parts[key]
