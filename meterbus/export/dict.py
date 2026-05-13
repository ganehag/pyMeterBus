"""Plain-dict export for pyMeterBus 2.0 models.

The exporter is intentionally deterministic and JSON-friendly, but it does not
serialize to JSON itself. Callers can choose their own JSON/YAML/TOML layer.
"""

from __future__ import annotations

from decimal import Decimal
from enum import Enum
from typing import Any

from meterbus.model import (
    AckFrame,
    ControlField,
    ControlFrame,
    DataInformation,
    DataRecord,
    DecodedValue,
    DecodeResult,
    Diagnostic,
    FixedDataCounter,
    FixedDataHeader,
    FixedDataMediumUnit,
    FixedDataTelegram,
    FixedDataUnit,
    Frame,
    LongFrame,
    PrimaryAddress,
    SecondaryAddress,
    ShortFrame,
    Telegram,
    Unit,
    UnknownRecord,
    ValueInformation,
    VariableDataHeader,
    VariableDataTelegram,
)

from .views import ExportView


def to_dict(value: Any, *, view: ExportView | str = ExportView.FULL) -> Any:
    """Convert a pyMeterBus v2 model object into plain Python data."""

    export_view = ExportView(view)
    if export_view is not ExportView.FULL:
        if not isinstance(value, DecodeResult):
            raise TypeError("non-full export views require a DecodeResult")
        if export_view is ExportView.SUMMARY:
            return _decode_result_summary_to_dict(value)
        if export_view is ExportView.RECORDS:
            return _decode_result_records_to_dict(value)

    if value is None:
        return None
    if isinstance(value, bool | int | float | str):
        return value
    if isinstance(value, Decimal):
        return str(value)
    if isinstance(value, bytes):
        return _bytes_to_hex(value)
    if isinstance(value, Enum):
        return value.value
    if isinstance(value, tuple | list):
        return [to_dict(item) for item in value]
    if isinstance(value, dict):
        return {str(key): to_dict(item) for key, item in value.items()}

    if isinstance(value, Diagnostic):
        return value.to_dict()
    if isinstance(value, DecodeResult):
        return _decode_result_to_dict(value)
    if isinstance(value, ControlField):
        return _control_field_to_dict(value)
    if isinstance(value, PrimaryAddress):
        return {"value": value.value}
    if isinstance(value, SecondaryAddress):
        return _secondary_address_to_dict(value)
    if isinstance(value, Frame):
        return _frame_to_dict(value)
    if isinstance(value, Unit):
        return _unit_to_dict(value)
    if isinstance(value, DecodedValue):
        return _decoded_value_to_dict(value)
    if isinstance(value, DataInformation):
        return _data_information_to_dict(value)
    if isinstance(value, ValueInformation):
        return _value_information_to_dict(value)
    if isinstance(value, DataRecord):
        return _data_record_to_dict(value)
    if isinstance(value, UnknownRecord):
        return _unknown_record_to_dict(value)
    if isinstance(value, VariableDataHeader):
        return _variable_data_header_to_dict(value)
    if isinstance(value, FixedDataUnit):
        return _fixed_data_unit_to_dict(value)
    if isinstance(value, FixedDataMediumUnit):
        return _fixed_data_medium_unit_to_dict(value)
    if isinstance(value, FixedDataHeader):
        return _fixed_data_header_to_dict(value)
    if isinstance(value, FixedDataCounter):
        return _fixed_data_counter_to_dict(value)
    if isinstance(value, Telegram):
        return _telegram_to_dict(value)

    raise TypeError(f"unsupported value for dict export: {type(value).__name__}")


def _bytes_to_hex(value: bytes) -> str:
    return value.hex(" ").upper()


def _drop_none(mapping: dict[str, Any]) -> dict[str, Any]:
    return {key: item for key, item in mapping.items() if item is not None}


def _decode_result_to_dict(result: DecodeResult) -> dict[str, Any]:
    return {
        "ok": result.ok,
        "telegram": to_dict(result.telegram),
        "frame": to_dict(result.frame),
        "diagnostics": to_dict(result.diagnostics),
        "raw": to_dict(result.raw),
    }


def _decode_result_summary_to_dict(result: DecodeResult) -> dict[str, Any]:
    telegram = result.telegram
    frame = result.frame

    payload: dict[str, Any] = {
        "ok": result.ok,
        "frame": _frame_summary_to_dict(frame) if frame is not None else None,
        "meter": _meter_summary_to_dict(telegram) if telegram is not None else None,
        "records": len(telegram.records) if isinstance(telegram, VariableDataTelegram) else None,
        "counters": len(telegram.counters) if isinstance(telegram, FixedDataTelegram) else None,
        "diagnostics": to_dict(result.diagnostics),
    }
    return _drop_none(payload)


