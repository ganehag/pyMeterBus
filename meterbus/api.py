"""Thin public decode API for pyMeterBus 2.0.

This module intentionally stops at frame-envelope decoding. Telegram body and
application record parsing belong in later slices.
"""

from __future__ import annotations

from meterbus.codec import FrameDecoder
from meterbus.model import DecodeError, DecodeMode, DecodeResult, Telegram


_FRAME_DECODER = FrameDecoder()


def decode(data: bytes | bytearray | memoryview | list[int] | tuple[int, ...], mode: DecodeMode = DecodeMode.STRICT) -> DecodeResult:
    """Decode bytes into the current v2 result model.

    For now this only decodes the frame envelope. `telegram` is intentionally
    `None` until application-level telegram decoding is implemented.
    """

    frame_result = _FRAME_DECODER.decode(data, mode=mode)
    return DecodeResult(
        ok=frame_result.ok,
        telegram=None,
        frame=frame_result.frame,
        diagnostics=frame_result.diagnostics,
        raw=frame_result.raw,
    )


def decode_one_frame(data: bytes | bytearray | memoryview | list[int] | tuple[int, ...], mode: DecodeMode = DecodeMode.STRICT):
    """Decode one frame or raise `DecodeError`.

    This is the strict convenience API for the frame-decoder stage.
    """

    result = decode(data, mode=mode)
    if result.frame is None or not result.ok:
        message = result.diagnostics[0].message if result.diagnostics else "unable to decode frame"
        raise DecodeError(message, diagnostics=result.diagnostics)
    return result.frame


def decode_one(data: bytes | bytearray | memoryview | list[int] | tuple[int, ...], mode: DecodeMode = DecodeMode.STRICT) -> Telegram:
    """Decode one application telegram or raise `DecodeError`.

    This placeholder is deliberately explicit: the public name exists, but
    application-level telegram decoding has not been implemented in this slice.
    """

    result = decode(data, mode=mode)
    if result.telegram is None:
        raise DecodeError(
            "application telegram decoding is not implemented yet",
            diagnostics=result.diagnostics,
        )
    return result.telegram
