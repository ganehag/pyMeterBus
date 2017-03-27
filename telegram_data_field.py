import decimal

from telegram_field import TelegramField


class TelegramDataField(TelegramField):
    REAL_FRACTION = 0x7FFFFF    # 23-Bit (fraction of real)
    REAL_EXPONENT = 0x7F80000   # 24-Bit to 31-Bit (exponent of real)
    REAL_SIGN = 0x80000000      # 32-Bit (signum of real)
    SIGN = 0x01                 # Mask for signum

    def __init__(self, parent=None):
        super(TelegramDataField, self).__init__()
        self._parent = parent
        self._parsed_value = None

    @property
    def parsed_value(self):
        return self._parsed_value

    @parsed_value.setter
    def parsed_value(self, value):
        self._parsed_value = value

    @property
    def parent(self):
        return self._parent

    @parent.setter
    def parent(self, value):
        self._parent = value

    def __parse_date(self, dateType):
        for case in switch(dateType):
            if case(MeasureUnit.DATE):
                # Type G: Day.Month.Year
                self.parsed_value = self.decodeDate
                break
            if case(MeasureUnit.DATE_TIME):
                # Type F: Day.Month.Year Hour:Minute
                self.parsed_value = self.decodeDateTime
                break
            if case(MeasureUnit.TIME):
                # Typ J: Hour:Minute:Second
                self.parsed_value = self.decodeTimeWithSeconds
                break
            if case(MeasureUnit.DATE_TIME_S):
                # Typ I: Day.Month.Year Hour:Minute:Second
                self.parsed_value = self.decodeDateTimeWithSeconds
                break
            if case():
                return False

        return True

    def debug(self):
        print("Field-Value (bytes):".ljust(30), end=' ')
        print(", ".join(map(hex, self.field_parts)))
        print("Field-Value:".ljust(30), self.parsed_value)
