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

from .record import _apply_vif_multiplier, _interpret_vif_value
from .value import ValueDecodeError, decode_value


@dataclass(frozen=True)
class CompactExpansionResult:
    """Expanded compact-frame records plus any unconsumed value bytes."""

    records: tuple[DataRecord, ...]
    undecoded_data: bytes
    diagnostics: tuple[Diagnostic, ...] = ()


def expand_compact_telegram(
    compact: CompactDataTelegram,
    template: FormatDataTelegram | Sequence[FormatDataRecordDescriptor],
    *,
    lsb_order: bool = True,
) -> CompactExpansionResult:
    """Expand compact-frame value bytes using an explicit template.

    Passing a `FormatDataTelegram` validates that the compact frame's Format
    Signature matches the format frame before expansion. Passing raw descriptors
    remains supported for lower-level callers that have already matched the
    template themselves.

    This function does not validate the compact frame's Full-Frame-CRC.
    """

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
    else:
        descriptors = template

    return expand_compact_data(compact.compact_data, descriptors, lsb_order=lsb_order)


def expand_compact_data(
    compact_data: bytes,
    descriptors: Sequence[FormatDataRecordDescriptor],
    *,
    lsb_order: bool = True,
) -> CompactExpansionResult:
    """Expand compact value bytes using explicit format descriptors."""

    records: list[DataRecord] = []
    diagnostics: list[Diagnostic] = []
    offset = 0

    for descriptor in descriptors:
        try:
            value_result = decode_value(
                compact_data[offset:],
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
            )

        value = _interpret_vif_value(value_result.value, descriptor.vif.kind)
        value = _apply_vif_multiplier(value, descriptor.vif.multiplier)
        consumed = value_result.consumed
        record = DataRecord(
            raw=descriptor.raw + compact_data[offset : offset + consumed],
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
        offset += consumed

    return CompactExpansionResult(
        records=tuple(records),
        undecoded_data=compact_data[offset:],
        diagnostics=tuple(diagnostics),
    )
