import simplejson as json
from .telegram_field import TelegramField


class WTelegramHeader(object):
    def __init__(self):
        # self._startField = TelegramField()
        self._lField = TelegramField()
        self._cField = TelegramField()
        # self._crcField = TelegramField()
        # self._stopField = TelegramField()

        self._headerLength = 2
        # self._headerLengthCRCStop = 8

    @property
    def headerLength(self):
        return self._headerLength

    # @property
    # def headerLengthCRCStop(self):
    #     return self._headerLengthCRCStop

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
    def interpreted(self):
        return {
            'length': hex(self.lField.parts[0]),
            'c': hex(self.cField.parts[0]),
        }

    # @property
    # def crcField(self):
    #     return self._crcField

    # @crcField.setter
    # def crcField(self, value):
    #     self._crcField = TelegramField(value)

    # @property
    # def stopField(self):
    #     return self._stopField

    # @stopField.setter
    # def stopField(self, value):
    #     self._stopField = TelegramField(value)

    def load(self, hat):
        header = hat
        if isinstance(hat, str):
            header = list(map(ord, hat))

        # self.startField = header[0]
        self.lField = header[0]
        self.cField = header[1]
        # self.crcField = header[-2]
        # self.stopField = header[-1]

    def to_JSON(self):
        return json.dumps(self.interpreted, sort_keys=False, indent=4, use_decimal=True)
