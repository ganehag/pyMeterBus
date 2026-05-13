from __future__ import annotations

import json
from pathlib import Path

import pytest

from meterbus.api import decode
from meterbus.model import DecodeMode
from tests.helpers.fixtures import parse_hex_fixture_text


_PROJECT_ROOT = Path(__file__).resolve().parents[1]
_CORPUS_PATH = _PROJECT_ROOT / "tests" / "fixtures" / "real_world_corpus.jsonl"


def _load_corpus() -> tuple[dict[str, object], ...]:
    if not _CORPUS_PATH.exists():
        return ()
    return tuple(
        json.loads(line)
        for line in _CORPUS_PATH.read_text(encoding="utf-8").splitlines()
        if line.strip()
    )


_CORPUS = _load_corpus()
_WIRED = tuple(entry for entry in _CORPUS if entry["category"] == "real_world_wired")
_NEGATIVE = tuple(entry for entry in _CORPUS if entry["category"] == "real_world_negative")
_NON_WIRED = tuple(entry for entry in _CORPUS if entry["category"] == "wireless_or_aggregator")


def _entry_id(entry: dict[str, object]) -> str:
    return str(entry["file"])


def test_real_world_corpus_file_is_optional_but_documented():
    importer = _PROJECT_ROOT / "scripts" / "import-real-world-corpus.py"

    assert importer.exists()
    if not _CORPUS_PATH.exists():
        pytest.skip("run scripts/import-real-world-corpus.py <zip> to generate real-world corpus fixtures")

    assert _CORPUS


@pytest.mark.skipif(not _CORPUS, reason="real-world corpus fixture not generated")
def test_real_world_corpus_has_expected_categories():
    categories = {entry["category"] for entry in _CORPUS}

    assert categories == {
        "real_world_wired",
        "real_world_negative",
        "wireless_or_aggregator",
    }
    assert len(_WIRED) >= 1
    assert len(_NEGATIVE) >= 1
    assert len(_NON_WIRED) >= 1


@pytest.mark.skipif(not _CORPUS, reason="real-world corpus fixture not generated")
@pytest.mark.parametrize("entry", _CORPUS, ids=_entry_id)
def test_real_world_corpus_entries_are_normalized(entry):
    raw = parse_hex_fixture_text(str(entry["hex"]))

    assert raw
    assert len(raw) == entry["bytes"]
    assert entry["file"].endswith(".hex")
    assert entry["kind"]
    assert entry["notes"]


@pytest.mark.skipif(not _WIRED, reason="real-world corpus fixture not generated")
@pytest.mark.parametrize("entry", _WIRED, ids=_entry_id)
def test_real_world_wired_frames_decode_without_frame_errors(entry):
    raw = parse_hex_fixture_text(str(entry["hex"]))

    for mode in (DecodeMode.STRICT, DecodeMode.LENIENT, DecodeMode.COMPAT):
        result = decode(raw, mode=mode)
        assert result.frame is not None
        assert result.raw == raw
        assert result.frame.raw == raw


@pytest.mark.skipif(not _NEGATIVE, reason="real-world corpus fixture not generated")
@pytest.mark.parametrize("entry", _NEGATIVE, ids=_entry_id)
def test_real_world_negative_wired_frames_are_not_clean_decodes(entry):
    raw = parse_hex_fixture_text(str(entry["hex"]))

    result = decode(raw, mode=DecodeMode.STRICT)

    assert result.ok is False
    assert result.diagnostics


@pytest.mark.skipif(not _NON_WIRED, reason="real-world corpus fixture not generated")
@pytest.mark.parametrize("entry", _NON_WIRED, ids=_entry_id)
def test_real_world_non_wired_payloads_are_not_silently_accepted(entry):
    raw = parse_hex_fixture_text(str(entry["hex"]))

    result = decode(raw, mode=DecodeMode.LENIENT)

    assert result.ok is False
    assert result.frame is None
    assert result.diagnostics
    assert result.diagnostics[0].code == "invalid_start_byte"
