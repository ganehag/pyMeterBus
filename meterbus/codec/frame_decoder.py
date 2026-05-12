"""Frame decoder for pyMeterBus 2.0.

This module only decodes the M-Bus frame envelope. It deliberately does not
parse application payload records.
"""

from __future__ import annotations

from dataclasses import dataclass

from meterbus.model import (
    AckFrame,
    ControlField,
    ControlFrame,
    DecodeMode,
    Diagnostic,
    Frame,
    FrameKind,
    LongFrame,
    PrimaryAddress,
    Severity,
    ShortFrame,
)

from .crc import checksum


@dataclass(frozen=True)
class FrameDecodeResult:
    """Result returned by the non-throwing frame decoder."""

    ok: bool
    frame: Frame | None
    diagnostics: tuple[Diagnostic, ...]
    raw: bytes


def _diagnostic(
    severity: Severity,
    code: str,
    message: str,
    *,
    offset: int | None = None,
    **context: object,
) -> Diagnostic:
    return Diagnostic(
        severity=severity,
        code=code,
        message=message,
        offset=offset,
        context=context,
    )


def _normalize_input(data: bytes | bytearray | memoryview | list[int] | tuple[int, ...]) -> bytes:
    if isinstance(data, bytes):
        return data
    if isinstance(data, bytearray):
        return bytes(data)
    if isinstance(data, memoryview):
        return data.tobytes()
    if isinstance(data, (list, tuple)):
        return bytes(data)
    raise TypeError(f"unsupported frame input type: {type(data).__name__}")


