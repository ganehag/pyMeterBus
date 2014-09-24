from telegram_field import TelegramField
from telegram_variable_data_record import TelegramVariableDataRecord

from dif_telegram_field import DIFTelegramField, DIFETelegramField
from vif_telegram_field import VIFTelegramField, VIFETelegramField

from telegram_data_field import TelegramDataField

class TelegramBodyPayload(object):
	def __init__(self, payload=None):
		self._bodyField = TelegramField()
		if payload != None:
			self._bodyField = TelegramField(payload)

		self._records = []

	@property
	def records(self):
	    return self._records
	@records.setter
	def records(self, value):
	    self._records = value


	@property
	def bodyField(self):
	    return self._bodyField
	@bodyField.setter
	def bodyField(self, value):
	    self._bodyField = TelegramField(value)


	def createTelegramBodyPayload(self, payload):
		self.bodyField = payload

	def setTelegramBodyPayload(self, payload):
		self.bodyField = payload

	def parse(self):
		self.records = []

		recordPos = 0

		try:
			while recordPos < len(self.bodyField.fieldParts):
				recordPos = self._parseVariableDataRecord(recordPos)
		except IndexError:
			print "UserDATA runaway -----------------------------------"

	def _parseVariableDataRecord(self, startPos):
		lowerBoundary = 0
		upperBoundary = 0
		lvarBit       = False

		rec             = TelegramVariableDataRecord()
		dif             = DIFTelegramField()
		dif.fieldParts.append( self.bodyField.fieldParts[startPos] )
		dif.parse()

		rec.dif         = dif

		if dif.isEndOfUserData:
			# only manufacturer specific data left, stop parsing
			return len(self.bodyField.fieldParts)

		difeList = []
		if dif.isExtensionBit:
			difeList = self._parseDIFEFIelds(startPos + 1)

		rec.difes += difeList

		# Increase startPos by 1 (DIF) and the count of DIFEs
		vif = VIFTelegramField()
		vif.fieldParts.append( self.bodyField.fieldParts[startPos + 1 + len(difeList)] ) # append
		vif.parent = rec
		vif.parse()

		rec.vif = vif

		vifeList = []

		if vif.isExtensionBit:
			# increase startPosition by 2 (DIF and VIF) and the number of DIFEs
			vifeList = self._parseVIFEFields(startPos + 2 + len(difeList), rec)
			# check if there exist a LVAR Byte at the beginning of the data field
			lvarBit = vifeList[0].isLvarBit

		rec.vifes += vifeList

		lowerBoundary = startPos + 2 + len(difeList) + len(vifeList)

		# if there exist a LVAR Byte at the beginning of the data field, change the data field length
		if lvarBit:
			dif.dataFieldLength = self.bodyField.fieldParts[lowerBoundary]
			lowerBoundary += 1

		upperBoundary = lowerBoundary + dif.dataFieldLength

		if dif.dataFieldLength == 0:
			return upperBoundary

		if len(self.bodyField.fieldParts) >= upperBoundary:
			dataField = TelegramDataField(rec)
			dataField.fieldParts += self.bodyField.fieldParts[lowerBoundary:upperBoundary]
			dataField.parse()
			rec.dataField = dataField

		self.records.append(rec)

		return upperBoundary

	def _parseDIFEFields(self, position):
		difeList        = []
		extensionBitSet = True
		dife            = None
		
		while extensionBitSet == True:
			if len(self.bodyField.fieldParts) < position:
				# TODO: Throw Exception
				pass
			dife = self._processSingleDIFEField(self.bodyField.fieldParts[position])
			difeList.append(dife)
			extensionBitSet = dife.isExtensionBit
			position += 1
		
		return difeList

	def _parseVIFEFields(self, position, parent):
		vifeList = []
		extensionBitSet = True
		vife = None
		
		while extensionBitSet == True:
			if len(self.bodyField.fieldParts) < position:
				# TODO: throw exception
				pass

			vife = self._processSingleVIFEField(self.bodyField.fieldParts[position], parent)
			vifeList.append(vife)
			extensionBitSet = vife.isExtensionBit
			position += 1
		
		return vifeList

	def _processSingleDIFEField(self, fieldValue):
		dife = DIFETelegramField()
		dife.fieldParts += fieldValue
		return dife

	def _processSingleVIFEField(self, fieldValue, parent):
		vife = VIFETelegramField()
		vife.fieldParts.append(fieldValue)
		vife.parent = parent
		vife.parse()
		return vife

	def debug(self):
		print "-------------------------------------------------------------"
		print "-------------------- BEGIN BODY PAYLOAD ---------------------"
		print "-------------------------------------------------------------"

		if self.records:
			for i in range(0, len(self.records)):
				print "RECORD:", i 
				self.records[i].debug()
		print "-------------------------------------------------------------"
		print "--------------------- END BODY PAYLOAD ----------------------"
		print "-------------------------------------------------------------"

