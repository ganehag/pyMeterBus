"""Variable-length DIF value helpers."""

from __future__ import annotations

from decimal import Decimal

from meterbus.model import ValueType


class VariableLengthValueError(ValueError):
    """Raised when a variable-length value is malformed."""


def decode_variable_value(raw: bytes, *, lsb_order: bool = True) -> tuple[bytes, int, object, ValueType]:
    """Decode a DIF=0Dh LVAR value.

    M-Bus variable-length values use the first byte as LVAR:

    * 00h..BFh: text string with LVAR characters
    * C0h..CFh: positive BCD number with (LVAR - C0h) bytes
    * D0h..DFh: negative BCD number with (LVAR - D0h) bytes
    * E0h..EFh: binary number with (LVAR - E0h) bytes
    * F0h..F4h: binary number with 16, 20, 24, 28, or 32 bytes
    * F5h: binary number with 48 bytes
    * F6h: binary number with 64 bytes
    * F7h..FFh: reserved, consumed as the marker only

    In Mode 1 / LSB order, text characters are transmitted last character
    first. In Mode 2 / MSB order, the first character is transmitted first.
    Raw bytes are always preserved exactly as transmitted.
    """

    return _decode_variable_value_at(raw, 0, lsb_order=lsb_order)


def _decode_variable_value_at(raw: bytes, start: int, *, lsb_order: bool = True) -> tuple[bytes, int, object, ValueType]:
    """Decode a variable-length value at `start` without copying the input suffix."""

    if start >= len(raw):
        raise VariableLengthValueError("variable-length value is missing length byte")

    marker = raw[start]
    length = _payload_length(marker)
    end = start + 1 + length
    if len(raw) < end:
        raise VariableLengthValueError("variable-length value is truncated")

    payload = raw[start + 1:end]
    consumed = end - start

    if marker <= 0xBF:
        text_payload = bytes(reversed(payload)) if lsb_order else payload
        return payload, consumed, text_payload.decode("latin-1"), ValueType.STRING

    if 0xC0 <= marker <= 0xCF:
        return payload, consumed, _decode_bcd(payload), ValueType.DECIMAL

    if 0xD0 <= marker <= 0xDF:
        return payload, consumed, -_decode_bcd(payload), ValueType.DECIMAL

    return payload, consumed, payload, ValueType.BINARY


def _payload_length(marker: int) -> int:
    if marker <= 0xBF:
        return marker
    if 0xC0 <= marker <= 0xCF:
        return marker - 0xC0
    if 0xD0 <= marker <= 0xDF:
        return marker - 0xD0
    if 0xE0 <= marker <= 0xEF:
        return marker - 0xE0
    if 0xF0 <= marker <= 0xF4:
        return 4 * (marker - 0xEC)
    if marker == 0xF5:
        return 48
    if marker == 0xF6:
        return 64
    return 0


def _decode_bcd(payload: bytes) -> Decimal:
    digits: list[str] = []
    for byte in payload:
        low = byte & 0x0F
        high = byte >> 4
        if low > 9 or high > 9:
            raise VariableLengthValueError("variable-length BCD value contains non-decimal nibble")
        digits.append(str(low))
        digits.append(str(high))
    return Decimal("".join(digits).lstrip("0") or "0")
