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


def test_decode_lvar_text_defaults_to_mode_1_character_order():
    result = decode_value(bytes([0x03]) + b"ABC", _variable_dif(), data_length=None)

    assert result.consumed == 4
    assert result.value.raw == b"ABC"
    assert result.value.value == "CBA"
    assert result.value.type is ValueType.STRING


def test_decode_lvar_text_supports_mode_2_character_order():
    result = decode_value(bytes([0x03]) + b"ABC", _variable_dif(), data_length=None, lsb_order=False)

    assert result.consumed == 4
    assert result.value.raw == b"ABC"
    assert result.value.value == "ABC"
    assert result.value.type is ValueType.STRING


def test_decode_lvar_text_supports_latin_1():
    result = decode_value(bytes([0x01, 0xE5]), _variable_dif(), data_length=None)

    assert result.consumed == 2
    assert result.value.raw == b"\xE5"
    assert result.value.value == "å"
    assert result.value.type is ValueType.STRING


def test_decode_variable_length_positive_bcd_value():
    result = decode_value(bytes([0xC2, 0x21, 0x43]), _variable_dif(), data_length=None)

    assert result.consumed == 3
    assert result.value.raw == b"\x21\x43"
    assert result.value.value == Decimal("1234")
    assert result.value.type is ValueType.DECIMAL


def test_decode_variable_length_negative_bcd_value():
    result = decode_value(bytes([0xD2, 0x21, 0x43]), _variable_dif(), data_length=None)

    assert result.consumed == 3
    assert result.value.raw == b"\x21\x43"
    assert result.value.value == Decimal("-1234")
    assert result.value.type is ValueType.DECIMAL


def test_decode_variable_length_binary_value():
    result = decode_value(bytes([0xE3, 0x41, 0x00, 0x42]), _variable_dif(), data_length=None)

    assert result.consumed == 4
    assert result.value.raw == b"A\x00B"
    assert result.value.value == b"A\x00B"
    assert result.value.type is ValueType.BINARY


def test_decode_variable_length_floating_point_marker_is_preserved_as_binary():
    result = decode_value(bytes([0xF2, 0x41, 0x42]), _variable_dif(), data_length=None)

    assert result.consumed == 3
    assert result.value.raw == b"AB"
    assert result.value.value == b"AB"
    assert result.value.type is ValueType.BINARY


def test_decode_variable_length_reserved_marker_consumes_marker_only():
    result = decode_value(bytes([0xFB, 0x41, 0x42]), _variable_dif(), data_length=None)

    assert result.consumed == 1
    assert result.value.raw == b""
    assert result.value.value == b""
    assert result.value.type is ValueType.BINARY


def test_decode_variable_length_invalid_bcd_raises():
    with pytest.raises(ValueDecodeError, match="non-decimal nibble"):
        decode_value(bytes([0xC1, 0xFA]), _variable_dif(), data_length=None)


def test_decode_record_uses_semantic_variable_length_value():
    result = decode_record(bytes([0x0D, 0x78, 0x03]) + b"ABC")
    record = result.record

    assert result.consumed == 6
    assert record.dif.data_encoding is DataEncoding.VARIABLE_LENGTH
    assert record.vif.kind == "fabrication_number"
    assert record.value.raw == b"ABC"
    assert record.value.value == "CBA"
    assert record.value.type is ValueType.STRING


def test_decode_amt_customer_record_uses_mode_1_character_order():
    result = decode_record(bytes.fromhex("0D FD 11 0C 47 41 20 6F 72 74 65 6D 61 75 71 41"))
    record = result.record

    assert result.consumed == 16
    assert record.vif.kind == "customer"
    assert record.value.raw == bytes.fromhex("47 41 20 6F 72 74 65 6D 61 75 71 41")
    assert record.value.value == "Aquametro AG"
    assert record.value.type is ValueType.STRING


def test_decode_variable_length_rejects_truncated_value():
    with pytest.raises(ValueDecodeError, match="truncated"):
        decode_value(bytes([0x03, 0x41]), _variable_dif(), data_length=None)


def test_parse_dif_variable_length_still_has_no_fixed_length():
    result = parse_dif(bytes([0x0D]))

    assert result.data_length is None
    assert result.data_information.data_encoding is DataEncoding.VARIABLE_LENGTH
