from .core_objects import DataEncoding, FunctionType
from .telegram_field import TelegramField


class DataInformationBlock(TelegramField):
    EXTENSION_BIT_MASK = 0x80  # 1000 0000
    FUNCTION_MASK = 0x30   # 0011 0000
    DATA_FIELD_MASK = 0x0F  # 0000 1111
    MORE_RECORDS_FOLLOW = 0x1F  # 0001 1111

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
    def is_manufacturer_specific(self):
        """Check for manufacturer specific record"""
        try:
            dif = self.parts[0]
            if dif in [0x0F]:
                return True
        except IndexError:
            pass

        return False

    @property
    def more_records_follow(self):
        try:
            dif = self.parts[0]
            return dif == self.MORE_RECORDS_FOLLOW
        except IndexError:
            pass

        return False

    @property
    def function_type(self):
        if self.is_eoud and self.more_records_follow:
            return FunctionType.MORE_RECORDS_FOLLOW

        elif self.parts[0] == 0x0F:
            # Manufacturer Specific
            return FunctionType.SPECIAL_FUNCTION

        elif self.parts[0] == 0x2F:
            return FunctionType.SPECIAL_FUNCTION_FILL_BYTE

        return FunctionType(
            (self.parts[0] & self.FUNCTION_MASK) >> 4)

    @property
    def is_variable_length(self):
        try:
            dif = self.parts[0]
            return (dif & self.DATA_FIELD_MASK) == 0x0D
        except IndexError:
            pass

        return False

    @property
    def length_encoding(self):
        len_enc = self.parts[0] & self.DATA_FIELD_MASK

        return {
            0: (0, DataEncoding.ENCODING_NULL),
            1: (len_enc, DataEncoding.ENCODING_INTEGER),  # 1 byte int [8 bit]
            2: (len_enc, DataEncoding.ENCODING_INTEGER),  # 2 byte int [16 bit] or date...
            3: (len_enc, DataEncoding.ENCODING_INTEGER),  # 3 byte int [24 bit]
            4: (len_enc, DataEncoding.ENCODING_INTEGER),  # 4 byte int [32 bit] or date...
            5: (4, DataEncoding.ENCODING_REAL),  # 4 byte float [32 bit]
            6: (6, DataEncoding.ENCODING_INTEGER),  # 6 byte int [48 bit]
            7: (8, DataEncoding.ENCODING_INTEGER),  # 8 byte int [64 bit]
            8: (0, DataEncoding.ENCODING_NULL),  # Nothing...
            9: (len_enc - 8, DataEncoding.ENCODING_BCD),  # 2 digit BCD [8 bit]
            10: (len_enc - 8, DataEncoding.ENCODING_BCD),  # 4 digit BCD [16 bit]
            11: (len_enc - 8, DataEncoding.ENCODING_BCD),  # 6 digit BCD [24 bit]
            12: (len_enc - 8, DataEncoding.ENCODING_BCD),  # 8 digit BCD [32 bit]
            13: (6, DataEncoding.ENCODING_VARIABLE_LENGTH),  # variable length
            14: (6, DataEncoding.ENCODING_BCD),  # 12 digit BCD [40 bit]
            15: (0, DataEncoding.ENCODING_NULL)  # Special Function FIXME
        }[len_enc]
