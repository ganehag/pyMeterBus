import simplejson as json
from .telegram_field import TelegramField


class TelegramHeader(object):
    def __init__(self):
        self._startField = TelegramField([0x68])
        self._lField = TelegramField([0x00])
        self._cField = TelegramField()
        self._aField = TelegramField()
        self._crcField = TelegramField()
        self._stopField = TelegramField([0x16])

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

    @property
    def interpreted(self):
        return {
            'start': hex(self.startField.parts[0]),
            'length': hex(self.lField.parts[0]),
            'c': hex(self.cField.parts[0]),
            'a': hex(self.aField.parts[0]),
            'crc': hex(self.crcField.parts[0]),
            'stop': hex(self.stopField.parts[0])
        }

    def load(self, hat):
        header = hat
        if isinstance(hat, str):
            header = list(map(ord, hat))

        if len(hat) == 8:
            self.startField = header[0]
            self.lField = header[1]
            self.lField = header[2]      # Re-set
            self.startField = header[3]  # Re-set
            self.cField = header[4]
            self.aField = header[5]
            self.crcField = header[-2]
            self.stopField = header[-1]
        elif len(hat) == 5:
            self.startField = header[0]
            self.cField = header[1]
            self.aField = header[2]
            self.crcField = header[-2]
            self.stopField = header[-1]

    def to_JSON(self):
        return json.dumps(self.interpreted, sort_keys=False, indent=4, use_decimal=True)
