"""Application telegram decoder for pyMeterBus 2.0.

This decoder recognizes variable-data telegrams carried by long frames with
CI 0x72. It decodes the fixed header and then decodes records until filler
bytes or undecodable trailing data are reached.
"""

from __future__ import annotations

from dataclasses import dataclass

from meterbus.model import (
    DecodeMode,
    DecodeResult,
    Diagnostic,
    LongFrame,
    Severity,
    VariableDataHeader,
    VariableDataTelegram,
)

from .frame_decoder import FrameDecoder
from .record import DataRecordDecodeError, decode_record

_VARIABLE_DATA_CI = 0x72
_VARIABLE_DATA_HEADER_LENGTH = 12
_FILLER_BYTE = 0x2F


@dataclass(frozen=True)
class TelegramDecoder:
    """Decode application-level telegrams from frame envelopes."""

    frame_decoder: FrameDecoder = FrameDecoder()

    def decode(
        self,
        data: bytes | bytearray | memoryview | list[int] | tuple[int, ...],
        mode: DecodeMode = DecodeMode.STRICT,
    ) -> DecodeResult:
        frame_result = self.frame_decoder.decode(data, mode=mode)
        if frame_result.frame is None or not frame_result.ok:
            return DecodeResult(
                ok=frame_result.ok,
                telegram=None,
                frame=frame_result.frame,
                diagnostics=frame_result.diagnostics,
                raw=frame_result.raw,
            )

        frame = frame_result.frame
        if not isinstance(frame, LongFrame) or frame.ci != _VARIABLE_DATA_CI:
            return DecodeResult(
                ok=frame_result.ok,
                telegram=None,
                frame=frame,
                diagnostics=frame_result.diagnostics,
                raw=frame_result.raw,
            )

        diagnostics = list(frame_result.diagnostics)
        if len(frame.payload) < _VARIABLE_DATA_HEADER_LENGTH:
            diagnostics.append(
                Diagnostic(
                    severity=Severity.FATAL if mode is DecodeMode.STRICT else Severity.ERROR,
                    code="truncated_variable_data_header",
                    message="Variable data telegram is too short to contain a complete header.",
                    context={
                        "expected_minimum_length": _VARIABLE_DATA_HEADER_LENGTH,
                        "actual_length": len(frame.payload),
                    },
                )
            )
            return DecodeResult(
                ok=False,
                telegram=None,
                frame=frame,
                diagnostics=tuple(diagnostics),
                raw=frame_result.raw,
            )

        header = decode_variable_data_header(frame.payload[:_VARIABLE_DATA_HEADER_LENGTH])
        application_data = frame.payload[_VARIABLE_DATA_HEADER_LENGTH:]
        records, undecoded_data, record_diagnostics = _decode_records(application_data, mode)
        diagnostics.extend(record_diagnostics)

        telegram = VariableDataTelegram(
            frame=frame,
            diagnostics=tuple(diagnostics),
            header=header,
            records=tuple(records),
            more_records_follow=False,
            raw_application_data=application_data,
            undecoded_data=undecoded_data,
        )
        return DecodeResult(
            ok=not any(diagnostic.severity is Severity.FATAL for diagnostic in diagnostics),
            telegram=telegram,
            frame=frame,
            diagnostics=tuple(diagnostics),
            raw=frame_result.raw,
        )


def decode_variable_data_header(raw: bytes) -> VariableDataHeader:
    """Decode the fixed 12-byte variable data header."""

    if len(raw) != _VARIABLE_DATA_HEADER_LENGTH:
        raise ValueError("variable data header must be exactly 12 bytes")

    return VariableDataHeader(
        identification_number=_decode_bcd_identification(raw[0:4]),
        manufacturer=_decode_manufacturer(raw[4:6]),
        manufacturer_raw=raw[4:6],
        version=raw[6],
        medium=raw[7],
        access_number=raw[8],
        status=raw[9],
        signature=raw[10:12],
        raw=raw,
    )


def _decode_records(application_data: bytes, mode: DecodeMode):
    records = []
    diagnostics: list[Diagnostic] = []
    offset = 0

    while offset < len(application_data):
        if application_data[offset] == _FILLER_BYTE:
            return records, application_data[offset:], diagnostics

        try:
            result = decode_record(application_data[offset:])
        except DataRecordDecodeError as exc:
            diagnostics.append(
                Diagnostic(
                    severity=Severity.FATAL if mode is DecodeMode.STRICT else Severity.ERROR,
                    code="record_decode_error",
                    message=str(exc),
                    offset=_VARIABLE_DATA_HEADER_LENGTH + offset,
                )
            )
            return records, application_data[offset:], diagnostics

        if result.consumed <= 0:
            diagnostics.append(
                Diagnostic(
                    severity=Severity.FATAL if mode is DecodeMode.STRICT else Severity.ERROR,
                    code="record_decoder_did_not_advance",
                    message="Record decoder did not consume any bytes.",
                    offset=_VARIABLE_DATA_HEADER_LENGTH + offset,
                )
            )
            return records, application_data[offset:], diagnostics

        records.append(result.record)
        offset += result.consumed

    return records, b"", diagnostics


def _decode_bcd_identification(raw: bytes) -> str:
    """Decode the little-endian BCD identification number."""

    digits: list[str] = []
    for byte in reversed(raw):
        digits.append(f"{byte >> 4:X}")
        digits.append(f"{byte & 0x0F:X}")
    return "".join(digits)


def _decode_manufacturer(raw: bytes) -> str:
    """Decode a two-byte EN 13757 manufacturer code."""

    value = raw[0] | (raw[1] << 8)
    return "".join(
        chr(((value >> shift) & 0x1F) + 64)
        for shift in (10, 5, 0)
    )


def decode_telegram(
    data: bytes | bytearray | memoryview | list[int] | tuple[int, ...],
    mode: DecodeMode = DecodeMode.STRICT,
) -> DecodeResult:
    """Decode one application telegram."""

    return TelegramDecoder().decode(data, mode=mode)
