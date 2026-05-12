"""Raw value decoder for pyMeterBus 2.0.

This module decodes value bytes using already parsed DIF metadata. It does not
apply VIF scaling and does not assemble full data records.
"""

from __future__ import annotations

import struct
from dataclasses import dataclass
from decimal import Decimal

from meterbus.model import DataEncoding, DataInformation, DecodedValue, Unit, ValueType


@dataclass(frozen=True)
class ValueDecodeResult:
    """Decoded value plus cursor information."""

    value: DecodedValue
    consumed: int


class ValueDecodeError(ValueError):
    """Raised when value bytes cannot be decoded for a DIF."""


def decode_value(
    data: bytes | bytearray | memoryview | list[int] | tuple[int, ...],
    dif: DataInformation,
    data_length: int | None,
    unit: Unit | None = None,
) -> ValueDecodeResult:
    """Decode one raw value using DIF encoding and declared byte length."""

    raw = _normalize_input(data)

    if dif.data_encoding is DataEncoding.NO_DATA:
        return ValueDecodeResult(DecodedValue(b"", None, ValueType.NONE, unit=unit), 0)

    if dif.data_encoding is DataEncoding.SPECIAL_FUNCTION:
        return ValueDecodeResult(DecodedValue(b"", None, ValueType.UNKNOWN, unit=unit), 0)

    if dif.data_encoding is DataEncoding.VARIABLE_LENGTH:
        value_raw, consumed = _decode_variable_length_raw(raw)
        return ValueDecodeResult(
            DecodedValue(value_raw, value_raw, ValueType.BINARY, unit=unit),
            consumed,
        )

    if data_length is None:
        raise ValueDecodeError("fixed-length value requires a data_length")

    if data_length < 0:
        raise ValueDecodeError("data_length must not be negative")

    if len(raw) < data_length:
        raise ValueDecodeError("not enough bytes for value")

    value_raw = raw[:data_length]

    if dif.data_encoding is DataEncoding.INTEGER:
        return ValueDecodeResult(
            DecodedValue(value_raw, int.from_bytes(value_raw, "little", signed=True), ValueType.INTEGER, unit=unit),
            data_length,
        )

    if dif.data_encoding is DataEncoding.BCD:
        return ValueDecodeResult(
            DecodedValue(value_raw, _decode_bcd(value_raw), ValueType.DECIMAL, unit=unit),
            data_length,
        )

    if dif.data_encoding is DataEncoding.REAL:
        if data_length != 4:
            raise ValueDecodeError("real values must be 4 bytes")
        return ValueDecodeResult(
            DecodedValue(value_raw, Decimal(str(struct.unpack("<f", value_raw)[0])), ValueType.DECIMAL, unit=unit),
            data_length,
        )

    return ValueDecodeResult(
        DecodedValue(value_raw, value_raw, ValueType.UNKNOWN, unit=unit),
        data_length,
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
    raise TypeError(f"unsupported value input type: {type(data).__name__}")


def _decode_bcd(raw: bytes) -> Decimal:
    digits: list[str] = []
    for byte in reversed(raw):
        high = byte >> 4
        low = byte & 0x0F
        if high > 9 or low > 9:
            raise ValueDecodeError("BCD value contains non-decimal nibble")
        digits.append(str(high))
        digits.append(str(low))
    value = "".join(digits).lstrip("0")
    if not value:
        value = "0"
    return Decimal(value)


def _decode_variable_length_raw(raw: bytes) -> tuple[bytes, int]:
    if not raw:
        raise ValueDecodeError("variable-length value is missing length byte")
    length = raw[0]
    end = 1 + length
    if len(raw) < end:
        raise ValueDecodeError("variable-length value is truncated")
    return raw[1:end], end
