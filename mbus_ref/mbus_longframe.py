import json
from mbus_c import *
from mbus_h import *
from mbus_telegram import *
from exceptions import *

class MBusLongFrame(MBusTelegram):
	def __init__(self, dbuf=None):
		super(MBusLongFrame, self).__init__()

	def compute_crc(self):
		return sum(self.data) % 256
		
	def check_crc(self):
		return self.compute_crc() == self.checksum

	@staticmethod
	def parse(data):
		if data and len(data) < MBUS_FRAME_BASE_SIZE_LONG:
			raise MBusFrameDecodeError("Invalid M-Bus length")

		if data[0] != MBUS_FRAME_LONG_START:
			raise MBusFrameDecodeError("Wrong start byte")

		base_frame           = MBusLongFrame()

		base_frame.type      = MBUS_FRAME_TYPE_LONG
		base_frame.base_size = MBUS_FRAME_BASE_SIZE_LONG

		base_frame.start1    = data[0]
		base_frame.length1   = data[1]
		base_frame.length2   = data[2]

		if base_frame.length1 < 3 or base_frame.length1 != base_frame.length2:
			raise MBusFrameDecodeError("Invalid M-Bus length1 value")

		base_frame.start2              = data[3]
		base_frame.control             = data[4]
		base_frame.address             = data[5]
		base_frame.control_information = data[6]
		base_frame.checksum            = data[-2]
		base_frame.stop                = data[-1]

		base_frame.data_size           = base_frame.length1 - 3
		base_frame.data                = data[4:-2]


		if not base_frame.check_crc():
			raise MBusFrameCRCError(base_frame.compute_crc(), base_frame.checksum)

		d = base_frame.parse_user_data()

		base_frame.records = []
		base_frame.info = d

		if 'records' in d:
		 	base_frame.records = d['records']

		return base_frame

	def dump_records(self):
		jdata = {
			'mbus_data': []
		}

		for idx, record in enumerate(self.records):
			row = {
				'id': idx,
				'function': None,
				'storage': None,
				'unit': None,
				'value': None
			}

			if record.drh['dib'].dif == MBUS_DIB_DIF_MANUFACTURER_SPECIFIC:
				row['function'] = 'manufacturer specific'
			elif record.drh['dib'].dif == MBUS_DIB_DIF_MORE_RECORDS_FOLLOW:
				row['function'] = 'more records'
			else:
				row['function'] = self.data_record_func(record)
				row['storage']  = self.data_record_storage_num(record)
				row['unit']     = self.vib_unit_lookup(record.drh['vib'])
				row['value']    = self.data_record_decode(record)
				# if ((tariff = mbus_data_record_tariff(record)) >= 0)
				# {
				# len += snprintf(&buff[len], sizeof(buff) - len, "        <Tariff>%ld</Tariff>\n",
				#                                 tariff);
				# len += snprintf(&buff[len], sizeof(buff) - len, "        <Device>%d</Device>\n", 
				#                                 mbus_data_record_device(record));
				# }



			jdata['mbus_data'].append(row)

		# self.print_hdr(self.info)
		print json.dumps(jdata, indent=4, separators=(',', ': '))


	def variable_medium_lookup(self, medium):
		for case in switch(medium):
			if case(MBUS_VARIABLE_DATA_MEDIUM_OTHER):
				return "Other"
			if case(MBUS_VARIABLE_DATA_MEDIUM_OIL):
				return "Oil"
			if case(MBUS_VARIABLE_DATA_MEDIUM_ELECTRICITY):
				return "Electricity"
			if case(MBUS_VARIABLE_DATA_MEDIUM_GAS):
				return "Gas"
			if case(MBUS_VARIABLE_DATA_MEDIUM_HEAT_OUT):
				return "Heat: Outlet"
			if case(MBUS_VARIABLE_DATA_MEDIUM_STEAM):
				return "Steam"
			if case(MBUS_VARIABLE_DATA_MEDIUM_HOT_WATER):
				return "Hot water"
			if case(MBUS_VARIABLE_DATA_MEDIUM_WATER):
				return "Water"
			if case(MBUS_VARIABLE_DATA_MEDIUM_HEAT_COST):
				return "Heat Cost Allocator"
			if case(MBUS_VARIABLE_DATA_MEDIUM_COMPR_AIR):
				return "Compressed Air"
			if case(MBUS_VARIABLE_DATA_MEDIUM_COOL_OUT):
				return "Cooling load meter: Outlet"
			if case(MBUS_VARIABLE_DATA_MEDIUM_COOL_IN):
				return "Cooling load meter: Inlet"
			if case(MBUS_VARIABLE_DATA_MEDIUM_HEAT_IN):
				return "Heat: Inlet"
			if case(MBUS_VARIABLE_DATA_MEDIUM_HEAT_COOL):
				return "Heat / Cooling load meter"
			if case(MBUS_VARIABLE_DATA_MEDIUM_BUS):
				return "Bus/System"
			if case(MBUS_VARIABLE_DATA_MEDIUM_UNKNOWN):
				return "Unknown Medium"
			if case(MBUS_VARIABLE_DATA_MEDIUM_COLD_WATER):
				return "Cold water"
			if case(MBUS_VARIABLE_DATA_MEDIUM_DUAL_WATER):
				return "Dual water"
			if case(MBUS_VARIABLE_DATA_MEDIUM_PRESSURE):
				return "Pressure"
			if case(MBUS_VARIABLE_DATA_MEDIUM_ADC):
				return "A/D Converter"
			if case(0x10): pass
			if case(0x20): return "Reserved"
			if case():
				return "Unknown medium ({0})".format(hex(medium))

	def print_hdr(self, hdr):
		print "ID           = {0}".format( self.bcd_decode(hdr['id_bcd']) )
		print "Manufacturer = {0}".format( self.decode_manufacturer(hdr['manufacturer']) )
		print "Version      = {0}".format( hdr['version'] )
		print "Medium       = {0} 0x{1:02x}".format( self.variable_medium_lookup( hdr['medium'] ), hdr['medium'] )
		print "Access #     = {0}".format( hdr['access_no'] )
		print "Status       = {0}".format( hdr['status'] )
		print "Signature    = 0x{0:02x}{1:02x}".format( *hdr['signature'])

	def parse_user_data(self, user_data=None):
		if user_data == None:
			user_data = self.data

		# 
		# var: user_data
		# C, A, CI + User Data sections

		### USER
		dType = None
		dError = None

		#
		# This entire block acts on data outside User Data...
		#
		direction = self.control & MBUS_CONTROL_MASK_DIR

		if direction == MBUS_CONTROL_MASK_DIR_S2M:
			if self.control_information == MBUS_CONTROL_INFO_ERROR_GENERAL:
				dType = MBUS_DATA_TYPE_ERROR

				if len(user_data) > 3:
					dError = user_data[3]
				else:
					dError = 0

			elif self.control_information == MBUS_CONTROL_INFO_RESP_FIXED:
				if len(user_data) <= 3:
					print "Got zero data_size."
					return -1

				dType = MBUS_DATA_TYPE_FIXED

			elif self.control_information == MBUS_CONTROL_INFO_RESP_VARIABLE:
				if len(user_data) <= 3:
					print "Got zero data_size."
					return -1

				dType = MBUS_DATA_TYPE_VARIABLE

		else:
			print "Wrong direction in frame (master to slave)"
			return -1

		if dType != None:
			for case in switch(dType):
				if case(MBUS_DATA_TYPE_ERROR):
					break

				if case(MBUS_DATA_TYPE_FIXED):
					return self.data_fixed_parse(user_data[3:])

				if case(MBUS_DATA_TYPE_VARIABLE):
					return self.parse_variable_data(user_data[3:])

		else:
			print "Unknown control information {0}".format( hex(self.control_information) )
			return -1

	def parse_variable_data(self, data):
		# print "Attempting to parse variable data [size = {0}]".format(len(data))
		# for c in data:
		# 	print hex(c), "",
		# print ""

		if len(data) < MBUS_DATA_VARIABLE_HEADER_LENGTH:
			print "Variable header too short."
			return -1

		hdr = {
			"id_bcd": data[0:4],
			"manufacturer": data[4:6],
			"version": data[6],
			"medium": data[7],
			"access_no": data[8],
			"status": data[9],
			"signature": data[10:12],
			"records": []
		}

		more_records_follow = False

		# print "A", self.data_size
		i = MBUS_DATA_VARIABLE_HEADER_LENGTH
		while i < self.data_size:
			# Skip filler DIF=0x2F
			if data[i] & 0xFF == MBUS_DIB_DIF_IDLE_FILLER:
				i += 1
				continue

			# copy timestamp
			# memcpy((void *)&(record->timestamp), (void *)&(frame->timestamp), sizeof(time_t));

			newRecord = MBusRecord()

			# Read and parse DIB (= DIF + DIFE)
			newRecord.drh['dib'].dif = data[i]

			if newRecord.drh['dib'].dif == MBUS_DIB_DIF_MANUFACTURER_SPECIFIC or \
			   newRecord.drh['dib'].dif == MBUS_DIB_DIF_MORE_RECORDS_FOLLOW:

				if newRecord.drh['dib'].dif & 0xFF == MBUS_DIB_DIF_MORE_RECORDS_FOLLOW:
					more_records_follow = True

				i += 1

				# just copy the remaining data as it is vendor specific
				# and append it as a record
				newRecord.data_len = self.data_size - i
				newRecord.data = data[i:i+newRecord.data_len] # eat remaining
				i += newRecord.data_len
				self.records.append( newRecord )
				continue

			# calculate length of data record
			# newRecord.setDataLen(newRecord.drh['dib'].dif)

			while ((i < self.data_size) and (data[i] & MBUS_DIB_DIF_EXTENSION_BIT)):
				newRecord.drh['dib'].dife.append( data[i+1] )
				i += 1

			i += 1

			# Read and parse VIF
			newRecord.drh['vib'].vif = data[i]
			i += 1
			
			if (newRecord.drh['vib'].vif & MBUS_DIB_VIF_WITHOUT_EXTENSION) == 0x7C:
				# variable length VIF in ASCII format
				var_vif_len = data[i]
				i += 1

				newRecord.drh['vib'].custom_vif = data[i:i+var_vif_len]

				i += var_vif_len


			# VIFE
			if newRecord.drh['vib'].vif & MBUS_DIB_VIF_EXTENSION_BIT:
				newRecord.drh['vib'].vife.append( data[i] )

				while ((i < self.data_size) and (data[i] & MBUS_DIB_VIF_EXTENSION_BIT)):
					newRecord.drh['vib'].vife.append( data[i+1] )
					i += 1

				i += 1


			# Re-calculate data length, if of variable length type
			if (newRecord.drh['dib'].dif & MBUS_DATA_RECORD_DIF_MASK_DATA) == 0x0D: # flag for variable length data
				if data[i] <= 0xBF:
					newRecord.data_len = data[i]
					i += 1

				elif data[i] >= 0xC0 and data[i] <= 0xCF:
					newRecord.data_len = (d - 0xC0) * 2
					i += 1

				elif data[i] >= 0xD0 and data[i] <= 0xDF:
					rnewRecord.data_len = (data[i] - 0xD0) * 2
					i += 1

				elif data[i] >= 0xE0 and data[i] <= 0xEF:
					newRecord.data_len = data[i] - 0xE0
					i += 1

				elif data[i] >= 0xF0 and data[i] <= 0xFA:
					newRecord.data_len = data[i] - 0xF0
					i += 1

			# if (i + record->data_len > frame->data_size)
			#    snprintf(error_str, sizeof(error_str), "Premature end of record at data.");

			newRecord.data = data[i:i+newRecord.data_len()]
			i += newRecord.data_len()

			# And action
			hdr['records'].append( newRecord )

		# Exit stage left
		return hdr
