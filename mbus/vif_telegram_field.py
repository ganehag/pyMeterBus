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

        if ivif_field & VIFTelegramField.EXTENSION_BIT_MASK == \
                VIFTelegramField.EXTENSION_BIT_MASK:
            self.extension_bit = True

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

            # Check against complete (no wildcards) bit masks
            for case in switch(ivif_field_noext):
                if case(VIFUnitMultiplierMasks.DATE.value):
                    self.type = VIFUnitMultiplierMasks.DATE
                    self.parse_date(self.parent.dif.data_field_length_and_encoding)
                    break
                if case(VIFUnitMultiplierMasks.DATE_TIME_GENERAL.value):
                    # ????
                    # self.type = VIFUnitMultiplierMasks.DATE_TIME_GENERAL
                    self.parse_date(self.parent.dif.data_field_length_and_encoding)
                    break
                if case(VIFUnitMultiplierMasks.UNITS_FOR_HCA.value):
                    # NO UNIT
                    self.type = VIFUnitMultiplierMasks.UNITS_FOR_HCA
                    break
                if case(VIFUnitMultiplierMasks.RES_THIRD_VIFE_TABLE.value):
                    # NO UNIT
                    self.type = VIFUnitMultiplierMasks.RES_THIRD_VIFE_TABLE
                    break
                if case(VIFUnitMultiplierMasks.FABRICATION_NO.value):
                    # NO UNIT
                    self.type = VIFUnitMultiplierMasks.FABRICATION_NO
                    break
                if case(VIFUnitMultiplierMasks.IDENTIFICATION.value):
                    # NO UNIT
                    self.type = VIFUnitMultiplierMasks.IDENTIFICATION
                    break
                if case(VIFUnitMultiplierMasks.ADDRESS.value):
                    # TODO
                    self.type = VIFUnitMultiplierMasks.ADDRESS
                    break
                if case(VIFUnitMultiplierMasks.VIF_FOLLOWING.value):
                    # TODO: Plain String?
                    self.type = VIFUnitMultiplierMasks.VIF_FOLLOWING
                    break
                if case(VIFUnitMultiplierMasks.ANY_VIF.value):
                    # TODO: Check 6.4
                    self.type = VIFUnitMultiplierMasks.ANY_VIF
                    break
                if case(VIFUnitMultiplierMasks.MANUFACTURER_SPEC.value):
                    # TODO: VIFE and data is manufacturer specification
                    self.type = VIFUnitMultiplierMasks.MANUFACTURER_SPEC
                    break
                if case():
                    if self.parseLastTwoBitsSet(ivif_field_noext):
                        pass
                    elif self.parseLastThreeBitsSet(ivif_field_noext):
                        pass
                    else:
                        print "EEEEERROORRRR", ivif_field_noext
                        # self.debug()
                        # exit(0)
                        pass  # TODO Handle Error

    def parseLastTwoBitsSet(self, ivif_field_noext):
        # set last two bits to 1 so that we can check against our other masks
        # ivif_field_noextLastTwo = ivif_field_noext |
        # VIFTelegramField.LAST_TWO_BIT_OR_MASK

        bits = ivif_field_noext & VIFTelegramField.LAST_TWO_BIT_OR_MASK
        vmm = VIFUnitMultiplierMasks

        try:
            self.type = VIFUnitMultiplierMasks(
                ivif_field_noext | VIFTelegramField.LAST_TWO_BIT_OR_MASK)

            print self.type

            multiplier, measurement_unit = {
                vmm.ON_TIME: (None, None),
                vmm.OPERATING_TIME: (bits - 3, MeasureUnit.C),
                vmm.FLOW_TEMPERATURE: (bits - 3, MeasureUnit.C),
                vmm.TEMPERATURE_DIFFERENCE: (bits - 3, MeasureUnit.K),
                vmm.EXTERNAL_TEMPERATURE: (bits - 3, MeasureUnit.C),
                vmm.PRESSURE: (bits - 3, MeasureUnit.BAR),
                vmm.AVG_DURATION: (None, None),
                vmm.ACTUALITY_DURATION: (None, None)
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

        if multiplier is not None:
            self.multiplier = multiplier

        if measurement_unit is not None:
            self.m_unit = measurement_unit

        return True

        # if ivif_field_noextLastTwo == VIFUnitMultiplierMasks.ON_TIME.value:
        #     self.type = VIFUnitMultiplierMasks.ON_TIME

        #     for case in switch(bits):
        #         if case(0):
        #             self.mUnit = MeasureUnit.SECONDS
        #             break
        #         if case(1):
        #             self.mUnit = MeasureUnit.MINUTES
        #             break
        #         if case(2):
        #             self.mUnit = MeasureUnit.HOURS
        #             break
        #         if case(3):
        #             self.mUnit = MeasureUnit.DAYS
        #             break
        #         if case():
        #             # TODO: Exception Handling
        #             break

        # elif ivif_field_noextLastTwo == VIFUnitMultiplierMasks.OPERATING_TIME.value:
        #     self.type = VIFUnitMultiplierMasks.OPERATING_TIME

        # elif ivif_field_noextLastTwo == VIFUnitMultiplierMasks.FLOW_TEMPERATURE.value:
        #     self.type = VIFUnitMultiplierMasks.FLOW_TEMPERATURE
        #     self.multiplier = l2b - 3
        #     self.mUnit = MeasureUnit.C

        # elif ivif_field_noextLastTwo == VIFUnitMultiplierMasks.RETURN_TEMPERATURE.value:
        #     self.type = VIFUnitMultiplierMasks.RETURN_TEMPERATURE;
        #     self.multiplier = l2b - 3
        #     self.mUnit = MeasureUnit.C

        # elif ivif_field_noextLastTwo == VIFUnitMultiplierMasks.TEMPERATURE_DIFFERENCE.value:
        #     self.type = VIFUnitMultiplierMasks.TEMPERATURE_DIFFERENCE;
        #     self.multiplier = l2b - 3
        #     self.mUnit = MeasureUnit.K

        # elif ivif_field_noextLastTwo == VIFUnitMultiplierMasks.EXTERNAL_TEMPERATURE.value:
        #     self.type = VIFUnitMultiplierMasks.EXTERNAL_TEMPERATURE;
        #     self.multiplier = l2b - 3
        #     self.mUnit = MeasureUnit.C

        # elif ivif_field_noextLastTwo == VIFUnitMultiplierMasks.PRESSURE.value:
        #     self.type = VIFUnitMultiplierMasks.PRESSURE;
        #     self.multiplier = l2b - 3
        #     self.mUnit = MeasureUnit.BAR

        # elif ivif_field_noextLastTwo == VIFUnitMultiplierMasks.AVG_DURATION.value:
        #     self.type = VIFUnitMultiplierMasks.AVG_DURATION

        # elif ivif_field_noextLastTwo == VIFUnitMultiplierMasks.ACTUALITY_DURATION.value:
        #     self.type = VIFUnitMultiplierMasks.ACTUALITY_DURATION

        # else:
        #     return False

        # return True

    def parseLastThreeBitsSet(self, ivif_field_noext):
        # set last three bits to 1 so that we can check against our other masks
        ivif_field_noextLastThree = (ivif_field_noext | VIFTelegramField.LAST_THREE_BIT_OR_MASK)

        onlyLastThreeBits = ivif_field_noext & VIFTelegramField.LAST_THREE_BIT_OR_MASK

        if ivif_field_noextLastThree == VIFUnitMultiplierMasks.ENERGY_WH.value:
            self.type = VIFUnitMultiplierMasks.ENERGY_WH
            self.multiplier = onlyLastThreeBits - 3
            self.mUnit = MeasureUnit.WH

        elif ivif_field_noextLastThree == VIFUnitMultiplierMasks.ENERGY_J.value:
            self.type = VIFUnitMultiplierMasks.ENERGY_J
            self.multiplier = onlyLastThreeBits
            self.mUnit = MeasureUnit.J

        elif ivif_field_noextLastThree == VIFUnitMultiplierMasks.VOLUME.value:
            self.type = VIFUnitMultiplierMasks.VOLUME
            self.multiplier = onlyLastThreeBits - 6
            self.mUnit = MeasureUnit.M3

        elif ivif_field_noextLastThree == VIFUnitMultiplierMasks.MASS.value:
            self.type = VIFUnitMultiplierMasks.MASS
            self.multiplier = onlyLastThreeBits - 3
            self.mUnit = MeasureUnit.KG

        elif ivif_field_noextLastThree == VIFUnitMultiplierMasks.POWER_W.value:
            self.type = VIFUnitMultiplierMasks.POWER_W
            self.multiplier = onlyLastThreeBits - 3
            self.mUnit = MeasureUnit.W

        elif ivif_field_noextLastThree == VIFUnitMultiplierMasks.POWER_J_H.value:
            self.type = VIFUnitMultiplierMasks.POWER_J_H
            self.multiplier = onlyLastThreeBits
            self.mUnit = MeasureUnit.J_H

        elif ivif_field_noextLastThree == VIFUnitMultiplierMasks.VOLUME_FLOW.value:
            self.type = VIFUnitMultiplierMasks.VOLUME_FLOW
            self.multiplier = onlyLastThreeBits - 6
            self.mUnit = MeasureUnit.M3_H

        elif ivif_field_noextLastThree == VIFUnitMultiplierMasks.VOLUME_FLOW_EXT.value:
            self.type = VIFUnitMultiplierMasks.VOLUME_FLOW_EXT
            self.multiplier = onlyLastThreeBits - 7
            self.mUnit = MeasureUnit.M3_MIN

        elif ivif_field_noextLastThree == VIFUnitMultiplierMasks.VOLUME_FLOW_EXT_S.value:
            self.type = VIFUnitMultiplierMasks.VOLUME_FLOW_EXT_S
            self.multiplier = onlyLastThreeBits - 9
            self.mUnit = MeasureUnit.M3_S

        elif ivif_field_noextLastThree == VIFUnitMultiplierMasks.MASS_FLOW.value:
            self.type = VIFUnitMultiplierMasks.MASS_FLOW
            self.multiplier = onlyLastThreeBits - 3
            self.mUnit = MeasureUnit.KG_H

        else:
            return False

        return True

    def parse_date(self, dateType):
        if dateType == TelegramDateMasks.DATE.value:
            self.mUnit = MeasureUnit.DATE

        elif dateType == TelegramDateMasks.DATE_TIME.value:
            self.type  = VIFUnitMultiplierMasks.DATE_TIME
            self.mUnit = MeasureUnit.DATE_TIME

        elif dateType == TelegramDateMasks.EXT_TIME.value:
            self.type  = VIFUnitMultiplierMasks.EXTENTED_TIME
            self.mUnit = MeasureUnit.DATE_TIME

        elif dateType == TelegramDateMasks.EXT_DATE_TIME.value:
            self.type  = VIFUnitMultiplierMasks.EXTENTED_DATE_TIME
            self.mUnit = MeasureUnit.DATE_TIME_S

        else:
            # TODO: THROW EXCEPTION
            pass

    def debug(self):
        iVifFieldBits = self.field_parts[0] & VIFTelegramField.UNIT_MULTIPLIER_MASK
        print "VIF-Field: "
        print "    Extension-Bit:".ljust(30), self.extension_bit
        print "    Field (String):".ljust(30), self.field_parts[0]
        print "    Field (compl):".ljust(30), "{0:b}".format( self.field_parts[0] )
        print "    Field-Value:".ljust(30), "{0:b}".format( iVifFieldBits )
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

        # Check against complete (no wildcards) bit masks
        for case in switch(iVifeFieldNoExt):
            if case(VIFExtensionFDMask.ACCESS_NUMBER.value):
                self.type = VIFExtensionFDMask.ACCESS_NUMBER
                break
            if case(VIFExtensionFDMask.MEDIUM.value):
                self.type = VIFExtensionFDMask.MEDIUM
                break
            if case(VIFExtensionFDMask.MANUFACTURER.value):
                self.type = VIFExtensionFDMask.MANUFACTURER
                break
            if case(VIFExtensionFDMask.PARAMETER_SET_ID.value):
                self.type = VIFExtensionFDMask.PARAMETER_SET_ID
                self.parent.dif.data_field_encoding = TelegramEncoding.ENCODING_VARIABLE_LENGTH
                self.lvar_bit = True
                break
            if case(VIFExtensionFDMask.MODEL_VERSION.value):
                self.type = VIFExtensionFDMask.MODEL_VERSION
                break
            if case(VIFExtensionFDMask.HARDWARE_VERSION.value):
                self.type = VIFExtensionFDMask.HARDWARE_VERSION
                break
            if case(VIFExtensionFDMask.SOFTWARE_VERSION.value):
                self.type = VIFExtensionFDMask.SOFTWARE_VERSION
                break
            if case(VIFExtensionFDMask.FIRMWARE_VERSION.value):
                self.type = VIFExtensionFDMask.FIRMWARE_VERSION
                break
            if case(VIFExtensionFDMask.CUSTOMER_LOCATION.value):
                self.type = VIFExtensionFDMask.CUSTOMER_LOCATION
                break
            if case(VIFExtensionFDMask.CUSTOMER.value):
                self.type = VIFExtensionFDMask.CUSTOMER
                break
            if case(VIFExtensionFDMask.ACCESS_CODE_USER.value):
                self.type = VIFExtensionFDMask.ACCESS_CODE_USER
                break
            if case(VIFExtensionFDMask.ACCESS_CODE_OPERATOR.value):
                self.type = VIFExtensionFDMask.ACCESS_CODE_OPERATOR
                break
            if case(VIFExtensionFDMask.ACCESS_CODE_SYSTEM_OPERATOR.value):
                self.type = VIFExtensionFDMask.ACCESS_CODE_SYSTEM_OPERATOR
                break
            if case(VIFExtensionFDMask.ACCESS_CODE_DEVELOPER.value):
                self.type = VIFExtensionFDMask.ACCESS_CODE_DEVELOPER
                break
            if case(VIFExtensionFDMask.PASSWORD.value):
                self.type = VIFExtensionFDMask.PASSWORD
                break
            if case(VIFExtensionFDMask.ERROR_FLAGS.value):
                self.type = VIFExtensionFDMask.ERROR_FLAGS
                break
            if case(VIFExtensionFDMask.ERROR_MASKS.value):
                self.type = VIFExtensionFDMask.ERROR_MASKS
                break
            if case(VIFExtensionFDMask.RESERVED.value):
                self.type = VIFExtensionFDMask.RESERVED
                break
            if case(VIFExtensionFDMask.DIGITAL_OUTPUT.value):
                self.type = VIFExtensionFDMask.DIGITAL_OUTPUT
                break
            if case(VIFExtensionFDMask.DIGITAL_INPUT):
                self.type = VIFExtensionFDMask.DIGITAL_INPUT
                break
            if case(VIFExtensionFDMask.BAUDRATE.value):
                self.type = VIFExtensionFDMask.BAUDRATE
                break
            if case(VIFExtensionFDMask.RESPONSE_DELAY.value):
                self.type = VIFExtensionFDMask.RESPONSE_DELAY
                break
            if case(VIFExtensionFDMask.RETRY.value):
                self.type = VIFExtensionFDMask.RETRY
                break
            if case(VIFExtensionFDMask.RESERVED_2.value):
                self.type = VIFExtensionFDMask.RESERVED_2
                break
            if case():
                pass
                # TODO: Error handling and implementation of the other code + multipliers

    def debug(self):
        field_bits = self.field_parts[0] & VIFETelegramField.UNIT_MULTIPLIER_MASK
        print "VIFE-Field: "
        print "    Extension-Bit:".ljust(30), self.extension_bit
        print "    Field (String):".ljust(30), self.field_parts[0]
        print "    Field (compl):".ljust(30), "{0:b}".format(self.field_parts[0])
        print "    Field-Value:".ljust(30), "{0:b}".format(field_bits)
        print "    Field-Type:".ljust(30),       self.type
        print "    Field-Unit:".ljust(30),       self.m_unit
        print "    Field-Multiplier:".ljust(30), self.multiplier
