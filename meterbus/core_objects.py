from enum import Enum


class MeasureUnit(Enum):
    KWH = "kWh"
    WH = "WH"
    J = "J"
    M3 = "m^3"
    L = "l"
    KG = "kg"
    W = "W"
    J_H = "J/h"
    M3_H = "m^3/h"
    M3_MIN = "m^3/min"
    M3_S = "m^3/s"
    KG_H = "kg/h"
    C = "C"
    K = "K"
    BAR = "bar"
    DATE = "date"
    TIME = "time"
    DATE_TIME = "date time"
    DATE_TIME_S = "date time to second"
    SECONDS = "seconds"
    MINUTES = "minutes"
    HOURS = "hours"
    DAYS = "days"
    NONE = "none"
    V = "V"
    A = "A"
    HCA = "H.C.A"
    CURRENCY = "Currency unit"
    BAUD = "Baud"
    BIT_TIMES = "Bittimes"
    PERCENT = "%"
    DBM = "dBm"


class FunctionType(Enum):
    INSTANTANEOUS_VALUE = 0
    MAXIMUM_VALUE = 1
    MINIMUM_VALUE = 2
    ERROR_STATE_VALUE = 3
    SPECIAL_FUNCTION = 4
    SPECIAL_FUNCTION_FILL_BYTE = 5
    MORE_RECORDS_FOLLOW = 6


class DataEncoding(Enum):
    ENCODING_NULL = 0
    ENCODING_INTEGER = 1
    ENCODING_REAL = 2
    ENCODING_BCD = 3
    ENCODING_VARIABLE_LENGTH = 4


class VIFUnit(Enum):
    ENERGY_WH = 0x07                # E000 0xxx
    ENERGY_J = 0x0F                 # E000 1xxx
    VOLUME = 0x17                   # E001 0xxx
    MASS = 0x1F                     # E001 1xxx
    ON_TIME = 0x23                  # E010 00xx
    OPERATING_TIME = 0x27           # E010 01xx
    POWER_W = 0x2F                  # E010 1xxx
    POWER_J_H = 0x37                # E011 0xxx
    VOLUME_FLOW = 0x3F              # E011 1xxx
    VOLUME_FLOW_EXT = 0x47          # E100 0xxx
    VOLUME_FLOW_EXT_S = 0x4F        # E100 1xxx
    MASS_FLOW = 0x57                # E101 0xxx
    FLOW_TEMPERATURE = 0x5B         # E101 10xx
    RETURN_TEMPERATURE = 0x5F       # E101 11xx
    TEMPERATURE_DIFFERENCE = 0x63   # E110 00xx
    EXTERNAL_TEMPERATURE = 0x67     # E110 01xx
    PRESSURE = 0x6B                 # E110 10xx
    DATE = 0x6C                     # E110 1100
    DATE_TIME_GENERAL = 0x6D        # E110 1101
    DATE_TIME = 0x6D                # E110 1101
    EXTENTED_TIME = 0x6D            # E110 1101
    EXTENTED_DATE_TIME = 0x6D       # E110 1101
    UNITS_FOR_HCA = 0x6E            # E110 1110
    RES_THIRD_VIFE_TABLE = 0x6F     # E110 1111
    AVG_DURATION = 0x73             # E111 00xx
    ACTUALITY_DURATION = 0x77       # E111 01xx
    FABRICATION_NO = 0x78           # E111 1000
    IDENTIFICATION = 0x79           # E111 1001
    ADDRESS = 0x7A                  # E111 1010

    # NOT THE ONES FOR SPECIAL PURPOSES
    FIRST_EXT_VIF_CODES = 0xFB      # 1111 1011
    VARIABLE_VIF = 0xFC             # E111 1111
    VIF_FOLLOWING = 0x7C            # E111 1100
    SECOND_EXT_VIF_CODES = 0xFD     # 1111 1101
    THIRD_EXT_VIF_CODES_RES = 0xEF  # 1110 1111
    ANY_VIF = 0x7E                  # E111 1110
    MANUFACTURER_SPEC = 0x7F        # E111 1111


class VIFUnitExt(Enum):
    # Currency Units
    CURRENCY_CREDIT = 0x03  # E000 00nn Credit of 10 nn-3 of the nominal ...
    CURRENCY_DEBIT = 0x07   # E000 01nn Debit of 10 nn-3 of the nominal ...

    # Enhanced Identification
    ACCESS_NUMBER = 0x08     # E000 1000 Access Number (transmission count)
    MEDIUM = 0x09            # E000 1001 Medium (as in fixed header)
    MANUFACTURER = 0x0A      # E000 1010 Manufacturer (as in fixed header)
    PARAMETER_SET_ID = 0x0B  # E000 1011 Parameter set identification Enha ...
    MODEL_VERSION = 0x0C     # E000 1100 Model / Version
    HARDWARE_VERSION = 0x0D  # E000 1101 Hardware version #
    FIRMWARE_VERSION = 0x0E  # E000 1110 Firmware version #
    SOFTWARE_VERSION = 0x0F  # E000 1111 Software version #

    # Implementation of all TC294 WG1 requirements (improved selection ..)
    CUSTOMER_LOCATION = 0x10            # E001 0000 Customer location
    CUSTOMER = 0x11                     # E001 0001 Customer
    ACCESS_CODE_USER = 0x12             # E001 0010 Access Code User
    ACCESS_CODE_OPERATOR = 0x13         # E001 0011 Access Code Operator
    ACCESS_CODE_SYSTEM_OPERATOR = 0x14  # E001 0100 Access Code System Operator
    ACCESS_CODE_DEVELOPER = 0x15        # E001 0101 Access Code Developer
    PASSWORD = 0x16                     # E001 0110 Password
    ERROR_FLAGS = 0x17                  # E001 0111 Error flags (binary)
    ERROR_MASKS = 0x18                  # E001 1000 Error mask
    RESERVED = 0x19                     # E001 1001 Reserved
    DIGITAL_OUTPUT = 0x1A               # E001 1010 Digital Output (binary)
    DIGITAL_INPUT = 0x1B                # E001 1011 Digital Input (binary)
    BAUDRATE = 0x1C                     # E001 1100 Baudrate [Baud]
    RESPONSE_DELAY = 0x1D               # E001 1101 response delay time
    RETRY = 0x1E                        # E001 1110 Retry
    RESERVED_2 = 0x1F                   # E001 1111 Reserved

    # Enhanced storage management
    FIRST_STORAGE_NR = 0x20             # E010 0000 First storage
    LAST_STORAGE_NR = 0x21              # E010 0001 Last storage
    SIZE_OF_STORAGE_BLOCK = 0x22        # E010 0010 Size of storage block
    RESERVED_3 = 0x23                   # E010 0011 Reserved
    STORAGE_INTERVAL = 0x27             # E010 01nn Storage interval
    STORAGE_INTERVAL_MONTH = 0x28       # E010 1000 Storage interval month(s)
    STORAGE_INTERVAL_YEARS = 0x29       # E010 1001 Storage interval year(s)

    # E010 1010 Reserved
    # E010 1011 Reserved
    DURATION_SINCE_LAST_READOUT = 0x2F  # E010 11nn Duration since last ...

    #  Enhanced tarif management
    START_OF_TARIFF = 0x30              # E011 0000 Start (date/time) of tariff
    DURATION_OF_TARIFF = 0x3            # E011 00nn Duration of tariff
    PERIOD_OF_TARIFF = 0x37             # E011 01nn Period of tariff
    PERIOD_OF_TARIFF_MONTH = 0x38       # E011 1000 Period of tariff months(s)
    PERIOD_OF_TARIFF_YEARS = 0x39       # E011 1001 Period of tariff year(s)
    DIMENSIONLESS = 0x3A                # E011 1010 dimensionless / no VIF

    # E011 1011 Reserved
    # E011 11xx Reserved
    # Electrical units
    VOLTS = 0x4F                            # E100 nnnn 10 nnnn-9 Volts
    AMPERE = 0x5F                           # E101 nnnn 10 nnnn-12 A
    RESET_COUNTER = 0x60                    # E110 0000 Reset counter
    CUMULATION_COUNTER = 0x61               # E110 0001 Cumulation counter
    CONTROL_SIGNAL = 0x62                   # E110 0010 Control signal
    DAY_OF_WEEK = 0x63                      # E110 0011 Day of week
    WEEK_NUMBER = 0x64                      # E110 0100 Week number
    TIME_POINT_OF_DAY_CHANGE = 0x65         # E110 0101 Time point of day ...
    STATE_OF_PARAMETER_ACTIVATION = 0x66    # E110 0110 State of parameter
    SPECIAL_SUPPLIER_INFORMATION = 0x67     # E110 0111 Special supplier ...
    DURATION_SINCE_LAST_CUMULATION = 0x6B   # E110 10pp Duration since last
    OPERATING_TIME_BATTERY = 0x6F           # E110 11pp Operating time battery
    DATEAND_TIME_OF_BATTERY_CHANGE = 0x70   # E111 0000 Date and time of bat...
    # E111 0001 to E111 1111 Reserved

    RSSI = 0x71                             # E111 0001 RSSI


