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
    elif vif == 0xFD:
        extension_bytes, offset = _parse_vife_chain(raw, offset)
        unit, kind, multiplier, enhancement = _decode_main_extension_vif(extension_bytes)
    elif vif == 0xFB:
        extension_bytes, offset = _parse_vife_chain(raw, offset)
        unit, kind, multiplier, enhancement = _decode_alternate_extension_vif(extension_bytes)
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
        return Unit("energy", "J"), "energy", _power10(base_vif), None
    if 0x10 <= base_vif <= 0x17:
        return Unit("volume", "m^3"), "volume", _power10((base_vif & 0x0F) - 6), None
    if 0x18 <= base_vif <= 0x1F:
        return Unit("mass", "kg"), "mass", _power10((base_vif & 0x07) - 3), None
    if 0x20 <= base_vif <= 0x23:
        return Unit("on_time", "s"), "on_time", _time_multiplier(base_vif & 0x03), None
    if 0x24 <= base_vif <= 0x27:
        return Unit("operating_time", "s"), "operating_time", _time_multiplier(base_vif & 0x03), None
    if 0x28 <= base_vif <= 0x2F:
        return Unit("power", "W"), "power", _power10((base_vif & 0x07) - 3), None
    if 0x30 <= base_vif <= 0x37:
        return Unit("power", "J/h"), "power", _power10(base_vif & 0x07), None
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
        return Unit("average_duration", "s"), "average_duration", _time_multiplier(base_vif & 0x03), None
    if 0x74 <= base_vif <= 0x77:
        return Unit("actuality_duration", "s"), "actuality_duration", _time_multiplier(base_vif & 0x03), None
    if base_vif == 0x78:
        return Unit("fabrication_number", None), "fabrication_number", Decimal("1"), None
    if base_vif == 0x79:
        return Unit("enhanced_identification", None), "enhanced_identification", Decimal("1"), None
    if base_vif == 0x7A:
        return Unit("bus_address", None), "bus_address", Decimal("1"), None
    if base_vif == 0x7E:
        return Unit("any_vif", None), "any_vif", Decimal("1"), None
    if base_vif == 0x7F:
        return Unit("manufacturer_specific", None), "manufacturer_specific", Decimal("1"), None

    return None, "unknown", Decimal("1"), f"unknown_base_vif_0x{base_vif:02X}"


