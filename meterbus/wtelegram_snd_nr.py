import json

from .wtelegram_header import WTelegramHeader
from .wtelegram_body import WTelegramBody
from .exceptions import MBusFrameDecodeError, MBusFrameCRCError, FrameMismatch


class WTelegramSndNr(object):
    @staticmethod
    def parse(data):
        if len(data) < 2 and data[1] != 0x44:  # SND-NR
            raise FrameMismatch()

        if data and len(data) < 11:
            raise MBusFrameDecodeError("Invalid M-Bus length")

        return WTelegramSndNr(data)

    def __init__(self, dbuf=None):
        self._header = WTelegramHeader()
        self._body = WTelegramBody()

        tgr = dbuf
        if isinstance(dbuf, str):
            tgr = list(map(ord, dbuf))

        self.header.load(tgr)
        headerLength = self.header.headerLength
        self.body.load(tgr[headerLength:])

        if not self.check_crc():
            raise MBusFrameCRCError(self.compute_crc(),
                                    self.header.crcField.parts[0])

    @property
    def header(self):
        return self._header

    @header.setter
    def header(self, value):
        self._header = value

    @property
    def body(self):
        return self._body

    @body.setter
    def body(self, value):
        self._body = value

    def compute_crc(self):
        return (self.header.cField.parts[0] +
                self.header.aField.parts[0]) % 256

    def check_crc(self):
        return True
        # return self.compute_crc() == self.header.crcField.parts[0]

    def to_JSON(self):
        return json.dumps({
            'head': json.loads(self.header.to_JSON()),
            'body': json.loads(self.body.to_JSON())
        }, sort_keys=False, indent=4)
