from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
from typing import Any

from meterbus.api import decode
from meterbus.export import to_dict
from meterbus.model import DecodeMode


_PROJECT_ROOT = Path(__file__).resolve().parents[1]
_EXPECTED_PATH = _PROJECT_ROOT / "tests" / "fixtures" / "legacy_blob_probe_expected.json"
_BLOB_ROOTS = (
    _PROJECT_ROOT / "tests" / "test-frames",
    _PROJECT_ROOT / "tests" / "error-frames",
    _PROJECT_ROOT / "tests" / "unsupported-frames",
)


def _blob_paths() -> list[Path]:
    paths: list[Path] = []
    for root in _BLOB_ROOTS:
        paths.extend(path for path in sorted(root.glob("*.blob*")) if path.is_file())
    return sorted(paths)


def _compact_decode(path: Path) -> dict[str, Any]:
    raw = path.read_bytes()
    relative_path = path.relative_to(_PROJECT_ROOT).as_posix()

    try:
        result = decode(raw, mode=DecodeMode.LENIENT)
        payload = to_dict(result)
    except Exception as exc:  # noqa: BLE001 - this probe records public decode escape hatches.
        return {
            "path": relative_path,
            "decode_raised": True,
            "exception_type": type(exc).__name__,
            "exception_message": str(exc),
        }

    frame = payload.get("frame") or {}
    telegram = payload.get("telegram") or {}

    return {
        "path": relative_path,
        "decode_raised": False,
        "ok": payload.get("ok"),
        "frame_kind": frame.get("kind"),
        "diagnostic_codes": [diagnostic.get("code") for diagnostic in payload.get("diagnostics", [])],
        "telegram_diagnostic_codes": [
            diagnostic.get("code") for diagnostic in telegram.get("diagnostics", [])
        ],
        "undecoded_data": telegram.get("undecoded_data"),
    }


def _classify(item: dict[str, Any]) -> str:
    if item.get("decode_raised"):
        return "raises_exception"

    diagnostic_codes = item.get("diagnostic_codes") or []
    telegram_diagnostic_codes = item.get("telegram_diagnostic_codes") or []

    if item.get("ok") is True and not diagnostic_codes and not telegram_diagnostic_codes:
        if item.get("undecoded_data") in ("", None):
            return "clean_decode"
        return "clean_with_undecoded_tail"

    if item.get("ok") is True:
        return "lenient_with_diagnostics"

    if item.get("frame_kind") is not None:
        return "frame_level_error"

    return "unparsed"


def _actual_classifications() -> dict[str, str]:
    return {
        item["path"]: _classify(item)
        for item in (_compact_decode(path) for path in _blob_paths())
    }


def _expected_classifications() -> dict[str, str]:
    return json.loads(_EXPECTED_PATH.read_text(encoding="utf-8"))


def test_legacy_blob_probe_expected_file_covers_all_blob_files():
    expected = _expected_classifications()
    actual_paths = {path.relative_to(_PROJECT_ROOT).as_posix() for path in _blob_paths()}

    assert set(expected) == actual_paths


def test_legacy_blob_probe_classifications_are_stable():
    assert _actual_classifications() == _expected_classifications()


def test_legacy_blob_probe_bucket_counts_are_stable():
    counts = Counter(_expected_classifications().values())

    assert counts == {
        "clean_decode": 31,
        "clean_with_undecoded_tail": 2,
        "frame_level_error": 1,
        "lenient_with_diagnostics": 18,
        "unparsed": 4,
    }


def test_legacy_blob_probe_public_decode_does_not_raise():
    actual = _actual_classifications()

    assert [path for path, status in actual.items() if status == "raises_exception"] == []


def test_legacy_blob_probe_unparsed_files_are_known_unsupported_or_invalid_inputs():
    actual = _actual_classifications()

    assert sorted(path for path, status in actual.items() if status == "unparsed") == [
        "tests/test-frames/invalid_length.blob",
        "tests/unsupported-frames/gabriel-wmbus.blob",
        "tests/unsupported-frames/gabriel-wmbus.blob.2",
        "tests/unsupported-frames/manual_frame1.blob",
    ]
