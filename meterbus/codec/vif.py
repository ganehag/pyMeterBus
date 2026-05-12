"""VIF/VIFE parser for pyMeterBus 2.0.

This module only parses value-information metadata. It does not decode record
values and does not assemble full data records.
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal

from meterbus.model import Unit, ValueInformation


@dataclass(frozen=True)
class ValueInformationParseResult:
    """Parsed VIF/VIFE metadata plus cursor information."""

    value_information: ValueInformation
    consumed: int
    has_extension: bool
    is_custom_vif: bool


class ValueInformationParseError(ValueError):
    """Raised when a VIF/VIFE block is malformed."""


def parse_vif(data: bytes | bytearray | memoryview | list[int] | tuple[int, ...]) -> ValueInformationParseResult:
    """Parse one VIF/VIFE block from the start of `data`."""

    raw = _normalize_input(data)
    if not raw:
        raise ValueInformationParseError("cannot parse VIF from empty input")

    vif = raw[0]
    base_vif = vif & 0x7F
    offset = 1
    extension_bytes: list[int] = []
    custom_vif: bytes | None = None

    if base_vif == 0x7C:
        custom_vif, offset = _parse_custom_vif(raw, offset)
        unit = Unit(name=custom_vif.decode("latin-1"), symbol=None)
        kind = "custom_vif"
        multiplier = Decimal("1")
        enhancement = None
    elif base_vif == 0x7B:
        extension_bytes, offset = _parse_vife_chain(raw, offset)
        unit, kind, multiplier, enhancement = _decode_extension_vif(extension_bytes)
    elif vif & 0x80:
        extension_bytes, offset = _parse_vife_chain(raw, offset)
        unit, kind, multiplier, enhancement = _decode_base_vif(base_vif)
        if enhancement is None:
            enhancement = "vife_extension"
    else:
        unit, kind, multiplier, enhancement = _decode_base_vif(base_vif)

    value_information = ValueInformation(
        raw=raw[:offset],
        unit=unit,
        kind=kind,
        multiplier=multiplier,
        extension_bytes=bytes(extension_bytes),
        custom_vif=custom_vif,
        enhancement=enhancement,
    )
    return ValueInformationParseResult(
        value_information=value_information,
        consumed=offset,
        has_extension=bool(extension_bytes),
        is_custom_vif=custom_vif is not None,
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
    raise TypeError(f"unsupported VIF input type: {type(data).__name__}")


def _parse_vife_chain(raw: bytes, offset: int) -> tuple[list[int], int]:
    extension_bytes: list[int] = []
    while True:
        if offset >= len(raw):
            raise ValueInformationParseError("VIF extension bit set but VIFE byte is missing")
        vife = raw[offset]
        extension_bytes.append(vife)
        offset += 1
        if not vife & 0x80:
            return extension_bytes, offset
        if len(extension_bytes) >= 10:
            raise ValueInformationParseError("too many VIFE extension bytes")


def _parse_custom_vif(raw: bytes, offset: int) -> tuple[bytes, int]:
    if offset >= len(raw):
        raise ValueInformationParseError("custom VIF length byte is missing")
    length = raw[offset]
    offset += 1
    end = offset + length
    if end > len(raw):
        raise ValueInformationParseError("custom VIF text is truncated")
    return raw[offset:end], end


def _decode_base_vif(base_vif: int) -> tuple[Unit | None, str, Decimal, str | None]:
    if 0x00 <= base_vif <= 0x07:
        return Unit("energy", "Wh"), "energy", _power10(base_vif - 3), None
    if 0x10 <= base_vif <= 0x17:
        return Unit("volume", "m^3"), "volume", _power10(base_vif - 9), None
    if base_vif == 0x75:
        return Unit("manufacturer", None), "manufacturer", Decimal("1"), None
    if base_vif == 0x78:
        return Unit("fabrication_number", None), "fabrication_number", Decimal("1"), None
    return None, "unknown", Decimal("1"), f"unknown_base_vif_0x{base_vif:02X}"


def _decode_extension_vif(extension_bytes: list[int]) -> tuple[Unit | None, str, Decimal, str | None]:
    if not extension_bytes:
        return None, "extension", Decimal("1"), "missing_vife"
    first = extension_bytes[0] & 0x7F
    if first == 0x1A:
        return Unit("relative_humidity", "%RH"), "relative_humidity", Decimal("1"), "first_extension_vif"
    if first == 0x71:
        return Unit("dimensionless", None), "dimensionless", Decimal("1"), "first_extension_vif"
    return None, "unknown_extension", Decimal("1"), f"unknown_first_extension_vif_0x{first:02X}"


def _power10(exponent: int) -> Decimal:
    return Decimal(10) ** Decimal(exponent)
