from __future__ import unicode_literals

import decimal
import string
import simplejson as json

from .core_objects import FunctionType
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

    @property
    def more_records_follow(self):
        return self.dib.more_records_follow and self.dib.is_eoud

    def _parse_vifx(self):
        if len(self.vib.parts) == 0:
            return None, None, None

        vif = self.vib.parts[0]
        vife = self.vib.parts[1:]
        vtf_ebm = self.EXTENSION_BIT_MASK

        if vif == VIFUnit.FIRST_EXT_VIF_CODES.value:  # 0xFB
            code = (vife[0] & self.UNIT_MULTIPLIER_MASK) | 0x200

        elif vif == VIFUnit.SECOND_EXT_VIF_CODES.value:  # 0xFD
            code = (vife[0] & self.UNIT_MULTIPLIER_MASK) | 0x100

        elif vif in [VIFUnit.VIF_FOLLOWING.value]:  # 0x7C
            return (1, self.vib.customVIF.decodeASCII, VIFUnit.VARIABLE_VIF)

        elif vif == 0xFC:
            #  && (vib->vife[0] & 0x78) == 0x70

            # Disable this for now as it is implicit
            # from 0xFC
            # if vif & vtf_ebm:
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

            # // custom VIF
            # n = (vib->vife[0] & 0x07);
            # snprintf(buff, sizeof(buff), "%s %s", mbus_unit_prefix(n-6), vib->custom_vif);
            # return buff;
            # return (1, "FixME", "FixMe")

        else:
            code = (vif & self.UNIT_MULTIPLIER_MASK)

        return VIFTable.lut[code]

    @property
    def unit(self):
        _, unit, _ = self._parse_vifx()
        if isinstance(unit, MeasureUnit):
            return unit.value
        return unit

    @property
    def value(self):
        value = self.parsed_value
        if type(value) == str and all(ord(c) < 128 for c in value):
            value = str(value)

        elif type(value) == str:
            try:
                value = value.decode('unicode_escape')
            except AttributeError:
                pass

        return value

    @property
    def function(self):
        func = self.dib.function_type
        return func.value

    @property
    def parsed_value(self):
        mult, unit, typ = self._parse_vifx()

        length, enc = self.dib.length_encoding

        te = DataEncoding
        tdf = self._dataField

        if self.dib.function_type == FunctionType.SPECIAL_FUNCTION:
            return self._dataField.decodeRAW

        if length != len(tdf.parts) and enc != te.ENCODING_VARIABLE_LENGTH:
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

        if (enc == te.ENCODING_VARIABLE_LENGTH and
            not all(chr(c) in string.printable for c in tdf.parts)):
            return tdf.decodeRAW

        return {
            te.ENCODING_INTEGER: lambda: int(
                tdf.decodeInt * mult) if mult > 1.0 else decimal.Decimal(
                tdf.decodeInt * mult),
            te.ENCODING_BCD: lambda: decimal.Decimal(
                tdf.decodeBCD * mult),
            te.ENCODING_REAL: lambda: decimal.Decimal(
                tdf.decodeReal * mult),
            te.ENCODING_VARIABLE_LENGTH: lambda: tdf.decodeASCII,
            te.ENCODING_NULL: lambda: None
        }.get(enc, lambda: None)()

    @property
    def interpreted(self):
        mult, unit, typ = self._parse_vifx()
        dlen, enc = self.dib.length_encoding

        try:
            unit = str(unit).decode('unicode_escape')
        except AttributeError:
            unit = str(unit)

        value = self.parsed_value
        if type(value) == str:
            try:
                value = value.decode('unicode_escape')
            except AttributeError:
                pass

        if self.dib.function_type == FunctionType.SPECIAL_FUNCTION:
            value = self._dataField.decodeRAW

        return {
            'value': value,
            'unit': unit,
            'type': str(typ),
            'function': str(self.dib.function_type)
        }

    def to_JSON(self):
        return json.dumps(self.interpreted, sort_keys=True, indent=4, use_decimal=True)
