from .exceptions import MBusFrameDecodeError, MBusFrameCRCError, FrameMismatch


class TelegramACK(object):
    @staticmethod
    def parse(data):
        if data is None:
            raise MBusFrameDecodeError("Data is None")

        if data is not None and len(data) < 1:
            raise MBusFrameDecodeError("Invalid M-Bus length")

        if data[0] != 0xE5:
            raise FrameMismatch()

        return TelegramACK()

    def __init__(self, dbuf=None):
        self.type = 0xE5
        self.base_size = 1

    def __len__(self):
       return 1

    def __iter__(self):
        yield 0xE5
