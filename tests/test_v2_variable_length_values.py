from __future__ import annotations

from decimal import Decimal

import pytest

from meterbus.codec import ValueDecodeError, decode_record, decode_value, parse_dif
from meterbus.model import DataEncoding, DataInformation, FunctionType, ValueType


def _variable_dif() -> DataInformation:
    return DataInformation(
        raw=b"\x0D",
        data_encoding=DataEncoding.VARIABLE_LENGTH,
        function=FunctionType.INSTANTANEOUS_VALUE,
        storage_number=0,
    )


def test_decode_variable_length_ascii_string_value():
    result = decode_value(bytes([0xC3]) + b"ABC", _variable_dif(), data_length=None)

    assert result.consumed == 4
    assert result.value.raw == b"ABC"
    assert result.value.value == "ABC"
    assert result.value.type is ValueType.STRING


def test_decode_variable_length_positive_bcd_value():
    result = decode_value(bytes([0xD2, 0x21, 0x43]), _variable_dif(), data_length=None)

    assert result.consumed == 3
    assert result.value.raw == b"\x21\x43"
    assert result.value.value == Decimal("1234")
    assert result.value.type is ValueType.DECIMAL


def test_decode_variable_length_negative_bcd_value():
    result = decode_value(bytes([0xE2, 0x21, 0x43]), _variable_dif(), data_length=None)

    assert result.consumed == 3
    assert result.value.raw == b"\x21\x43"
    assert result.value.value == Decimal("-1234")
    assert result.value.type is ValueType.DECIMAL


def test_decode_variable_length_plain_marker_stays_binary():
    result = decode_value(bytes([0x03]) + b"ABC", _variable_dif(), data_length=None)

    assert result.consumed == 4
    assert result.value.raw == b"ABC"
    assert result.value.value == b"ABC"
    assert result.value.type is ValueType.BINARY


def test_decode_variable_length_ascii_with_control_byte_stays_binary():
    result = decode_value(bytes([0xC3, 0x41, 0x00, 0x42]), _variable_dif(), data_length=None)

    assert result.consumed == 4
    assert result.value.raw == b"A\x00B"
    assert result.value.value == b"A\x00B"
    assert result.value.type is ValueType.BINARY


def test_decode_variable_length_invalid_bcd_stays_binary():
    result = decode_value(bytes([0xD1, 0xFA]), _variable_dif(), data_length=None)

    assert result.consumed == 2
    assert result.value.raw == b"\xFA"
    assert result.value.value == b"\xFA"
    assert result.value.type is ValueType.BINARY


def test_decode_record_uses_semantic_variable_length_value():
    result = decode_record(bytes([0x0D, 0x78, 0xC3]) + b"ABC")
    record = result.record

    assert result.consumed == 6
    assert record.dif.data_encoding is DataEncoding.VARIABLE_LENGTH
    assert record.vif.kind == "fabrication_number"
    assert record.value.raw == b"ABC"
    assert record.value.value == "ABC"
    assert record.value.type is ValueType.STRING


def test_decode_variable_length_rejects_truncated_value():
    with pytest.raises(ValueDecodeError, match="truncated"):
        decode_value(bytes([0xC3, 0x41]), _variable_dif(), data_length=None)


def test_parse_dif_variable_length_still_has_no_fixed_length():
    result = parse_dif(bytes([0x0D]))

    assert result.data_length is None
    assert result.data_information.data_encoding is DataEncoding.VARIABLE_LENGTH
