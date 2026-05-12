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
    elif base_vif in (0x7B, 0x7D):
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
    if 0x08 <= base_vif <= 0x0F:
        return Unit("energy", "J"), "energy", _power10(base_vif - 3), None
    if 0x10 <= base_vif <= 0x17:
        return Unit("volume", "m^3"), "volume", _power10((base_vif & 0x0F) - 6), None
    if 0x18 <= base_vif <= 0x1F:
        return Unit("mass", "kg"), "mass", _power10((base_vif & 0x07) - 3), None
    if 0x20 <= base_vif <= 0x27:
        return Unit("operating_time", "s"), "operating_time", _duration_multiplier(base_vif & 0x07), None
    if 0x28 <= base_vif <= 0x2F:
        return Unit("power", "W"), "power", _power10((base_vif & 0x07) - 3), None
    if 0x30 <= base_vif <= 0x37:
        return Unit("power", "J/h"), "power", _power10((base_vif & 0x07) - 3), None
    if 0x38 <= base_vif <= 0x3F:
        return Unit("volume_flow", "m^3/h"), "volume_flow", _power10((base_vif & 0x07) - 6), None
    if 0x40 <= base_vif <= 0x47:
        return Unit("volume_flow", "m^3/min"), "volume_flow", _power10((base_vif & 0x07) - 7), None
    if 0x48 <= base_vif <= 0x4F:
        return Unit("volume_flow", "m^3/s"), "volume_flow", _power10((base_vif & 0x07) - 9), None
    if 0x50 <= base_vif <= 0x57:
        return Unit("mass_flow", "kg/h"), "mass_flow", _power10((base_vif & 0x07) - 3), None
    if 0x58 <= base_vif <= 0x5B:
        return Unit("flow_temperature", "degC"), "flow_temperature", _power10((base_vif & 0x03) - 3), None
    if 0x5C <= base_vif <= 0x5F:
        return Unit("return_temperature", "degC"), "return_temperature", _power10((base_vif & 0x03) - 3), None
    if 0x60 <= base_vif <= 0x63:
        return Unit("temperature_difference", "K"), "temperature_difference", _power10((base_vif & 0x03) - 3), None
    if 0x64 <= base_vif <= 0x67:
        return Unit("external_temperature", "degC"), "external_temperature", _power10((base_vif & 0x03) - 3), None
    if 0x68 <= base_vif <= 0x6B:
        return Unit("pressure", "bar"), "pressure", _power10((base_vif & 0x03) - 3), None
    if base_vif == 0x6C:
        return Unit("date", None), "date", Decimal("1"), None
    if base_vif == 0x6D:
        return Unit("datetime", None), "datetime", Decimal("1"), None
    if base_vif == 0x6E:
        return Unit("heat_cost_allocator", None), "heat_cost_allocator", Decimal("1"), None
    if base_vif == 0x6F:
        return Unit("reserved", None), "reserved", Decimal("1"), None
    if 0x70 <= base_vif <= 0x73:
        return Unit("average_duration", "s"), "average_duration", _duration_multiplier(base_vif & 0x03), None
    if base_vif == 0x74:
        return Unit("actuality_duration", "s"), "actuality_duration", Decimal("1"), None
    if base_vif == 0x75:
        return Unit("manufacturer", None), "manufacturer", Decimal("1"), None
    if base_vif == 0x76:
        return Unit("enhanced_identification", None), "enhanced_identification", Decimal("1"), None
    if base_vif == 0x77:
        return Unit("bus_address", None), "bus_address", Decimal("1"), None
    if base_vif == 0x78:
        return Unit("fabrication_number", None), "fabrication_number", Decimal("1"), None
    if base_vif == 0x79:
        return Unit("enhanced_identification", None), "enhanced_identification", Decimal("1"), None
    if base_vif == 0x7A:
        return Unit("bus_address", None), "bus_address", Decimal("1"), None

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


def _duration_multiplier(selector: int) -> Decimal:
    return (Decimal("60") ** Decimal(selector))


def _power10(exponent: int) -> Decimal:
    return Decimal(10) ** Decimal(exponent)
