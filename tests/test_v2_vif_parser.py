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
    manufacturer = parse_vif(bytes([0x75])).value_information

    assert fabrication.kind == "fabrication_number"
    assert fabrication.unit.name == "fabrication_number"
    assert manufacturer.kind == "manufacturer"
    assert manufacturer.unit.name == "manufacturer"


def test_parse_first_extension_vif_relative_humidity():
    result = parse_vif(bytes([0x7B, 0x1A]))
    vif = result.value_information

    assert result.consumed == 2
    assert result.has_extension is True
    assert vif.raw == b"\x7B\x1A"
    assert vif.extension_bytes == b"\x1A"
    assert vif.unit.name == "relative_humidity"
    assert vif.unit.symbol == "%RH"
    assert vif.kind == "relative_humidity"
    assert vif.multiplier == Decimal("1")
    assert vif.enhancement == "first_extension_vif"


def test_parse_first_extension_vif_dimensionless():
    result = parse_vif(bytes([0xFD, 0x71]))
    vif = result.value_information

    assert result.consumed == 2
    assert result.has_extension is True
    assert vif.raw == b"\xFD\x71"
    assert vif.extension_bytes == b"\x71"
    assert vif.unit.name == "dimensionless"
    assert vif.kind == "dimensionless"
    assert vif.enhancement == "first_extension_vif"


def test_parse_custom_vif():
    result = parse_vif(bytes([0x7C, 0x03]) + b"ABC")
    vif = result.value_information

    assert result.consumed == 5
    assert result.is_custom_vif is True
    assert vif.kind == "custom_vif"
    assert vif.custom_vif == b"ABC"
    assert vif.unit.name == "ABC"


def test_parse_unknown_vif_is_preserved():
    result = parse_vif(bytes([0x55]))
    vif = result.value_information

    assert result.consumed == 1
    assert vif.unit is None
    assert vif.kind == "unknown"
    assert vif.enhancement == "unknown_base_vif_0x55"


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
