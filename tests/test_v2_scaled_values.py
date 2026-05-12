from __future__ import annotations

from decimal import Decimal

from meterbus.api import decode
from meterbus.codec import decode_record
from meterbus.model import ValueType
from tests.helpers.fixtures import load_hex_fixture


def test_record_decoder_applies_vif_multiplier_to_numeric_value():
    result = decode_record(bytes([0x02, 0x13, 0x34, 0x12]))
    record = result.record

    assert record.vif.kind == "volume"
    assert record.vif.multiplier == Decimal("0.001")
    assert record.value.raw == b"\x34\x12"
    assert record.value.value == Decimal("4.660")
    assert record.value.type is ValueType.DECIMAL
    assert record.value.unit.name == "volume"
    assert record.value.scaled is True


def test_record_decoder_leaves_multiplier_one_values_unscaled():
    result = decode_record(bytes([0x02, 0x75, 0x0A, 0x00]))
    record = result.record

    assert record.vif.kind == "manufacturer"
    assert record.vif.multiplier == Decimal("1")
    assert record.value.value == 10
    assert record.value.type is ValueType.INTEGER
    assert record.value.scaled is False


def test_record_decoder_does_not_scale_non_numeric_values():
    result = decode_record(bytes([0x0D, 0x78, 0x03]) + b"ABC")
    record = result.record

    assert record.value.value == b"ABC"
    assert record.value.type is ValueType.BINARY
    assert record.value.scaled is False


def test_fixture_record_values_remain_stable_when_multiplier_is_one():
    telegram = decode(load_hex_fixture("frames/long_basic.hex").data).telegram

    assert len(telegram.records) == 3
    assert telegram.records[0].value.value == Decimal("64000449")
    assert telegram.records[0].value.scaled is False
    assert telegram.records[1].value.value == 10
    assert telegram.records[1].value.scaled is False
    assert telegram.records[2].value.value == 30
    assert telegram.records[2].value.scaled is False
