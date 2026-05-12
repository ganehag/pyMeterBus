from __future__ import annotations

from decimal import Decimal

import pytest

from meterbus.api import decode
from meterbus.codec import ValueInformationParseError, parse_dif, parse_vif
from tests.helpers.fixtures import load_hex_fixture


def test_parse_energy_vif():
    result = parse_vif(bytes([0x03]))
    vif = result.value_information

    assert result.consumed == 1
    assert result.has_extension is False
    assert result.is_custom_vif is False
    assert vif.raw == b"\x03"
    assert vif.unit.name == "energy"
    assert vif.unit.symbol == "Wh"
    assert vif.kind == "energy"
    assert vif.multiplier == Decimal("1")
    assert vif.extension_bytes == b""


def test_parse_volume_vif():
    result = parse_vif(bytes([0x13]))
    vif = result.value_information

    assert result.consumed == 1
    assert vif.unit.name == "volume"
    assert vif.unit.symbol == "m^3"
    assert vif.kind == "volume"
    assert vif.multiplier == Decimal("0.001")


def test_parse_known_plain_fixture_vifs():
    fabrication = parse_vif(bytes([0x78])).value_information

    assert fabrication.kind == "fabrication_number"
    assert fabrication.unit.name == "fabrication_number"


def test_parse_main_extension_vif_customer_location_and_customer():
    location = parse_vif(bytes([0xFD, 0x10])).value_information
    customer = parse_vif(bytes([0xFD, 0x11])).value_information

    assert location.kind == "customer_location"
    assert location.unit.name == "customer_location"
    assert location.enhancement == "main_extension_vif"
    assert customer.kind == "customer"
    assert customer.unit.name == "customer"
    assert customer.enhancement == "main_extension_vif"


@pytest.mark.parametrize(
    ("vife", "kind", "unit", "symbol"),
    [
        (0x08, "unique_message_identification", "unique_message_identification", None),
        (0x09, "device_type", "device_type", None),
        (0x0A, "manufacturer", "manufacturer", None),
        (0x0B, "parameter_set_identification", "parameter_set_identification", None),
        (0x0C, "model_version", "model_version", None),
        (0x0D, "hardware_version_number", "hardware_version_number", None),
        (0x0E, "metrology_firmware_version_number", "metrology_firmware_version_number", None),
        (0x0F, "software_version_number", "software_version_number", None),
        (0x12, "access_code_user", "access_code_user", None),
        (0x13, "access_code_operator", "access_code_operator", None),
        (0x14, "access_code_system_operator", "access_code_system_operator", None),
        (0x15, "access_code_developer", "access_code_developer", None),
        (0x16, "password", "password", None),
        (0x17, "error_flags", "error_flags", None),
        (0x18, "error_mask", "error_mask", None),
        (0x19, "security_key", "security_key", None),
        (0x1A, "digital_output", "digital_output", None),
        (0x1B, "digital_input", "digital_input", None),
        (0x1C, "baud_rate", "baud_rate", "baud"),
        (0x1D, "response_delay_time", "response_delay_time", "bit-times"),
        (0x1E, "retry", "retry", None),
        (0x1F, "remote_control", "remote_control", None),
    ],
)
def test_parse_main_extension_identification_and_selection_vifs(vife, kind, unit, symbol):
    vif = parse_vif(bytes([0xFD, vife])).value_information

    assert vif.raw == bytes([0xFD, vife])
    assert vif.extension_bytes == bytes([vife])
    assert vif.kind == kind
    assert vif.unit.name == unit
    assert vif.unit.symbol == symbol
    assert vif.multiplier == Decimal("1")
    assert vif.enhancement == "main_extension_vif"


@pytest.mark.parametrize(
    ("vife", "kind", "symbol", "multiplier"),
    [
        (0x24, "storage_interval", "s", Decimal("1")),
        (0x25, "storage_interval", "s", Decimal("60")),
        (0x26, "storage_interval", "s", Decimal("3600")),
        (0x27, "storage_interval", "s", Decimal("86400")),
        (0x2C, "duration_since_last_readout", "s", Decimal("1")),
        (0x2D, "duration_since_last_readout", "s", Decimal("60")),
        (0x2E, "duration_since_last_readout", "s", Decimal("3600")),
        (0x2F, "duration_since_last_readout", "s", Decimal("86400")),
        (0x31, "tariff_duration", "s", Decimal("60")),
        (0x32, "tariff_duration", "s", Decimal("3600")),
        (0x33, "tariff_duration", "s", Decimal("86400")),
        (0x34, "tariff_period", "s", Decimal("1")),
        (0x35, "tariff_period", "s", Decimal("60")),
        (0x36, "tariff_period", "s", Decimal("3600")),
        (0x37, "tariff_period", "s", Decimal("86400")),
    ],
)
def test_parse_main_extension_duration_vifs(vife, kind, symbol, multiplier):
    vif = parse_vif(bytes([0xFD, vife])).value_information

    assert vif.kind == kind
    assert vif.unit.symbol == symbol
    assert vif.multiplier == multiplier
    assert vif.enhancement == "main_extension_vif"


