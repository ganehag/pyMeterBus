from __future__ import annotations

from meterbus.codec import decode_record
from meterbus.model import ValueType


def test_decode_date_value_from_vif_6c():
    result = decode_record(bytes([0x02, 0x6C, 0x21, 0x2C]))
    record = result.record

    assert result.consumed == 4
    assert record.vif.kind == "date"
    assert record.value.raw == b"\x21\x2C"
    assert record.value.value == "2022-12-01"
    assert record.value.type is ValueType.DATE
    assert record.value.scaled is False


def test_decode_datetime_value_from_vif_6d():
    result = decode_record(bytes([0x04, 0x6D, 0x22, 0x0E, 0x15, 0x0C]))
    record = result.record

    assert result.consumed == 6
    assert record.vif.kind == "datetime"
    assert record.value.raw == b"\x22\x0E\x15\x0C"
    assert record.value.value == "2024-12-21T14:34:00"
    assert record.value.type is ValueType.DATETIME
    assert record.value.scaled is False


def test_invalid_date_value_falls_back_to_raw_integer_value():
    result = decode_record(bytes([0x02, 0x6C, 0x00, 0x00]))
    record = result.record

    assert record.vif.kind == "date"
    assert record.value.raw == b"\x00\x00"
    assert record.value.value == 0
    assert record.value.type is ValueType.INTEGER
    assert record.value.scaled is False


def test_invalid_datetime_value_falls_back_to_raw_integer_value():
    result = decode_record(bytes([0x04, 0x6D, 0x3F, 0x1F, 0x00, 0x00]))
    record = result.record

    assert record.vif.kind == "datetime"
    assert record.value.raw == b"\x3F\x1F\x00\x00"
    assert record.value.value == 2039615
    assert record.value.type is ValueType.INTEGER
    assert record.value.scaled is False
