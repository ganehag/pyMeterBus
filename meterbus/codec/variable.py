"""Variable-length DIF value helpers."""

from __future__ import annotations

from decimal import Decimal

from meterbus.model import ValueType


class VariableLengthValueError(ValueError):
    """Raised when a variable-length value is malformed."""


def decode_variable_value(raw: bytes) -> tuple[bytes, int, object, ValueType]:
    if not raw:
        raise VariableLengthValueError("variable-length value is missing length byte")

    marker = raw[0]
    length = marker if marker < 0xC0 else marker & 0x0F
    if marker >= 0xF0:
        length = 0

    end = 1 + length
    if len(raw) < end:
        raise VariableLengthValueError("variable-length value is truncated")

    payload = raw[1:end]

    if 0xC0 <= marker <= 0xCF:
        text = _ascii_or_none(payload)
        if text is not None:
            return payload, end, text, ValueType.STRING

    if 0xD0 <= marker <= 0xEF:
        decimal = _bcd_or_none(payload)
        if decimal is not None:
            if marker >= 0xE0:
                decimal = -decimal
            return payload, end, decimal, ValueType.DECIMAL

    return payload, end, payload, ValueType.BINARY


def _ascii_or_none(payload: bytes) -> str | None:
    try:
        text = payload.decode("ascii")
    except UnicodeDecodeError:
        return None
    if any(ord(char) < 32 or ord(char) > 126 for char in text):
        return None
    return text


def _bcd_or_none(payload: bytes) -> Decimal | None:
    digits: list[str] = []
    for byte in payload:
        low = byte & 0x0F
        high = byte >> 4
        if low > 9 or high > 9:
            return None
        digits.append(str(low))
        digits.append(str(high))
    return Decimal("".join(digits).lstrip("0") or "0")
