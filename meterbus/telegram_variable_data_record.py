from __future__ import unicode_literals

import decimal
import string
import simplejson as json

from .core_objects import FunctionType
from .telegram_field import TelegramField
from .value_information_block import ValueInformationBlock
from .data_information_block import DataInformationBlock

from .core_objects import VIFTable, VIFUnit, VIFUnitEnhExt, DataEncoding, MeasureUnit, VIFUnitExt, VIFUnitSecExt
from typing import Any, Dict, Optional, Union, Tuple


class TelegramVariableDataRecord(object):
    UNIT_MULTIPLIER_MASK = 0x7F    # 0111 1111
    EXTENSION_BIT_MASK = 0x80      # 1000 0000

    def __init__(self) -> None:
        self.dib = DataInformationBlock()
        self.vib = ValueInformationBlock()

        self._dataField = TelegramField()

    @property
    def dataField(self) -> TelegramField:
        return self._dataField

    @dataField.setter
    def dataField(self, value: TelegramField) -> None:
        assert isinstance(value, TelegramField)
        self._dataField = value

    @property
    def more_records_follow(self) -> bool:
        return self.dib.more_records_follow and self.dib.is_eoud

    def _parse_vifx(self) -> Tuple[Union[None, int, float], Union[None, str, MeasureUnit], Union[None, str, VIFUnit, VIFUnitExt, VIFUnitSecExt], Union[None, VIFUnitEnhExt]]:
        """
        """
        if len(self.vib.parts) == 0:
            return None, None, None, None

        vif = self.vib.parts[0]
        vife = self.vib.parts[1:]
        vif_enh = None

        if vif == VIFUnit.FIRST_EXT_VIF_CODES.value:  # 0xFB
            code = (vife[0] & self.UNIT_MULTIPLIER_MASK) | 0x200

        elif vif == VIFUnit.SECOND_EXT_VIF_CODES.value:  # 0xFD
            code = (vife[0] & self.UNIT_MULTIPLIER_MASK) | 0x100

        elif vif in [VIFUnit.VIF_FOLLOWING.value]:  # 0x7C
            return (1, self.vib.customVIF.decodeASCII, VIFUnit.VARIABLE_VIF, None)

        elif vif == 0xFC:
            #  && (vib->vife[0] & 0x78) == 0x70

            # Disable this for now as it is implicit
            # from 0xFC
            # if vif & vtf_ebm:
            code = vife[0] & self.UNIT_MULTIPLIER_MASK

            def factor()-> int: 
                if 0x70 <= code <= 0x77:
                    return pow(10.0, (vife[0] & 0x07) - 6)
                if 0x78 <= code <= 0x7B:
                    return pow(10.0, (vife[0] & 0x03) - 3)
                if code == 0x7D:
                    return 1
                return 1

            return (factor(), self.vib.customVIF.decodeASCII,
                    VIFUnit.VARIABLE_VIF, None)

            # // custom VIF
            # n = (vib->vife[0] & 0x07);
            # snprintf(buff, sizeof(buff), "%s %s", mbus_unit_prefix(n-6), vib->custom_vif);
            # return buff;
            # return (1, "FixME", "FixMe", None)

        elif vif & self.EXTENSION_BIT_MASK:
            code = (vif & self.UNIT_MULTIPLIER_MASK)
            vif_enh = vife[0] & self.UNIT_MULTIPLIER_MASK

        else:
            code = (vif & self.UNIT_MULTIPLIER_MASK)

        return (
            *VIFTable.lut[code],
            VIFTable.enh.get(vif_enh, VIFUnitEnhExt.UNKNOWN_ENHANCEMENT) if vif_enh else None,
        )

    @property
    def unit(self) -> Optional[str]:
        _, unit, _, _ = self._parse_vifx()
        if isinstance(unit, MeasureUnit):
            return unit.value
        return unit

    @property
    def value(self) -> Union[str, decimal.Decimal]:
        value = self.parsed_value
        if isinstance(value, str):
            if all(ord(c) < 128 for c in value):
                 str(value)

            elif isinstance(value, bytes):
                value = value.decode('unicode_escape')

        return value

    @property
    def function(self) -> int:
        func = self.dib.function_type
        return func.value

    @property
    def parsed_value(self) -> Optional[Union[str, int, decimal.Decimal]]:
        mult, unit, _, _ = self._parse_vifx()

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

        def encode() -> Union[None, str, int, decimal.Decimal]:
            if enc == te.ENCODING_INTEGER:
                assert mult is not None
                if mult > 1.0:
                    # TODO: If 'mult' is for example 1.1, why should the result be rounded to an int?
                    return int(tdf.decodeInt * mult) 
                return decimal.Decimal(tdf.decodeInt * mult)
            if enc == te.ENCODING_BCD:
                assert mult is not None
                return decimal.Decimal(tdf.decodeBCD * mult)
            if enc == te.ENCODING_REAL: 
                assert mult is not None
                return decimal.Decimal(tdf.decodeReal * mult)
            if enc == te.ENCODING_VARIABLE_LENGTH:
                return tdf.decodeASCII
            if enc == te.ENCODING_NULL:
                return None
            return None

        return encode()

    @property
    def interpreted(self) -> Dict[str, Union[    decimal.Decimal, str, int]]:
        _, unit, typ, unit_enh = self._parse_vifx()
        storage_number, tariff, device = self.dib.parse_dife()

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

        record = {
            'value': value,
            'unit': unit,
            'type': str(typ),
            'storage_number': storage_number,
            'function': str(self.dib.function_type)
        }

        if unit_enh is not None:
            record['unit_enh'] = str(unit_enh)

        if tariff is not None:
            record['tariff'] = tariff

        if device is not None:
            record['device'] = device

        return record

    def to_JSON(self) -> str:
        return json.dumps(self.interpreted, sort_keys=True,
                          indent=4, use_decimal=True)
