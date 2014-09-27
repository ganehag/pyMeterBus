from telegram_field import TelegramField
from mbus_support import switch
from mbus_protocol import *


class VIFTelegramField(TelegramField):
    EXTENSION_BIT_MASK = 0x80      # 1000 0000
    LAST_TWO_BIT_OR_MASK = 0x03    # 0000 0011
    LAST_THREE_BIT_OR_MASK = 0x07  # 0000 0111
    UNIT_MULTIPLIER_MASK = 0x7F    # 0111 1111

    def __init__(self, parts=None):
        super(VIFTelegramField, self).__init__(parts)

        self._extension_bit = False
        self._m_unit = MeasureUnit.NONE
        self._type = None
        self._multiplier = 0

        self._parent = None  # Reference to a TelegramVariableDataRecord

    @property
    def is_extension_bit(self):
        return self._extension_bit

    @property
    def extension_bit(self):
        return self._extension_bit

    @extension_bit.setter
    def extension_bit(self, value):
        self._extension_bit = value

    @property
    def m_unit(self):
        return self._m_unit

    @m_unit.setter
    def m_unit(self, value):
        self._m_unit = value

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

    #
    # METHODS
    #

    def parse(self):
        ivif_field = self.field_parts[0]
        vmm = VIFUnitMultiplierMasks

        self.extension_bit = \
            (ivif_field & VIFTelegramField.EXTENSION_BIT_MASK ==
                VIFTelegramField.EXTENSION_BIT_MASK)

        if ivif_field == VIFUnitMultiplierMasks.FIRST_EXT_VIF_CODES.value:
            # load from next VIFE according to table 29 from DIN_EN_13757_3
            self.type = VIFUnitMultiplierMasks.FIRST_EXT_VIF_CODES

        elif ivif_field == \
                VIFUnitMultiplierMasks.SECOND_EXT_VIF_CODES.value:
            # TODO: load from next VIFE according to table 28 from
            # DIN_EN_13757_3
            self.type = VIFUnitMultiplierMasks.SECOND_EXT_VIF_CODES

        else:
            # Get rid of the first (extension) bit
            ivif_field_noext = ivif_field & \
                VIFTelegramField.UNIT_MULTIPLIER_MASK

            try:
                self.type = VIFUnitMultiplierMasks(ivif_field_noext)

                if self.type in [vmm.DATE, vmm.DATE_TIME_GENERAL]:
                    self.parse_date(
                        self.parent.dif.data_field_length_and_encoding)

            except ValueError:
                if self.parseLastTwoBitsSet(ivif_field_noext):
                    pass
                elif self.parseLastThreeBitsSet(ivif_field_noext):
                    pass
                else:
                    # print "EEEEERROORRRR", ivif_field_noext
                    # self.debug()
                    # exit(0)
                    pass  # TODO Handle Error

    def parseLastTwoBitsSet(self, ivif_field_noext):
        bits = ivif_field_noext & VIFTelegramField.LAST_TWO_BIT_OR_MASK
        vmm = VIFUnitMultiplierMasks

        try:
            self.type = VIFUnitMultiplierMasks(
                ivif_field_noext | VIFTelegramField.LAST_TWO_BIT_OR_MASK)

            self.multiplier, self.m_unit = {
                vmm.ON_TIME: (0, MeasureUnit.NONE),
                vmm.OPERATING_TIME: (0, MeasureUnit.NONE),
                vmm.FLOW_TEMPERATURE: (bits - 3, MeasureUnit.C),
                vmm.RETURN_TEMPERATURE: (bits - 3, MeasureUnit.C),
                vmm.TEMPERATURE_DIFFERENCE: (bits - 3, MeasureUnit.K),
                vmm.EXTERNAL_TEMPERATURE: (bits - 3, MeasureUnit.C),
                vmm.PRESSURE: (bits - 3, MeasureUnit.BAR),
                vmm.AVG_DURATION: (0, MeasureUnit.NONE),
                vmm.ACTUALITY_DURATION: (0, MeasureUnit.NONE)
            }[self.type]

        except KeyError:
            return False
        except ValueError:
            return False

        try:
            if self.type == VIFUnitMultiplierMasks.ON_TIME:
                self.m_unit = {
                    0: MeasureUnit.SECONDS,
                    1: MeasureUnit.MINUTES,
                    2: MeasureUnit.HOURS,
                    3: MeasureUnit.DAYS
                }[bits]
        except KeyError:
            return False

        return True

    def parseLastThreeBitsSet(self, ivif_field_noext):
        # set last three bits to 1 so that we can check against our other masks
        ivif_field_noextLastThree = \
            (ivif_field_noext | VIFTelegramField.LAST_THREE_BIT_OR_MASK)

        threeBits = ivif_field_noext & VIFTelegramField.LAST_THREE_BIT_OR_MASK

        try:
            self.type = VIFUnitMultiplierMasks(ivif_field_noextLastThree)
        except ValueError:
            return False

        vmm = VIFUnitMultiplierMasks

        try:
            self.multiplier, self.m_unit = {
                vmm.ENERGY_WH:   (threeBits - 3, MeasureUnit.WH),
                vmm.ENERGY_J:    (threeBits, MeasureUnit.J),
                vmm.VOLUME:      (threeBits - 6, MeasureUnit.M3),
                vmm.MASS:        (threeBits - 3, MeasureUnit.KG),
                vmm.POWER_W:     (threeBits - 3, MeasureUnit.W),
                vmm.POWER_J_H:   (threeBits, MeasureUnit.J_H),
                vmm.VOLUME_FLOW: (threeBits - 6, MeasureUnit.M3_H),
                vmm.VOLUME_FLOW_EXT: (threeBits - 7, MeasureUnit.M3_MIN),
                vmm.VOLUME_FLOW_EXT_S: (threeBits - 9, MeasureUnit.M3_S),
                vmm.MASS_FLOW:   (threeBits - 3, MeasureUnit.KG_H)
            }[self.type]
        except KeyError:
            return False

        return True

    def parse_date(self, dateType):
        if dateType == TelegramDateMasks.DATE.value:
            self.m_unit = MeasureUnit.DATE

        elif dateType == TelegramDateMasks.DATE_TIME.value:
            self.type = VIFUnitMultiplierMasks.DATE_TIME
            self.m_unit = MeasureUnit.DATE_TIME

        elif dateType == TelegramDateMasks.EXT_TIME.value:
            self.type = VIFUnitMultiplierMasks.EXTENTED_TIME
            self.m_unit = MeasureUnit.DATE_TIME

        elif dateType == TelegramDateMasks.EXT_DATE_TIME.value:
            self.type = VIFUnitMultiplierMasks.EXTENTED_DATE_TIME
            self.m_unit = MeasureUnit.DATE_TIME_S

        else:
            # TODO: THROW EXCEPTION
            pass

    def debug(self):
        bits = self.field_parts[0] & VIFTelegramField.UNIT_MULTIPLIER_MASK
        print "VIF-Field: "
        print "    Extension-Bit:".ljust(30), self.extension_bit
        print "    Field (String):".ljust(30), self.field_parts[0]
        print "    Field (compl):".ljust(30), "{0:b}".format(
            self.field_parts[0])
        print "    Field-Value:".ljust(30), "{0:b}".format(bits)
        print "    Field-Type:".ljust(30),       self.type
        print "    Field-Unit:".ljust(30),       self.m_unit
        print "    Field-Multiplier:".ljust(30), self.multiplier