class FrameDecoder:
    """Decode M-Bus frame envelopes using direct byte inspection."""

    def decode(
        self,
        data: bytes | bytearray | memoryview | list[int] | tuple[int, ...],
        mode: DecodeMode = DecodeMode.STRICT,
    ) -> FrameDecodeResult:
        try:
            raw = _normalize_input(data)
        except (TypeError, ValueError) as exc:
            diagnostic = _diagnostic(
                Severity.FATAL,
                "unsupported_input_type",
                str(exc),
            )
            return FrameDecodeResult(False, None, (diagnostic,), b"")

        if not raw:
            diagnostic = _diagnostic(
                Severity.FATAL,
                "empty_input",
                "Cannot decode an empty frame.",
            )
            return FrameDecodeResult(False, None, (diagnostic,), raw)

        start = raw[0]
        if start == 0xE5:
            return self._decode_ack(raw, mode)
        if start == 0x10:
            return self._decode_short(raw, mode)
        if start == 0x68:
            return self._decode_long_or_control(raw, mode)

        diagnostic = _diagnostic(
            Severity.FATAL,
            "invalid_start_byte",
            "Frame does not start with a known M-Bus start byte.",
            offset=0,
            start_byte=start,
        )
        return FrameDecodeResult(False, None, (diagnostic,), raw)

    def _decode_ack(self, raw: bytes, mode: DecodeMode) -> FrameDecodeResult:
        diagnostics: list[Diagnostic] = []
        if len(raw) != 1:
            diagnostics.append(
                _diagnostic(
                    Severity.ERROR if mode is DecodeMode.STRICT else Severity.WARNING,
                    "trailing_bytes",
                    "ACK frame contains trailing bytes.",
                    offset=1,
                    expected_length=1,
                    actual_length=len(raw),
                )
            )
            if mode is DecodeMode.STRICT:
                return FrameDecodeResult(False, None, tuple(diagnostics), raw)

        frame = AckFrame(raw=raw, diagnostics=tuple(diagnostics))
        return FrameDecodeResult(True, frame, tuple(diagnostics), raw)

    def _decode_short(self, raw: bytes, mode: DecodeMode) -> FrameDecodeResult:
        diagnostics: list[Diagnostic] = []
        expected_length = 5
        if len(raw) != expected_length:
            diagnostics.append(
                _diagnostic(
                    Severity.FATAL if mode is DecodeMode.STRICT else Severity.ERROR,
                    "length_mismatch",
                    "Short frame length must be exactly 5 bytes.",
                    expected_length=expected_length,
                    actual_length=len(raw),
                )
            )
            if mode is DecodeMode.STRICT or len(raw) < expected_length:
                return FrameDecodeResult(False, None, tuple(diagnostics), raw)

        frame_bytes = raw[:expected_length]
        if frame_bytes[4] != 0x16:
            diagnostics.append(
                _diagnostic(
                    Severity.FATAL if mode is DecodeMode.STRICT else Severity.ERROR,
                    "invalid_stop_byte",
                    "Short frame stop byte must be 0x16.",
                    offset=4,
                    expected=0x16,
                    actual=frame_bytes[4],
                )
            )
            if mode is DecodeMode.STRICT:
                return FrameDecodeResult(False, None, tuple(diagnostics), raw)

        computed = checksum(frame_bytes[1:3])
        given = frame_bytes[3]
        checksum_valid = computed == given
        if not checksum_valid:
            diagnostics.append(
                _diagnostic(
                    Severity.FATAL if mode is DecodeMode.STRICT else Severity.ERROR,
                    "checksum_mismatch",
                    "Short frame checksum does not match.",
                    offset=3,
                    expected=computed,
                    actual=given,
                )
            )
            if mode is DecodeMode.STRICT:
                return FrameDecodeResult(False, None, tuple(diagnostics), raw)

        if len(raw) > expected_length:
            diagnostics.append(
                _diagnostic(
                    Severity.WARNING,
                    "trailing_bytes",
                    "Short frame contains trailing bytes.",
                    offset=expected_length,
                    expected_length=expected_length,
                    actual_length=len(raw),
                )
            )

        frame = ShortFrame(
            raw=raw,
            checksum=given,
            checksum_valid=checksum_valid,
            diagnostics=tuple(diagnostics),
            control=ControlField(raw=frame_bytes[1]),
            address=PrimaryAddress(frame_bytes[2]),
        )
        return FrameDecodeResult(not any(d.severity is Severity.FATAL for d in diagnostics), frame, tuple(diagnostics), raw)

    def _decode_long_or_control(self, raw: bytes, mode: DecodeMode) -> FrameDecodeResult:
        diagnostics: list[Diagnostic] = []
        if len(raw) < 6:
            diagnostic = _diagnostic(
                Severity.FATAL if mode is DecodeMode.STRICT else Severity.ERROR,
                "truncated_frame",
                "Long/control frame is too short to contain length fields.",
                expected_minimum_length=6,
                actual_length=len(raw),
            )
            return FrameDecodeResult(False, None, (diagnostic,), raw)

        length_1 = raw[1]
        length_2 = raw[2]
        if length_1 != length_2:
            diagnostics.append(
                _diagnostic(
                    Severity.FATAL if mode is DecodeMode.STRICT else Severity.ERROR,
                    "length_mismatch",
                    "Repeated length fields do not match.",
                    offset=2,
                    length_1=length_1,
                    length_2=length_2,
                )
            )
            if mode is DecodeMode.STRICT:
                return FrameDecodeResult(False, None, tuple(diagnostics), raw)

        if raw[3] != 0x68:
            diagnostics.append(
                _diagnostic(
                    Severity.FATAL if mode is DecodeMode.STRICT else Severity.ERROR,
                    "invalid_repeated_start_byte",
                    "Long/control frame repeated start byte must be 0x68.",
                    offset=3,
                    expected=0x68,
                    actual=raw[3],
                )
            )
            if mode is DecodeMode.STRICT:
                return FrameDecodeResult(False, None, tuple(diagnostics), raw)

        length = length_1
        if length < 3:
            diagnostics.append(
                _diagnostic(
                    Severity.FATAL if mode is DecodeMode.STRICT else Severity.ERROR,
                    "invalid_length",
                    "Long/control frame length must include C, A, and CI fields.",
                    offset=1,
                    length=length,
                )
            )
            return FrameDecodeResult(False, None, tuple(diagnostics), raw)

        expected_total_length = length + 6
        if len(raw) != expected_total_length:
            diagnostics.append(
                _diagnostic(
                    Severity.FATAL if mode is DecodeMode.STRICT else Severity.ERROR,
                    "length_mismatch",
                    "Frame length does not match length fields.",
                    expected_length=expected_total_length,
                    actual_length=len(raw),
                )
            )
            if mode is DecodeMode.STRICT or len(raw) < expected_total_length:
                return FrameDecodeResult(False, None, tuple(diagnostics), raw)

        frame_bytes = raw[:expected_total_length]
        stop_index = expected_total_length - 1
        if frame_bytes[stop_index] != 0x16:
            diagnostics.append(
                _diagnostic(
                    Severity.FATAL if mode is DecodeMode.STRICT else Severity.ERROR,
                    "invalid_stop_byte",
                    "Long/control frame stop byte must be 0x16.",
                    offset=stop_index,
                    expected=0x16,
                    actual=frame_bytes[stop_index],
                )
            )
            if mode is DecodeMode.STRICT:
                return FrameDecodeResult(False, None, tuple(diagnostics), raw)

        checksum_index = expected_total_length - 2
        checksum_data = frame_bytes[4:checksum_index]
        computed = checksum(checksum_data)
        given = frame_bytes[checksum_index]
        checksum_valid = computed == given
        if not checksum_valid:
            diagnostics.append(
                _diagnostic(
                    Severity.FATAL if mode is DecodeMode.STRICT else Severity.ERROR,
                    "checksum_mismatch",
                    "Long/control frame checksum does not match.",
                    offset=checksum_index,
                    expected=computed,
                    actual=given,
                )
            )
            if mode is DecodeMode.STRICT:
                return FrameDecodeResult(False, None, tuple(diagnostics), raw)

        if len(raw) > expected_total_length:
            diagnostics.append(
                _diagnostic(
                    Severity.WARNING,
                    "trailing_bytes",
                    "Frame contains trailing bytes.",
                    offset=expected_total_length,
                    expected_length=expected_total_length,
                    actual_length=len(raw),
                )
            )

        control = ControlField(raw=frame_bytes[4])
        address = PrimaryAddress(frame_bytes[5])
        ci = frame_bytes[6]
        if length == 3:
            frame = ControlFrame(
                raw=raw,
                checksum=given,
                checksum_valid=checksum_valid,
                diagnostics=tuple(diagnostics),
                length=length,
                control=control,
                address=address,
                ci=ci,
            )
        else:
            frame = LongFrame(
                raw=raw,
                checksum=given,
                checksum_valid=checksum_valid,
                diagnostics=tuple(diagnostics),
                length=length,
                control=control,
                address=address,
                ci=ci,
                payload=frame_bytes[7:checksum_index],
            )

        return FrameDecodeResult(not any(d.severity is Severity.FATAL for d in diagnostics), frame, tuple(diagnostics), raw)


def decode_frame(
    data: bytes | bytearray | memoryview | list[int] | tuple[int, ...],
    mode: DecodeMode = DecodeMode.STRICT,
) -> FrameDecodeResult:
    """Decode one M-Bus frame envelope."""

    return FrameDecoder().decode(data, mode=mode)
