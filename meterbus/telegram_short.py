from .defines import *
from .telegram_header import TelegramHeader
from .exceptions import MBusFrameDecodeError, MBusFrameCRCError, FrameMismatch


class TelegramShort(object):
    @staticmethod
    def parse(data):
        if data is None:
            raise MBusFrameDecodeError("Data is None")

        if data is not None and len(data) < 5:
            raise MBusFrameDecodeError("Invalid M-Bus length")

        if data[0] != FRAME_SHORT_START:
            raise FrameMismatch()

        return TelegramShort(data)

    def __init__(self, dbuf=None):
        self._header = TelegramHeader()
        if dbuf != None:
            tgr = dbuf
            if isinstance(dbuf, str):
                tgr = list(map(ord, dbuf))

            elif isinstance(dbuf, bytes):
                tgr = list(dbuf)

            self._header.load(tgr)

            if not self.check_crc():
                raise MBusFrameCRCError(self.compute_crc(),
                                        self.header.crcField.parts[0])
        else:
           self._header.startField.parts = [FRAME_SHORT_START]
           self._header.lField.parts = [0x00]  # not used in short frame
           self._header.cField.parts = [0x00]
           self._header.aField.parts = [0x00]
           self._header.crcField.parts = [0x00]
           self._header.stopField.parts = [FRAME_STOP]

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

    def __len__(self):
       return 0x05

    def __iter__(self):
        yield self._header.startField.parts[0]
        yield self._header.cField.parts[0]
        yield self._header.aField.parts[0]
        yield self.compute_crc()
        yield self._header.stopField.parts[0]
