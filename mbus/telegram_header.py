import json
from telegram_field import TelegramField


class TelegramHeader(object):
    def __init__(self):
        self._startField = TelegramField()
        self._lField = TelegramField()
        self._cField = TelegramField()
        self._aField = TelegramField()
        self._crcField = TelegramField()
        self._stopField = TelegramField()

        self._headerLength = 6
        self._headerLengthCRCStop = 8

    @property
    def headerLength(self):
        return self._headerLength

    @property
    def headerLengthCRCStop(self):
        return self._headerLengthCRCStop

    @property
    def startField(self):
        return self._startField

    @startField.setter
    def startField(self, value):
        self._startField = TelegramField(value)

    @property
    def lField(self):
        return self._lField

    @lField.setter
    def lField(self, value):
        self._lField = TelegramField(value)

    @property
    def cField(self):
        return self._cField

    @cField.setter
    def cField(self, value):
        self._cField = TelegramField(value)

    @property
    def aField(self):
        return self._aField

    @aField.setter
    def aField(self, value):
        self._aField = TelegramField(value)

    @property
    def crcField(self):
        return self._crcField

    @crcField.setter
    def crcField(self, value):
        self._crcField = TelegramField(value)

    @property
    def stopField(self):
        return self._stopField

    @stopField.setter
    def stopField(self, value):
        self._stopField = TelegramField(value)

    def createTelegramHeader(self, hat):
        header = hat
        if isinstance(hat, basestring):
            header = hat.split(" ")

        self.startField = header[0]
        self.lField = header[1]
        self.lField = header[2]      # Re-set
        self.startField = header[3]  # Re-set
        self.cField = header[4]
        self.aField = header[5]
        self.crcField = header[-2]
        self.stopField = header[-1]

    def debug(self):
        print "Start Field:".ljust(30), 		hex(self.startField.field_parts[0])
        print "Length of Telegram:".ljust(30),	hex(self.lField.field_parts[0])
        print "C-Field (mode):".ljust(30),		hex(self.cField.field_parts[0])
        print "A-Field (mode):".ljust(30),		hex(self.aField.field_parts[0])
        print "CRC:".ljust(30),					hex(self.crcField.field_parts[0])
        print "Stop Field:".ljust(30),			hex(self.stopField.field_parts[0])

    def to_JSON(self):
        return json.dumps({
            'start': hex(self.startField.field_parts[0]),
            'length': hex(self.lField.field_parts[0]),
            'c': hex(self.cField.field_parts[0]),
            'a': hex(self.aField.field_parts[0]),
            'crc': hex(self.crcField.field_parts[0]),
            'stop': hex(self.stopField.field_parts[0])
        }, sort_keys=False, indent=4)
