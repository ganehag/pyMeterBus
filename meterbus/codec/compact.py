"""Explicit compact-frame expansion for pyMeterBus 2.0.

Compact M-Bus frames carry only value bytes. They must be expanded with an
explicit template derived from a matching format frame or full frame. This
module does not maintain a hidden template cache and does not guess record
boundaries.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

from meterbus.model import (
    CompactDataTelegram,
    DataRecord,
    Diagnostic,
    FormatDataRecordDescriptor,
    FormatDataTelegram,
    Severity,
)

from .crc import crc16_en13757_bytes
from .record import _apply_vif_multiplier, _interpret_vif_value
from .value import ValueDecodeError, _decode_value_at


@dataclass(frozen=True)
class CompactExpansionResult:
    """Expanded compact-frame records plus any unconsumed value bytes."""

    records: tuple[DataRecord, ...]
    undecoded_data: bytes
    diagnostics: tuple[Diagnostic, ...] = ()
    recovered_application_data: bytes = b""


def expand_compact_telegram(
    compact: CompactDataTelegram,
    template: FormatDataTelegram | Sequence[FormatDataRecordDescriptor],
    *,
    lsb_order: bool = True,
    crc_byteorder: str = "big",
) -> CompactExpansionResult:
    """Expand compact-frame value bytes using an explicit template.

    Passing a `FormatDataTelegram` validates that the compact frame's Format
    Signature matches the format frame before expansion and, when possible,
    validates the compact frame's Full-Frame-CRC against the recovered full
    application data. Passing raw descriptors remains supported for lower-level
    callers that have already matched and validated the template themselves.
    """

    validate_crc = False
    if isinstance(template, FormatDataTelegram):
        if compact.format_signature != template.format_signature:
            diagnostic = Diagnostic(
                severity=Severity.ERROR,
                code="compact_format_signature_mismatch",
                message="Compact M-Bus frame Format Signature does not match the supplied format template.",
                context={
                    "compact_format_signature": compact.format_signature,
                    "template_format_signature": template.format_signature,
                },
            )
            return CompactExpansionResult(
                records=(),
                undecoded_data=compact.compact_data,
                diagnostics=(diagnostic,),
            )
        descriptors = template.descriptors
        validate_crc = True
    else:
        descriptors = template

    result = expand_compact_data(compact.compact_data, descriptors, lsb_order=lsb_order)
    if not validate_crc or result.diagnostics or result.undecoded_data:
        return result

    if compact.full_frame_crc is None:
        diagnostic = Diagnostic(
            severity=Severity.ERROR,
            code="compact_full_frame_crc_missing",
            message="Compact M-Bus frame does not contain a complete Full-Frame-CRC field.",
        )
        return _with_diagnostic(result, diagnostic)

    calculated_crc = crc16_en13757_bytes(result.recovered_application_data, byteorder=crc_byteorder)
    if calculated_crc != compact.full_frame_crc:
        diagnostic = Diagnostic(
            severity=Severity.ERROR,
            code="compact_full_frame_crc_mismatch",
            message="Compact M-Bus frame Full-Frame-CRC does not match the recovered full application data.",
            context={
                "transmitted_full_frame_crc": compact.full_frame_crc,
                "calculated_full_frame_crc": calculated_crc,
                "crc_byteorder": crc_byteorder,
            },
        )
        return _with_diagnostic(result, diagnostic)

    return result


def expand_compact_data(
    compact_data: bytes,
    descriptors: Sequence[FormatDataRecordDescriptor],
    *,
    lsb_order: bool = True,
) -> CompactExpansionResult:
    """Expand compact value bytes using explicit format descriptors."""

    records: list[DataRecord] = []
    recovered_parts: list[bytes] = []
    diagnostics: list[Diagnostic] = []
    offset = 0

    for descriptor in descriptors:
        try:
            value_result = _decode_value_at(
                compact_data,
                offset,
                descriptor.dif,
                descriptor.data_length,
                unit=descriptor.vif.unit,
                lsb_order=lsb_order,
            )
        except ValueDecodeError as exc:
            diagnostics.append(
                Diagnostic(
                    severity=Severity.ERROR,
                    code="compact_value_decode_error",
                    message=str(exc),
                    offset=offset,
                    context={"descriptor_index": descriptor.index},
                )
            )
            return CompactExpansionResult(
                records=tuple(records),
                undecoded_data=compact_data[offset:],
                diagnostics=tuple(diagnostics),
                recovered_application_data=b"".join(recovered_parts),
            )

        value = _interpret_vif_value(value_result.value, descriptor.vif.kind)
        value = _apply_vif_multiplier(value, descriptor.vif.multiplier)
        consumed = value_result.consumed
        raw_value = compact_data[offset : offset + consumed]
        raw_record = descriptor.raw + raw_value
        record = DataRecord(
            raw=raw_record,
            dif=descriptor.dif,
            vif=descriptor.vif,
            value=value,
            function=descriptor.dif.function,
            storage_number=descriptor.dif.storage_number,
            tariff=descriptor.dif.tariff,
            subunit=descriptor.dif.subunit,
            more_records_follow=False,
            diagnostics=(),
        )
        records.append(record)
        recovered_parts.append(raw_record)
        offset += consumed

    return CompactExpansionResult(
        records=tuple(records),
        undecoded_data=compact_data[offset:],
        diagnostics=tuple(diagnostics),
        recovered_application_data=b"".join(recovered_parts),
    )


def _with_diagnostic(result: CompactExpansionResult, diagnostic: Diagnostic) -> CompactExpansionResult:
    return CompactExpansionResult(
        records=result.records,
        undecoded_data=result.undecoded_data,
        diagnostics=result.diagnostics + (diagnostic,),
        recovered_application_data=result.recovered_application_data,
    )
