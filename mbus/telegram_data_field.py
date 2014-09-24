from mbus_support import *
from mbus_protocol import *
from telegram_field import TelegramField

class TelegramDataField(TelegramField):
	REAL_FRACTION             = 0x7FFFFF   # 23-Bit (fraction of real)
	REAL_EXPONENT             = 0x7F80000  # 24-Bit to 31-Bit (exponent of real)
	REAL_SIGN                 = 0x80000000 # 32-Bit (signum of real)
	SIGN                      = 0x01       # Mask for signum

	def __init__(self, parent=None):
		super(TelegramDataField, self).__init__()
		self._parent = parent

	@property
	def parent(self):
	    return self._parent
	@parent.setter
	def parent(self, value):
	    self._parent = value

	def parse(self):
		enc        = self.parent.dif.dataFieldEncoding
		length     = self.parent.dif.dataFieldLength
		unit       = self.parent.vif.mUnit
		multiplier = self.parent.vif.multiplier

		if length != len(self.fieldParts):
			# TODO: Throw exception
			return

		#print enc
		#print length
		#print unit
		#print multiplier

		if self.parseDate(unit):
			# value is parsed, we are done here
			return

		for case in switch(enc):
			if case(TelegramEncoding.ENCODING_INTEGER):
				self.parsedValue = self.decodeInt * pow(10, multiplier)
				break
			if case(TelegramEncoding.ENCODING_BCD):
				self.parsedValue = self.decodeBCD * pow(10, multiplier)
				# print self.
				break
			if case(TelegramEncoding.ENCODING_REAL):
				self.parsedValue = self.decodeReal * pow(10, multiplier)
				break
			if case(TelegramEncoding.ENCODING_VARIABLE_LENGTH):
				self.parsedValue = self.decodeASCII
				break
			if case(TelegramEncoding.ENCODING_NULL): pass
			if case():
				# TODO: Exception
				break

	def parseDate(self, dateType):
		for case in switch(dateType):
			if case(Measure_Unit.DATE):
				# Type G: Day.Month.Year
				self.parsedValue = self.decodeDate
				break
			if case(Measure_Unit.DATE_TIME):
				# Type F: Day.Month.Year Hour:Minute
				self.parsedValue = self.decodeDateTime
				break
			if case(Measure_Unit.TIME):
				# Typ J: Hour:Minute:Second
				self.parsedValue = self.decodeTimeWithSeconds
				break
			if case(Measure_Unit.DATE_TIME_S):
				# Typ I: Day.Month.Year Hour:Minute:Second
				self.parsedValue = self.decodeDateTimeWithSeconds
				break
			if case():
				return False

		return True

	def debug(self):
		print "Field-Value (bytes):".ljust(30), ", ".join(map(hex, self.fieldParts))
		print "Field-Value:".ljust(30), self.parsedValue