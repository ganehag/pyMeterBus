"""Single data-record decoder for pyMeterBus 2.0.

This module assembles exactly one variable-data record from a byte slice. It
does not loop through a telegram payload.
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal

from meterbus.model import DataRecord, DecodedValue, ValueType

from .dif import DataInformationParseError, parse_dif
from .value import ValueDecodeError, decode_value
from .vif import ValueInformationParseError, parse_vif


@dataclass(frozen=True)
class DataRecordDecodeResult:
    """Decoded record plus cursor information."""

    record: DataRecord
    consumed: int


class DataRecordDecodeError(ValueError):
    """Raised when a single data record cannot be decoded."""


def decode_record(data: bytes | bytearray | memoryview | list[int] | tuple[int, ...]) -> DataRecordDecodeResult:
    """Decode one DIF/VIF/value record from the start of `data`."""

    raw = _normalize_input(data)
    if not raw:
        raise DataRecordDecodeError("cannot decode record from empty input")

    try:
        dif_result = parse_dif(raw)
        vif_offset = dif_result.consumed
        vif_result = parse_vif(raw[vif_offset:])
        value_offset = vif_offset + vif_result.consumed
        value_result = decode_value(
            raw[value_offset:],
            dif_result.data_information,
            dif_result.data_length,
            unit=vif_result.value_information.unit,
        )
    except (DataInformationParseError, ValueInformationParseError, ValueDecodeError) as exc:
        raise DataRecordDecodeError(str(exc)) from exc

    consumed = value_offset + value_result.consumed
    value = _interpret_vif_value(value_result.value, vif_result.value_information.kind)
    value = _apply_vif_multiplier(value, vif_result.value_information.multiplier)
    record = DataRecord(
        raw=raw[:consumed],
        dif=dif_result.data_information,
        vif=vif_result.value_information,
        value=value,
        function=dif_result.data_information.function,
        storage_number=dif_result.data_information.storage_number,
        tariff=dif_result.data_information.tariff,
        subunit=dif_result.data_information.subunit,
        more_records_follow=dif_result.is_special_function,
        diagnostics=(),
    )
    return DataRecordDecodeResult(record=record, consumed=consumed)


def _interpret_vif_value(value: DecodedValue, kind: str) -> DecodedValue:
    if kind == "date":
        return _decode_date_value(value)
    if kind == "datetime":
        return _decode_datetime_value(value)
    return value


def _decode_date_value(value: DecodedValue) -> DecodedValue:
    if len(value.raw) != 2:
        return value

    raw_value = value.raw[0] | (value.raw[1] << 8)
    day = raw_value & 0x1F
    month = (raw_value >> 8) & 0x0F
    year = ((raw_value >> 5) & 0x07) | ((raw_value >> 9) & 0x78)
    year += 2000

    if not _valid_date_parts(year, month, day):
        return value

    return DecodedValue(
        raw=value.raw,
        value=f"{year:04d}-{month:02d}-{day:02d}",
        type=ValueType.DATE,
        unit=value.unit,
        scaled=False,
    )


def _decode_datetime_value(value: DecodedValue) -> DecodedValue:
    if len(value.raw) != 4:
        return value

    minute = value.raw[0] & 0x3F
    hour = value.raw[1] & 0x1F
    day = value.raw[2] & 0x1F
    month = value.raw[3] & 0x0F
    year = ((value.raw[2] & 0xE0) >> 5) | ((value.raw[3] & 0xF0) >> 1)
    year += 2000

    if not _valid_date_parts(year, month, day) or hour > 23 or minute > 59:
        return value

    return DecodedValue(
        raw=value.raw,
        value=f"{year:04d}-{month:02d}-{day:02d}T{hour:02d}:{minute:02d}:00",
        type=ValueType.DATETIME,
        unit=value.unit,
        scaled=False,
    )


def _valid_date_parts(year: int, month: int, day: int) -> bool:
    if not 1 <= month <= 12:
        return False
    if not 1 <= day <= 31:
        return False
    if month in {4, 6, 9, 11} and day > 30:
        return False
    if month == 2:
        leap_year = year % 4 == 0 and (year % 100 != 0 or year % 400 == 0)
        return day <= 29 if leap_year else day <= 28
    return True


def _apply_vif_multiplier(value: DecodedValue, multiplier: Decimal) -> DecodedValue:
    if multiplier == Decimal("1"):
        return value
    if not isinstance(value.value, (int, Decimal)):
        return value

    scaled_value = Decimal(value.value) * multiplier
    return DecodedValue(
        raw=value.raw,
        value=scaled_value,
        type=ValueType.DECIMAL,
        unit=value.unit,
        scaled=True,
    )


def _normalize_input(data: bytes | bytearray | memoryview | list[int] | tuple[int, ...]) -> bytes:
    if isinstance(data, bytes):
        return data
    if isinstance(data, bytearray):
        return bytes(data)
    if isinstance(data, memoryview):
        return data.tobytes()
    if isinstance(data, (list, tuple)):
        return bytes(data)
    raise TypeError(f"unsupported record input type: {type(data).__name__}")
