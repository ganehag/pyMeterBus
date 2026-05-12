from __future__ import annotations

from decimal import Decimal

from meterbus.api import decode
from tests.helpers.fixtures import load_hex_fixture


def test_variable_data_record_loop_decodes_records_until_filler():
    result = decode(load_hex_fixture("frames/long_basic.hex").data)
    telegram = result.telegram

    assert result.ok is True
    assert len(telegram.records) == 3
    assert telegram.undecoded_data == bytes.fromhex("2F 2F")

    first, second, third = telegram.records

    assert first.raw == bytes.fromhex("0C 78 49 04 00 64")
    assert first.vif.kind == "fabrication_number"
    assert first.value.value == Decimal("64000449")

    assert second.raw == bytes.fromhex("02 75 0A 00")
    assert second.vif.kind == "manufacturer"
    assert second.value.value == 10

    assert third.raw == bytes.fromhex("01 FD 71 1E")
    assert third.vif.kind == "dimensionless"
    assert third.value.value == 30


def test_record_loop_keeps_full_raw_application_data():
    result = decode(load_hex_fixture("frames/long_basic.hex").data)
    telegram = result.telegram

    assert telegram.raw_application_data == result.frame.payload[12:]
    assert telegram.raw_application_data.startswith(telegram.records[0].raw)
    assert telegram.raw_application_data.endswith(telegram.undecoded_data)
