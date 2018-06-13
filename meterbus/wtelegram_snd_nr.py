from builtins import (bytes, str, open, super, range,
                      zip, round, input, int, pow, object)

import simplejson as json

from .wtelegram_header import WTelegramHeader
from .wtelegram_body import WTelegramFrame
from .exceptions import MBusFrameDecodeError, MBusFrameCRCError, FrameMismatch


class WTelegramSndNr(WTelegramFrame):
    @staticmethod
    def parse(data):
        try:
            if data[1] != 0x44:  # SND-NR
                raise FrameMismatch()
        except IndexError:
            raise FrameMismatch()

        if data and len(data) < 11:
            raise MBusFrameDecodeError("Invalid M-Bus length")

        return WTelegramSndNr(data)

    def __init__(self, dbuf=None):
        tgr = dbuf
        if isinstance(dbuf, str):
            tgr = list(map(ord, dbuf))

        if tgr:
            super().__init__()
            self.load(tgr)

            if not self.check_crc():
                raise MBusFrameCRCError(self.compute_crc(),
                                        self.header.crcField.parts[0])

    def compute_crc(self):
        return (self.header.cField.parts[0] +
                self.header.aField.parts[0]) % 256

    def check_crc(self):
        return True
        # return self.compute_crc() == self.header.crcField.parts[0]

    def to_JSON(self):
        return json.dumps(self.interpreted, sort_keys=False, indent=4, use_decimal=True)
