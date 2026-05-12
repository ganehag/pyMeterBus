from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from tests.helpers.fixtures import load_hex_fixture


_PROJECT_ROOT = Path(__file__).resolve().parents[1]


def _run_cli(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "-m", "meterbus.cli.decode", *args],
        check=False,
        text=True,
        capture_output=True,
    )


def test_decode_cli_outputs_compact_json_for_valid_frame():
    raw = load_hex_fixture("frames/ack.hex").data.hex()

    completed = _run_cli(raw)

    assert completed.returncode == 0
    assert completed.stderr == ""
    assert "\n" not in completed.stdout.strip()
    payload = json.loads(completed.stdout)
    assert payload["ok"] is True
    assert payload["frame"]["kind"] == "ack"


def test_decode_cli_outputs_pretty_json_with_indent():
    raw = load_hex_fixture("frames/ack.hex").data.hex()

    completed = _run_cli("--indent", "2", raw)

    assert completed.returncode == 0
    assert "\n" in completed.stdout
    assert '  "diagnostics"' in completed.stdout
    assert json.loads(completed.stdout)["frame"]["kind"] == "ack"


def test_decode_cli_supports_lenient_mode():
    raw = bytearray(load_hex_fixture("frames/short.hex").data)
    raw[3] = 0x00

    completed = _run_cli("--mode", "lenient", raw.hex())

    assert completed.returncode == 0
    payload = json.loads(completed.stdout)
    assert payload["ok"] is True
    assert payload["frame"]["checksum_valid"] is False
    assert payload["diagnostics"][0]["severity"] == "error"


def test_decode_cli_supports_summary_view():
    raw = (_PROJECT_ROOT / "tests" / "test-frames" / "amt_meter.blob").read_bytes().hex()

    completed = _run_cli("--mode", "lenient", "--view", "summary", raw)

    assert completed.returncode == 0
    payload = json.loads(completed.stdout)
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


def test_decode_cli_supports_records_view():
    raw = (_PROJECT_ROOT / "tests" / "test-frames" / "amt_meter.blob").read_bytes().hex()

    completed = _run_cli("--mode", "lenient", "--view", "records", raw)

    assert completed.returncode == 0
    payload = json.loads(completed.stdout)
    assert payload["ok"] is True
    assert payload["meter"]["manufacturer"] == "AMT"
    assert len(payload["records"]) == 22
    assert payload["records"][0]["kind"] == "energy"
    assert payload["records"][0]["unit"] == "Wh"


def test_decode_cli_rejects_unknown_view():
    raw = load_hex_fixture("frames/ack.hex").data.hex()

    completed = _run_cli("--view", "compact", raw)

    assert completed.returncode == 2
    assert completed.stdout == ""
    assert "invalid choice" in completed.stderr


def test_decode_cli_returns_one_when_decode_result_is_not_ok():
    completed = _run_cli("00")

    assert completed.returncode == 1
    payload = json.loads(completed.stdout)
    assert payload["ok"] is False
    assert payload["diagnostics"][0]["code"] == "invalid_start_byte"


def test_decode_cli_returns_two_for_invalid_hex_input():
    completed = _run_cli("not-hex")

    assert completed.returncode == 2
    assert completed.stdout == ""
    assert "invalid hex input" in completed.stderr