class VIFUnitSecExt(Enum):
    RELATIVE_HUMIDITY = 0x1A


class VIFTable(object):
    # Primary VIFs (main table), range 0x00 - 0xFF

    lut = {
        # E000 0nnn    Energy Wh (0.001Wh to 10000Wh)
        0x00: (1.0e-3, MeasureUnit.WH, VIFUnit.ENERGY_WH),
        0x01: (1.0e-2, MeasureUnit.WH, VIFUnit.ENERGY_WH),
        0x02: (1.0e-1, MeasureUnit.WH, VIFUnit.ENERGY_WH),
        0x03: (1.0e0,  MeasureUnit.WH, VIFUnit.ENERGY_WH),
        0x04: (1.0e1,  MeasureUnit.WH, VIFUnit.ENERGY_WH),
        0x05: (1.0e2,  MeasureUnit.WH, VIFUnit.ENERGY_WH),
        0x06: (1.0e3,  MeasureUnit.WH, VIFUnit.ENERGY_WH),
        0x07: (1.0e4,  MeasureUnit.WH, VIFUnit.ENERGY_WH),

        # E000 1nnn    Energy  J (0.001kJ to 10000kJ)
        0x08: (1.0e0, MeasureUnit.J, VIFUnit.ENERGY_J),
        0x09: (1.0e1, MeasureUnit.J, VIFUnit.ENERGY_J),
        0x0A: (1.0e2, MeasureUnit.J, VIFUnit.ENERGY_J),
        0x0B: (1.0e3, MeasureUnit.J, VIFUnit.ENERGY_J),
        0x0C: (1.0e4, MeasureUnit.J, VIFUnit.ENERGY_J),
        0x0D: (1.0e5, MeasureUnit.J, VIFUnit.ENERGY_J),
        0x0E: (1.0e6, MeasureUnit.J, VIFUnit.ENERGY_J),
        0x0F: (1.0e7, MeasureUnit.J, VIFUnit.ENERGY_J),

        # E001 0nnn    Volume m^3 (0.001l to 10000l)
        0x10: (1.0e-6, MeasureUnit.M3, VIFUnit.VOLUME),
        0x11: (1.0e-5, MeasureUnit.M3, VIFUnit.VOLUME),
        0x12: (1.0e-4, MeasureUnit.M3, VIFUnit.VOLUME),
        0x13: (1.0e-3, MeasureUnit.M3, VIFUnit.VOLUME),
        0x14: (1.0e-2, MeasureUnit.M3, VIFUnit.VOLUME),
        0x15: (1.0e-1, MeasureUnit.M3, VIFUnit.VOLUME),
        0x16: (1.0e0,  MeasureUnit.M3, VIFUnit.VOLUME),
        0x17: (1.0e1,  MeasureUnit.M3, VIFUnit.VOLUME),

        # E001 1nnn    Mass kg (0.001kg to 10000kg) 
        0x18: (1.0e-3, MeasureUnit.KG, VIFUnit.MASS),
        0x19: (1.0e-2, MeasureUnit.KG, VIFUnit.MASS),
        0x1A: (1.0e-1, MeasureUnit.KG, VIFUnit.MASS),
        0x1B: (1.0e0,  MeasureUnit.KG, VIFUnit.MASS),
        0x1C: (1.0e1,  MeasureUnit.KG, VIFUnit.MASS),
        0x1D: (1.0e2,  MeasureUnit.KG, VIFUnit.MASS),
        0x1E: (1.0e3,  MeasureUnit.KG, VIFUnit.MASS),
        0x1F: (1.0e4,  MeasureUnit.KG, VIFUnit.MASS),

        # E010 00nn    On Time s 
        0x20: (1.0, MeasureUnit.SECONDS, VIFUnit.ON_TIME),  # seconds 
        0x21: (60.0, MeasureUnit.SECONDS, VIFUnit.ON_TIME),  # minutes 
        0x22: (3600.0, MeasureUnit.SECONDS, VIFUnit.ON_TIME),  # hours   
        0x23: (86400.0, MeasureUnit.SECONDS, VIFUnit.ON_TIME),  # days    

        # E010 01nn    Operating Time s 
        0x24: (1.0, MeasureUnit.SECONDS, VIFUnit.OPERATING_TIME),  # sec
        0x25: (60.0, MeasureUnit.SECONDS, VIFUnit.OPERATING_TIME),  # min
        0x26: (3600.0, MeasureUnit.SECONDS, VIFUnit.OPERATING_TIME),  # hours
        0x27: (86400.0, MeasureUnit.SECONDS, VIFUnit.OPERATING_TIME),  # days

        # E010 1nnn    Power W (0.001W to 10000W) 
        0x28: (1.0e-3, MeasureUnit.W, VIFUnit.POWER_W),
        0x29: (1.0e-2, MeasureUnit.W, VIFUnit.POWER_W),
        0x2A: (1.0e-1, MeasureUnit.W, VIFUnit.POWER_W),
        0x2B: (1.0e0,  MeasureUnit.W, VIFUnit.POWER_W),
        0x2C: (1.0e1,  MeasureUnit.W, VIFUnit.POWER_W),
        0x2D: (1.0e2,  MeasureUnit.W, VIFUnit.POWER_W),
        0x2E: (1.0e3,  MeasureUnit.W, VIFUnit.POWER_W),
        0x2F: (1.0e4,  MeasureUnit.W, VIFUnit.POWER_W),

        # E011 0nnn    Power J/h (0.001kJ/h to 10000kJ/h) 
        0x30: (1.0e0, MeasureUnit.J_H, VIFUnit.POWER_J_H),
        0x31: (1.0e1, MeasureUnit.J_H, VIFUnit.POWER_J_H),
        0x32: (1.0e2, MeasureUnit.J_H, VIFUnit.POWER_J_H),
        0x33: (1.0e3, MeasureUnit.J_H, VIFUnit.POWER_J_H),
        0x34: (1.0e4, MeasureUnit.J_H, VIFUnit.POWER_J_H),
        0x35: (1.0e5, MeasureUnit.J_H, VIFUnit.POWER_J_H),
        0x36: (1.0e6, MeasureUnit.J_H, VIFUnit.POWER_J_H),
        0x37: (1.0e7, MeasureUnit.J_H, VIFUnit.POWER_J_H),

        # E011 1nnn    Volume Flow m3/h (0.001l/h to 10000l/h) 
        0x38: (1.0e-6, MeasureUnit.M3_H, VIFUnit.VOLUME_FLOW),
        0x39: (1.0e-5, MeasureUnit.M3_H, VIFUnit.VOLUME_FLOW),
        0x3A: (1.0e-4, MeasureUnit.M3_H, VIFUnit.VOLUME_FLOW),
        0x3B: (1.0e-3, MeasureUnit.M3_H, VIFUnit.VOLUME_FLOW),
        0x3C: (1.0e-2, MeasureUnit.M3_H, VIFUnit.VOLUME_FLOW),
        0x3D: (1.0e-1, MeasureUnit.M3_H, VIFUnit.VOLUME_FLOW),
        0x3E: (1.0e0,  MeasureUnit.M3_H, VIFUnit.VOLUME_FLOW),
        0x3F: (1.0e1,  MeasureUnit.M3_H, VIFUnit.VOLUME_FLOW),

        # E100 0nnn     Volume Flow ext.  m^3/min (0.0001l/min to 1000l/min) 
        0x40: (1.0e-7, MeasureUnit.M3_MIN, VIFUnit.VOLUME_FLOW_EXT),
        0x41: (1.0e-6, MeasureUnit.M3_MIN, VIFUnit.VOLUME_FLOW_EXT),
        0x42: (1.0e-5, MeasureUnit.M3_MIN, VIFUnit.VOLUME_FLOW_EXT),
        0x43: (1.0e-4, MeasureUnit.M3_MIN, VIFUnit.VOLUME_FLOW_EXT),
        0x44: (1.0e-3, MeasureUnit.M3_MIN, VIFUnit.VOLUME_FLOW_EXT),
        0x45: (1.0e-2, MeasureUnit.M3_MIN, VIFUnit.VOLUME_FLOW_EXT),
        0x46: (1.0e-1, MeasureUnit.M3_MIN, VIFUnit.VOLUME_FLOW_EXT),
        0x47: (1.0e0,  MeasureUnit.M3_MIN, VIFUnit.VOLUME_FLOW_EXT),

        # E100 1nnn     Volume Flow ext.  m^3/s (0.001ml/s to 10000ml/s) 
        0x48: (1.0e-9, MeasureUnit.M3_S, VIFUnit.VOLUME_FLOW_EXT_S),
        0x49: (1.0e-8, MeasureUnit.M3_S, VIFUnit.VOLUME_FLOW_EXT_S),
        0x4A: (1.0e-7, MeasureUnit.M3_S, VIFUnit.VOLUME_FLOW_EXT_S),
        0x4B: (1.0e-6, MeasureUnit.M3_S, VIFUnit.VOLUME_FLOW_EXT_S),
        0x4C: (1.0e-5, MeasureUnit.M3_S, VIFUnit.VOLUME_FLOW_EXT_S),
        0x4D: (1.0e-4, MeasureUnit.M3_S, VIFUnit.VOLUME_FLOW_EXT_S),
        0x4E: (1.0e-3, MeasureUnit.M3_S, VIFUnit.VOLUME_FLOW_EXT_S),
        0x4F: (1.0e-2, MeasureUnit.M3_S, VIFUnit.VOLUME_FLOW_EXT_S),

        # E101 0nnn     Mass flow kg/h (0.001kg/h to 10000kg/h) 
        0x50: (1.0e-3, MeasureUnit.KG_H, VIFUnit.MASS_FLOW),
        0x51: (1.0e-2, MeasureUnit.KG_H, VIFUnit.MASS_FLOW),
        0x52: (1.0e-1, MeasureUnit.KG_H, VIFUnit.MASS_FLOW),
        0x53: (1.0e0,  MeasureUnit.KG_H, VIFUnit.MASS_FLOW),
        0x54: (1.0e1,  MeasureUnit.KG_H, VIFUnit.MASS_FLOW),
        0x55: (1.0e2,  MeasureUnit.KG_H, VIFUnit.MASS_FLOW),
        0x56: (1.0e3,  MeasureUnit.KG_H, VIFUnit.MASS_FLOW),
        0x57: (1.0e4,  MeasureUnit.KG_H, VIFUnit.MASS_FLOW),

        # E101 10nn     Flow Temperature degC (0.001degC to 1degC) 
        0x58: (1.0e-3, MeasureUnit.C, VIFUnit.FLOW_TEMPERATURE),
        0x59: (1.0e-2, MeasureUnit.C, VIFUnit.FLOW_TEMPERATURE),
        0x5A: (1.0e-1, MeasureUnit.C, VIFUnit.FLOW_TEMPERATURE),
        0x5B: (1.0e0,  MeasureUnit.C, VIFUnit.FLOW_TEMPERATURE),

        # E101 11nn Return Temperature degC (0.001degC to 1degC) 
        0x5C: (1.0e-3, MeasureUnit.C, VIFUnit.RETURN_TEMPERATURE),
        0x5D: (1.0e-2, MeasureUnit.C, VIFUnit.RETURN_TEMPERATURE),
        0x5E: (1.0e-1, MeasureUnit.C, VIFUnit.RETURN_TEMPERATURE),
        0x5F: (1.0e0,  MeasureUnit.C, VIFUnit.RETURN_TEMPERATURE),

        # E110 00nn    Temperature Difference  K   (mK to  K) 
        0x60: (1.0e-3, MeasureUnit.K, VIFUnit.TEMPERATURE_DIFFERENCE),
        0x61: (1.0e-2, MeasureUnit.K, VIFUnit.TEMPERATURE_DIFFERENCE),
        0x62: (1.0e-1, MeasureUnit.K, VIFUnit.TEMPERATURE_DIFFERENCE),
        0x63: (1.0e0,  MeasureUnit.K, VIFUnit.TEMPERATURE_DIFFERENCE),

        # E110 01nn     External Temperature degC (0.001degC to 1degC) 
        0x64: (1.0e-3, MeasureUnit.C, VIFUnit.EXTERNAL_TEMPERATURE),
        0x65: (1.0e-2, MeasureUnit.C, VIFUnit.EXTERNAL_TEMPERATURE),
        0x66: (1.0e-1, MeasureUnit.C, VIFUnit.EXTERNAL_TEMPERATURE),
        0x67: (1.0e0,  MeasureUnit.C, VIFUnit.EXTERNAL_TEMPERATURE),

        # E110 10nn     Pressure bar (1mbar to 1000mbar) 
        0x68: (1.0e-3, MeasureUnit.BAR, VIFUnit.PRESSURE),
        0x69: (1.0e-2, MeasureUnit.BAR, VIFUnit.PRESSURE),
        0x6A: (1.0e-1, MeasureUnit.BAR, VIFUnit.PRESSURE),
        0x6B: (1.0e0,  MeasureUnit.BAR, VIFUnit.PRESSURE),

        # E110 110n     Time Point 
        0x6C: (1.0e0, MeasureUnit.DATE, VIFUnit.DATE),            # type G
        0x6D: (1.0e0, MeasureUnit.DATE_TIME, VIFUnit.DATE_TIME),  # type F

        # E110 1110     Units for H.C.A. dimensionless 
        0x6E: (1.0e0, MeasureUnit.HCA, VIFUnit.UNITS_FOR_HCA),

        # E110 1111     Reserved 
        0x6F: (0.0, MeasureUnit.NONE, VIFUnit.RES_THIRD_VIFE_TABLE),

        # E111 00nn     Averaging Duration s 
        0x70: (1.0, MeasureUnit.SECONDS, VIFUnit.AVG_DURATION),  # seconds
        0x71: (60.0, MeasureUnit.SECONDS, VIFUnit.AVG_DURATION),  # minutes
        0x72: (3600.0, MeasureUnit.SECONDS, VIFUnit.AVG_DURATION),  # hours
        0x73: (86400.0, MeasureUnit.SECONDS, VIFUnit.AVG_DURATION),  # days

        # E111 01nn     Actuality Duration s 
        0x74: (1.0, MeasureUnit.SECONDS, VIFUnit.ACTUALITY_DURATION),
        0x75: (60.0, MeasureUnit.SECONDS, VIFUnit.ACTUALITY_DURATION),
        0x76: (3600.0, MeasureUnit.SECONDS, VIFUnit.ACTUALITY_DURATION),
        0x77: (86400.0, MeasureUnit.SECONDS, VIFUnit.ACTUALITY_DURATION),

        # Fabrication No 
        0x78: (1.0, MeasureUnit.NONE, VIFUnit.FABRICATION_NO),

        # E111 1001 (Enhanced) Identification 
        0x79: (1.0, MeasureUnit.NONE, VIFUnit.IDENTIFICATION),

        # E111 1010 Bus Address 
        0x7A: (1.0, MeasureUnit.NONE, VIFUnit.ADDRESS),

        # Unknown VIF: 7Ch
        0x7C: (1.0, MeasureUnit.NONE, VIFUnit.ANY_VIF),

        # Any VIF: 7Eh
        0x7E: (1.0, MeasureUnit.NONE, VIFUnit.ANY_VIF),

        # Manufacturer specific: 7Fh 
        0x7F: (1.0, MeasureUnit.NONE, VIFUnit.MANUFACTURER_SPEC),

        # Any VIF: 7Eh 
        0xFE: (1.0, MeasureUnit.NONE, VIFUnit.ANY_VIF),

        # Manufacturer specific: FFh 
        0xFF: (1.0, MeasureUnit.NONE, VIFUnit.MANUFACTURER_SPEC),


        # Main VIFE-Code Extension table (following VIF=FDh for primary VIF)
        # See 8.4.4 a, only some of them are here. Using range 0x100 - 0x1FF

        # E000 00nn Credit of 10nn-3 of the nominal local legal currency units
        0x100: (1.0e-3, MeasureUnit.CURRENCY, VIFUnitExt.CURRENCY_CREDIT),
        0x101: (1.0e-2, MeasureUnit.CURRENCY, VIFUnitExt.CURRENCY_CREDIT),
        0x102: (1.0e-1, MeasureUnit.CURRENCY, VIFUnitExt.CURRENCY_CREDIT),
        0x103: (1.0e0,  MeasureUnit.CURRENCY, VIFUnitExt.CURRENCY_CREDIT),

        # E000 01nn Debit of 10nn-3 of the nominal local legal currency units
        0x104: (1.0e-3, MeasureUnit.CURRENCY, VIFUnitExt.CURRENCY_DEBIT),
        0x105: (1.0e-2, MeasureUnit.CURRENCY, VIFUnitExt.CURRENCY_DEBIT),
        0x106: (1.0e-1, MeasureUnit.CURRENCY, VIFUnitExt.CURRENCY_DEBIT),
        0x107: (1.0e0,  MeasureUnit.CURRENCY, VIFUnitExt.CURRENCY_DEBIT),

        # E000 1000 Access Number (transmission count) 
        0x108: (1.0e0,  MeasureUnit.NONE, VIFUnitExt.ACCESS_NUMBER),

        # E000 1001 Medium (as in fixed header) 
        0x109: (1.0e0,  MeasureUnit.NONE, VIFUnitExt.MEDIUM),

        # E000 1010 Manufacturer (as in fixed header) 
        0x10A: (1.0e0,  MeasureUnit.NONE, VIFUnitExt.MANUFACTURER),

        # E000 1011 Parameter set identification 
        0x10B: (1.0e0,  MeasureUnit.NONE, VIFUnitExt.PARAMETER_SET_ID),

        # E000 1100 Model / Version 
        0x10C: (1.0e0,  MeasureUnit.NONE, VIFUnitExt.MODEL_VERSION),

        # E000 1101 Hardware version # 
        0x10D: (1.0e0,  MeasureUnit.NONE, VIFUnitExt.HARDWARE_VERSION),

        # E000 1110 Firmware version # 
        0x10E: (1.0e0,  MeasureUnit.NONE, VIFUnitExt.FIRMWARE_VERSION),

        # E000 1111 Software version # 
        0x10F: (1.0e0,  MeasureUnit.NONE, VIFUnitExt.SOFTWARE_VERSION),

        # E001 0000 Customer location 
        0x110: (1.0e0,  MeasureUnit.NONE, VIFUnitExt.CUSTOMER_LOCATION),

        # E001 0001 Customer 
        0x111: (1.0e0,  MeasureUnit.NONE, VIFUnitExt.CUSTOMER),

        # E001 0010 Access Code User 
        0x112: (1.0e0,  MeasureUnit.NONE, VIFUnitExt.ACCESS_CODE_USER),

        # E001 0011 Access Code Operator 
        0x113: (1.0e0,  MeasureUnit.NONE, VIFUnitExt.ACCESS_CODE_OPERATOR),

        # E001 0100 Access Code System Operator 
        0x114: (1.0e0,  MeasureUnit.NONE, VIFUnitExt.ACCESS_CODE_SYSTEM_OPERATOR),

        # E001 0101 Access Code Developer 
        0x115: (1.0e0,  MeasureUnit.NONE, VIFUnitExt.ACCESS_CODE_DEVELOPER),

        # E001 0110 Password 
        0x116: (1.0e0,  MeasureUnit.NONE, VIFUnitExt.PASSWORD),

        # E001 0111 Error flags (binary) 
        0x117: (1.0e0,  MeasureUnit.NONE, VIFUnitExt.ERROR_FLAGS),

        # E001 1000 Error mask 
        0x118: (1.0e0,  MeasureUnit.NONE, VIFUnitExt.ERROR_MASKS),

        # E001 1001 Reserved 
        0x119: (1.0e0,  MeasureUnit.NONE, VIFUnitExt.RESERVED),

        # E001 1010 Digital Output (binary) 
        0x11A: (1.0e0,  MeasureUnit.NONE, VIFUnitExt.DIGITAL_OUTPUT),

        # E001 1011 Digital Input (binary) 
        0x11B: (1.0e0,  MeasureUnit.NONE, VIFUnitExt.DIGITAL_INPUT),

        # E001 1100 Baudrate [Baud] 
        0x11C: (1.0e0,  MeasureUnit.BAUD, VIFUnitExt.BAUDRATE),

        # E001 1101 Response delay time [bittimes] 
        0x11D: (1.0e0,  MeasureUnit.BIT_TIMES, VIFUnitExt.RESPONSE_DELAY),

        # E001 1110 Retry 
        0x11E: (1.0e0,  MeasureUnit.NONE, VIFUnitExt.RETRY),

        # E001 1111 Reserved 
        0x11F: (1.0e0,  MeasureUnit.NONE, VIFUnitExt.RESERVED_2),

        # E010 0000 First storage # for cyclic storage 
        0x120: (1.0e0,  MeasureUnit.NONE, VIFUnitExt.FIRST_STORAGE_NR),

        # E010 0001 Last storage # for cyclic storage 
        0x121: (1.0e0,  MeasureUnit.NONE, VIFUnitExt.LAST_STORAGE_NR),

        # E010 0010 Size of storage block 
        0x122: (1.0e0,  MeasureUnit.NONE, VIFUnitExt.SIZE_OF_STORAGE_BLOCK),

        # E010 0011 Reserved 
        0x123: (1.0e0,  MeasureUnit.NONE, VIFUnitExt.RESERVED_3),

        # E010 01nn Storage interval [sec(s)..day(s)] 
        0x124: (1.0,  MeasureUnit.SECONDS, VIFUnitExt.STORAGE_INTERVAL),
        0x125: (60.0,  MeasureUnit.SECONDS, VIFUnitExt.STORAGE_INTERVAL),
        0x126: (3600.0,  MeasureUnit.SECONDS, VIFUnitExt.STORAGE_INTERVAL),
        0x127: (86400.0,  MeasureUnit.SECONDS, VIFUnitExt.STORAGE_INTERVAL),
        0x128: (2629743.83, MeasureUnit.SECONDS, VIFUnitExt.STORAGE_INTERVAL),
        0x129: (31556926.0, MeasureUnit.SECONDS, VIFUnitExt.STORAGE_INTERVAL),

        # E010 1010 Reserved 
        0x12A: (1.0e0,  MeasureUnit.NONE, VIFUnitExt.RESERVED),

        # E010 1011 Reserved 
        0x12B: (1.0e0,  MeasureUnit.NONE, VIFUnitExt.RESERVED),

        # E010 11nn Duration since last readout [sec(s)..day(s)] 
        0x12C: (1.0, MeasureUnit.SECONDS, VIFUnitExt.DURATION_SINCE_LAST_READOUT),  # seconds 
        0x12D: (60.0, MeasureUnit.SECONDS, VIFUnitExt.DURATION_SINCE_LAST_READOUT),  # minutes 
        0x12E: (3600.0, MeasureUnit.SECONDS, VIFUnitExt.DURATION_SINCE_LAST_READOUT),  # hours   
        0x12F: (86400.0, MeasureUnit.SECONDS, VIFUnitExt.DURATION_SINCE_LAST_READOUT),  # days    

        # E011 0000 Start (date/time) of tariff  
        # The information about usage of data type F (date and time) or data type G (date) can 
        # be derived from the datafield (0010b: type G / 0100: type F). 
        0x130: (1.0e0,  MeasureUnit.NONE, VIFUnitExt.RESERVED),  # ???? 

        # E011 00nn Duration of tariff (nn=01 ..11: min to days) 
        0x131: (60.0,  MeasureUnit.SECONDS, VIFUnitExt.STORAGE_INTERVAL),   # minute(s) 
        0x132: (3600.0,  MeasureUnit.SECONDS, VIFUnitExt.STORAGE_INTERVAL),   # hour(s)   
        0x133: (86400.0,  MeasureUnit.SECONDS, VIFUnitExt.STORAGE_INTERVAL),   # day(s)    

        # E011 01nn Period of tariff [sec(s) to day(s)]  
        0x134: (1.0, MeasureUnit.SECONDS, VIFUnitExt.PERIOD_OF_TARIFF),  # seconds  
        0x135: (60.0, MeasureUnit.SECONDS, VIFUnitExt.PERIOD_OF_TARIFF),  # minutes  
        0x136: (3600.0, MeasureUnit.SECONDS, VIFUnitExt.PERIOD_OF_TARIFF),  # hours    
        0x137: (86400.0, MeasureUnit.SECONDS, VIFUnitExt.PERIOD_OF_TARIFF),  # days     
        0x138: (2629743.83, MeasureUnit.SECONDS, VIFUnitExt.PERIOD_OF_TARIFF),  # month(s) 
        0x139: (31556926.0, MeasureUnit.SECONDS, VIFUnitExt.PERIOD_OF_TARIFF),  # year(s)  

        # E011 1010 dimensionless / no VIF 
        0x13A: (1.0e0,  MeasureUnit.NONE, VIFUnitExt.DIMENSIONLESS),

        # E011 1011 Reserved 
        0x13B: (1.0e0,  MeasureUnit.NONE, VIFUnitExt.RESERVED),

        # E011 11xx Reserved 
        0x13C: (1.0e0,  MeasureUnit.NONE, VIFUnitExt.RESERVED),
        0x13D: (1.0e0,  MeasureUnit.NONE, VIFUnitExt.RESERVED),
        0x13E: (1.0e0,  MeasureUnit.NONE, VIFUnitExt.RESERVED),
        0x13F: (1.0e0,  MeasureUnit.NONE, VIFUnitExt.RESERVED),

        # E100 nnnn   Volts electrical units 
        0x140: (1.0e-9, MeasureUnit.V, VIFUnitExt.VOLTS),
        0x141: (1.0e-8, MeasureUnit.V, VIFUnitExt.VOLTS),
        0x142: (1.0e-7, MeasureUnit.V, VIFUnitExt.VOLTS),
        0x143: (1.0e-6, MeasureUnit.V, VIFUnitExt.VOLTS),
        0x144: (1.0e-5, MeasureUnit.V, VIFUnitExt.VOLTS),
        0x145: (1.0e-4, MeasureUnit.V, VIFUnitExt.VOLTS),
        0x146: (1.0e-3, MeasureUnit.V, VIFUnitExt.VOLTS),
        0x147: (1.0e-2, MeasureUnit.V, VIFUnitExt.VOLTS),
        0x148: (1.0e-1, MeasureUnit.V, VIFUnitExt.VOLTS),
        0x149: (1.0e0,  MeasureUnit.V, VIFUnitExt.VOLTS),
        0x14A: (1.0e1,  MeasureUnit.V, VIFUnitExt.VOLTS),
        0x14B: (1.0e2,  MeasureUnit.V, VIFUnitExt.VOLTS),
        0x14C: (1.0e3,  MeasureUnit.V, VIFUnitExt.VOLTS),
        0x14D: (1.0e4,  MeasureUnit.V, VIFUnitExt.VOLTS),
        0x14E: (1.0e5,  MeasureUnit.V, VIFUnitExt.VOLTS),
        0x14F: (1.0e6,  MeasureUnit.V, VIFUnitExt.VOLTS),

        # E101 nnnn   A 
        0x150: (1.0e-12, MeasureUnit.A, VIFUnitExt.AMPERE),
        0x151: (1.0e-11, MeasureUnit.A, VIFUnitExt.AMPERE),
        0x152: (1.0e-10, MeasureUnit.A, VIFUnitExt.AMPERE),
        0x153: (1.0e-9,  MeasureUnit.A, VIFUnitExt.AMPERE),
        0x154: (1.0e-8,  MeasureUnit.A, VIFUnitExt.AMPERE),
        0x155: (1.0e-7,  MeasureUnit.A, VIFUnitExt.AMPERE),
        0x156: (1.0e-6,  MeasureUnit.A, VIFUnitExt.AMPERE),
        0x157: (1.0e-5,  MeasureUnit.A, VIFUnitExt.AMPERE),
        0x158: (1.0e-4,  MeasureUnit.A, VIFUnitExt.AMPERE),
        0x159: (1.0e-3,  MeasureUnit.A, VIFUnitExt.AMPERE),
        0x15A: (1.0e-2,  MeasureUnit.A, VIFUnitExt.AMPERE),
        0x15B: (1.0e-1,  MeasureUnit.A, VIFUnitExt.AMPERE),
        0x15C: (1.0e0,   MeasureUnit.A, VIFUnitExt.AMPERE),
        0x15D: (1.0e1,   MeasureUnit.A, VIFUnitExt.AMPERE),
        0x15E: (1.0e2,   MeasureUnit.A, VIFUnitExt.AMPERE),
        0x15F: (1.0e3,   MeasureUnit.A, VIFUnitExt.AMPERE),

        # E110 0000 Reset counter 
        0x160: (1.0e0,  MeasureUnit.NONE, VIFUnitExt.RESET_COUNTER),

        # E110 0001 Cumulation counter 
        0x161: (1.0e0,  MeasureUnit.NONE, VIFUnitExt.CUMULATION_COUNTER),

        # E110 0010 Control signal 
        0x162: (1.0e0,  MeasureUnit.NONE, VIFUnitExt.CONTROL_SIGNAL),

        # E110 0011 Day of week 
        0x163: (1.0e0,  MeasureUnit.NONE, VIFUnitExt.DAY_OF_WEEK),

        # E110 0100 Week number 
        0x164: (1.0e0,  MeasureUnit.NONE, VIFUnitExt.WEEK_NUMBER),

        # E110 0101 Time point of day change 
        0x165: (1.0e0,  MeasureUnit.NONE, VIFUnitExt.TIME_POINT_OF_DAY_CHANGE),

        # E110 0110 State of parameter activation 
        0x166: (1.0e0,  MeasureUnit.NONE, VIFUnitExt.STATE_OF_PARAMETER_ACTIVATION),

        # E110 0111 Special supplier information 
        0x167: (1.0e0,  MeasureUnit.NONE, VIFUnitExt.SPECIAL_SUPPLIER_INFORMATION),

        # E110 10pp Duration since last cumulation [hour(s)..years(s)] 
        0x168: (3600.0, MeasureUnit.SECONDS, VIFUnitExt.DURATION_SINCE_LAST_CUMULATION),  # hours    
        0x169: (86400.0, MeasureUnit.SECONDS, VIFUnitExt.DURATION_SINCE_LAST_CUMULATION),  # days     
        0x16A: (2629743.83, MeasureUnit.SECONDS, VIFUnitExt.DURATION_SINCE_LAST_CUMULATION),  # month(s) 
        0x16B: (31556926.0, MeasureUnit.SECONDS, VIFUnitExt.DURATION_SINCE_LAST_CUMULATION),  # year(s)  

        # E110 11pp Operating time battery [hour(s)..years(s)] 
        0x16C: (3600.0, MeasureUnit.SECONDS, VIFUnitExt.OPERATING_TIME_BATTERY),  # hours    
        0x16D: (86400.0, MeasureUnit.SECONDS, VIFUnitExt.OPERATING_TIME_BATTERY),  # days     
        0x16E: (2629743.83, MeasureUnit.SECONDS, VIFUnitExt.OPERATING_TIME_BATTERY),  # month(s) 
        0x16F: (31556926.0, MeasureUnit.SECONDS, VIFUnitExt.OPERATING_TIME_BATTERY),  # year(s)  

        # E111 0000 Date and time of battery change 
        0x170: (1.0e0,  MeasureUnit.NONE, VIFUnitExt.DATEAND_TIME_OF_BATTERY_CHANGE),

        # E111 0001-1111 Reserved 
        0x171: (1.0e0,  MeasureUnit.DBM, VIFUnitExt.RSSI),
        0x172: (1.0e0,  MeasureUnit.NONE, VIFUnitExt.RESERVED),
        0x173: (1.0e0,  MeasureUnit.NONE, VIFUnitExt.RESERVED),
        0x174: (1.0e0,  MeasureUnit.NONE, VIFUnitExt.RESERVED),
        0x175: (1.0e0,  MeasureUnit.NONE, VIFUnitExt.RESERVED),
        0x176: (1.0e0,  MeasureUnit.NONE, VIFUnitExt.RESERVED),
        0x177: (1.0e0,  MeasureUnit.NONE, VIFUnitExt.RESERVED),
        0x178: (1.0e0,  MeasureUnit.NONE, VIFUnitExt.RESERVED),
        0x179: (1.0e0,  MeasureUnit.NONE, VIFUnitExt.RESERVED),
        0x17A: (1.0e0,  MeasureUnit.NONE, VIFUnitExt.RESERVED),
        0x17B: (1.0e0,  MeasureUnit.NONE, VIFUnitExt.RESERVED),
        0x17C: (1.0e0,  MeasureUnit.NONE, VIFUnitExt.RESERVED),
        0x17D: (1.0e0,  MeasureUnit.NONE, VIFUnitExt.RESERVED),
        0x17E: (1.0e0,  MeasureUnit.NONE, VIFUnitExt.RESERVED),
        0x17F: (1.0e0,  MeasureUnit.NONE, VIFUnitExt.RESERVED),


        # Alternate VIFE-Code Extension table (following VIF=0FBh for primary VIF)
        # See 8.4.4 b, only some of them are here. Using range 0x200 - 0x2FF 

        # E000 000n Energy 10(n-1) MWh 0.1MWh to 1MWh 
        0x200: (1.0e5,  MeasureUnit.WH, "Energy"),
        0x201: (1.0e6,  MeasureUnit.WH, "Energy"),

        # E000 001n Reserved 
        0x202: (1.0e0,  "Reserved", "Reserved"),
        0x203: (1.0e0,  "Reserved", "Reserved"),

        # E000 01nn Reserved 
        0x204: (1.0e0,  "Reserved", "Reserved"),
        0x205: (1.0e0,  "Reserved", "Reserved"),
        0x206: (1.0e0,  "Reserved", "Reserved"),
        0x207: (1.0e0,  "Reserved", "Reserved"),

        # E000 100n Energy 10(n-1) GJ 0.1GJ to 1GJ 
        0x208: (1.0e8,  "Reserved", "Energy"),
        0x209: (1.0e9,  "Reserved", "Energy"),

        # E000 101n Reserved 
        0x20A: (1.0e0,  "Reserved", "Reserved"),
        0x20B: (1.0e0,  "Reserved", "Reserved"),

        # E000 11nn Reserved 
        0x20C: (1.0e0,  "Reserved", "Reserved"),
        0x20D: (1.0e0,  "Reserved", "Reserved"),
        0x20E: (1.0e0,  "Reserved", "Reserved"),
        0x20F: (1.0e0,  "Reserved", "Reserved"),

        # E001 000n Volume 10(n+2) m3 100m3 to 1000m3 
        0x210: (1.0e2,  MeasureUnit.M3, "Volume"),
        0x211: (1.0e3,  MeasureUnit.M3, "Volume"),

        # E001 001n Reserved 
        0x212: (1.0e0,  "Reserved", "Reserved"),
        0x213: (1.0e0,  "Reserved", "Reserved"),

        # E001 01nn Reserved 
        0x214: (1.0e0,  "Reserved", "Reserved"),
        0x215: (1.0e0,  "Reserved", "Reserved"),
        0x216: (1.0e0,  "Reserved", "Reserved"),
        0x217: (1.0e0,  "Reserved", "Reserved"),

        # E001 100n Mass 10(n+2) t 100t to 1000t 
        0x218: (1.0e5,  MeasureUnit.KG, "Mass"),
        0x219: (1.0e6,  MeasureUnit.KG, "Mass"),

        # E001 1010 to E010 0000 Reserved 
        0x21A: (1.0e-1,  MeasureUnit.PERCENT, VIFUnitSecExt.RELATIVE_HUMIDITY),
        0x21B: (1.0e0,  "Reserved", "Reserved"),
        0x21C: (1.0e0,  "Reserved", "Reserved"),
        0x21D: (1.0e0,  "Reserved", "Reserved"),
        0x21E: (1.0e0,  "Reserved", "Reserved"),
        0x21F: (1.0e0,  "Reserved", "Reserved"),
        0x220: (1.0e0,  "Reserved", "Reserved"),

        # E010 0001 Volume 0,1 feet^3 
        0x221: (1.0e-1, "feet^3", "Volume"),

        # E010 001n Volume 0,1-1 american gallon 
        0x222: (1.0e-1, "American gallon", "Volume"),
        0x223: (1.0e-0, "American gallon", "Volume"),

        # E010 0100    Volume flow 0,001 american gallon/min 
        0x224: (1.0e-3, "American gallon/min", "Volume flow"),

        # E010 0101 Volume flow 1 american gallon/min 
        0x225: (1.0e0,  "American gallon/min", "Volume flow"),

        # E010 0110 Volume flow 1 american gallon/h 
        0x226: (1.0e0,  "American gallon/h", "Volume flow"),

        # E010 0111 Reserved 
        0x227: (1.0e0, "Reserved", "Reserved"),

        # E010 100n Power 10(n-1) MW 0.1MW to 1MW 
        0x228: (1.0e5, MeasureUnit.W, "Power"),
        0x229: (1.0e6, MeasureUnit.W, "Power"),

        # E010 101n Reserved 
        0x22A: (1.0e0, "Reserved", "Reserved"),
        0x22B: (1.0e0, "Reserved", "Reserved"),

        # E010 11nn Reserved 
        0x22C: (1.0e0, "Reserved", "Reserved"),
        0x22D: (1.0e0, "Reserved", "Reserved"),
        0x22E: (1.0e0, "Reserved", "Reserved"),
        0x22F: (1.0e0, "Reserved", "Reserved"),

        # E011 000n Power 10(n-1) GJ/h 0.1GJ/h to 1GJ/h 
        0x230: (1.0e8, MeasureUnit.J, "Power"),
        0x231: (1.0e9, MeasureUnit.J, "Power"),

        # E011 0010 to E101 0111 Reserved 
        0x232: (1.0e0, "Reserved", "Reserved"),
        0x233: (1.0e0, "Reserved", "Reserved"),
        0x234: (1.0e0, "Reserved", "Reserved"),
        0x235: (1.0e0, "Reserved", "Reserved"),
        0x236: (1.0e0, "Reserved", "Reserved"),
        0x237: (1.0e0, "Reserved", "Reserved"),
        0x238: (1.0e0, "Reserved", "Reserved"),
        0x239: (1.0e0, "Reserved", "Reserved"),
        0x23A: (1.0e0, "Reserved", "Reserved"),
        0x23B: (1.0e0, "Reserved", "Reserved"),
        0x23C: (1.0e0, "Reserved", "Reserved"),
        0x23D: (1.0e0, "Reserved", "Reserved"),
        0x23E: (1.0e0, "Reserved", "Reserved"),
        0x23F: (1.0e0, "Reserved", "Reserved"),
        0x240: (1.0e0, "Reserved", "Reserved"),
        0x241: (1.0e0, "Reserved", "Reserved"),
        0x242: (1.0e0, "Reserved", "Reserved"),
        0x243: (1.0e0, "Reserved", "Reserved"),
        0x244: (1.0e0, "Reserved", "Reserved"),
        0x245: (1.0e0, "Reserved", "Reserved"),
        0x246: (1.0e0, "Reserved", "Reserved"),
        0x247: (1.0e0, "Reserved", "Reserved"),
        0x248: (1.0e0, "Reserved", "Reserved"),
        0x249: (1.0e0, "Reserved", "Reserved"),
        0x24A: (1.0e0, "Reserved", "Reserved"),
        0x24B: (1.0e0, "Reserved", "Reserved"),
        0x24C: (1.0e0, "Reserved", "Reserved"),
        0x24D: (1.0e0, "Reserved", "Reserved"),
        0x24E: (1.0e0, "Reserved", "Reserved"),
        0x24F: (1.0e0, "Reserved", "Reserved"),
        0x250: (1.0e0, "Reserved", "Reserved"),
        0x251: (1.0e0, "Reserved", "Reserved"),
        0x252: (1.0e0, "Reserved", "Reserved"),
        0x253: (1.0e0, "Reserved", "Reserved"),
        0x254: (1.0e0, "Reserved", "Reserved"),
        0x255: (1.0e0, "Reserved", "Reserved"),
        0x256: (1.0e0, "Reserved", "Reserved"),
        0x257: (1.0e0, "Reserved", "Reserved"),

        # E101 10nn Flow Temperature 10(nn-3) degF 0.001degF to 1degF 
        0x258: (1.0e-3, "degF", "Flow temperature"),
        0x259: (1.0e-2, "degF", "Flow temperature"),
        0x25A: (1.0e-1, "degF", "Flow temperature"),
        0x25B: (1.0e0,  "degF", "Flow temperature"),

        # E101 11nn Return Temperature 10(nn-3) degF 0.001degF to 1degF 
        0x25C: (1.0e-3, "degF", "Return temperature"),
        0x25D: (1.0e-2, "degF", "Return temperature"),
        0x25E: (1.0e-1, "degF", "Return temperature"),
        0x25F: (1.0e0,  "degF", "Return temperature"),

        # E110 00nn Temperature Difference 10(nn-3) degF 0.001degF to 1degF 
        0x260: (1.0e-3, "degF", "Temperature difference"),
        0x261: (1.0e-2, "degF", "Temperature difference"),
        0x262: (1.0e-1, "degF", "Temperature difference"),
        0x263: (1.0e0,  "degF", "Temperature difference"),

        # E110 01nn External Temperature 10(nn-3) degF 0.001degF to 1degF 
        0x264: (1.0e-3, "degF", "External temperature"),
        0x265: (1.0e-2, "degF", "External temperature"),
        0x266: (1.0e-1, "degF", "External temperature"),
        0x267: (1.0e0,  "degF", "External temperature"),

        # E110 1nnn Reserved 
        0x268: (1.0e0, "Reserved", "Reserved"),
        0x269: (1.0e0, "Reserved", "Reserved"),
        0x26A: (1.0e0, "Reserved", "Reserved"),
        0x26B: (1.0e0, "Reserved", "Reserved"),
        0x26C: (1.0e0, "Reserved", "Reserved"),
        0x26D: (1.0e0, "Reserved", "Reserved"),
        0x26E: (1.0e0, "Reserved", "Reserved"),
        0x26F: (1.0e0, "Reserved", "Reserved"),

        # E111 00nn Cold / Warm Temperature Limit 10(nn-3) degF 0.001degF to 1degF 
        0x270: (1.0e-3, "degF", "Cold / Warm Temperature Limit"),
        0x271: (1.0e-2, "degF", "Cold / Warm Temperature Limit"),
        0x272: (1.0e-1, "degF", "Cold / Warm Temperature Limit"),
        0x273: (1.0e0,  "degF", "Cold / Warm Temperature Limit"),

        # E111 01nn Cold / Warm Temperature Limit 10(nn-3) degC 0.001degC to 1degC 
        0x274: (1.0e-3, MeasureUnit.C, "Cold / Warm Temperature Limit"),
        0x275: (1.0e-2, MeasureUnit.C, "Cold / Warm Temperature Limit"),
        0x276: (1.0e-1, MeasureUnit.C, "Cold / Warm Temperature Limit"),
        0x277: (1.0e0,  MeasureUnit.C, "Cold / Warm Temperature Limit"),

        # E111 1nnn cumul. count max power 10(nnn-3) W 0.001W to 10000W 
        0x278: (1.0e-3, MeasureUnit.W, "Cumul count max power"),
        0x279: (1.0e-3, MeasureUnit.W, "Cumul count max power"),
        0x27A: (1.0e-1, MeasureUnit.W, "Cumul count max power"),
        0x27B: (1.0e0,  MeasureUnit.W, "Cumul count max power"),
        0x27C: (1.0e1,  MeasureUnit.W, "Cumul count max power"),
        0x27D: (1.0e2,  MeasureUnit.W, "Cumul count max power"),
        0x27E: (1.0e3,  MeasureUnit.W, "Cumul count max power"),
        0x27F: (1.0e4,  MeasureUnit.W, "Cumul count max power")
    }