class VIFETelegramField(TelegramField):
    EXTENSION_BIT_MASK = 0x80        # 1000 0000
    LAST_TWO_BIT_OR_MASK = 0x03      # 0000 0011
    LAST_FOUR_BIT_OR_MASK = 0x0F     # 0000 1111
    UNIT_MULTIPLIER_MASK = 0x7F      # 0111 1111

    def __init__(self, parts=None):
        super(VIFETelegramField, self).__init__(parts)

        self._extension_bit = False
        self._lvar_bit = False
        self._m_unit = MeasureUnit.NONE
        self._type = None
        self._multiplier = 0

        self._parent = None  # TelegramVariableDataRecord

    @property
    def is_lvar_bit(self):
        return self._lvar_bit

    @property
    def is_extension_bit(self):
        return self._extension_bit

    @property
    def extension_bit(self):
        return self._extension_bit

    @extension_bit.setter
    def extension_bit(self, value):
        self._extension_bit = value

    @property
    def lvar_bit(self):
        return self._lvar_bit

    @lvar_bit.setter
    def lvar_bit(self, value):
        self._lvar_bit = value

    @property
    def m_unit(self):
        return self._m_unit

    @m_unit.setter
    def m_unit(self, value):
        self._m_unit = value

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
        vifeField = self.field_parts[0]
        iVifeField = vifeField

        # Get rid of the first (extension) bit
        iVifeFieldNoExt = (iVifeField & self.UNIT_MULTIPLIER_MASK)

        if iVifeField & self.EXTENSION_BIT_MASK == self.EXTENSION_BIT_MASK:
            self.extension_bit = True

        try:
            self.type = VIFExtensionFDMask(iVifeFieldNoExt)

            if self.type == VIFExtensionFDMask.PARAMETER_SET_ID:
                self.lvar_bit = True
                self.parent.dif.data_field_encoding = \
                    TelegramEncoding.ENCODING_VARIABLE_LENGTH
        except ValueError:
            return

        # TODO: Error handling and impl. of the other code + multipliers

    def debug(self):
        field_bits = self.field_parts[0] & \
            VIFETelegramField.UNIT_MULTIPLIER_MASK
        print "VIFE-Field: "
        print "    Extension-Bit:".ljust(30), self.extension_bit
        print "    Field (String):".ljust(30), self.field_parts[0]
        print "    Field (compl):".ljust(30), "{0:b}".format(
            self.field_parts[0])
        print "    Field-Value:".ljust(30), "{0:b}".format(field_bits)
        print "    Field-Type:".ljust(30),       self.type
        print "    Field-Unit:".ljust(30),       self.m_unit
        print "    Field-Multiplier:".ljust(30), self.multiplier
