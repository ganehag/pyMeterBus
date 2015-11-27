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

        if vif == VIFUnit.FIRST_EXT_VIF_CODES.value:  # 0xFB
            code = (vife[0] & self.UNIT_MULTIPLIER_MASK) | 0x200

        elif vif == VIFUnit.SECOND_EXT_VIF_CODES.value:  # 0xFD
            code = (vife[0] & self.UNIT_MULTIPLIER_MASK) | 0x100

        elif vif in [VIFUnit.VIF_FOLLOWING.value, 0xFC]:  # 0x7C || 0xFC
            if vif & vtf_ebm:
                code = vife[0] & self.UNIT_MULTIPLIER_MASK
                factor = 1

                if 0x70 <= code <= 0x77:
                    factor = pow(10.0, (vife[0] & 0x07) - 6)
                elif 0x78 <= code <= 0x7B:
                    factor = pow(10.0, (vife[0] & 0x03) - 3)
                elif code == 0x7D:
                    factor = 1

                return (factor, self.vib.customVIF.decodeASCII,
                        VIFUnit.VARIABLE_VIF)

        elif vif == VIFUnit.VIF_FOLLOWING:
            return (1, "FixMe", "FixMe")

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
                MeasureUnit.DATE_TIME_S: lambda: tdf.decodeDateTimeWithSeconds,

                MeasureUnit.DBM: lambda: (int(tdf.decodeInt) * 2) - 130
            }[unit]()
        except KeyError:
            pass

        return {
            te.ENCODING_INTEGER: lambda: int(
                tdf.decodeInt * mult) if mult > 1.0 else decimal.Decimal(
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
            'unit': str(unit),
            'type': str(typ),
            'function': str(self.dib.function_type)
        }, use_decimal=True)
