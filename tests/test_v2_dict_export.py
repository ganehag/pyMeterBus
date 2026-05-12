from __future__ import annotations

from decimal import Decimal

import pytest

from meterbus.api import decode
from meterbus.export import to_dict
from meterbus.model import (
    DataEncoding,
    DataInformation,
    DataRecord,
    DecodedValue,
    Diagnostic,
    FunctionType,
    Severity,
    Unit,
    ValueInformation,
    ValueType,
)
from tests.helpers.fixtures import load_hex_fixture


def test_export_ack_decode_result_to_plain_dict():
    result = decode(load_hex_fixture("frames/ack.hex").data)

    exported = to_dict(result)

    assert exported == {
        "ok": True,
        "telegram": None,
        "frame": {
            "kind": "ack",
            "raw": "E5",
            "diagnostics": [],
        },
        "diagnostics": [],
        "raw": "E5",
    }


def test_export_short_frame_to_plain_dict():
    result = decode(load_hex_fixture("frames/short.hex").data)

    exported = to_dict(result.frame)

    assert exported == {
        "kind": "short",
        "raw": "10 08 0B 13 16",
        "checksum": 0x13,
        "checksum_valid": True,
        "diagnostics": [],
        "control": {"raw": 0x08},
        "address": {"value": 0x0B},
    }


def test_export_long_frame_includes_envelope_and_payload():
    raw = load_hex_fixture("frames/long_basic.hex").data
    result = decode(raw)

    exported = to_dict(result.frame)

    assert exported["kind"] == "long"
    assert exported["length"] == 0x3D
    assert exported["control"] == {"raw": 0x08}
    assert exported["address"] == {"value": 0x0B}
    assert exported["ci"] == 0x72
    assert exported["payload"] == raw[7:-2].hex(" ").upper()


def test_export_diagnostic_and_context_to_plain_dict():
    diagnostic = Diagnostic(
        Severity.ERROR,
        "checksum_mismatch",
        "Checksum mismatch",
        offset=3,
        context={"expected": 0x13, "actual": 0x00},
    )

    assert to_dict(diagnostic) == {
        "severity": "error",
        "code": "checksum_mismatch",
        "message": "Checksum mismatch",
        "offset": 3,
        "context": {"expected": 0x13, "actual": 0x00},
    }


def test_export_lenient_decode_result_preserves_diagnostics():
    raw = bytearray(load_hex_fixture("frames/short.hex").data)
    raw[3] = 0x00

    result = decode(bytes(raw), mode="lenient")
    exported = to_dict(result)

    assert exported["ok"] is True
    assert exported["frame"]["checksum_valid"] is False
    assert exported["diagnostics"] == [
        {
            "severity": "error",
            "code": "checksum_mismatch",
            "message": "Short frame checksum does not match.",
            "offset": 3,
            "context": {"expected": 0x13, "actual": 0x00},
        }
    ]


def test_export_record_value_decimal_without_float_artifacts():
    unit = Unit(name="relative_humidity", symbol="%RH")
    dif = DataInformation(
        raw=b"\x02",
        data_encoding=DataEncoding.INTEGER,
        function=FunctionType.INSTANTANEOUS_VALUE,
        storage_number=0,
    )
    vif = ValueInformation(
        raw=b"\xFC\x03",
        unit=unit,
        kind="variable_vif",
        multiplier=Decimal("0.01"),
    )
    value = DecodedValue(
        raw=b"\xC8\x11",
        value=Decimal("45.52"),
        type=ValueType.DECIMAL,
        unit=unit,
        scaled=True,
    )
    record = DataRecord(
        raw=b"\x02\xFC\x03\xC8\x11",
        dif=dif,
        vif=vif,
        value=value,
        function=FunctionType.INSTANTANEOUS_VALUE,
        storage_number=0,
    )

    exported = to_dict(record)

    assert exported["value"]["value"] == "45.52"
    assert exported["vif"]["multiplier"] == "0.01"
    assert exported["value"]["unit"] == {"name": "relative_humidity", "symbol": "%RH"}


def test_export_rejects_unsupported_objects_loudly():
    with pytest.raises(TypeError, match="unsupported value for dict export"):
        to_dict(object())
