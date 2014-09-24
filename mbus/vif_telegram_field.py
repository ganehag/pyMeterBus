from telegram_field import TelegramField
from mbus_support import switch
from mbus_protocol import *

class VIFTelegramField(TelegramField):
	EXTENSION_BIT_MASK        = 0x80 # 1000 0000
	LAST_TWO_BIT_OR_MASK      = 0x03 # 0000 0011
	LAST_THREE_BIT_OR_MASK    = 0x07 # 0000 0111
	UNIT_MULTIPLIER_MASK      = 0x7F # 0111 1111

	def __init__(self, parts=None):
		super(VIFTelegramField, self).__init__(parts)

		self._extensionBit = False
		self._mUnit        = Measure_Unit.NONE
		self._type         = None
		self._multiplier   = 0

		self._parent       = None # TelegramVariableDataRecord

	@property
	def isExtensionBit(self):
		return self._extensionBit

	@property
	def extensionBit(self):
		return self._extensionBit
	@extensionBit.setter
	def extensionBit(self, value):
		self._extensionBit = value
	
	

	@property
	def mUnit(self):
	    return self._mUnit
	@mUnit.setter
	def mUnit(self, value):
	    self._mUnit = value
	
	@property
	def type(self):
	    return self._type
	@type.setter
	def type(self, value):
	    self._type = value
	
	@property
	def multiplier(self):
	    return self._multiplier
	@multiplier.setter
	def multiplier(self, value):
	    self._multiplier = value

	@property
	def parent(self):
	    return self._parent
	@parent.setter
	def parent(self, value):
	    self._parent = value
	
	

	def parse(self):
		iVifField = self.fieldParts[0]

		if iVifField & VIFTelegramField.EXTENSION_BIT_MASK == VIFTelegramField.EXTENSION_BIT_MASK:
			self.extensionBit = True

		if iVifField == VIF_Unit_Multiplier_Masks.FIRST_EXT_VIF_CODES.value:
			# load from next VIFE according to table 29 from DIN_EN_13757_3
			self.type = VIF_Unit_Multiplier_Masks.FIRST_EXT_VIF_CODES

		elif iVifField == VIF_Unit_Multiplier_Masks.SECOND_EXT_VIF_CODES.value:
			# TODO: load from next VIFE according to table 28 from DIN_EN_13757_3
			self.type = VIF_Unit_Multiplier_Masks.SECOND_EXT_VIF_CODES

		else:
			# Get rid of the first (extension) bit
			iVifFieldNoExt = iVifField & VIFTelegramField.UNIT_MULTIPLIER_MASK

			# Check against complete (no wildcards) bit masks
			for case in switch(iVifFieldNoExt):
				if case(VIF_Unit_Multiplier_Masks.DATE.value):
					self.type = VIF_Unit_Multiplier_Masks.DATE
					self.parseDate(self.parent.dif.dataFieldLengthAndEncoding)
					break
				if case(VIF_Unit_Multiplier_Masks.DATE_TIME_GENERAL.value):
					### ????
					# self.type = VIF_Unit_Multiplier_Masks.DATE_TIME_GENERAL
					self.parseDate(self.parent.dif.dataFieldLengthAndEncoding)
					break
				if case(VIF_Unit_Multiplier_Masks.UNITS_FOR_HCA.value):
					# NO UNIT
					self.type = VIF_Unit_Multiplier_Masks.UNITS_FOR_HCA
					break
				if case(VIF_Unit_Multiplier_Masks.RES_THIRD_VIFE_TABLE.value):
					# NO UNIT
					self.type = VIF_Unit_Multiplier_Masks.RES_THIRD_VIFE_TABLE
					break
				if case(VIF_Unit_Multiplier_Masks.FABRICATION_NO.value):
					# NO UNIT
					self.type = VIF_Unit_Multiplier_Masks.FABRICATION_NO
					break
				if case(VIF_Unit_Multiplier_Masks.IDENTIFICATION.value):
					# NO UNIT
					self.type = VIF_Unit_Multiplier_Masks.IDENTIFICATION
					break
				if case(VIF_Unit_Multiplier_Masks.ADDRESS.value):
					# TODO
					self.type = VIF_Unit_Multiplier_Masks.ADDRESS
					break
				if case(VIF_Unit_Multiplier_Masks.VIF_FOLLOWING.value):
					# TODO: Plain String?
					self.type = VIF_Unit_Multiplier_Masks.VIF_FOLLOWING
					break
				if case(VIF_Unit_Multiplier_Masks.ANY_VIF.value):
					# TODO: Check 6.4
					self.type = VIF_Unit_Multiplier_Masks.ANY_VIF
					break
				if case(VIF_Unit_Multiplier_Masks.MANUFACTURER_SPEC.value):
					# TODO: VIFE and data is manufacturer specification
					self.type = VIF_Unit_Multiplier_Masks.MANUFACTURER_SPEC
					break
				if case():
					if self.parseLastTwoBitsSet(iVifFieldNoExt):
						pass
					elif self.parseLastThreeBitsSet(iVifFieldNoExt):
						pass
					else:
						print "EEEEERROORRRR"
						pass # TODO Handle Error

	def parseLastTwoBitsSet(self, iVifFieldNoExt):
		# set last two bits to 1 so that we can check against our other masks
		iVifFieldNoExtLastTwo = iVifFieldNoExt | VIFTelegramField.LAST_TWO_BIT_OR_MASK
		onlyLastTwoBits       = iVifFieldNoExt & VIFTelegramField.LAST_TWO_BIT_OR_MASK
		
		if iVifFieldNoExtLastTwo == VIF_Unit_Multiplier_Masks.ON_TIME.value:
			self.type = VIF_Unit_Multiplier_Masks.ON_TIME

			for case in switch(onlyLastTwoBits):
				if case(0):
					self.mUnit = Measure_Unit.SECONDS
					break
				if case(1):
					self.mUnit = Measure_Unit.MINUTES
					break
				if case(2):
					self.mUnit = Measure_Unit.HOURS
					break
				if case(3):
					self.mUnit = Measure_Unit.DAYS;
					break
				if case():
					# TODO: Exception Handling
					break
		
		elif iVifFieldNoExtLastTwo == VIF_Unit_Multiplier_Masks.OPERATING_TIME.value:
			self.type = VIF_Unit_Multiplier_Masks.OPERATING_TIME

		elif iVifFieldNoExtLastTwo == VIF_Unit_Multiplier_Masks.FLOW_TEMPERATURE.value:
			self.type = VIF_Unit_Multiplier_Masks.FLOW_TEMPERATURE
			self.multiplier = onlyLastTwoBits - 3
			self.mUnit = Measure_Unit.C

		elif iVifFieldNoExtLastTwo == VIF_Unit_Multiplier_Masks.RETURN_TEMPERATURE.value:
			self.type = VIF_Unit_Multiplier_Masks.RETURN_TEMPERATURE;
			self.multiplier = onlyLastTwoBits - 3
			self.mUnit = Measure_Unit.C

		elif iVifFieldNoExtLastTwo == VIF_Unit_Multiplier_Masks.TEMPERATURE_DIFFERENCE.value:
			self.type = VIF_Unit_Multiplier_Masks.TEMPERATURE_DIFFERENCE;
			self.multiplier = onlyLastTwoBits - 3
			self.mUnit = Measure_Unit.K

		elif iVifFieldNoExtLastTwo == VIF_Unit_Multiplier_Masks.EXTERNAL_TEMPERATURE.value:
			self.type = VIF_Unit_Multiplier_Masks.EXTERNAL_TEMPERATURE;
			self.multiplier = onlyLastTwoBits - 3
			self.mUnit = Measure_Unit.C

		elif iVifFieldNoExtLastTwo == VIF_Unit_Multiplier_Masks.PRESSURE.value:
			self.type = VIF_Unit_Multiplier_Masks.PRESSURE;
			self.multiplier = onlyLastTwoBits - 3
			self.mUnit = Measure_Unit.BAR

		elif iVifFieldNoExtLastTwo == VIF_Unit_Multiplier_Masks.AVG_DURATION.value:
			self.type = VIF_Unit_Multiplier_Masks.AVG_DURATION

		elif iVifFieldNoExtLastTwo == VIF_Unit_Multiplier_Masks.ACTUALITY_DURATION.value:
			self.type = VIF_Unit_Multiplier_Masks.ACTUALITY_DURATION

		else:
			return False

		return True


	def parseLastThreeBitsSet(self, iVifFieldNoExt):
		# set last three bits to 1 so that we can check against our other masks
		iVifFieldNoExtLastThree = (iVifFieldNoExt | VIFTelegramField.LAST_THREE_BIT_OR_MASK)

		onlyLastThreeBits = iVifFieldNoExt & VIFTelegramField.LAST_THREE_BIT_OR_MASK
		
		if iVifFieldNoExtLastThree == VIF_Unit_Multiplier_Masks.ENERGY_WH.value:
			self.type = VIF_Unit_Multiplier_Masks.ENERGY_WH
			self.multiplier = onlyLastThreeBits - 3
			self.mUnit = Measure_Unit.WH

		elif iVifFieldNoExtLastThree == VIF_Unit_Multiplier_Masks.ENERGY_J.value:
			self.type = VIF_Unit_Multiplier_Masks.ENERGY_J
			self.multiplier = onlyLastThreeBits
			self.mUnit = Measure_Unit.J

		elif iVifFieldNoExtLastThree == VIF_Unit_Multiplier_Masks.VOLUME.value:
			self.type = VIF_Unit_Multiplier_Masks.VOLUME
			self.multiplier = onlyLastThreeBits - 6
			self.mUnit = Measure_Unit.M3

		elif iVifFieldNoExtLastThree == VIF_Unit_Multiplier_Masks.MASS.value:
			self.type = VIF_Unit_Multiplier_Masks.MASS
			self.multiplier = onlyLastThreeBits - 3
			self.mUnit = Measure_Unit.KG

		elif iVifFieldNoExtLastThree == VIF_Unit_Multiplier_Masks.POWER_W.value:
			self.type = VIF_Unit_Multiplier_Masks.POWER_W
			self.multiplier = onlyLastThreeBits - 3
			self.mUnit = Measure_Unit.W

		elif iVifFieldNoExtLastThree == VIF_Unit_Multiplier_Masks.POWER_J_H.value:
			self.type = VIF_Unit_Multiplier_Masks.POWER_J_H
			self.multiplier = onlyLastThreeBits
			self.mUnit = Measure_Unit.J_H

		elif iVifFieldNoExtLastThree == VIF_Unit_Multiplier_Masks.VOLUME_FLOW.value:
			self.type = VIF_Unit_Multiplier_Masks.VOLUME_FLOW
			self.multiplier = onlyLastThreeBits - 6
			self.mUnit = Measure_Unit.M3_H

		elif iVifFieldNoExtLastThree == VIF_Unit_Multiplier_Masks.VOLUME_FLOW_EXT.value:
			self.type = VIF_Unit_Multiplier_Masks.VOLUME_FLOW_EXT
			self.multiplier = onlyLastThreeBits - 7
			self.mUnit = Measure_Unit.M3_MIN

		elif iVifFieldNoExtLastThree == VIF_Unit_Multiplier_Masks.VOLUME_FLOW_EXT_S.value:
			self.type = VIF_Unit_Multiplier_Masks.VOLUME_FLOW_EXT_S
			self.multiplier = onlyLastThreeBits - 9
			self.mUnit = Measure_Unit.M3_S

		elif iVifFieldNoExtLastThree == VIF_Unit_Multiplier_Masks.MASS_FLOW.value:
			self.type = VIF_Unit_Multiplier_Masks.MASS_FLOW
			self.multiplier = onlyLastThreeBits - 3
			self.mUnit = Measure_Unit.KG_H

		else:
			return False

		return True

	def parseDate(self, dateType):
		if dateType == Telegram_Date_Masks.DATE.value:
			self.mUnit = Measure_Unit.DATE

		elif dateType == Telegram_Date_Masks.DATE_TIME.value:
			self.type  = VIF_Unit_Multiplier_Masks.DATE_TIME
			self.mUnit = Measure_Unit.DATE_TIME

		elif dateType == Telegram_Date_Masks.EXT_TIME.value:
			self.type  = VIF_Unit_Multiplier_Masks.EXTENTED_TIME
			self.mUnit = Measure_Unit.DATE_TIME

		elif dateType == Telegram_Date_Masks.EXT_DATE_TIME.value:
			self.type  = VIF_Unit_Multiplier_Masks.EXTENTED_DATE_TIME
			self.mUnit = Measure_Unit.DATE_TIME_S

		else:
			# TODO: THROW EXCEPTION
			pass

	
	def debug(self):
		iVifFieldBits = self.fieldParts[0] & VIFTelegramField.UNIT_MULTIPLIER_MASK
		print "VIF-Field: "
		print "    Extension-Bit:".ljust(30), self.extensionBit
		print "    Field (String):".ljust(30), self.fieldParts[0]
		print "    Field (compl):".ljust(30), "{0:b}".format( self.fieldParts[0] )
		print "    Field-Value:".ljust(30), "{0:b}".format( iVifFieldBits )
		print "    Field-Type:".ljust(30),       self.type
		print "    Field-Unit:".ljust(30),       self.mUnit
		print "    Field-Multiplier:".ljust(30), self.multiplier

