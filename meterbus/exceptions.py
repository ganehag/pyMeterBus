class MBusError(Exception):
    """Base class for exceptions in this module."""
    pass


class FrameMismatch(MBusError):
    def __init__(self):
        pass

class MBusFrameDecodeError(MBusError):
    def __init__(self, msg):
        self.msg = msg


class MBusFrameCRCError(MBusError):
    def __init__(self, computed, expected):
        self.computed = computed
        self.expected = expected

class MbusFrameLengthError(MBusError):
    def __init__(self, length):
        self.length = length
