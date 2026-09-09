"""Format-frame descriptor parser for pyMeterBus 2.0.

M-Bus Format frames contain record headers only: DIF/DIFE followed by VIF/VIFE,
without value bytes. These descriptors can later be used as templates for
compact-frame expansion.
"""

from __future__ import annotations

from dataclasses import dataclass

from meterbus.model import Diagnostic, FormatDataRecordDescriptor, Severity

from .dif import DataInformationParseError, _parse_dif_at
from .vif import ValueInformationParseError, _parse_vif_at

_FILLER_BYTE = 0x2F


@dataclass(frozen=True)
class FormatDescriptorDecodeResult:
    """Decoded format-frame descriptors plus unparsed tail metadata."""

    descriptors: tuple[FormatDataRecordDescriptor, ...]
    undecoded_data: bytes
    diagnostics: tuple[Diagnostic, ...] = ()


def decode_format_descriptors(format_data: bytes) -> FormatDescriptorDecodeResult:
    """Decode repeated DIF/DIFE + VIF/VIFE descriptors from format-frame data.

    The parser intentionally stops at filler bytes or malformed descriptor data
    and preserves the remaining bytes as `undecoded_data`. It does not invent
    data values and does not expand compact frames.
    """

    descriptors: list[FormatDataRecordDescriptor] = []
    diagnostics: list[Diagnostic] = []
    offset = 0

    while offset < len(format_data):
        if format_data[offset] == _FILLER_BYTE:
            return FormatDescriptorDecodeResult(
                descriptors=tuple(descriptors),
                undecoded_data=format_data[offset:],
                diagnostics=tuple(diagnostics),
            )

        start = offset
        try:
            dif_result = _parse_dif_at(format_data, offset)
            offset += dif_result.consumed
            vif_result = _parse_vif_at(format_data, offset)
            offset += vif_result.consumed
        except (DataInformationParseError, ValueInformationParseError) as exc:
            diagnostics.append(
                Diagnostic(
                    severity=Severity.ERROR,
                    code="format_descriptor_decode_error",
                    message=str(exc),
                    offset=start,
                )
            )
            return FormatDescriptorDecodeResult(
                descriptors=tuple(descriptors),
                undecoded_data=format_data[start:],
                diagnostics=tuple(diagnostics),
            )

        descriptors.append(
            FormatDataRecordDescriptor(
                raw=format_data[start:offset],
                dif=dif_result.data_information,
                vif=vif_result.value_information,
                index=len(descriptors) + 1,
                data_length=dif_result.data_length,
            )
        )

    return FormatDescriptorDecodeResult(
        descriptors=tuple(descriptors),
        undecoded_data=b"",
        diagnostics=tuple(diagnostics),
    )
