from __future__ import annotations

import csv
import importlib.util
from pathlib import Path


_PROJECT_ROOT = Path(__file__).resolve().parents[1]
_REPORTER_PATH = _PROJECT_ROOT / "scripts" / "report-real-world-corpus.py"


def _load_reporter_module():
    spec = importlib.util.spec_from_file_location("report_real_world_corpus", _REPORTER_PATH)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_real_world_corpus_reporter_builds_rows_for_all_categories():
    reporter = _load_reporter_module()
    entries = [
        {
            "file": "ack.hex",
            "category": "real_world_wired",
            "kind": "ack",
            "bytes": 1,
            "notes": "valid ACK",
            "hex": "E5",
        },
        {
            "file": "bad.hex",
            "category": "real_world_negative",
            "kind": "empty",
            "bytes": 0,
            "notes": "empty input",
            "hex": "",
        },
        {
            "file": "wireless.hex",
            "category": "wireless_or_aggregator",
            "kind": "non_wired_start",
            "bytes": 2,
            "notes": "not wired M-Bus",
            "hex": "2E 44",
        },
    ]

    rows = reporter.build_rows(entries)

    assert len(rows) == 3
    assert rows[0]["file"] == "ack.hex"
    assert rows[0]["frame_kind"] == "ack"
    assert rows[0]["strict_ok"] == "true"
    assert rows[0]["lenient_ok"] == "true"
    assert rows[0]["compat_ok"] == "true"

    assert rows[1]["strict_ok"] == "false"
    assert rows[1]["strict_diagnostics"] == "empty_input"

    assert rows[2]["strict_ok"] == "false"
    assert rows[2]["lenient_ok"] == "false"
    assert rows[2]["strict_diagnostics"] == "invalid_start_byte"


def test_real_world_corpus_reporter_writes_csv_and_markdown(tmp_path):
    reporter = _load_reporter_module()
    rows = reporter.build_rows(
        [
            {
                "file": "ack.hex",
                "category": "real_world_wired",
                "kind": "ack",
                "bytes": 1,
                "notes": "valid ACK",
                "hex": "E5",
            }
        ]
    )
    csv_path = tmp_path / "report.csv"
    markdown_path = tmp_path / "report.md"

    reporter.write_csv(rows, csv_path)
    reporter.write_markdown(rows, markdown_path)

    with csv_path.open(encoding="utf-8", newline="") as handle:
        csv_rows = list(csv.DictReader(handle))

    assert csv_rows[0]["file"] == "ack.hex"
    assert csv_rows[0]["strict_ok"] == "true"

    markdown = markdown_path.read_text(encoding="utf-8")
    assert "# Real-world M-Bus corpus decode report" in markdown
    assert "| strict ok | 1 |" in markdown
    assert "ack.hex" in markdown
