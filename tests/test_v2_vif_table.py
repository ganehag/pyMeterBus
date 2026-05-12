from __future__ import annotations

from decimal import Decimal

import pytest

from meterbus.codec import parse_vif


@pytest.mark.parametrize(
    ("vif", "kind", "unit_name", "symbol", "multiplier"),
    [
        (0x00, "energy", "energy", "Wh", Decimal("0.001")),
        (0x03, "energy", "energy", "Wh", Decimal("1")),
        (0x07, "energy", "energy", "Wh", Decimal("10000")),
        (0x08, "energy", "energy", "J", Decimal("1")),
        (0x0F, "energy", "energy", "J", Decimal("10000000")),
        (0x10, "volume", "volume", "m^3", Decimal("0.000001")),
        (0x13, "volume", "volume", "m^3", Decimal("0.001")),
        (0x17, "volume", "volume", "m^3", Decimal("10")),
        (0x18, "mass", "mass", "kg", Decimal("0.001")),
        (0x1F, "mass", "mass", "kg", Decimal("10000")),
        (0x28, "power", "power", "W", Decimal("0.001")),
        (0x2F, "power", "power", "W", Decimal("10000")),
        (0x30, "power", "power", "J/h", Decimal("1")),
        (0x37, "power", "power", "J/h", Decimal("10000000")),
        (0x38, "volume_flow", "volume_flow", "m^3/h", Decimal("0.000001")),
        (0x3F, "volume_flow", "volume_flow", "m^3/h", Decimal("10")),
        (0x40, "volume_flow", "volume_flow", "m^3/min", Decimal("0.0000001")),
        (0x47, "volume_flow", "volume_flow", "m^3/min", Decimal("1")),
        (0x48, "volume_flow", "volume_flow", "m^3/s", Decimal("0.000000001")),
        (0x4F, "volume_flow", "volume_flow", "m^3/s", Decimal("0.01")),
        (0x50, "mass_flow", "mass_flow", "kg/h", Decimal("0.001")),
        (0x57, "mass_flow", "mass_flow", "kg/h", Decimal("10000")),
        (0x58, "flow_temperature", "flow_temperature", "degC", Decimal("0.001")),
        (0x5B, "flow_temperature", "flow_temperature", "degC", Decimal("1")),
        (0x5C, "return_temperature", "return_temperature", "degC", Decimal("0.001")),
        (0x5F, "return_temperature", "return_temperature", "degC", Decimal("1")),
        (0x60, "temperature_difference", "temperature_difference", "K", Decimal("0.001")),
        (0x63, "temperature_difference", "temperature_difference", "K", Decimal("1")),
        (0x64, "external_temperature", "external_temperature", "degC", Decimal("0.001")),
        (0x67, "external_temperature", "external_temperature", "degC", Decimal("1")),
        (0x68, "pressure", "pressure", "bar", Decimal("0.001")),
        (0x6B, "pressure", "pressure", "bar", Decimal("1")),
    ],
)
def test_base_vif_numeric_ranges(vif, kind, unit_name, symbol, multiplier):
    result = parse_vif(bytes([vif]))
    value_information = result.value_information

    assert result.consumed == 1
    assert value_information.kind == kind
    assert value_information.unit.name == unit_name
    assert value_information.unit.symbol == symbol
    assert value_information.multiplier == multiplier
    assert value_information.extension_bytes == b""
    assert value_information.enhancement is None


@pytest.mark.parametrize(
    ("vif", "kind", "unit_name"),
    [
        (0x6C, "date", "date"),
        (0x6D, "datetime", "datetime"),
        (0x6E, "heat_cost_allocator", "heat_cost_allocator"),
        (0x6F, "reserved", "reserved"),
        (0x74, "actuality_duration", "actuality_duration"),
        (0x75, "manufacturer", "manufacturer"),
        (0x76, "enhanced_identification", "enhanced_identification"),
        (0x77, "bus_address", "bus_address"),
        (0x78, "fabrication_number", "fabrication_number"),
        (0x79, "enhanced_identification", "enhanced_identification"),
        (0x7A, "bus_address", "bus_address"),
        (0x7E, "any_vif", "any_vif"),
        (0x7F, "manufacturer_specific", "manufacturer_specific"),
    ],
)
def test_base_vif_discrete_values(vif, kind, unit_name):
    value_information = parse_vif(bytes([vif])).value_information

    assert value_information.kind == kind
    assert value_information.unit.name == unit_name
    assert value_information.multiplier == Decimal("1")


@pytest.mark.parametrize(
    ("vif", "kind", "multiplier"),
    [
        (0x20, "on_time", Decimal("1")),
        (0x21, "on_time", Decimal("60")),
        (0x22, "on_time", Decimal("3600")),
        (0x23, "on_time", Decimal("86400")),
        (0x24, "operating_time", Decimal("1")),
        (0x25, "operating_time", Decimal("60")),
        (0x26, "operating_time", Decimal("3600")),
        (0x27, "operating_time", Decimal("86400")),
        (0x70, "average_duration", Decimal("1")),
        (0x71, "average_duration", Decimal("60")),
        (0x72, "average_duration", Decimal("3600")),
        (0x73, "average_duration", Decimal("86400")),
    ],
)
def test_base_vif_duration_ranges(vif, kind, multiplier):
    value_information = parse_vif(bytes([vif])).value_information

    assert value_information.kind == kind
    assert value_information.unit.symbol == "s"
    assert value_information.multiplier == multiplier


def test_unknown_base_vif_stays_preserved():
    value_information = parse_vif(bytes([0x7D])).value_information

    assert value_information.unit is None
    assert value_information.kind == "unknown"
    assert value_information.multiplier == Decimal("1")
    assert value_information.enhancement == "unknown_base_vif_0x7D"
