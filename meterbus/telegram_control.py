from .telegram_body import TelegramBody
from .telegram_header import TelegramHeader
from .exceptions import MBusFrameCRCError, MBusFrameDecodeError, MBusFrameEncodeError, FrameMismatch

from .defines import *

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

        if tgr is not None:
            headerLength = self.header.headerLength
            firstHeader = tgr[0:headerLength]

            # Copy CRC and stopByte into header
            resultHeader = firstHeader + tgr[-2:]

            self.header.load(resultHeader)

            if self.header.lField.parts[0] != 3:
                raise FrameMismatch()

            self.body.load(tgr[headerLength:-2])

            if not self.check_crc():
                raise MBusFrameCRCError(self.compute_crc(),
                                        self.header.crcField.parts[0])
        else:
            self.header.cField.parts = [
                CONTROL_MASK_SND_UD | CONTROL_MASK_DIR_M2S
            ]
            self.body.bodyHeader.ci_field = 0x00

    def set_baud(self, baud):
        # From http://www.m-bus.com/mbusdoc/md6.php (6.1 CI-Field)
        command = ({
            300: 0xB8,  # Usergroup July 93
            600: 0xB9,  # Usergroup July 93
            1200: 0xBA,  # Usergroup July 93
            2400: 0xBB,  # Usergroup July 93
            4800: 0xBC,  # Usergroup July 93
            9600: 0xBD,  # Usergroup July 93
            19200: 0xBE,  # suggestion
            38400: 0xBF   # suggestion
        }).get(baud, None)
        if command is None:
            raise MBusFrameEncodeError("Invalid baudrate")

        self.body.bodyHeader.ci_field.parts = [command]

    def set_ram_readout(self):
        # From http://www.m-bus.com/mbusdoc/md6.php (6.1 CI-Field)
        # request readout of complete RAM content (Techem suggestion)
        self.body.bodyHeader.ci_field.parts = [0xB1]

    def set_eeprom_readout(self):
        # From http://www.m-bus.com/mbusdoc/md6.php (6.1 CI-Field)
        # request readout of complete RAM content (Techem suggestion)
        self.body.bodyHeader.ci_field.parts = [0xB4]

    def set_application_reset(self):
        # From http://www.m-bus.com/mbusdoc/md6.php (6.1 CI-Field)
        # application reset (Usergroup March 94)
        self.body.bodyHeader.ci_field.parts = [0x50]

    def set_software_test(self):
        # From http://www.m-bus.com/mbusdoc/md6.php (6.1 CI-Field)
        # start software test (Techem suggestion)
        self.body.bodyHeader.ci_field.parts = [0xB6]

    @property
    def address(self):
        return self._header.aField

    @address.setter
    def address(self, value):
        self._header.aField = value

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
        return (
            len(self.header.startField.parts) * 2 +
            len(self.header.lField.parts) * 2 +
            len(self.header.cField.parts) +
            len(self.header.aField.parts) +
            len(self.body.bodyHeader.ci_field.parts) +
            1 +
            len(self.header.stopField.parts)
        )

    def __iter__(self):
        yield self.header.startField.parts[0]
        yield len(self.body.bodyHeader.ci_field.parts) + 2
        yield len(self.body.bodyHeader.ci_field.parts) + 2
        yield self.header.startField.parts[0]

        yield self.header.cField.parts[0]
        yield self.header.aField.parts[0]
        yield self.body.bodyHeader.ci_field.parts[0]
        yield self.compute_crc()
        yield self._header.stopField.parts[0]
