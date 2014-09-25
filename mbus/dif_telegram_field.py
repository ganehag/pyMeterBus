from telegram_field import TelegramField
from mbus_support import switch
from mbus_protocol import *


class DIFTelegramField(TelegramField):
    FUNCTION_MASK = 0x30        # 0011 0000
    EXTENSION_BIT = 0x80        # 1000 0000
    DATA_FIELD_MASK = 0x0F      # 0000 1111
    FILL_BYTES_MASK = 0x2F
    LSB_SAVE_NUMBER_BIT = 0x40  # 0100 0000

    def __init__(self, parts=None):
        super(DIFTelegramField, self).__init__(parts)

        self._extension_bit = False
        self._save_number_bit = False
        self._end_of_user_data_bit = False

        # functionType of the Telegram
        # 00b (0) -> Instantaneous value
        # 01b (1) -> Maximum value
        # 10b (2) -> Minimum value
        # 11b (3) -> value during error state
        self._function_type = TelegramFunctionType.INSTANTANEOUS_VALUE

        # encoding and length of Telegram
        # 0000 (0-Bit) -> No data
        # 0001 (8-Bit) -> Integer/Binary
        # 0010 (16-Bit)-> Integer/Binary
        # 0011 (24-Bit)-> Integer/Binary
        # 0100 (32-Bit)-> Integer/Binary
        # 0101 (32-Bit)-> Real
        # 0110 (48-Bit)-> Integer/Binary
        # 0111 (64-Bit)-> Integer/Binary
        # 1000 (0-Bit) -> Selection for Readout
        # 1001 (8-Bit) -> 2 digit BCD
        # 1010 (16-Bit)-> 4 digit BCD
        # 1011 (24-Bit)-> 6 digit BCD
        # 1100 (32-Bit)-> 8 digit BCD
        # 1101 (32-Bit)-> variable length
        # 1110 (48-Bit)-> 12 digit BCD
        # 1111 (64-Bit)-> Special Functions
        self._data_field_length_and_encoding = 0

        # length of the data field in bytes
        # => value of 4 means 4 byte (32-Bit) length of data field
        self._data_field_length = 0
        self._data_field_encoding = TelegramEncoding.ENCODING_NULL

    @property
    def is_fill_byte(self):
        return self.function_type == \
            TelegramFunctionType.SPECIAL_FUNCTION_FILL_BYTE

    @property
    def is_extension_bit(self):
        return self._extension_bit

    @property
    def is_end_of_user_data(self):
        return self.end_of_user_data_bit

    @property
    def end_of_user_data_bit(self):
        return self._end_of_user_data_bit

    @end_of_user_data_bit.setter
    def end_of_user_data_bit(self, value):
        self._end_of_user_data_bit = value

    @property
    def save_number_bit(self):
        return self._save_number_bit

    @save_number_bit.setter
    def save_number_bit(self, value):
        self._save_number_bit = value

    @property
    def end_of_user_data_bit(self):
        return self._end_of_user_data_bit

    @property
    def function_type(self):
        return self._function_type

    @function_type.setter
    def function_type(self, value):
        self._function_type = value

    @property
    def data_field_length_and_encoding(self):
        return self._data_field_length_and_encoding

    @data_field_length_and_encoding.setter
    def data_field_length_and_encoding(self, value):
        self._data_field_length_and_encoding = value

    @property
    def data_field_length(self):
        return self._data_field_length

    @data_field_length.setter
    def data_field_length(self, value):
        self._data_field_length = value

    @property
    def data_field_encoding(self):
        return self._data_field_encoding

    @data_field_encoding.setter
    def data_field_encoding(self, value):
        self._data_field_encoding = value

    def parse(self):
        iDifField = self.field_parts[0]

        # there are some special functions where the other fields
        # don't need to be interpreted (for exampl 2F as a fill byte)
        for case in switch(iDifField):
            if case(0x0F):
                # MANUFACTURER Start of manufacturer specific data structures
                # to end of user data
                self.endOfUserDataBit = True
                return
            if case(0x1F):
                # Same meaning as DIF = 0Fh + More records follow in next
                # telegram
                self.endOfUserDataBit = True
                return
            if case(self.FILL_BYTES_MASK):
                self.function_type = \
                    TelegramFunctionType.SPECIAL_FUNCTION_FILL_BYTE
                self.dataFieldLength = 0
                return
            if case(0x3F):
                pass
            if case(0x4F):
                pass
            if case(0x5F):
                pass
            if case(0x6F):
                pass
            if case(0x7F):
                return

        if iDifField & self.EXTENSION_BIT is self.EXTENSION_BIT:
            self.extensionBit = True

        if iDifField & self.LSB_SAVE_NUMBER_BIT is self.LSB_SAVE_NUMBER_BIT:
            self.saveNumberBit = True

        # first extract only bit 5 and 6 of the telegram field
        # and afterwards move it to the right four bits so that we get
        # an integer value (this integer value is then translated to our
        # enum value)
        self.function_type = TelegramFunctionType(
            (iDifField & self.FUNCTION_MASK) >> 4)

        self.parse_encoding_and_length(iDifField)

    def parse_encoding_and_length(self, idif_field):
        self.data_field_length_and_encoding = idif_field & self.DATA_FIELD_MASK
        len_enc = self.data_field_length_and_encoding

        (self.data_field_length, self.data_field_encoding) = {
            0: (0, TelegramEncoding.ENCODING_NULL),
            1: (len_enc, TelegramEncoding.ENCODING_INTEGER),
            2: (len_enc, TelegramEncoding.ENCODING_INTEGER),
            3: (len_enc, TelegramEncoding.ENCODING_INTEGER),
            4: (len_enc, TelegramEncoding.ENCODING_INTEGER),
            5: (4, TelegramEncoding.ENCODING_REAL),
            6: (6, TelegramEncoding.ENCODING_INTEGER),
            7: (8, TelegramEncoding.ENCODING_INTEGER),
            8: (0, TelegramEncoding.ENCODING_NULL),
            9: (len_enc - 8, TelegramEncoding.ENCODING_BCD),
            10: (len_enc - 8, TelegramEncoding.ENCODING_BCD),
            11: (len_enc - 8, TelegramEncoding.ENCODING_BCD),
            12: (len_enc - 8, TelegramEncoding.ENCODING_BCD),
            13: (6, TelegramEncoding.ENCODING_VARIABLE_LENGTH),
            14: (6, TelegramEncoding.ENCODING_BCD),
            15: (None, None)
        }[len_enc]

        # for case in switch(self.data_field_length_and_encoding):
        #     if case(0):
        #         self.data_field_length = 0
        #         self.data_field_encoding = TelegramEncoding.ENCODING_NULL
        #         break
        #     if case(1):
        #         pass
        #     if case(2):
        #         pass
        #     if case(3):
        #         pass
        #     if case(4):
        #         self.data_field_length = self._dataFieldLengthAndEncoding
        #         self.data_field_encoding = TelegramEncoding.ENCODING_INTEGER
        #         break
        #     if case(5):
        #         # With data field = `1101b` several data types with variable
        #         # length can be used. The length of the data is given after
        #         # the DRH with the first byte of real data, which is here
        #         # called LVAR (e.g. LVAR = 02h: ASCII string with two
        #         # characters follows).
        #         self.data_field_length = 4
        #         self.data_field_encoding = TelegramEncoding.ENCODING_REAL
        #         break
        #     if case(6):
        #         self._dataFieldLength = 6
        #         self._dataFieldEncoding = TelegramEncoding.ENCODING_INTEGER
        #         break
        #     if case(7):
        #         self._dataFieldLength = 8
        #         self._dataFieldEncoding = TelegramEncoding.ENCODING_INTEGER
        #         break
        #     if case(8):
        #         self._dataFieldLength = 0
        #         self._dataFieldEncoding = TelegramEncoding.ENCODING_NULL
        #         break
        #     if case(9):
        #         pass
        #     if case(10):
        #         pass
        #     if case(11):
        #         pass
        #     if case(12):
        #         self._dataFieldLength = self._dataFieldLengthAndEncoding - 8
        #         self._dataFieldEncoding = TelegramEncoding.ENCODING_BCD
        #         break
        #     if case(13):
        #         self._dataFieldLength = 6
        #         self._dataFieldEncoding = \
        #             TelegramEncoding.ENCODING_VARIABLE_LENGTH
        #         break
        #     if case(14):
        #         self._dataFieldLength = 6
        #         self._dataFieldEncoding = TelegramEncoding.ENCODING_BCD
        #         break
        #     if case(15):
        #         # self._dataFieldLength   = 8
        #         # self._dataFieldEncoding = TelegramEncoding.ENCODING_NULL
        #         # We have already processed these values earlier
        #         break

    def debug(self):
        print "DIF-Field:"
        print "    Extension-Bit:".ljust(30), self.is_extension_bit
        print "    SaveNumber-Bit:".ljust(30), self._save_number_bit
        print "    EndOfUserData-Bit:".ljust(30), self.is_end_of_user_data
        print "    Function-Type:".ljust(30), self.function_type
        print "    DataField:".ljust(30), self.data_field_length_and_encoding
        print "    DataFieldEncoding:".ljust(30), self.data_field_encoding
        print "    dataFieldLength:".ljust(30), self.data_field_length


class DIFETelegramField(TelegramField):
    def ___init__(self, parts=None):
        super(DIFETelegramField, self).__init__(parts)
        self._extension_bit = False

    @property
    def extension_bit(self):
        return self._extension_bit

    @extension_bit.setter
    def extension_bit(self, value):
        self._extension_bit = value

    def debug(self):
        print "DIFE-Field:"
        print "    Extension-Bit:".ljust(30), self.extensionBit
        # TODO: // FIX!!!
