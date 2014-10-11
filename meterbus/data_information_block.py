from .core_objects import DataEncoding, FunctionType
from .telegram_field import TelegramField


class DataInformationBlock(TelegramField):
    EXTENSION_BIT_MASK = 0x80      # 1000 0000
    FUNCTION_MASK = 0x30           # 0011 0000
    DATA_FIELD_MASK = 0x0F         # 0000 1111

    def __init__(self, parts=None):
        super(DataInformationBlock, self).__init__(parts)

    @property
    def has_extension_bit(self):
        """Check for extension bit on last byte"""
        try:
            return (self.parts[-1] & self.EXTENSION_BIT_MASK) > 0
        except IndexError:
            return False

    @property
    def has_lvar_bit(self):
        """returns true if first VIFE has LVAR active"""
        try:
            return (self.parts[1] & self.EXTENSION_BIT_MASK) > 0
        except IndexError:
            return False

    @property
    def is_eoud(self):
        """Check for end of user data bit VIF byte"""
        try:
            dif = self.parts[0]
            if dif in [0x0F, 0x1F]:
                return True
        except IndexError:
            pass

        return False

    @property
    def function_type(self):
        if self.parts[0] == 0x0F:
            return FunctionType.SPECIAL_FUNCTION

        elif self.parts[0] == 0x2F:
            return FunctionType.SPECIAL_FUNCTION_FILL_BYTE

        return FunctionType(
            (self.parts[0] & self.FUNCTION_MASK) >> 4)

    @property
    def length_encoding(self):
        len_enc = self.parts[0] & self.DATA_FIELD_MASK

        return {
            0: (0, DataEncoding.ENCODING_NULL),
            1: (len_enc, DataEncoding.ENCODING_INTEGER),
            2: (len_enc, DataEncoding.ENCODING_INTEGER),
            3: (len_enc, DataEncoding.ENCODING_INTEGER),
            4: (len_enc, DataEncoding.ENCODING_INTEGER),
            5: (4, DataEncoding.ENCODING_REAL),
            6: (6, DataEncoding.ENCODING_INTEGER),
            7: (8, DataEncoding.ENCODING_INTEGER),
            8: (0, DataEncoding.ENCODING_NULL),
            9: (len_enc - 8, DataEncoding.ENCODING_BCD),
            10: (len_enc - 8, DataEncoding.ENCODING_BCD),
            11: (len_enc - 8, DataEncoding.ENCODING_BCD),
            12: (len_enc - 8, DataEncoding.ENCODING_BCD),
            13: (6, DataEncoding.ENCODING_VARIABLE_LENGTH),
            14: (6, DataEncoding.ENCODING_BCD),
            15: (0, DataEncoding.ENCODING_NULL)  # Not right FIXME
        }[len_enc]
