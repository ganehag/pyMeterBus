"""Thin public decode API for pyMeterBus 2.0.

This module currently decodes frame envelopes and variable-data telegram
headers. DIF/VIF application records belong in later slices.
"""

from __future__ import annotations

from meterbus.codec import FrameDecoder, TelegramDecoder
from meterbus.model import DecodeError, DecodeMode, DecodeResult, Telegram


_FRAME_DECODER = FrameDecoder()
_TELEGRAM_DECODER = TelegramDecoder(frame_decoder=_FRAME_DECODER)


def decode(data: bytes | bytearray | memoryview | list[int] | tuple[int, ...], mode: DecodeMode = DecodeMode.STRICT) -> DecodeResult:
    """Decode bytes into the current v2 result model."""

    return _TELEGRAM_DECODER.decode(data, mode=mode)


def decode_one_frame(data: bytes | bytearray | memoryview | list[int] | tuple[int, ...], mode: DecodeMode = DecodeMode.STRICT):
    """Decode one frame or raise `DecodeError`."""

    frame_result = _FRAME_DECODER.decode(data, mode=mode)
    if frame_result.frame is None or not frame_result.ok:
        message = frame_result.diagnostics[0].message if frame_result.diagnostics else "unable to decode frame"
        raise DecodeError(message, diagnostics=frame_result.diagnostics)
    return frame_result.frame


def decode_one(data: bytes | bytearray | memoryview | list[int] | tuple[int, ...], mode: DecodeMode = DecodeMode.STRICT) -> Telegram:
    """Decode one application telegram or raise `DecodeError`."""

    result = decode(data, mode=mode)
    if result.telegram is None:
        raise DecodeError(
            "application telegram decoding is not available for this frame",
            diagnostics=result.diagnostics,
        )
    return result.telegram
