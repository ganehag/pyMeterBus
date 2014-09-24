from telegram_field import TelegramField
from mbus_support import switch
from mbus_protocol import *

class DIFTelegramField(TelegramField):
	EXTENSION_BIT          = 0x80     # 1000 0000
	LSB_SAVE_NUMBER_BIT    = 0x40     # 0100 0000
	FUNCTION_MASK          = 0x30     # 0011 0000
	DATA_FIELD_MASK        = 0x0F     # 0000 1111

	FILL_BYTES_MASK        = 0x2F

	def __init__(self, parts=None):
		super(DIFTelegramField, self).__init__(parts)

		self._extensionBit     = False
		self._saveNumberBit    = False
		self._endOfUserDataBit = False

		# functionType of the Telegram
		# 00b (0) -> Instantaneous value
		# 01b (1) -> Maximum value
		# 10b (2) -> Minimum value
		# 11b (3) -> value during error state
		self._functionType     = TelegramFunctionType.INSTANTANEOUS_VALUE

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
		self._dataFieldLengthAndEncoding = 0

		# length of the data field in bytes
		# => value of 4 means 4 byte (32-Bit) length of data field
		self._dataFieldLength = 0
		self._dataFieldEncoding = TelegramEncoding.ENCODING_NULL

	@property
	def isFillByte(self):
	    return self._functionType == TelegramFunctionType.SPECIAL_FUNCTION_FILL_BYTE

	@property
	def isExtensionBit(self):
	    return self._extensionBit

	@property
	def isEndOfUserData(self):
	    return self._endOfUserDataBit

	@property
	def saveNumberBit(self):
	    return self._saveNumberBit
	@saveNumberBit.setter
	def saveNumberBit(self, value):
	    self._saveNumberBit = value
	

	@property
	def endOfUserDataBit(self):
	    return self._endOfUserDataBit
	@endOfUserDataBit.setter
	def endOfUserDataBit(self, value):
	    self._endOfUserDataBit = value
	
	@property
	def functionType(self):
	    return self._functionType
	@functionType.setter
	def functionType(self, value):
	    self._functionType = value

	@property
	def dataFieldLengthAndEncoding(self):
	    return self._dataFieldLengthAndEncoding
	@dataFieldLengthAndEncoding.setter
	def dataFieldLengthAndEncoding(self, value):
	    self._dataFieldLengthAndEncoding = value
	
	@property
	def dataFieldLength(self):
	    return self._dataFieldLength
	@dataFieldLength.setter
	def dataFieldLength(self, value):
	    self._dataFieldLength = value
	
	@property
	def dataFieldEncoding(self):
	    return self._dataFieldEncoding
	@dataFieldEncoding.setter
	def dataFieldEncoding(self, value):
	    self._dataFieldEncoding = value
	

	def parse(self):
		iDifField = self.fieldParts[0]

		# there are some special functions where the other fields
		# don't need to be interpreted (for exampl 2F as a fill byte)
		for case in switch(iDifField):
			if case(0x0F):
				# MANUFACTURER Start of manufacturer specific data structures to end of user data
				self.endOfUserDataBit = True
				return
			if case(0x1F):
				# Same meaning as DIF = 0Fh + More records follow in next telegram
				self.endOfUserDataBit = True
				return
			if case(self.FILL_BYTES_MASK):
				self.functionType = TelegramFunctionType.SPECIAL_FUNCTION_FILL_BYTE
				self.dataFieldLength = 0
				return
			if case(0x3F): pass
			if case(0x4F): pass
			if case(0x5F): pass
			if case(0x6F): pass
			if case(0x7F):
				return

		if iDifField & self.EXTENSION_BIT == self.EXTENSION_BIT:
			self.extensionBit = True

		if iDifField & self.LSB_SAVE_NUMBER_BIT == self.LSB_SAVE_NUMBER_BIT:
			self.saveNumberBit = True

		# first extract only bit 5 and 6 of the telegram field
		# and afterwards move it to the right four bits so that we get 
		# an integer value (this integer value is then translated to our enum value)
		self.functionType = TelegramFunctionType( (iDifField & self.FUNCTION_MASK) >> 4 )

		self.parseEncodingAndLength(iDifField)

	def parseEncodingAndLength(self, iDifField):
		self._dataFieldLengthAndEncoding = iDifField & self.DATA_FIELD_MASK

		for case in switch(self._dataFieldLengthAndEncoding):
			if case(0):
				self._dataFieldLength = 0
				self._dataFieldEncoding = TelegramEncoding.ENCODING_NULL
				break
			if case(1): pass
			if case(2): pass
			if case(3): pass
			if case(4):
				self._dataFieldLength   = self._dataFieldLengthAndEncoding
				self._dataFieldEncoding = TelegramEncoding.ENCODING_INTEGER
				break
			if case(5):
				# With data field = `1101b` several data types with variable length can be used. The length of 
				# the data is given after the DRH with the first byte of real data, which is here called LVAR 
				# (e.g. LVAR = 02h: ASCII string with two characters follows).
				self._dataFieldLength   = 4
				self._dataFieldEncoding = TelegramEncoding.ENCODING_REAL
				break
			if case(6):
				self._dataFieldLength   = 6
				self._dataFieldEncoding = TelegramEncoding.ENCODING_INTEGER
				break
			if case(7):
				self._dataFieldLength   = 8
				self._dataFieldEncoding = TelegramEncoding.ENCODING_INTEGER
				break
			if case(8):
				self._dataFieldLength   = 0
				self._dataFieldEncoding = TelegramEncoding.ENCODING_NULL
				break
			if case(9): pass
			if case(10): pass
			if case(11): pass
			if case(12):
				self._dataFieldLength   = self._dataFieldLengthAndEncoding - 8
				self._dataFieldEncoding = TelegramEncoding.ENCODING_BCD
				break
			if case(13):
				self._dataFieldLength   = 6
				self._dataFieldEncoding = TelegramEncoding.ENCODING_VARIABLE_LENGTH
				break
			if case(14):
				self._dataFieldLength   = 6
				self._dataFieldEncoding = TelegramEncoding.ENCODING_BCD
				break
			if case(15):
				# self._dataFieldLength   = 8
				# self._dataFieldEncoding = TelegramEncoding.ENCODING_NULL
				# We have already processed these values earlier
				break

	def debug(self):
		print "DIF-Field:"
		print "    Extension-Bit:".ljust(30), self.isExtensionBit
		print "    SaveNumber-Bit:".ljust(30), self._saveNumberBit
		print "    EndOfUserData-Bit:".ljust(30), self.isEndOfUserData
		print "    Function-Type:".ljust(30), self.functionType
		print "    DataField:".ljust(30), self.dataFieldLengthAndEncoding
		print "    DataFieldEncoding:".ljust(30), self.dataFieldEncoding
		print "    dataFieldLength:".ljust(30), self.dataFieldLength

class DIFETelegramField(TelegramField):
	def ___init__(self, parts=None):
		super(DIFETelegramField, self).__init__(parts)
		self._extensionBit = False

	@property
	def extensionBit(self):
	    return self._extensionBit
	@extensionBit.setter
	def extensionBit(self, value):
	    self._extensionBit = value

	def debug(self):
		print "DIFE-Field:"
		print "    Extension-Bit:".ljust(30), self.extensionBit
		# TODO: // FIX!!!
	