@pytest.mark.parametrize(
    ("vife", "kind", "symbol", "multiplier"),
    [
        (0x40, "voltage", "V", Decimal("0.000000001")),
        (0x4F, "voltage", "V", Decimal("1000000")),
        (0x50, "current", "A", Decimal("0.000000000001")),
        (0x5F, "current", "A", Decimal("1000")),
        (0x71, "rf_level", "dBm", Decimal("1")),
        (0x74, "remaining_battery_lifetime", "days", Decimal("1")),
    ],
)
def test_parse_main_extension_units(vife, kind, symbol, multiplier):
    vif = parse_vif(bytes([0xFD, vife])).value_information

    assert vif.kind == kind
    assert vif.unit.symbol == symbol
    assert vif.multiplier == multiplier


def test_parse_second_level_extension_vif_currently_selected_application():
    result = parse_vif(bytes([0xFD, 0xFD, 0x00]))
    vif = result.value_information

    assert result.consumed == 3
    assert result.has_extension is True
    assert vif.raw == b"\xFD\xFD\x00"
    assert vif.extension_bytes == b"\xFD\x00"
    assert vif.kind == "currently_selected_application"
    assert vif.enhancement == "second_level_extension_vif"


@pytest.mark.parametrize(
    ("vife", "kind", "symbol", "multiplier"),
    [
        (0x00, "energy", "MWh", Decimal("0.1")),
        (0x01, "energy", "MWh", Decimal("1")),
        (0x02, "reactive_energy", "kvarh", Decimal("1")),
        (0x03, "reactive_energy", "kvarh", Decimal("10")),
        (0x04, "apparent_energy", "kVAh", Decimal("1")),
        (0x05, "apparent_energy", "kVAh", Decimal("10")),
        (0x08, "energy", "GJ", Decimal("0.1")),
        (0x09, "energy", "GJ", Decimal("1")),
        (0x1A, "relative_humidity", "%", Decimal("0.1")),
        (0x1B, "relative_humidity", "%", Decimal("1")),
        (0x20, "volume", "ft^3", Decimal("1")),
        (0x21, "volume", "ft^3", Decimal("0.1")),
        (0x2C, "frequency", "Hz", Decimal("0.001")),
        (0x2F, "frequency", "Hz", Decimal("1")),
        (0x34, "apparent_power", "kVA", Decimal("0.001")),
        (0x37, "apparent_power", "kVA", Decimal("1")),
    ],
)
def test_parse_alternate_extension_vifs(vife, kind, symbol, multiplier):
    vif = parse_vif(bytes([0xFB, vife])).value_information

    assert vif.raw == bytes([0xFB, vife])
    assert vif.extension_bytes == bytes([vife])
    assert vif.kind == kind
    assert vif.unit.symbol == symbol
    assert vif.multiplier == multiplier
    assert vif.enhancement == "alternate_extension_vif"


def test_parse_combinable_vife_preserves_base_vif_kind():
    result = parse_vif(bytes([0x83, 0x33]))
    vif = result.value_information

    assert result.consumed == 2
    assert vif.raw == b"\x83\x33"
    assert vif.kind == "energy"
    assert vif.unit.symbol == "Wh"
    assert vif.extension_bytes == b"\x33"
    assert vif.enhancement == "vife_extension"


def test_parse_custom_vif():
    result = parse_vif(bytes([0x7C, 0x03]) + b"ABC")
    vif = result.value_information

    assert result.consumed == 5
    assert result.is_custom_vif is True
    assert vif.kind == "custom_vif"
    assert vif.custom_vif == b"ABC"
    assert vif.unit.name == "ABC"


def test_parse_manufacturer_specific_vif_is_preserved():
    result = parse_vif(bytes([0x7F]))
    vif = result.value_information

    assert result.consumed == 1
    assert vif.unit.name == "manufacturer_specific"
    assert vif.kind == "manufacturer_specific"
    assert vif.multiplier == Decimal("1")


def test_parse_vif_after_first_dif_from_long_fixture():
    telegram = decode(load_hex_fixture("frames/long_basic.hex").data).telegram
    dif_result = parse_dif(telegram.raw_application_data)
    vif_result = parse_vif(telegram.raw_application_data[dif_result.consumed:])
    vif = vif_result.value_information

    assert vif_result.consumed == 1
    assert vif.raw == b"\x78"
    assert vif.kind == "fabrication_number"
    assert vif.unit.name == "fabrication_number"


def test_parse_vif_accepts_input_sequence_types():
    assert parse_vif(bytearray([0x78])).value_information.raw == b"\x78"
    assert parse_vif(memoryview(b"\x78")).value_information.raw == b"\x78"
    assert parse_vif([0x78]).value_information.raw == b"\x78"
    assert parse_vif((0x78,)).value_information.raw == b"\x78"


def test_parse_vif_rejects_empty_input():
    with pytest.raises(ValueInformationParseError, match="empty input"):
        parse_vif(b"")


def test_parse_vif_rejects_missing_vife():
    with pytest.raises(ValueInformationParseError, match="VIFE byte is missing"):
        parse_vif(bytes([0xFD]))


def test_parse_vif_rejects_truncated_custom_vif():
    with pytest.raises(ValueInformationParseError, match="custom VIF text is truncated"):
        parse_vif(bytes([0x7C, 0x03, 0x41]))


def test_parse_vif_rejects_unsupported_input_type():
    with pytest.raises(TypeError, match="unsupported VIF input type"):
        parse_vif(object())
