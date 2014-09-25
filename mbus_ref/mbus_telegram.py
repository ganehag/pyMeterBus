from mbus_h import *

class switch(object):
    def __init__(self, value):
        self.value = value
        self.fall = False

    def __iter__(self):
        """Return the match method once, then stop"""
        yield self.match
        raise StopIteration

    def match(self, *args):
        """Indicate whether or not to enter a case suite"""
        if self.fall or not args:
            return True
        elif self.value in args: # changed for v1.5, see below
            self.fall = True
            return True
        else:
            return False

class MBusDataInformationBlock(object):
	def __init__(self):
		self.dif = None # CHAR
		self.dife = []  # CHAR[10]

class MBusValueInformationBlock(object):
	def __init__(self):
		self.vif = None # CHAR
		self.vife = []  # CHAR[10]

		self.custom_vif = [] # CHAR[128]

class MBusTelegram(object):
	def __init__(self):
		self.type = None
		self.base_size = None

		self.start1       = 0
		self.length1      = 0
		self.length2      = 0
		self.start2       = 0
		self.control      = 0    
		self.address      = 0
		self.ctrl_info    = 0
		# variable data field
		self.checksum     = 0
		self.stop         = 0

		self.data_size    = 0

		self.data         = []
		self.records      = []

	@staticmethod
	def parse(data):
		raise MBusFrameDecodeError("Missing parse function for Frame")

	#------------------------------------------------------------------------------
	# Decode data and write to string
	#
	# Data format (for record->data data array)
	#
	# Length in Bit   Code    Meaning           Code      Meaning
	#      0          0000    No data           1000      Selection for Readout
	#      8          0001     8 Bit Integer    1001      2 digit BCD
	#     16          0010    16 Bit Integer    1010      4 digit BCD
	#     24          0011    24 Bit Integer    1011      6 digit BCD
	#     32          0100    32 Bit Integer    1100      8 digit BCD
	#   32 / N        0101    32 Bit Real       1101      variable length
	#     48          0110    48 Bit Integer    1110      12 digit BCD
	#     64          0111    64 Bit Integer    1111      Special Functions
	#
	# The Code is stored in record->drh.dib.dif
	#
	#/
	#/ Return a string containing the data
	#/
	# Source: MBDOC48.PDF
	#
	#------------------------------------------------------------------------------
	def data_record_decode(self, record):
		# Ignore extension bit

		vif  = record.drh['vib'].vif & MBUS_DIB_VIF_WITHOUT_EXTENSION
		vife = 0
		try:
			vife = record.drh['vib'].vife[0] & MBUS_DIB_VIF_WITHOUT_EXTENSION
		except IndexError:
			pass

		for case in switch(record.drh['dib'].dif & MBUS_DATA_RECORD_DIF_MASK_DATA):
			if case(0x00): # NO Data
				return ""

			if case(0x01): # 1 byte integer (8 bit)
				return self.int_decode(record.data)

			if case(0x02): # 2 byte (16 bit)

				if vif == 0x6C: # E110 1100  Time Point (date)
					#mbus_data_tm_decode(&time, record->data, 2);
					#snprintf(buff, sizeof(buff), "%04d-%02d-%02d",
					#                             (time.tm_year + 2000),
					#                             (time.tm_mon + 1),
					#                              time.tm_mday);
					pass
				else: # 2 byte integer
					return self.int_decode(record.data)

				break
			if case(0x03): # 3 byte (24 bit)
				return self.int_decode(record.data)

			if case(0x04): # 3 byte (32 bit)
				# E110 1101  Time Point (date/time)
				# E011 0000  Start (date/time) of tariff
				# E111 0000  Date and time of battery change
				if (vif == 0x6D) or \
					((record.drh['vib'].vif == 0xFD) and (vife == 0x30)) or \
					((record.drh['vib'].vif == 0xFD) and (vife == 0x70)):
					#mbus_data_tm_decode(&time, record->data, 4);
					#snprintf(buff, sizeof(buff), "%04d-%02d-%02dT%02d:%02d:%02d",
					#                             (time.tm_year + 2000),
					#                             (time.tm_mon + 1),
					#                              time.tm_mday,
					#                              time.tm_hour,
					#                              time.tm_min,
					#                              time.tm_sec);
					pass
					break

				else: # 4 byte integer
					return self.int_decode(record.data)
			
			if case(0x05): # 4 Byte Real (32 bit)
				return self.float_decode(record.data)

			if case(0x06): # 6 byte integer (48 bit)
				return long_long_decode(record.data)

			if case(0x07): # 8 byte integer (64 bit)
				return long_long_decode(record.data)

			# Disabled?
			#if case(0x08):
			#	break

			if case(0x09): # 2 digit BCD (8 bit)
				return int( self.bcd_decode(record.data) )

			if case(0x0A): # 4 digit BCD (16 bit)
				return int( self.bcd_decode(record.data) )

			if case(0x0B): # 6 digit BCD (24 bit)
				return int( self.bcd_decode(record.data) )

			if case(0x0C): # 8 digit BCD (32 bit)
				return int( self.bcd_decode(record.data) )

			if case(0x0E): # 12 digit BCD (48 bit)
				return int( self.bcd_decode(record.data) )

			if case(0x0F): # special functions
				# mbus_data_bin_decode(buff, record->data, record->data_len, sizeof(buff));
				break

			if case(0x0D): pass
			if case():
				return "Unknown DIF ({0})".format(hex(record.drh['dib'].dif))

		return "FIXME"

	##------------------------------------------------------------------------------
	## Lookup the unit from the VIB (VIF or VIFE)
	##
	##  Enhanced Identification
	##    E000 1000      Access Number (transmission count)
	##    E000 1001      Medium (as in fixed header)
	##    E000 1010      Manufacturer (as in fixed header)
	##    E000 1011      Parameter set identification
	##    E000 1100      Model / Version
	##    E000 1101      Hardware version #
	##    E000 1110      Firmware version #
	##    E000 1111      Software version #
	##------------------------------------------------------------------------------
	def vib_unit_lookup(self, vib):
		if vib.vif == 0xFD or vib.vif == 0xFB: # first type of VIF extention: see table 8.4.4

			if len(vib.vife) == 0:
				return "Missing VIF extension"

			elif vib.vife[0] == 0x08 or vib.vife[0] == 0x88:
				# E000 1000
				return "Access Number (transmission count)"

			elif vib.vife[0] == 0x09 or vib.vife[0] == 0x89:
				#E000 1001
				return "Medium (as in fixed header)"

			elif vib.vife[0] == 0x0A or vib.vife[0] == 0x8A:
				#E000 1010
				return "Manufacturer (as in fixed header)"

			elif vib.vife[0] == 0x0B or vib.vife[0] == 0x8B:
				#E000 1010
				return "Parameter set identification"
			elif vib.vife[0] == 0x0C or vib.vife[0] == 0x8C:
				# E000 1100
				return "Model / Version"
			elif vib.vife[0] == 0x0D or vib.vife[0] == 0x8D:
				# E000 1100
				return "Hardware version"
			elif vib.vife[0] == 0x0E or vib.vife[0] == 0x8E:
				# E000 1101
				return "Firmware version"
			elif vib.vife[0] == 0x0F or vib.vife[0] == 0x8F:
				# E000 1101
				return "Software version"
			elif vib.vife[0] == 0x16:
				# VIFE = E001 0110 Password
				return "Password"
			elif vib.vife[0] == 0x17 or vib.vife[0] == 0x97:
				# VIFE = E001 0111 Error flags
				return "Error flags"
			elif vib.vife[0] == 0x10:
				# VIFE = E001 0000 Customer location
				return "Customer location"
			elif vib.vife[0] == 0x11:
				# VIFE = E001 0001 Customer
				return "Customer"
			elif vib.vife[0] == 0x1A:
				# VIFE = E001 1010 Digital output (binary)
				return "Digital output (binary)"
			elif vib.vife[0] == 0x1B:
				# VIFE = E001 1011 Digital input (binary)
				return "Digital input (binary)"
			elif (vib.vife[0] & 0x70) == 0x40:
				# VIFE = E100 nnnn 10^(nnnn-9) V
				n = (vib.vife[0] & 0x0F)
				return "{0} V".format( mbus_unit_prefix(n-9) )
			elif (vib.vife[0] & 0x70) == 0x50:
				# VIFE = E101 nnnn 10nnnn-12 A
				n = (vib.vife[0] & 0x0F)
				return "{0} A".format( mbus_unit_prefix(n-12) )
			elif (vib.vife[0] & 0xF0) == 0x70:
				# VIFE = E111 nnn Reserved
				return "Reserved VIF extension"
			else:
				return "Unrecognized VIF extension: {0}".format( hex(vib.vife[0]) )

		elif vib.vif == 0x7C:
			# custom VIF
			return vib.custom_vif

		elif vib.vif == 0xFC and (vib.vife[0] & 0x78) == 0x70:
			# custom VIF
			n = vib.vife[0] & 0x07
			return "{0} {1}".format(mbus_unit_prefix(n-6), vib.custom_vif)


		return "FIXME" # mbus_vif_unit_lookup(vib->vif); # no extention, use VIF


	def data_record_func(self, record):
		for case in switch(record.drh['dib'].dif & MBUS_DATA_RECORD_DIF_MASK_FUNCTION):
			if case(0x00):
				return "Instantaneous value"
			if case(0x10):
				return "Maximum value"
			if case(0x20):
				return "Minimum value"
			if case(0x30):
				return "Value during error state"
			if case():
				return "Unknown"

	def data_record_storage_num(self, record):
		bit_index = 0
		result    = 0

		result |= (record.drh['dib'].dif & MBUS_DATA_RECORD_DIF_MASK_STORAGE_NO) >> 6
		bit_index += 1

		for item in record.drh['dib'].dife:
			result |= (item & MBUS_DATA_RECORD_DIFE_MASK_STORAGE_NO) << bit_index
			bit_index += 4


		return result

	def int_decode(self, int_data):
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

	def bcd_decode(self, bcd_data):
		val = 0
		i = len(bcd_data)
		while(i > 0):
			val = (val * 10 ) + ((bcd_data[i-1]>>4) & 0xF)
			val = (val * 10 ) + ( bcd_data[i-1]     & 0xF)

			i -= 1

		return val

	def decode_manufacturer(self, bytes):
		m_id  = self.int_decode(bytes)
		return "{0}{1}{2}".format(
			chr( ((m_id>>10) & 0x001F) + 64 ),
			chr( ((m_id>>5)  & 0x001F) + 64 ),
			chr( ((m_id)     & 0x001F) + 64 )
		)

	def __repr__(self):
		x = {
			MBUS_FRAME_TYPE_ACK:     'MBUS_FRAME_TYPE_ACK',
			MBUS_FRAME_TYPE_SHORT:   'MBUS_FRAME_TYPE_SHORT',
			MBUS_FRAME_TYPE_CONTROL: 'MBUS_FRAME_TYPE_CONTROL',
			MBUS_FRAME_TYPE_LONG:    'MBUS_FRAME_TYPE_LONG'
		}

		return "<MBusTelegram: {0}>"#.format(x[self.type])
