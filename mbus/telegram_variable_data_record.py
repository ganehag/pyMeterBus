import decimal
import simplejson as json
from dif_telegram_field import DIFTelegramField
from vif_telegram_field import VIFTelegramField
from telegram_data_field import TelegramDataField

from value_information_block import ValueInformationBlock
from data_information_block import DataInformationBlock

import vif_table

from mbus_protocol import TelegramEncoding, VIFUnitMultiplierMasks


class TelegramVariableDataRecord(object):
    UNIT_MULTIPLIER_MASK = 0x7F

    def __init__(self):
        # self._dif = DIFTelegramField()
        # self._difes = []

        # self._vif = VIFTelegramField()
        # self._vif.parent = self
        # self._vifes = []

        self.dib = DataInformationBlock()
        self.vib = ValueInformationBlock()


        self._dataField = TelegramDataField()
        self._dataField.parent = self

    # def parse(self):
    #     self.difes = []
    #     self.vifes = []

    #     self.dif = DIFTelegramField()
    #     self.dif.parse()
    #     self.vif = VIFTelegramField()
    #     self.vif.parent = self

    #     self.dataField = TelegramDataField()
    #     self.dataField.parent = self
    #     self.dataField.parse()

    def _parse_vifx(self):
        vif = self.vib.field_parts[0]
        vife = self.vib.field_parts[1:]
        vmm = VIFUnitMultiplierMasks
        vtf_ebm = VIFTelegramField.EXTENSION_BIT_MASK

        if vif == vmm.FIRST_EXT_VIF_CODES.value:
            code = (vife[0] & self.UNIT_MULTIPLIER_MASK) | 0x100

        elif vif == vmm.SECOND_EXT_VIF_CODES.value:
            code = (vife[0] & self.UNIT_MULTIPLIER_MASK) | 0x200

        else:
            code = (vif & self.UNIT_MULTIPLIER_MASK)

        return vif_table.VIFTable.lut[code]

    @property
    def unit(self):
        _, unit, _ = self._parse_vifx()
        return unit

    @property
    def parsed_value(self):
        mult, unit, typ = self._parse_vifx()

        length, enc = self.dib.length_encoding

        # enc = self.dif.data_field_encoding
        # length = self.dif.data_field_length

        te = TelegramEncoding
        tdf = self._dataField

        if length != len(tdf.field_parts):
            return None

        return {
            te.ENCODING_INTEGER: lambda: int(
                tdf.decodeInt * mult),
            te.ENCODING_BCD: lambda: decimal.Decimal(
                tdf.decodeBCD * mult),
            te.ENCODING_REAL: lambda: decimal.Decimal(
                tdf.decodeReal * mult),
            te.ENCODING_VARIABLE_LENGTH: lambda: tdf.decodeASCII,
            te.ENCODING_NULL: None
        }.get(enc, lambda: None)()

    # @property
    # def dif(self):
    #     return self._dif

    # @dif.setter
    # def dif(self, value):
    #     self._dif = value

    # @property
    # def vif(self):
    #     return self._vif

    # @vif.setter
    # def vif(self, value):
    #     self._vif = value

    # @property
    # def difes(self):
    #     return self._difes

    # @difes.setter
    # def difes(self, value):
    #     self._difes = value

    # @property
    # def vifes(self):
    #     return self._vifes

    # @vifes.setter
    # def vifes(self, value):
    #     self._vifes = value

    @property
    def dataField(self):
        return self._dataField

    @dataField.setter
    def dataField(self, value):
        self._dataField = value

    def debug(self):
        print "VARIABLE DATA RECORD:"

        self.dif.debug()

        for item in self.difes:
            item.debug()

        self.vif.debug()

        for item in self.vifes:
            item.debug()

        self.dataField.debug()

        print "======================="

    def to_JSON(self):
        mult, unit, typ = self._parse_vifx()
        return json.dumps({
            'value': self.parsed_value,
            'unit': str(unit),
            'type': str(typ),
            'function': str(self.dib.function_type)
        }, use_decimal=True)
