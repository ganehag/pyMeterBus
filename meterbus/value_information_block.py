from .telegram_field import TelegramField


class ValueInformationBlock(TelegramField):
    EXTENSION_BIT_MASK = 0x80      # 1000 0000

    def __init__(self, parts=None):
        super(ValueInformationBlock, self).__init__(parts)

    @property
    def has_extension_bit(self):
        try:
            return (self.parts[-1] & self.EXTENSION_BIT_MASK) > 0
        except IndexError:
            return False

    @property
    def has_lvar_bit(self):
        """returns true if first VIFE has LVAR set"""
        try:
            return (self.parts[1] & self.EXTENSION_BIT_MASK) > 0
        except IndexError:
            return False