def _decode_main_extension_vif(extension_bytes: list[int]) -> tuple[Unit | None, str, Decimal, str | None]:
    if not extension_bytes:
        return None, "extension", Decimal("1"), "missing_vife"

    first = extension_bytes[0] & 0x7F
    if first == 0x7D and len(extension_bytes) > 1:
        return _decode_second_level_extension_vif(extension_bytes[1] & 0x7F)

    if 0x00 <= first <= 0x03:
        return Unit("currency_credit", "currency"), "currency_credit", _power10(first - 3), "main_extension_vif"
    if 0x04 <= first <= 0x07:
        return Unit("currency_debit", "currency"), "currency_debit", _power10((first & 0x03) - 3), "main_extension_vif"

    table: dict[int, tuple[Unit | None, str, Decimal, str | None]] = {
        0x08: (Unit("unique_message_identification", None), "unique_message_identification", Decimal("1"), "main_extension_vif"),
        0x09: (Unit("device_type", None), "device_type", Decimal("1"), "main_extension_vif"),
        0x0A: (Unit("manufacturer", None), "manufacturer", Decimal("1"), "main_extension_vif"),
        0x0B: (Unit("parameter_set_identification", None), "parameter_set_identification", Decimal("1"), "main_extension_vif"),
        0x0C: (Unit("model_version", None), "model_version", Decimal("1"), "main_extension_vif"),
        0x0D: (Unit("hardware_version_number", None), "hardware_version_number", Decimal("1"), "main_extension_vif"),
        0x0E: (Unit("metrology_firmware_version_number", None), "metrology_firmware_version_number", Decimal("1"), "main_extension_vif"),
        0x0F: (Unit("software_version_number", None), "software_version_number", Decimal("1"), "main_extension_vif"),
        0x10: (Unit("customer_location", None), "customer_location", Decimal("1"), "main_extension_vif"),
        0x11: (Unit("customer", None), "customer", Decimal("1"), "main_extension_vif"),
        0x12: (Unit("access_code_user", None), "access_code_user", Decimal("1"), "main_extension_vif"),
        0x13: (Unit("access_code_operator", None), "access_code_operator", Decimal("1"), "main_extension_vif"),
        0x14: (Unit("access_code_system_operator", None), "access_code_system_operator", Decimal("1"), "main_extension_vif"),
        0x15: (Unit("access_code_developer", None), "access_code_developer", Decimal("1"), "main_extension_vif"),
        0x16: (Unit("password", None), "password", Decimal("1"), "main_extension_vif"),
        0x17: (Unit("error_flags", None), "error_flags", Decimal("1"), "main_extension_vif"),
        0x18: (Unit("error_mask", None), "error_mask", Decimal("1"), "main_extension_vif"),
        0x19: (Unit("security_key", None), "security_key", Decimal("1"), "main_extension_vif"),
        0x1A: (Unit("digital_output", None), "digital_output", Decimal("1"), "main_extension_vif"),
        0x1B: (Unit("digital_input", None), "digital_input", Decimal("1"), "main_extension_vif"),
        0x1C: (Unit("baud_rate", "baud"), "baud_rate", Decimal("1"), "main_extension_vif"),
        0x1D: (Unit("response_delay_time", "bit-times"), "response_delay_time", Decimal("1"), "main_extension_vif"),
        0x1E: (Unit("retry", None), "retry", Decimal("1"), "main_extension_vif"),
        0x1F: (Unit("remote_control", None), "remote_control", Decimal("1"), "main_extension_vif"),
        0x20: (Unit("first_storage_number", None), "first_storage_number", Decimal("1"), "main_extension_vif"),
        0x21: (Unit("last_storage_number", None), "last_storage_number", Decimal("1"), "main_extension_vif"),
        0x22: (Unit("size_of_storage_block", None), "size_of_storage_block", Decimal("1"), "main_extension_vif"),
        0x23: (Unit("tariff_subunit_descriptor", None), "tariff_subunit_descriptor", Decimal("1"), "main_extension_vif"),
        0x28: (Unit("storage_interval", "month"), "storage_interval", Decimal("1"), "main_extension_vif"),
        0x29: (Unit("storage_interval", "year"), "storage_interval", Decimal("1"), "main_extension_vif"),
        0x2A: (Unit("operator_specific_data", None), "operator_specific_data", Decimal("1"), "main_extension_vif"),
        0x2B: (Unit("time_point_second", "s"), "time_point_second", Decimal("1"), "main_extension_vif"),
        0x30: (Unit("tariff_start_datetime", None), "tariff_start_datetime", Decimal("1"), "main_extension_vif"),
        0x38: (Unit("tariff_period", "month"), "tariff_period", Decimal("1"), "main_extension_vif"),
        0x39: (Unit("tariff_period", "year"), "tariff_period", Decimal("1"), "main_extension_vif"),
        0x3A: (Unit("dimensionless", None), "dimensionless", Decimal("1"), "main_extension_vif"),
        0x3B: (Unit("wireless_mbus_data_container", None), "wireless_mbus_data_container", Decimal("1"), "main_extension_vif"),
        0x60: (Unit("reset_counter", None), "reset_counter", Decimal("1"), "main_extension_vif"),
        0x61: (Unit("cumulation_counter", None), "cumulation_counter", Decimal("1"), "main_extension_vif"),
        0x62: (Unit("control_signal", None), "control_signal", Decimal("1"), "main_extension_vif"),
        0x63: (Unit("day_of_week", None), "day_of_week", Decimal("1"), "main_extension_vif"),
        0x64: (Unit("week_number", None), "week_number", Decimal("1"), "main_extension_vif"),
        0x65: (Unit("time_point_of_day_change", None), "time_point_of_day_change", Decimal("1"), "main_extension_vif"),
        0x66: (Unit("state_of_parameter_activation", None), "state_of_parameter_activation", Decimal("1"), "main_extension_vif"),
        0x67: (Unit("special_supplier_information", None), "special_supplier_information", Decimal("1"), "main_extension_vif"),
        0x70: (Unit("battery_change_datetime", None), "battery_change_datetime", Decimal("1"), "main_extension_vif"),
        0x71: (Unit("rf_level", "dBm"), "rf_level", Decimal("1"), "main_extension_vif"),
        0x72: (Unit("daylight_savings", None), "daylight_savings", Decimal("1"), "main_extension_vif"),
        0x73: (Unit("listening_window_management", None), "listening_window_management", Decimal("1"), "main_extension_vif"),
        0x74: (Unit("remaining_battery_lifetime", "days"), "remaining_battery_lifetime", Decimal("1"), "main_extension_vif"),
        0x75: (Unit("meter_stop_count", None), "meter_stop_count", Decimal("1"), "main_extension_vif"),
        0x76: (Unit("manufacturer_specific_protocol_data_container", None), "manufacturer_specific_protocol_data_container", Decimal("1"), "main_extension_vif"),
    }
    if first in table:
        return table[first]

    if 0x24 <= first <= 0x27:
        return Unit("storage_interval", "s"), "storage_interval", _time_multiplier(first & 0x03), "main_extension_vif"
    if 0x2C <= first <= 0x2F:
        return Unit("duration_since_last_readout", "s"), "duration_since_last_readout", _time_multiplier(first & 0x03), "main_extension_vif"
    if 0x31 <= first <= 0x33:
        return Unit("tariff_duration", "s"), "tariff_duration", _time_multiplier(first & 0x03), "main_extension_vif"
    if 0x34 <= first <= 0x37:
        return Unit("tariff_period", "s"), "tariff_period", _time_multiplier(first & 0x03), "main_extension_vif"
    if 0x3C <= first <= 0x3F:
        return Unit("nominal_transmission_period", "s"), "nominal_transmission_period", _time_multiplier(first & 0x03), "main_extension_vif"
    if 0x40 <= first <= 0x4F:
        return Unit("voltage", "V"), "voltage", _power10((first & 0x0F) - 9), "main_extension_vif"
    if 0x50 <= first <= 0x5F:
        return Unit("current", "A"), "current", _power10((first & 0x0F) - 12), "main_extension_vif"
    if 0x68 <= first <= 0x6B:
        return Unit("duration_since_last_cumulation", None), "duration_since_last_cumulation", _long_duration_multiplier(first & 0x03), "main_extension_vif"
    if 0x6C <= first <= 0x6F:
        return Unit("battery_operating_time", None), "battery_operating_time", _long_duration_multiplier(first & 0x03), "main_extension_vif"

    return None, "reserved_extension", Decimal("1"), f"reserved_main_extension_vif_0x{first:02X}"