def _decode_result_records_to_dict(result: DecodeResult) -> dict[str, Any]:
    telegram = result.telegram
    records = telegram.records if isinstance(telegram, VariableDataTelegram) else ()
    counters = telegram.counters if isinstance(telegram, FixedDataTelegram) else ()

    payload: dict[str, Any] = {
        "ok": result.ok,
        "meter": _meter_summary_to_dict(telegram) if telegram is not None else None,
        "records": [_record_summary_to_dict(record) for record in records],
        "counters": [_fixed_data_counter_to_dict(counter) for counter in counters],
        "diagnostics": to_dict(result.diagnostics),
    }
    return _drop_none(payload)


def _frame_summary_to_dict(frame: Frame) -> dict[str, Any]:
    return _drop_none(
        {
            "kind": to_dict(frame.kind),
            "checksum_valid": frame.checksum_valid,
        }
    )


def _meter_summary_to_dict(telegram: Telegram) -> dict[str, Any] | None:
    if isinstance(telegram, VariableDataTelegram):
        header = telegram.header
        return _drop_none(
            {
                "manufacturer": header.manufacturer,
                "identification_number": header.identification_number,
                "medium": header.medium,
                "version": header.version,
            }
        )
    if isinstance(telegram, FixedDataTelegram):
        header = telegram.header
        return _drop_none(
            {
                "identification_number": header.identification_number,
                "access_number": header.access_number,
                "status": header.status,
                "medium_unit_raw": to_dict(header.medium_unit_raw),
                "medium": header.medium_unit.medium if header.medium_unit is not None else None,
            }
        )
    return None


def _record_summary_to_dict(record: DataRecord | UnknownRecord) -> dict[str, Any]:
    if isinstance(record, UnknownRecord):
        return _drop_none(
            {
                "kind": "unknown_record",
                "reason": record.reason,
                "diagnostics": to_dict(record.diagnostics),
            }
        )

    unit = record.value.unit or record.vif.unit
    return _drop_none(
        {
            "kind": record.vif.kind,
            "value": to_dict(record.value.value),
            "unit": unit.symbol if unit is not None else None,
            "function": to_dict(record.function),
            "storage_number": record.storage_number,
            "tariff": record.tariff,
            "subunit": record.subunit,
            "diagnostics": to_dict(record.diagnostics) if record.diagnostics else None,
        }
    )


def _control_field_to_dict(control: ControlField) -> dict[str, Any]:
    return _drop_none(
        {
            "raw": control.raw,
            "direction": to_dict(control.direction),
            "function": to_dict(control.function),
            "fcb": control.fcb,
            "fcv": control.fcv,
        }
    )


def _secondary_address_to_dict(address: SecondaryAddress) -> dict[str, Any]:
    return {
        "identification_number": address.identification_number,
        "manufacturer": address.manufacturer,
        "manufacturer_raw": to_dict(address.manufacturer_raw),
        "version": address.version,
        "medium": address.medium,
    }


def _frame_to_dict(frame: Frame) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "kind": to_dict(frame.kind),
        "raw": to_dict(frame.raw),
        "checksum": frame.checksum,
        "checksum_valid": frame.checksum_valid,
        "diagnostics": to_dict(frame.diagnostics),
    }

    if isinstance(frame, AckFrame):
        return _drop_none(payload)

    if isinstance(frame, ShortFrame | ControlFrame | LongFrame):
        payload["control"] = to_dict(frame.control)
        payload["address"] = to_dict(frame.address)

    if isinstance(frame, ControlFrame | LongFrame):
        payload["length"] = frame.length
        payload["ci"] = frame.ci

    if isinstance(frame, LongFrame):
        payload["payload"] = to_dict(frame.payload)

    return _drop_none(payload)


def _unit_to_dict(unit: Unit) -> dict[str, Any]:
    return _drop_none({"name": unit.name, "symbol": unit.symbol})


def _decoded_value_to_dict(value: DecodedValue) -> dict[str, Any]:
    return _drop_none(
        {
            "raw": to_dict(value.raw),
            "value": to_dict(value.value),
            "type": to_dict(value.type),
            "unit": to_dict(value.unit),
            "scaled": value.scaled,
        }
    )


