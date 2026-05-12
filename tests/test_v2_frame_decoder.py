from __future__ import annotations

from meterbus.codec import FrameDecoder, checksum, decode_frame
from meterbus.model import (
    AckFrame,
    ControlFrame,
    DecodeMode,
    FrameKind,
    LongFrame,
    Severity,
    ShortFrame,
)
from tests.helpers.fixtures import load_hex_fixture


def test_checksum_returns_low_byte_sum():
    assert checksum(b"\x08\x0B") == 0x13
    assert checksum(bytes([0xFF, 0x02])) == 0x01


def test_decode_ack_frame_fixture():
    raw = load_hex_fixture("frames/ack.hex").data

    result = decode_frame(raw)

    assert result.ok is True
    assert isinstance(result.frame, AckFrame)
    assert result.frame.kind is FrameKind.ACK
    assert result.frame.raw == b"\xE5"
    assert result.diagnostics == ()


def test_decode_short_frame_fixture():
    raw = load_hex_fixture("frames/short.hex").data

    result = decode_frame(raw)

    assert result.ok is True
    assert isinstance(result.frame, ShortFrame)
    assert result.frame.kind is FrameKind.SHORT
    assert result.frame.raw == raw
    assert result.frame.control.raw == 0x08
    assert result.frame.address.value == 0x0B
    assert result.frame.checksum == 0x13
    assert result.frame.checksum_valid is True


def test_decode_control_frame_fixture():
    raw = load_hex_fixture("frames/control.hex").data

    result = decode_frame(raw)

    assert result.ok is True
    assert isinstance(result.frame, ControlFrame)
    assert result.frame.kind is FrameKind.CONTROL
    assert result.frame.raw == raw
    assert result.frame.length == 3
    assert result.frame.control.raw == 0x08
    assert result.frame.address.value == 0x0B
    assert result.frame.ci == 0x72
    assert result.frame.checksum == 0x85
    assert result.frame.checksum_valid is True


def test_decode_long_frame_fixture_preserves_payload():
    raw = load_hex_fixture("frames/long_basic.hex").data

    result = decode_frame(raw)

    assert result.ok is True
    assert isinstance(result.frame, LongFrame)
    assert result.frame.kind is FrameKind.LONG
    assert result.frame.raw == raw
    assert result.frame.length == 0x3D
    assert result.frame.control.raw == 0x08
    assert result.frame.address.value == 0x0B
    assert result.frame.ci == 0x72
    assert result.frame.checksum == 0xDD
    assert result.frame.checksum_valid is True
    assert result.frame.payload == raw[7:-2]


def test_invalid_start_byte_returns_diagnostic():
    raw = load_hex_fixture("frames/invalid_start.hex").data

    result = decode_frame(raw)

    assert result.ok is False
    assert result.frame is None
    assert len(result.diagnostics) == 1
    assert result.diagnostics[0].severity is Severity.FATAL
    assert result.diagnostics[0].code == "invalid_start_byte"


def test_empty_input_returns_diagnostic():
    result = decode_frame(b"")

    assert result.ok is False
    assert result.frame is None
    assert result.diagnostics[0].code == "empty_input"


def test_short_frame_checksum_mismatch_fails_in_strict_mode():
    raw = bytearray(load_hex_fixture("frames/short.hex").data)
    raw[3] = 0x00

    result = decode_frame(bytes(raw), mode=DecodeMode.STRICT)

    assert result.ok is False
    assert result.frame is None
    assert result.diagnostics[0].code == "checksum_mismatch"
    assert result.diagnostics[0].severity is Severity.FATAL


def test_short_frame_checksum_mismatch_is_preserved_in_lenient_mode():
    raw = bytearray(load_hex_fixture("frames/short.hex").data)
    raw[3] = 0x00

    result = decode_frame(bytes(raw), mode=DecodeMode.LENIENT)

    assert result.ok is True
    assert isinstance(result.frame, ShortFrame)
    assert result.frame.checksum_valid is False
    assert result.diagnostics[0].code == "checksum_mismatch"
    assert result.diagnostics[0].severity is Severity.ERROR


def test_ack_with_trailing_bytes_fails_in_strict_mode():
    result = decode_frame(b"\xE5\x00", mode=DecodeMode.STRICT)

    assert result.ok is False
    assert result.frame is None
    assert result.diagnostics[0].code == "trailing_bytes"


def test_ack_with_trailing_bytes_is_preserved_in_lenient_mode():
    result = decode_frame(b"\xE5\x00", mode=DecodeMode.LENIENT)

    assert result.ok is True
    assert isinstance(result.frame, AckFrame)
    assert result.frame.raw == b"\xE5\x00"
    assert result.diagnostics[0].code == "trailing_bytes"


def test_accepts_bytearray_memoryview_and_integer_lists():
    raw = load_hex_fixture("frames/short.hex").data
    decoder = FrameDecoder()

    assert decoder.decode(bytearray(raw)).ok is True
    assert decoder.decode(memoryview(raw)).ok is True
    assert decoder.decode(list(raw)).ok is True
    assert decoder.decode(tuple(raw)).ok is True


def test_long_frame_length_mismatch_fails_in_strict_mode():
    raw = bytearray(load_hex_fixture("frames/control.hex").data)
    raw[1] = 0x04

    result = decode_frame(bytes(raw), mode=DecodeMode.STRICT)

    assert result.ok is False
    assert result.frame is None
    assert result.diagnostics[0].code == "length_mismatch"


def test_invalid_long_frame_length_does_not_construct_partial_frame_in_lenient_mode():
    result = decode_frame(bytes([0x68, 0x02, 0x02, 0x68, 0x16]), mode=DecodeMode.LENIENT)

    assert result.ok is False
    assert result.frame is None
    assert result.diagnostics[0].code == "truncated_frame"
    assert result.diagnostics[0].severity is Severity.ERROR


def test_long_frame_declared_length_below_mandatory_fields_returns_diagnostic():
    result = decode_frame(bytes([0x68, 0x02, 0x02, 0x68, 0x00, 0x16]), mode=DecodeMode.LENIENT)

    assert result.ok is False
    assert result.frame is None
    assert result.diagnostics[0].code == "invalid_length"
    assert result.diagnostics[0].severity is Severity.ERROR