def _decode_second_level_extension_vif(second: int) -> tuple[Unit | None, str, Decimal, str | None]:
    if second == 0x00:
        return Unit("currently_selected_application", None), "currently_selected_application", Decimal("1"), "second_level_extension_vif"
    if second in (0x02, 0x03):
        symbol = "month" if second == 0x02 else "year"
        return Unit("remaining_battery_lifetime", symbol), "remaining_battery_lifetime", Decimal("1"), "second_level_extension_vif"
    return None, "reserved_second_level_extension", Decimal("1"), f"reserved_second_level_extension_vif_0x{second:02X}"


def _decode_alternate_extension_vif(extension_bytes: list[int]) -> tuple[Unit | None, str, Decimal, str | None]:
    if not extension_bytes:
        return None, "extension", Decimal("1"), "missing_vife"

    first = extension_bytes[0] & 0x7F
    if 0x00 <= first <= 0x01:
        return Unit("energy", "MWh"), "energy", _power10((first & 0x01) - 1), "alternate_extension_vif"
    if 0x02 <= first <= 0x03:
        return Unit("reactive_energy", "kvarh"), "reactive_energy", _power10(first & 0x01), "alternate_extension_vif"
    if 0x04 <= first <= 0x05:
        return Unit("apparent_energy", "kVAh"), "apparent_energy", _power10(first & 0x01), "alternate_extension_vif"
    if 0x08 <= first <= 0x09:
        return Unit("energy", "GJ"), "energy", _power10((first & 0x01) - 1), "alternate_extension_vif"
    if 0x0C <= first <= 0x0F:
        return Unit("energy", "MCal"), "energy", _power10((first & 0x03) - 1), "alternate_extension_vif"
    if 0x10 <= first <= 0x11:
        return Unit("volume", "m^3"), "volume", _power10((first & 0x01) + 2), "alternate_extension_vif"
    if 0x14 <= first <= 0x17:
        return Unit("reactive_power", "kVAR"), "reactive_power", _power10((first & 0x03) - 3), "alternate_extension_vif"
    if 0x18 <= first <= 0x19:
        return Unit("mass", "t"), "mass", _power10((first & 0x01) + 2), "alternate_extension_vif"
    if 0x1A <= first <= 0x1B:
        return Unit("relative_humidity", "%"), "relative_humidity", _power10((first & 0x01) - 1), "alternate_extension_vif"
    if first == 0x20:
        return Unit("volume", "ft^3"), "volume", Decimal("1"), "alternate_extension_vif"
    if first == 0x21:
        return Unit("volume", "ft^3"), "volume", Decimal("0.1"), "alternate_extension_vif"
    if 0x28 <= first <= 0x29:
        return Unit("power", "MW"), "power", _power10((first & 0x01) - 1), "alternate_extension_vif"
    if first == 0x2A:
        return Unit("phase_u_u", "deg"), "phase_u_u", Decimal("0.1"), "alternate_extension_vif"
    if first == 0x2B:
        return Unit("phase_u_i", "deg"), "phase_u_i", Decimal("0.1"), "alternate_extension_vif"
    if 0x2C <= first <= 0x2F:
        return Unit("frequency", "Hz"), "frequency", _power10((first & 0x03) - 3), "alternate_extension_vif"
    if 0x30 <= first <= 0x31:
        return Unit("power", "GJ/h"), "power", _power10((first & 0x01) - 1), "alternate_extension_vif"
    if 0x34 <= first <= 0x37:
        return Unit("apparent_power", "kVA"), "apparent_power", _power10((first & 0x03) - 3), "alternate_extension_vif"
    if first == 0x68:
        return Unit("resulting_rating_factor", "HCA/h"), "resulting_rating_factor", _power2(-12), "alternate_extension_vif"
    if first == 0x69:
        return Unit("thermal_output_rating_factor", "W"), "thermal_output_rating_factor", Decimal("1"), "alternate_extension_vif"
    if first == 0x6A:
        return Unit("thermal_coupling_rating_factor_overall", None), "thermal_coupling_rating_factor_overall", _power2(-12), "alternate_extension_vif"
    if first == 0x6B:
        return Unit("thermal_coupling_rating_factor_room_side", None), "thermal_coupling_rating_factor_room_side", _power2(-12), "alternate_extension_vif"
    if first == 0x6C:
        return Unit("thermal_coupling_rating_factor_heater_side", None), "thermal_coupling_rating_factor_heater_side", _power2(-12), "alternate_extension_vif"
    if first == 0x6D:
        return Unit("low_temperature_rating_factor", None), "low_temperature_rating_factor", _power2(-12), "alternate_extension_vif"
    if first == 0x6E:
        return Unit("display_output_scaling_factor", "HCA/kWh"), "display_output_scaling_factor", _power2(-12), "alternate_extension_vif"
    if 0x74 <= first <= 0x77:
        return Unit("cold_warm_temperature_limit", "degC"), "cold_warm_temperature_limit", _power10((first & 0x03) - 3), "alternate_extension_vif"
    if 0x78 <= first <= 0x7F:
        return Unit("cumulative_maximum_active_power", "W"), "cumulative_maximum_active_power", _power10((first & 0x07) - 3), "alternate_extension_vif"

    return None, "reserved_alternate_extension", Decimal("1"), f"reserved_alternate_extension_vif_0x{first:02X}"


def _time_multiplier(selector: int) -> Decimal:
    return (Decimal("1"), Decimal("60"), Decimal("3600"), Decimal("86400"))[selector]


def _long_duration_multiplier(selector: int) -> Decimal:
    return (Decimal("3600"), Decimal("86400"), Decimal("1"), Decimal("1"))[selector]


def _power10(exponent: int) -> Decimal:
    return Decimal(10) ** Decimal(exponent)


def _power2(exponent: int) -> Decimal:
    return Decimal(2) ** Decimal(exponent)
