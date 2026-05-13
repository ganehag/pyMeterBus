from __future__ import annotations

import json
import subprocess
import sys

from meterbus.codec.crc import crc16_en13757_bytes
from tests.helpers.fixtures import load_hex_fixture


def _checksum(data: bytes) -> int:
    return sum(data) & 0xFF


def _long_application_frame(payload: bytes, *, ci: int) -> bytes:
    body = bytes([0x08, 0x0B, ci]) + payload
    return bytes([0x68, len(body), len(body), 0x68]) + body + bytes([_checksum(body), 0x16])


def _format_frame(format_data: bytes, *, signature: bytes = b"\x12\x34") -> bytes:
    return _long_application_frame(bytes([0x00]) + signature + format_data, ci=0x69)


def _compact_frame(compact_data: bytes, *, signature: bytes = b"\x12\x34", crc: bytes = b"\xAB\xCD") -> bytes:
    return _long_application_frame(signature + crc + compact_data, ci=0x79)


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
    raw = load_hex_fixture("frames/long_basic.hex").data.hex()

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
            "manufacturer": "WEP",
            "identification_number": "00000021",
            "medium": 27,
            "version": 2,
        },
        "records": 3,
        "diagnostics": [],
    }


def test_decode_cli_supports_records_view():
    raw = load_hex_fixture("frames/long_basic.hex").data.hex()

    completed = _run_cli("--mode", "lenient", "--view", "records", raw)

    assert completed.returncode == 0
    payload = json.loads(completed.stdout)
    assert payload["ok"] is True
    assert payload["meter"]["manufacturer"] == "WEP"
    assert len(payload["records"]) == 3
    assert payload["records"][0]["kind"] == "fabrication_number"
    assert payload["records"][0]["value"] == "64000449"
    assert payload["records"][1]["kind"] == "manufacturer"
    assert payload["records"][1]["value"] == 10
    assert payload["records"][2]["kind"] == "dimensionless"
    assert payload["records"][2]["value"] == 30


def test_decode_cli_expands_compact_frame_with_template():
    format_frame = _format_frame(bytes.fromhex("02 03"))
    compact_data = bytes.fromhex("34 12")
    full_frame_crc = crc16_en13757_bytes(bytes.fromhex("02 03 34 12"))
    compact_frame = _compact_frame(compact_data, crc=full_frame_crc)

    completed = _run_cli(
        "--compact-template",
        format_frame.hex(),
        compact_frame.hex(),
    )

    assert completed.returncode == 0
    assert completed.stderr == ""
    payload = json.loads(completed.stdout)
    assert payload["ok"] is True
    assert payload["telegram"]["application_kind"] == "compact_data"
    assert payload["compact_expansion"]["diagnostics"] == []
    assert payload["compact_expansion"]["undecoded_data"] == ""
    assert payload["compact_expansion"]["recovered_application_data"] == "02 03 34 12"
    assert payload["compact_expansion"]["records"][0]["vif"]["kind"] == "energy"
    assert payload["compact_expansion"]["records"][0]["value"]["value"] == 4660


def test_decode_cli_returns_one_for_compact_template_crc_mismatch():
    format_frame = _format_frame(bytes.fromhex("02 03"))
    compact_frame = _compact_frame(bytes.fromhex("34 12"), crc=b"\x00\x00")

    completed = _run_cli("--compact-template", format_frame.hex(), compact_frame.hex())

    assert completed.returncode == 1
    assert completed.stderr == ""
    payload = json.loads(completed.stdout)
    assert payload["compact_expansion"]["diagnostics"][-1]["code"] == "compact_full_frame_crc_mismatch"


def test_decode_cli_rejects_compact_template_with_invalid_hex():
    raw = load_hex_fixture("frames/ack.hex").data.hex()

    completed = _run_cli("--compact-template", "not-hex", raw)

    assert completed.returncode == 2
    assert completed.stdout == ""
    assert "invalid compact template hex input" in completed.stderr


def test_decode_cli_rejects_compact_template_for_non_compact_input():
    raw = load_hex_fixture("frames/ack.hex").data.hex()
    format_frame = _format_frame(bytes.fromhex("02 03"))

    completed = _run_cli("--compact-template", format_frame.hex(), raw)

    assert completed.returncode == 1
    assert completed.stdout == ""
    assert "compact template can only be used" in completed.stderr


def test_decode_cli_rejects_non_format_compact_template():
    raw = _compact_frame(bytes.fromhex("34 12")).hex()
    bad_template = load_hex_fixture("frames/ack.hex").data.hex()

    completed = _run_cli("--compact-template", bad_template, raw)

    assert completed.returncode == 1
    assert completed.stdout == ""
    assert "compact template must decode to an M-Bus Format frame" in completed.stderr


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
