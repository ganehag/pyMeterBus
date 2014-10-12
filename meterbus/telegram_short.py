from .telegram_header import TelegramHeader
from .exceptions import MBusFrameDecodeError, MBusFrameCRCError, FrameMismatch


class TelegramShort(object):
    @staticmethod
    def parse(data):
        if data and len(data) < 5:
            raise MBusFrameDecodeError("Invalid M-Bus length")

        if data[0] != 0x10:
            raise FrameMismatch()

        return TelegramShort(data)

    def __init__(self, dbuf=None):
        self._header = TelegramHeader()
        self._header.load(dbuf)

        if not self.check_crc():
            raise MBusFrameCRCError(self.compute_crc(),
                                    self.header.crcField.parts[0])

    @property
    def header(self):
        return self._header

    @header.setter
    def header(self, value):
        self._header = value

    def compute_crc(self):
        return (self.header.cField.parts[0] +
                self.header.aField.parts[0]) % 256

    def check_crc(self):
        return self.compute_crc() == self.header.crcField.parts[0]
