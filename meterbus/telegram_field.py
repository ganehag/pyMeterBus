import struct
from .core_objects import DateCalculator

from builtins import (bytes, str, open, super, range,
                      zip, round, input, int, pow, object)


class TelegramField(object):
    def __init__(self, parts=None):
        self._parts = []

        if parts is not None:
            if isinstance(parts, str):
                self.parts += list(map(ord, parts))

            elif isinstance(parts, (list, tuple)):
                self.parts += parts

            else:
                self.parts += [parts]

    @property
    def decodeInt(self):
        int_data = self.parts
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
        bcd_data = self.parts
        val = 0
        i = len(bcd_data)
        while i > 0:
            val = (val * 10) + ((bcd_data[i-1] >> 4) & 0xF)
            val = (val * 10) + (bcd_data[i-1] & 0xF)

            i -= 1

        return val

    @property
    def decodeReal(self):
        real_data = self.parts
        return struct.unpack('f', bytes(real_data))[0]

    @property
    def decodeManufacturer(self):
        m_id = self.decodeInt
        return "{0}{1}{2}".format(
            chr(((m_id >> 10) & 0x001F) + 64),
            chr(((m_id >> 5) & 0x001F) + 64),
            chr(((m_id) & 0x001F) + 64))

    @property
    def decodeASCII(self):
        return "".join(map(chr, reversed(self.parts)))

    @property
    def decodeRAW(self):
        return " ".join(map(lambda x: "%02X" % x, self.parts))

    @property
    def decodeDate(self):
        return DateCalculator.getDate(
            self.parts[0], self.parts[1], False)

    @property
    def decodeDateTime(self):
        return DateCalculator.getDateTime(
            self.parts[0], self.parts[1], self.parts[2],
            self.parts[3], False)

    @property
    def decodeTimeWithSeconds(self):
        return DateCalculator.getTimeWithSeconds(
            self.parts[0], self.parts[1], self.parts[2])

    @property
    def decodeDateTimeWithSeconds(self):
        return DateCalculator.getDateTimeWithSeconds(
            self.parts[0], self.parts[1], self.parts[2],
            self.parts[3], self.parts[4], False)

    @property
    def parts(self):
        return self._parts

    @parts.setter
    def parts(self, val):
        if isinstance(val, (list, tuple)):
            self._parts = list(val)
        else:
            self._parts = val

    @parts.deleter
    def parts(self):
        self._parts = []

    @property
    def parts_bytes(self):
        return list(map(ord, self._parts))
        # FIXME: ord? chr?

    def debug_fields(self, highlight, cval=0):
        color = ['\033[92m',
                 '\033[94m',
                 '\033[93m']

        ENDC = '\033[0m'

        if highlight >= len(self.parts):
            return

        d = []
        for c, item in enumerate(self.parts):
            if c == highlight:
                d.append(color[cval] + "{0:02X}".format(item) + ENDC)
            else:
                d.append("{0:02X}".format(item))

        print((" ".join(d)))

    def __str__(self):
        return " ".join(
            [hex(x).replace('0x', '').zfill(2) for x in self.parts])

    def __getitem__(self, key):
        return self.parts[key]

    def __len__(self):
        return len(self.parts)
