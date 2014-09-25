from enum import Enum


class TelegramFunctionType(Enum):
    INSTANTANEOUS_VALUE = 0
    MAXIMUM_VALUE = 1
    MINIMUM_VALUE = 2
    ERROR_STATE_VALUE = 3
    SPECIAL_FUNCTION = 4
    SPECIAL_FUNCTION_FILL_BYTE = 5


class TelegramEncoding(Enum):
    ENCODING_NULL = 0
    ENCODING_INTEGER = 1
    ENCODING_REAL = 2
    ENCODING_BCD = 3
    ENCODING_VARIABLE_LENGTH = 4


class VIFUnitMultiplierMasks(Enum):
    ENERGY_WH = 0x70                # E000 0xxx
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
    VIF_FOLLOWING = 0x7C            # E111 1100
    SECOND_EXT_VIF_CODES = 0xFD     # 1111 1101
    THIRD_EXT_VIF_CODES_RES = 0xEF  # 1110 1111
    ANY_VIF = 0x7E                  # E111 1110
    MANUFACTURER_SPEC = 0x7F        # E111 1111


class VIFExtensionFDMask(Enum):
    # Currency Units
    CURRENCY_CREDIT = 0x03  # E000 00nn	Credit of 10 nn-3 of the nominal ...
    CURRENCY_DEBIT = 0x07   # E000 01nn	Debit of 10 nn-3 of the nominal ...

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
        return "{0}:{1}".format(
            DateCalculator.getTime(minute, hour),
            DateCalculator.getSeconds(second)
        )

    @staticmethod
    def getTime(minute, hour):
        return "{0}:{1}".format(
            DateCalculator.getHour(hour),
            DateCalculator.getMinutes(minute)
        )

    @staticmethod
    def getDate(day, month, century):
        return "{0}.{1}.{2}".format(
            DateCalculator.getDay(day),
            DateCalculator.getMonth(month),
            DateCalculator.getYear(day, month, 0, False)
        )

    @staticmethod
    def getDateTime(minute, hour, day, month, century):
        return "{0} {1}".format(
            DateCalculator.getDate(day, month, century),
            DateCalculator.getTime(minute, hour)
        )

    @staticmethod
    def getDateTimeWithSeconds(second, minute, hour, day, month, century):
        return "{0} {1}".format(
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
