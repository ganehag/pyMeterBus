import struct
from mbus_protocol import DateCalculator

class TelegramField(object):
	def __init__(self, parts=None):
		self._fieldParts = []
		self._parsedValue = None

		if parts != None:
			if isinstance(parts, (list, tuple)):
				self.fieldParts += parts
			else:
				self.fieldParts += [ parts ]

	@property
	def decodeInt(self):
		int_data = self.fieldParts
		value = 0
		neg = int_data[-1] & 0x80

		i = len(int_data)
		while  i > 0:
			if neg:
				value = (value << 8) + (int_data[i - 1] ^ 0xFF)
			else:
				value = (value << 8) + int_data[i - 1]

			i -= 1

		if neg:
			value = (value * -1) - 1

		return value

	@property
	def decodeBCD(self):
		bcd_data = self.fieldParts
		val = 0
		i = len(bcd_data)
		while(i > 0):
			val = (val * 10 ) + ((bcd_data[i-1]>>4) & 0xF)
			val = (val * 10 ) + ( bcd_data[i-1]     & 0xF)

			i -= 1

		return val

	@property
	def decodeReal(self):
		real_data = self.fieldParts
		return struct.unpack('f', "".join( map(chr, real_data) ))[0]

	@property
	def decodeManufacturer(self):
		m_id  = self.decodeInt
		return "{0}{1}{2}".format(
			chr( ((m_id>>10) & 0x001F) + 64 ),
			chr( ((m_id>>5)  & 0x001F) + 64 ),
			chr( ((m_id)     & 0x001F) + 64 )
		)

	@property
	def decodeASCII(self):
		return "".join(map(chr, self.fieldParts))
	

	@property
	def decodeDate(self):
		return DateCalculator.getDate(self.fieldParts[0], self.fieldParts[1], False)

	@property
	def decodeDateTime(self):
		return DateCalculator.getDateTime(self.fieldParts[0], self.fieldParts[1], self.fieldParts[2], self.fieldParts[3], False)

	@property
	def decodeTimeWithSeconds(self):
		return DateCalculator.getTimeWithSeconds(self.fieldParts[0], self.fieldParts[1], self.fieldParts[2])

	@property
	def decodeDateTimeWithSeconds(self):
		return DateCalculator.getDateTimeWithSeconds(self.fieldParts[0], self.fieldParts[1], self.fieldParts[2], self.fieldParts[3], self.fieldParts[4], False)

	@property
	def fieldParts(self):
		return self._fieldParts

	@fieldParts.setter
	def fieldParts(self, val):
		if isinstance(val, (list, tuple)):
			self._fieldParts = list(val)
		else:
			self._fieldParts = val

	@fieldParts.deleter
	def fieldParts(self):
		self._fieldParts = []

	@property
	def fieldPartsBytes(self):
		return map(ord, self._fieldParts)

	@property
	def parsedValue(self):
	    return self._parsedValue
	@parsedValue.setter
	def parsedValue(self, value):
	    self._parsedValue = value
	

	def __str__(self):
		return " ".join(self.fieldParts)

	def __getitem__(self, key):
		return self.fieldParts[key]