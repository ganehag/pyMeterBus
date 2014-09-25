import itertools, collections
import json

from mbus_h import *
from mbus_telegram import *

class MBusRecord(object):
	def __init__(self):
		self.drh = {
			'dib': MBusDataInformationBlock(), 
			'vib': MBusValueInformationBlock()
		}
		# self.data_len  = 0
		self.data      = None # data[234]
		self.timestamp = None

	def data_len(self):
		return {
			0x0: 0, 0x1: 1,
			0x2: 2, 0x3: 3,
			0x4: 4, 0x5: 4,
			0x6: 6, 0x7: 8,

			0x8: 0, 0x9: 1,
			0xA: 2, 0xB: 3,
			0xC: 4, 0xD: 0, # variable data length, data length stored in data field
			0xE: 6, 0xF: 8
		}[self.drh['dib'].dif & MBUS_DATA_RECORD_DIF_MASK_DATA]




#
# HEADER FOR VARIABLE LENGTH DATA FORMAT
#
    #Ident.Nr. Manufr. Version Medium Access No. Status  Signature
    #4 Byte    2 Byte  1 Byte  1 Byte   1 Byte   1 Byte  2 Byte

    # ex
    # 88 63 80 09 82 4D 02 04 15 00 00 00

#    unsigned id_bcd[4]         # 88 63 80 09
#    unsigned manufacturer[2]   # 82 4D
#    unsigned version           # 02
#    unsigned medium            # 04
#    unsigned access_no         # 15
#    unsigned status            # 00
#    unsigned signature[2]      # 00 00



#
# VARIABLE LENGTH DATA FORMAT
#
#    mbus_data_variable_header header

#    mbus_data_record *record
#    size_t nrecords

#    unsigned data
#    size_t  data_len

#    unsigned more_records_follow

    # are these needed/used?
#    unsigned mdh
#    unsigned mfg_data
#    size_t  mfg_data_len

#
# FIXED LENGTH DATA FORMAT
#
    # ex
    # 35 01 00 00 counter 2 = 135 l (historic value)
    #
    # e.g.
    #
    # 78 56 34 12 identification number = 12345678
    # 0A          transmission counter = 0Ah = 10d
    # 00          status 00h: counters coded BCD, actual values, no errors
    # E9 7E       Type&Unit: medium water, unit1 = 1l, unit2 = 1l (same, but historic)
    # 01 00 00 00 counter 1 = 1l (actual value)
    # 35 01 00 00 counter 2 = 135 l (historic value)

#    unsigned id_bcd[4]
#    unsigned tx_cnt
#    unsigned status
#    unsigned cnt1_type
#    unsigned cnt2_type
#    unsigned cnt1_val[4]
#    unsigned cnt2_val[4]


#
# ABSTRACT DATA FORMAT (error, fixed or variable length)
#


#    mbus_data_variable data_var
#    mbus_data_fixed    data_fix



#
# HEADER FOR SECONDARY ADDRESSING
#
    #Ident.Nr. Manufr. Version Medium
    #4 Byte    2 Byte  1 Byte  1 Byte

    # ex
    # 14 49 10 01 10 57 01 06

#    unsigned id_bcd[4]         # 14 49 10 01
#    unsigned manufacturer[2]   # 10 57
#    unsigned version           # 01
#    unsigned medium            # 06
