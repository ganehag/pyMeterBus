from __future__ import annotations

import pytest

import meterbus
from meterbus.api import decode, decode_one, decode_one_frame
from meterbus.model import DecodeError, DecodeMode, DecodeResult, FrameKind, ShortFrame, VariableDataTelegram
from tests.helpers.fixtures import load_hex_fixture


def test_decode_returns_decode_result_with_frame_but_no_telegram_for_short_frame():
    raw = load_hex_fixture("frames/short.hex").data

    result = decode(raw)

    assert isinstance(result, DecodeResult)
    assert result.ok is True
    assert isinstance(result.frame, ShortFrame)
    assert result.frame.kind is FrameKind.SHORT
    assert result.telegram is None
    assert result.raw == raw
    assert result.diagnostics == ()


def test_decode_returns_variable_data_telegram_with_records_for_long_frame():
    raw = load_hex_fixture("frames/long_basic.hex").data

    result = decode(raw)

    assert result.ok is True
    assert isinstance(result.telegram, VariableDataTelegram)
    assert result.telegram.header.identification_number == "00000021"
    assert result.telegram.header.manufacturer == "WEP"
    assert result.telegram.header.version == 2
    assert result.telegram.header.medium == 0x1B
    assert result.telegram.header.access_number == 0x12
    assert result.telegram.header.status == 0
    assert len(result.telegram.records) == 3
    assert result.telegram.records[0].vif.kind == "fabrication_number"
    assert result.telegram.records[1].vif.kind == "manufacturer"
    assert result.telegram.records[2].vif.kind == "dimensionless"
    assert result.telegram.raw_application_data == result.frame.payload[12:]
    assert result.telegram.undecoded_data.startswith(b"\x2F\x2F")


def test_decode_is_exposed_from_meterbus_package_root():
    raw = load_hex_fixture("frames/ack.hex").data

    result = meterbus.decode(raw)

    assert result.ok is True
    assert result.frame.kind is FrameKind.ACK


def test_decode_one_frame_returns_frame_or_raises_decode_error():
    raw = load_hex_fixture("frames/short.hex").data

    frame = decode_one_frame(raw)

    assert isinstance(frame, ShortFrame)

    with pytest.raises(DecodeError) as exc_info:
        decode_one_frame(b"\x00")

    assert exc_info.value.diagnostics[0].code == "invalid_start_byte"


def test_decode_one_frame_supports_lenient_mode():
    raw = bytearray(load_hex_fixture("frames/short.hex").data)
    raw[3] = 0x00

    frame = decode_one_frame(bytes(raw), mode=DecodeMode.LENIENT)

    assert isinstance(frame, ShortFrame)
    assert frame.checksum_valid is False


def test_decode_one_returns_variable_data_telegram():
    raw = load_hex_fixture("frames/long_basic.hex").data

    telegram = decode_one(raw)

    assert isinstance(telegram, VariableDataTelegram)
    assert telegram.header.identification_number == "00000021"
    assert len(telegram.records) == 3


def test_decode_one_raises_when_no_application_telegram_is_available():
    raw = load_hex_fixture("frames/short.hex").data

    with pytest.raises(DecodeError) as exc_info:
        decode_one(raw)

    assert str(exc_info.value) == "application telegram decoding is not available for this frame"


def test_decode_preserves_frame_decoder_errors_in_decode_result():
    result = decode(b"")

    assert result.ok is False
    assert result.frame is None
    assert result.telegram is None
    assert result.diagnostics[0].code == "empty_input"
