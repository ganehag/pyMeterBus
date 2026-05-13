from __future__ import annotations

import json
from pathlib import Path

import pytest

from meterbus.api import decode
from meterbus.export import ExportView, to_dict, to_json
from meterbus.model import DecodeMode


_PROJECT_ROOT = Path(__file__).resolve().parents[1]


def _decode_amt_meter():
    raw_hex = (_PROJECT_ROOT / "tests" / "fixtures" / "legacy_frames" / "amt_meter.hex").read_text()
    return decode(bytes.fromhex(raw_hex), mode=DecodeMode.LENIENT)


def test_export_view_enum_is_public():
    assert ExportView.FULL == "full"
    assert ExportView.SUMMARY == "summary"
    assert ExportView.RECORDS == "records"


def test_to_dict_defaults_to_full_export():
    payload = to_dict(_decode_amt_meter())

    assert payload["ok"] is True
    assert "raw" in payload
    assert "telegram" in payload
    assert payload["telegram"]["header"]["manufacturer"] == "AMT"
    assert len(payload["telegram"]["records"]) == 22


def test_to_dict_supports_summary_export_view_enum():
    payload = to_dict(_decode_amt_meter(), view=ExportView.SUMMARY)

    assert payload == {
        "ok": True,
        "frame": {
            "kind": "long",
            "checksum_valid": True,
        },
        "meter": {
            "manufacturer": "AMT",
            "identification_number": "05564531",
            "medium": 4,
            "version": 192,
        },
        "records": 22,
        "diagnostics": [],
    }


def test_to_dict_supports_summary_export_view_string():
    assert to_dict(_decode_amt_meter(), view="summary") == to_dict(
        _decode_amt_meter(), view=ExportView.SUMMARY
    )


def test_to_dict_supports_records_export_view():
    payload = to_dict(_decode_amt_meter(), view=ExportView.RECORDS)

    assert payload["ok"] is True
    assert payload["meter"] == {
        "manufacturer": "AMT",
        "identification_number": "05564531",
        "medium": 4,
        "version": 192,
    }
    assert len(payload["records"]) == 22
    assert payload["records"][0] == {
        "kind": "energy",
        "value": "289756000",
        "unit": "Wh",
        "function": "instantaneous_value",
        "storage_number": 0,
    }
    assert payload["records"][1] == {
        "kind": "volume",
        "value": 18038,
        "unit": "m^3",
        "function": "instantaneous_value",
        "storage_number": 0,
    }


def test_to_json_supports_export_view():
    payload = json.loads(to_json(_decode_amt_meter(), view=ExportView.SUMMARY))

    assert payload["ok"] is True
    assert payload["meter"]["manufacturer"] == "AMT"
    assert payload["records"] == 22


def test_to_json_supports_export_view_with_indent():
    text = to_json(_decode_amt_meter(), view=ExportView.SUMMARY, indent=2)

    assert "\n" in text
    assert '  "meter"' in text
    assert json.loads(text)["meter"]["identification_number"] == "05564531"


def test_invalid_export_view_raises_value_error():
    with pytest.raises(ValueError):
        to_dict(_decode_amt_meter(), view="compact")


def test_non_full_export_view_requires_decode_result():
    with pytest.raises(TypeError, match="non-full export views require a DecodeResult"):
        to_dict(object(), view=ExportView.SUMMARY)
