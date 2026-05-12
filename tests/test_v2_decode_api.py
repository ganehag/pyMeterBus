from __future__ import annotations

import pytest

import meterbus
from meterbus.api import decode, decode_one, decode_one_frame
from meterbus.model import DecodeError, DecodeMode, DecodeResult, FrameKind, ShortFrame
from tests.helpers.fixtures import load_hex_fixture


def test_decode_returns_decode_result_with_frame_but_no_telegram_yet():
    raw = load_hex_fixture("frames/short.hex").data

    result = decode(raw)

    assert isinstance(result, DecodeResult)
    assert result.ok is True
    assert isinstance(result.frame, ShortFrame)
    assert result.frame.kind is FrameKind.SHORT
    assert result.telegram is None
    assert result.raw == raw
    assert result.diagnostics == ()


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


def test_decode_one_raises_until_application_telegram_decoding_exists():
    raw = load_hex_fixture("frames/short.hex").data

    with pytest.raises(DecodeError) as exc_info:
        decode_one(raw)

    assert str(exc_info.value) == "application telegram decoding is not implemented yet"


def test_decode_preserves_frame_decoder_errors_in_decode_result():
    result = decode(b"")

    assert result.ok is False
    assert result.frame is None
    assert result.telegram is None
    assert result.diagnostics[0].code == "empty_input"
