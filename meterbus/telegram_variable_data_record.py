import decimal
import simplejson as json

from .telegram_field import TelegramField
from .value_information_block import ValueInformationBlock
from .data_information_block import DataInformationBlock

from .core_objects import VIFTable, VIFUnit, DataEncoding, MeasureUnit


class TelegramVariableDataRecord(object):
    UNIT_MULTIPLIER_MASK = 0x7F    # 0111 1111
    EXTENSION_BIT_MASK = 0x80      # 1000 0000

    def __init__(self):
        self.dib = DataInformationBlock()
        self.vib = ValueInformationBlock()

        self._dataField = TelegramField()

    @property
    def dataField(self):
        return self._dataField

    @dataField.setter
    def dataField(self, value):
        self._dataField = value

    def _parse_vifx(self):
        vif = self.vib.parts[0]
        vife = self.vib.parts[1:]
        vtf_ebm = self.EXTENSION_BIT_MASK

        if vif == VIFUnit.FIRST_EXT_VIF_CODES.value:
            code = (vife[0] & self.UNIT_MULTIPLIER_MASK) | 0x100

        elif vif == VIFUnit.SECOND_EXT_VIF_CODES.value:
            code = (vife[0] & self.UNIT_MULTIPLIER_MASK) | 0x200

        else:
            code = (vif & self.UNIT_MULTIPLIER_MASK)

        return VIFTable.lut[code]

    @property
    def unit(self):
        _, unit, _ = self._parse_vifx()
        return unit

    @property
    def parsed_value(self):
        mult, unit, typ = self._parse_vifx()

        length, enc = self.dib.length_encoding

        te = DataEncoding
        tdf = self._dataField

        if length != len(tdf.parts):
            return None

        try:
            return {
                # Type G: Day.Month.Year
                MeasureUnit.DATE: lambda: tdf.decodeDate,

                # Type F: Day.Month.Year Hour:Minute
                MeasureUnit.DATE_TIME: lambda: tdf.decodeDateTime,

                # Typ J: Hour:Minute:Second
                MeasureUnit.TIME: lambda: tdf.decodeTimeWithSeconds,

                # Typ I: Day.Month.Year Hour:Minute:Second
                MeasureUnit.DATE_TIME_S: lambda: tdf.decodeDateTimeWithSeconds
            }[unit]()
        except KeyError:
            pass

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

    def to_JSON(self):
        mult, unit, typ = self._parse_vifx()
        return json.dumps({
            'value': self.parsed_value,
            'unit': str(unit.name),
            'type': str(typ),
            'function': str(self.dib.function_type)
        }, use_decimal=True)