class TelegramDateMasks(Enum):
    DATE = 0x02             # "Auctual Date",            0010 Type G
    DATE_TIME = 0x04        # "Actual Date and Time",    0100 Type F
    EXT_TIME = 0x03         # "Extented Date",           0011 Type J
    EXT_DATE_TIME = 0x60    # "Extented Daten and Time", 0110 Type I


class DateCalculator(object):
    SECOND_MASK = 0x3F          # 0011 1111
    MINUTE_MASK = 0x3F          # 0011 1111
    HOUR_MASK = 0x1F            # 0001 1111
    DAY_MASK = 0x1F             # 0001 1111
    MONTH_MASK = 0x0F           # 0000 1111
    YEAR_MASK = 0xE0            # 1110 0000
    YEAR_MASK_2 = 0xF0          # 1111 0000
    HUNDERT_YEAR_MASK = 0xC0    # 1100 0000
    WEEK_DAY = 0xE0             # 1110 0000
    WEEK = 0x3F                 # 0011 1111
    TIME_INVALID = 0x80         # 1000 0000
    SOMMERTIME = 0x40           # 0100 0000
    LEAP_YEAR = 0x80            # 1000 0000
    DIF_SOMMERTIME = 0xC0       # 1100 0000

    @staticmethod
    def getTimeWithSeconds(second, minute, hour):
        return "{0}:{1:02}".format(
            DateCalculator.getTime(minute, hour),
            DateCalculator.getSeconds(second)
        )

    @staticmethod
    def getTime(minute, hour):
        return "{0:02}:{1:02}".format(
            DateCalculator.getHour(hour),
            DateCalculator.getMinutes(minute)
        )

    @staticmethod
    def getDate(day, month, century):
        return "{0:04}-{1:02}-{2:02}".format(
            DateCalculator.getYear(day, month, 0, False),
            DateCalculator.getMonth(month),
            DateCalculator.getDay(day)
        )

    @staticmethod
    def getDateTime(minute, hour, day, month, century):
        return "{0}T{1}".format(
            DateCalculator.getDate(day, month, century),
            DateCalculator.getTime(minute, hour)
        )

    @staticmethod
    def getDateTimeWithSeconds(second, minute, hour, day, month, century):
        return "{0}T{1}".format(
            DateCalculator.getDate(day, month, century),
            DateCalculator.getTimeWithSeconds(second, minute, hour)
        )

    @staticmethod
    def getSeconds(second):
        return second & DateCalculator.SECOND_MASK

    @staticmethod
    def getMinutes(minute):
        return minute & DateCalculator.MINUTE_MASK

    @staticmethod
    def getHour(hour):
        return hour & DateCalculator.HOUR_MASK

    @staticmethod
    def getDay(day):
        return day & DateCalculator.DAY_MASK

    @staticmethod
    def getMonth(month):
        return month & DateCalculator.MONTH_MASK

    @staticmethod
    def getYear(yearValue1, yearValue2, hundertYearValue, calcHundertYear):
        year1 = yearValue1 & DateCalculator.YEAR_MASK
        year2 = yearValue2 & DateCalculator.YEAR_MASK_2
        hundertYear = 1

        # we move the bits of year1 value 4 bits to the right
        # and concat (or) them with year2. Afterwards we have
        # to move the result one bit to the right so that it
        # is at the right position (0xxx xxxx).
        year = (year2 | (year1 >> 4)) >> 1

        # to be compatible with older meters it is recommended to interpret the
        # years 0 to 80 as 2000 to 2080. Only year values in between 0 and 99
        # should be used

        # another option is to calculate the hundert year value (in new meters)
        # from a third value the hundert year is generated and calculated
        # the year is then calculated according to following formula:
        # year = 1900 + 100 * hundertYear + year

        if calcHundertYear:
            # We have to load the hundert year format as well
            hundertYear = \
                (hundertYearValue & DateCalculator.HUNDERT_YEAR_MASK) >> 6
            year = 1900 + (100 * hundertYear) + year

        else:
            if year < 81:
                year = 2000 + year
            else:
                year = 1900 + year

        return year