class TelegramBodyHeader(object):
	def __init__(self):
		self._ciField     = TelegramField() # control information field
		self._idNrField   = TelegramField() # identification number field
		self._mField      = TelegramField() # manufacturer
		self._vField      = TelegramField() # version
		self._medField    = TelegramField() # measured medium
		self._accNrField  = TelegramField() # access number
		self._statusField = TelegramField() # status
		self._sigField    = TelegramField() # signature field

	def createTelegramBodyHeader(self, bodyHeader):
		self.ciField     = bodyHeader[0]
		self.idNrField   = bodyHeader[1:5]
		self.mField      = bodyHeader[5:7]
		self.vField      = bodyHeader[7]
		self.medField    = bodyHeader[8]
		self.accNrField  = bodyHeader[9]
		self.statusField = bodyHeader[10]
		self.sigField    = bodyHeader[11:13]

	@property
	def idNr(self):
		"""ID number of telegram in reverse byte order"""
		return self._idNrField[::-1] # Extended Slices (What's New in Python 2.3)
	
	@property
	def ciField(self):
		return self._ciField
	@ciField.setter
	def ciField(self, value):
		self._ciField = TelegramField(value)

	@property
	def idNrField(self):
		return self._idNrField
	@idNrField.setter
	def idNrField(self, value):
		self._idNrField = TelegramField(value)

	@property
	def mField(self):
	    return self._mField
	@mField.setter
	def mField(self, value):
	    self._mField = TelegramField(value)

	@property
	def vField(self):
	    return self._vField
	@vField.setter
	def vField(self, value):
	    self._vField = TelegramField(value)

	@property
	def medField(self):
	    return self._medField
	@medField.setter
	def medField(self, value):
	    self._medField = TelegramField(value)

	@property
	def accNrField(self):
	    return self._accNrField
	@accNrField.setter
	def accNrField(self, value):
	    self._accNrField = TelegramField(value)

	@property
	def statusField(self):
	    return self._statusField
	@statusField.setter
	def statusField(self, value):
	    self._statusField = TelegramField(value)

	@property
	def sigField(self):
	    return self._sigField
	@sigField.setter
	def sigField(self, value):
	    self._sigField = TelegramField(value)

	def debug(self):
		print "Type of TelegramBodyHeader:".ljust(30), 	hex(self.ciField.fieldParts[0])
		print "Identification#:".ljust(30),				", ".join(map(hex, self.idNr))
		print "Manufacturer:".ljust(30), 				self.mField.decodeManufacturer
		print "Version:".ljust(30),						hex(self.vField.fieldParts[0])
		print "Medium:".ljust(30),						hex(self.medField.fieldParts[0])
		print "StatusField:".ljust(30),					hex(self.statusField.fieldParts[0])
		print "Sig-Fields:".ljust(30),					", ".join(map(hex, self.sigField.fieldParts)) # FIX PARSE

class TelegramBody(object):
	def __init__(self):
		self._bodyHeader       = TelegramBodyHeader()
		self._bodyPayload      = TelegramBodyPayload()
		self._bodyHeaderLength = 13

	@property
	def bodyHeaderLength(self):
		return self._bodyHeaderLength
	
	@property
	def bodyHeader(self):
	    return self._bodyHeader
	@bodyHeader.setter
	def bodyHeader(self, value):
	    self._bodyHeader = TelegramBodyHeader()
	    self._bodyHeader.createTelegramBodyHeader(value[0:self.bodyHeaderLength])

	@property
	def bodyPayload(self):
		return self._bodyPayload
	@bodyPayload.setter
	def bodyPayload(self, value):
		self._bodyPayload = TelegramBodyPayload(value)

	def createTelegramBody(self, body):
		self.bodyHeader = body[0:self.bodyHeaderLength]
		self.bodyPayload.createTelegramBodyPayload(body[self.bodyHeaderLength:])

	def parse(self):
		self.bodyPayload.parse() # Load from raw into records

	def debug(self):
		self.bodyHeader.debug()
		self.bodyPayload.debug()