class VIFETelegramField(TelegramField):
	EXTENSION_BIT_MASK        = 0x80 # 1000 0000
	LAST_TWO_BIT_OR_MASK      = 0x03 # 0000 0011
	LAST_FOUR_BIT_OR_MASK     = 0x0F # 0000 1111
	UNIT_MULTIPLIER_MASK      = 0x7F # 0111 1111

	def __init__(self, parts=None):
		super(VIFETelegramField, self).__init__(parts)
		self._extensionBit = False
		self._lvarBit      = False
		self._mUnit        = Measure_Unit.NONE
		self._type         = None
		self._multiplier   = 0

		self._parent       = None # TelegramVariableDataRecord

	@property
	def isLvarBit(self):
	    return self._lvarBit

	@property
	def isExtensionBit(self):
	    return self._extensionBit

	@property
	def extensionBit(self):
	    return self._extensionBit
	@extensionBit.setter
	def extensionBit(self, value):
	    self._extensionBit = value
	
	@property
	def type(self):
	    return self._type
	@type.setter
	def type(self, value):
	    self._type = value
	
	@property
	def mUnit(self):
	    return self._mUnit
	@mUnit.setter
	def mUnit(self, value):
	    self._mUnit = value

	@property
	def lvarBit(self):
	    return self._lvarBit
	@lvarBit.setter
	def lvarBit(self, value):
	    self._lvarBit = value

	@property
	def multiplier(self):
	    return self._multiplier
	@multiplier.setter
	def multiplier(self, value):
	    self._multiplier = value

	@property
	def parent(self):
	    return self._parent
	@parent.setter
	def parent(self, value):
	    self._parent = value

	def parse(self):
		vifeField          = self.fieldParts[0]
		iVifeField         = vifeField

		# Get rid of the first (extension) bit
		iVifeFieldNoExt    = (iVifeField & self.UNIT_MULTIPLIER_MASK)

		if iVifeField & self.EXTENSION_BIT_MASK == self.EXTENSION_BIT_MASK:
			self.extensionBit = True

		# Check against complete (no wildcards) bit masks
		for case in switch(iVifeFieldNoExt):
			if case(VIF_Extension_FD_Mask.ACCESS_NUMBER.value):
				self.type = VIF_Extension_FD_Mask.ACCESS_NUMBER
				break
			if case(VIF_Extension_FD_Mask.MEDIUM.value):
				self.type = VIF_Extension_FD_Mask.MEDIUM
				break
			if case(VIF_Extension_FD_Mask.MANUFACTURER.value):
				self.type = VIF_Extension_FD_Mask.MANUFACTURER
				break
			if case(VIF_Extension_FD_Mask.PARAMETER_SET_ID.value):
				self.type = VIF_Extension_FD_Mask.PARAMETER_SET_ID
				self.parent.dif.dataFieldEncoding = TelegramEncoding.ENCODING_VARIABLE_LENGTH
				self.lvarBit = True
				break
			if case(VIF_Extension_FD_Mask.MODEL_VERSION.value):
				self.type = VIF_Extension_FD_Mask.MODEL_VERSION
				break
			if case(VIF_Extension_FD_Mask.HARDWARE_VERSION.value):
				self.type = VIF_Extension_FD_Mask.HARDWARE_VERSION
				break
			if case(VIF_Extension_FD_Mask.SOFTWARE_VERSION.value):
				self.type = VIF_Extension_FD_Mask.SOFTWARE_VERSION
				break
			if case(VIF_Extension_FD_Mask.FIRMWARE_VERSION.value):
				self.type = VIF_Extension_FD_Mask.FIRMWARE_VERSION
				break
			if case(VIF_Extension_FD_Mask.CUSTOMER_LOCATION.value):
				self.type = VIF_Extension_FD_Mask.CUSTOMER_LOCATION
				break
			if case(VIF_Extension_FD_Mask.CUSTOMER.value):
				self.type = VIF_Extension_FD_Mask.CUSTOMER
				break
			if case(VIF_Extension_FD_Mask.ACCESS_CODE_USER.value):
				self.type = VIF_Extension_FD_Mask.ACCESS_CODE_USER
				break
			if case(VIF_Extension_FD_Mask.ACCESS_CODE_OPERATOR.value):
				self.type = VIF_Extension_FD_Mask.ACCESS_CODE_OPERATOR
				break
			if case(VIF_Extension_FD_Mask.ACCESS_CODE_SYSTEM_OPERATOR.value):
				self.type = VIF_Extension_FD_Mask.ACCESS_CODE_SYSTEM_OPERATOR
				break
			if case(VIF_Extension_FD_Mask.ACCESS_CODE_DEVELOPER.value):
				self.type = VIF_Extension_FD_Mask.ACCESS_CODE_DEVELOPER
				break
			if case(VIF_Extension_FD_Mask.PASSWORD.value):
				self.type = VIF_Extension_FD_Mask.PASSWORD
				break
			if case(VIF_Extension_FD_Mask.ERROR_FLAGS.value):
				self.type = VIF_Extension_FD_Mask.ERROR_FLAGS
				break
			if case(VIF_Extension_FD_Mask.ERROR_MASKS.value):
				self.type = VIF_Extension_FD_Mask.ERROR_MASKS
				break
			if case(VIF_Extension_FD_Mask.RESERVED.value):
				self.type = VIF_Extension_FD_Mask.RESERVED
				break
			if case(VIF_Extension_FD_Mask.DIGITAL_OUTPUT.value):
				self.type = VIF_Extension_FD_Mask.DIGITAL_OUTPUT
				break
			if case(VIF_Extension_FD_Mask.DIGITAL_INPUT):
				self.type = VIF_Extension_FD_Mask.DIGITAL_INPUT
				break
			if case(VIF_Extension_FD_Mask.BAUDRATE.value):
				self.type = VIF_Extension_FD_Mask.BAUDRATE
				break
			if case(VIF_Extension_FD_Mask.RESPONSE_DELAY.value):
				self.type = VIF_Extension_FD_Mask.RESPONSE_DELAY
				break
			if case(VIF_Extension_FD_Mask.RETRY.value):
				self.type = VIF_Extension_FD_Mask.RETRY
				break
			if case(VIF_Extension_FD_Mask.RESERVED_2.value):
				self.type = VIF_Extension_FD_Mask.RESERVED_2
				break
			if case(): pass
				# TODO: Error handling and implementation of the other code + multipliers

	def debug(self):
		iVifeFieldBits = self.fieldParts[0] & VIFETelegramField.UNIT_MULTIPLIER_MASK
		print "VIFE-Field: "
		print "    Extension-Bit:".ljust(30), self.extensionBit
		print "    Field (String):".ljust(30), self.fieldParts[0]
		print "    Field (compl):".ljust(30), "{0:b}".format( self.fieldParts[0] )
		print "    Field-Value:".ljust(30), "{0:b}".format( iVifeFieldBits )
		print "    Field-Type:".ljust(30),       self.type
		print "    Field-Unit:".ljust(30),       self.mUnit
		print "    Field-Multiplier:".ljust(30), self.multiplier


