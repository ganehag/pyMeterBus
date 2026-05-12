from __future__ import annotations

from decimal import Decimal

import pytest

from meterbus.codec import ValueDecodeError, decode_value, parse_dif, parse_vif
from meterbus.model import DataEncoding, DataInformation, FunctionType, Unit, ValueType
from tests.helpers.fixtures import load_hex_fixture


def _dif(encoding: DataEncoding) -> DataInformation:
    return DataInformation(
        raw=b"",
        data_encoding=encoding,
        function=FunctionType.INSTANTANEOUS_VALUE,
        storage_number=0,
    )


def test_decode_no_data_value_consumes_no_bytes():
    result = decode_value(b"abc", _dif(DataEncoding.NO_DATA), data_length=0)

    assert result.consumed == 0
    assert result.value.raw == b""
    assert result.value.value is None
    assert result.value.type is ValueType.NONE


def test_decode_signed_little_endian_integer():
    unit = Unit("temperature", "degC")

    result = decode_value(bytes([0xFE, 0xFF]), _dif(DataEncoding.INTEGER), data_length=2, unit=unit)

    assert result.consumed == 2
    assert result.value.raw == b"\xFE\xFF"
    assert result.value.value == -2
    assert result.value.type is ValueType.INTEGER
    assert result.value.unit is unit


def test_decode_bcd_value():
    result = decode_value(bytes([0x49, 0x04, 0x00, 0x64]), _dif(DataEncoding.BCD), data_length=4)

    assert result.consumed == 4
    assert result.value.raw == b"\x49\x04\x00\x64"
    assert result.value.value == Decimal("64000449")
    assert result.value.type is ValueType.DECIMAL


def test_decode_real32_value():
    result = decode_value(bytes.fromhex("00 00 80 3F"), _dif(DataEncoding.REAL), data_length=4)

    assert result.consumed == 4
    assert result.value.value == Decimal("1.0")
    assert result.value.type is ValueType.DECIMAL


def test_decode_variable_length_text_payload_uses_mode_1_order_by_default():
    result = decode_value(bytes([0x03, 0x41, 0x42, 0x43, 0x99]), _dif(DataEncoding.VARIABLE_LENGTH), data_length=None)

    assert result.consumed == 4
    assert result.value.raw == b"ABC"
    assert result.value.value == "CBA"
    assert result.value.type is ValueType.STRING


def test_decode_variable_length_text_payload_can_use_mode_2_order():
    result = decode_value(
        bytes([0x03, 0x41, 0x42, 0x43, 0x99]),
        _dif(DataEncoding.VARIABLE_LENGTH),
        data_length=None,
        lsb_order=False,
    )

    assert result.consumed == 4
    assert result.value.raw == b"ABC"
    assert result.value.value == "ABC"
    assert result.value.type is ValueType.STRING


def test_decode_special_function_consumes_no_bytes():
    result = decode_value(b"abc", _dif(DataEncoding.SPECIAL_FUNCTION), data_length=0)

    assert result.consumed == 0
    assert result.value.raw == b""
    assert result.value.value is None
    assert result.value.type is ValueType.UNKNOWN


def test_decode_unknown_encoding_preserves_fixed_raw_value():
    result = decode_value(bytes([0xAA, 0xBB]), _dif(DataEncoding.UNKNOWN), data_length=2)

    assert result.consumed == 2
    assert result.value.raw == b"\xAA\xBB"
    assert result.value.value == b"\xAA\xBB"
    assert result.value.type is ValueType.UNKNOWN


def test_decode_first_fixture_value_without_scaling():
    raw = load_hex_fixture("frames/long_basic.hex").data
    application_data = raw[7:-2][12:]
    dif_result = parse_dif(application_data)
    vif_result = parse_vif(application_data[dif_result.consumed:])
    value_offset = dif_result.consumed + vif_result.consumed

    result = decode_value(
        application_data[value_offset:],
        dif_result.data_information,
        dif_result.data_length,
        unit=vif_result.value_information.unit,
    )

    assert result.consumed == 4
    assert result.value.raw == b"\x49\x04\x00\x64"
    assert result.value.value == Decimal("64000449")
    assert result.value.unit.name == "fabrication_number"


def test_decode_value_accepts_input_sequence_types():
    dif = _dif(DataEncoding.INTEGER)

    assert decode_value(bytearray([1]), dif, 1).value.value == 1
    assert decode_value(memoryview(b"\x01"), dif, 1).value.value == 1
    assert decode_value([1], dif, 1).value.value == 1
    assert decode_value((1,), dif, 1).value.value == 1


def test_decode_value_rejects_unsupported_input_type():
    with pytest.raises(TypeError, match="unsupported value input type"):
        decode_value(object(), _dif(DataEncoding.INTEGER), 1)


def test_decode_value_rejects_truncated_fixed_value():
    with pytest.raises(ValueDecodeError, match="not enough bytes"):
        decode_value(b"\x01", _dif(DataEncoding.INTEGER), 2)


def test_decode_value_rejects_invalid_bcd_nibble():
    with pytest.raises(ValueDecodeError, match="non-decimal nibble"):
        decode_value(bytes([0xFA]), _dif(DataEncoding.BCD), 1)


def test_decode_value_rejects_wrong_real_length():
    with pytest.raises(ValueDecodeError, match="real values must be 4 bytes"):
        decode_value(b"\x00\x00", _dif(DataEncoding.REAL), 2)


def test_decode_value_rejects_truncated_variable_length_value():
    with pytest.raises(ValueDecodeError, match="truncated"):
        decode_value(bytes([0x03, 0x41]), _dif(DataEncoding.VARIABLE_LENGTH), None)