def _data_information_to_dict(dif: DataInformation) -> dict[str, Any]:
    return _drop_none(
        {
            "raw": to_dict(dif.raw),
            "data_encoding": to_dict(dif.data_encoding),
            "function": to_dict(dif.function),
            "storage_number": dif.storage_number,
            "tariff": dif.tariff,
            "subunit": dif.subunit,
            "extension_bytes": to_dict(dif.extension_bytes),
        }
    )


def _value_information_to_dict(vif: ValueInformation) -> dict[str, Any]:
    return _drop_none(
        {
            "raw": to_dict(vif.raw),
            "unit": to_dict(vif.unit),
            "kind": vif.kind,
            "multiplier": to_dict(vif.multiplier),
            "extension_bytes": to_dict(vif.extension_bytes),
            "custom_vif": to_dict(vif.custom_vif),
            "enhancement": vif.enhancement,
        }
    )


def _data_record_to_dict(record: DataRecord) -> dict[str, Any]:
    return _drop_none(
        {
            "raw": to_dict(record.raw),
            "dif": to_dict(record.dif),
            "vif": to_dict(record.vif),
            "value": to_dict(record.value),
            "function": to_dict(record.function),
            "storage_number": record.storage_number,
            "tariff": record.tariff,
            "subunit": record.subunit,
            "more_records_follow": record.more_records_follow,
            "diagnostics": to_dict(record.diagnostics),
        }
    )


def _unknown_record_to_dict(record: UnknownRecord) -> dict[str, Any]:
    return {
        "raw": to_dict(record.raw),
        "reason": record.reason,
        "diagnostics": to_dict(record.diagnostics),
    }


def _variable_data_header_to_dict(header: VariableDataHeader) -> dict[str, Any]:
    return _drop_none(
        {
            "identification_number": header.identification_number,
            "manufacturer": header.manufacturer,
            "manufacturer_raw": to_dict(header.manufacturer_raw),
            "version": header.version,
            "medium": header.medium,
            "access_number": header.access_number,
            "status": header.status,
            "signature": to_dict(header.signature),
            "raw": to_dict(header.raw),
        }
    )


def _fixed_data_unit_to_dict(unit: FixedDataUnit) -> dict[str, Any]:
    return _drop_none(
        {
            "code": unit.code,
            "label": unit.label,
            "symbol": unit.symbol,
            "multiplier": to_dict(unit.multiplier),
        }
    )


def _fixed_data_medium_unit_to_dict(medium_unit: FixedDataMediumUnit) -> dict[str, Any]:
    return {
        "raw": to_dict(medium_unit.raw),
        "medium_code": medium_unit.medium_code,
        "medium": medium_unit.medium,
        "counter_1_unit": to_dict(medium_unit.counter_1_unit),
        "counter_2_unit": to_dict(medium_unit.counter_2_unit),
    }


def _fixed_data_header_to_dict(header: FixedDataHeader) -> dict[str, Any]:
    return {
        "identification_number": header.identification_number,
        "access_number": header.access_number,
        "status": header.status,
        "medium_unit_raw": to_dict(header.medium_unit_raw),
        "medium_unit": to_dict(header.medium_unit),
        "raw": to_dict(header.raw),
    }


def _fixed_data_counter_to_dict(counter: FixedDataCounter) -> dict[str, Any]:
    return _drop_none(
        {
            "index": counter.index,
            "raw": to_dict(counter.raw),
            "value": to_dict(counter.value),
            "unit": to_dict(counter.unit),
            "scaled_value": to_dict(counter.scaled_value),
        }
    )


def _telegram_to_dict(telegram: Telegram) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "application_kind": to_dict(telegram.application_kind),
        "frame": to_dict(telegram.frame),
        "diagnostics": to_dict(telegram.diagnostics),
    }

    if isinstance(telegram, VariableDataTelegram):
        payload.update(
            {
                "header": to_dict(telegram.header),
                "records": to_dict(telegram.records),
                "more_records_follow": telegram.more_records_follow,
                "raw_application_data": to_dict(telegram.raw_application_data),
                "undecoded_data": to_dict(telegram.undecoded_data),
            }
        )
    elif isinstance(telegram, FixedDataTelegram):
        payload.update(
            {
                "header": to_dict(telegram.header),
                "counters": to_dict(telegram.counters),
                "raw_application_data": to_dict(telegram.raw_application_data),
                "undecoded_data": to_dict(telegram.undecoded_data),
            }
        )

    return _drop_none(payload)
