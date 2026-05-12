from __future__ import annotations

from decimal import Decimal

import pytest

from meterbus.api import decode
from meterbus.codec import DataRecordDecodeError, decode_record
from meterbus.model import DataEncoding, FunctionType, ValueType
from tests.helpers.fixtures import load_hex_fixture


def test_decode_first_record_from_long_fixture_payload():
    telegram = decode(load_hex_fixture("frames/long_basic.hex").data).telegram

    result = decode_record(telegram.raw_application_data)
    record = result.record

    assert result.consumed == 6
    assert record.raw == b"\x0C\x78\x49\x04\x00\x64"
    assert record.dif.raw == b"\x0C"
    assert record.dif.data_encoding is DataEncoding.BCD
    assert record.vif.raw == b"\x78"
    assert record.vif.kind == "fabrication_number"
    assert record.value.raw == b"\x49\x04\x00\x64"
    assert record.value.value == Decimal("64000449")
    assert record.value.type is ValueType.DECIMAL
    assert record.value.unit.name == "fabrication_number"
    assert record.function is FunctionType.INSTANTANEOUS_VALUE
    assert record.storage_number == 0
    assert record.tariff is None
    assert record.subunit is None
    assert record.more_records_follow is False
    assert record.diagnostics == ()


def test_decode_integer_record():
    result = decode_record(bytes([0x02, 0x13, 0x34, 0x12]))
    record = result.record

    assert result.consumed == 4
    assert record.raw == b"\x02\x13\x34\x12"
    assert record.dif.data_encoding is DataEncoding.INTEGER
    assert record.vif.kind == "volume"
    assert record.value.value == 0x1234
    assert record.value.type is ValueType.INTEGER
    assert record.value.unit.name == "volume"


def test_decode_record_with_dife_metadata():
    result = decode_record(bytes([0x84, 0x51, 0x78, 0x01, 0x00, 0x00, 0x00]))
    record = result.record

    assert result.consumed == 7
    assert record.dif.raw == b"\x84\x51"
    assert record.dif.extension_bytes == b"\x51"
    assert record.storage_number == 2
    assert record.tariff == 1
    assert record.subunit == 1
    assert record.value.value == 1


def test_decode_no_data_record_consumes_only_dif_and_vif():
    result = decode_record(bytes([0x00, 0x78, 0x99]))
    record = result.record

    assert result.consumed == 2
    assert record.raw == b"\x00\x78"
    assert record.value.value is None
    assert record.value.type is ValueType.NONE


def test_decode_record_accepts_input_sequence_types():
    assert decode_record(bytearray([0x01, 0x78, 0x01])).record.value.value == 1
    assert decode_record(memoryview(b"\x01\x78\x01")).record.value.value == 1
    assert decode_record([0x01, 0x78, 0x01]).record.value.value == 1
    assert decode_record((0x01, 0x78, 0x01)).record.value.value == 1


def test_decode_record_rejects_empty_input():
    with pytest.raises(DataRecordDecodeError, match="empty input"):
        decode_record(b"")


def test_decode_record_rejects_unsupported_input_type():
    with pytest.raises(TypeError, match="unsupported record input type"):
        decode_record(object())


def test_decode_record_wraps_dif_parse_errors():
    with pytest.raises(DataRecordDecodeError, match="DIFE byte is missing"):
        decode_record(bytes([0x84]))


def test_decode_record_wraps_vif_parse_errors():
    with pytest.raises(DataRecordDecodeError, match="VIFE byte is missing"):
        decode_record(bytes([0x01, 0xFD]))


def test_decode_record_wraps_value_decode_errors():
    with pytest.raises(DataRecordDecodeError, match="not enough bytes"):
        decode_record(bytes([0x02, 0x78, 0x01]))
