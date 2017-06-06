from .telegram_body import TelegramBody
from .telegram_header import TelegramHeader
from .exceptions import MBusFrameCRCError, MBusFrameDecodeError, FrameMismatch


class TelegramControl(object):
    @staticmethod
    def parse(data):
        if data is None:
            raise MBusFrameDecodeError("Data is None")

        if data is not None and len(data) < 9:
            raise MBusFrameDecodeError("Invalid M-Bus length")

        if data[0] != 0x68:
            raise FrameMismatch()

        return TelegramControl(data)

    def __init__(self, dbuf=None):
        self._header = TelegramHeader()
        self._body = TelegramBody()

        tgr = dbuf

        if isinstance(dbuf, str):
            tgr = list(map(ord, dbuf))
        elif isinstance(dbuf, bytes):
            tgr = list(dbuf)

        headerLength = self.header.headerLength
        firstHeader = tgr[0:headerLength]

        # Copy CRC and stopByte into header
        resultHeader = firstHeader + tgr[-2:]

        self.header.load(resultHeader)

        if self.header.lField.parts[0] > 3:
            raise FrameMismatch()

        self.body.load(tgr[headerLength:-2])

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
                self.header.aField.parts[0] +
                self.body.bodyHeader.ci_field.parts[0]) % 256

    def check_crc(self):
        return self.compute_crc() == self.header.crcField.parts[0]

    def __len__(self):
       return 0x09

    def __iter__(self):
        yield self.header.startField.parts[0]
        yield self.header.lField.parts[0]
        yield self.header.lField.parts[0]
        yield self.header.startField.parts[0]

        yield self.header.cField.parts[0]
        yield self.header.aField.parts[0]
        yield self.body.bodyHeader.ci_field.parts[0]
        yield self.compute_crc()
        yield self._header.stopField.parts[0]
