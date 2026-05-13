#!/usr/bin/env python3
"""Import a zip of real-world M-Bus `.hex` telegrams into the test corpus.

The importer is intentionally dependency-free. It keeps three classes of input
separate:

- structurally valid wired M-Bus frames;
- wired-looking malformed/truncated/checksum-negative frames;
- non-wired-start payloads that are likely wireless M-Bus or aggregator-stripped
  data.

It writes a JSONL fixture file consumed by `tests/test_v2_real_world_corpus.py`.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import zipfile
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Iterable


_DEFAULT_OUTPUT = Path("tests/fixtures/real_world_corpus.jsonl")
_HEX_TOKEN_RE = re.compile(r"[0-9a-fA-F]{2}")


def _parse_hex_text(text: str) -> bytes:
    tokens: list[str] = []
    for line in text.splitlines():
        line_without_comment = line.split("#", 1)[0]
        tokens.extend(_HEX_TOKEN_RE.findall(line_without_comment))
    return bytes.fromhex("".join(tokens))


def _format_hex(data: bytes) -> str:
    return data.hex(" ").upper()


def _classify(data: bytes) -> tuple[str, str, str]:
    if not data:
        return "real_world_negative", "empty", "empty input"

    start = data[0]

    if start == 0xE5:
        if len(data) == 1:
            return "real_world_wired", "ack", "valid ACK"
        return "real_world_negative", "ack_invalid", "ACK with trailing bytes"

    if start == 0x10:
        if len(data) < 5:
            return "real_world_negative", "short_invalid", "short frame shorter than 5 bytes"
        issues: list[str] = []
        if data[4] != 0x16:
            issues.append("invalid stop byte")
        if data[3] != ((data[1] + data[2]) & 0xFF):
            issues.append("checksum mismatch")
        if len(data) != 5:
            issues.append("trailing bytes")
        if issues:
            return "real_world_negative", "short_invalid", "; ".join(issues)
        return "real_world_wired", "short", "valid short frame"

    if start == 0x68:
        if len(data) < 6:
            return "real_world_negative", "long_invalid", "long/control frame shorter than 6 bytes"

        length_1 = data[1]
        length_2 = data[2]
        expected_length = length_1 + 6
        issues: list[str] = []

        if length_1 != length_2:
            issues.append("length fields differ")
        if len(data) != expected_length:
            issues.append(f"length mismatch expected {expected_length} got {len(data)}")
        if data[3] != 0x68:
            issues.append("invalid repeated start byte")

        if len(data) >= expected_length and expected_length >= 6:
            if data[expected_length - 1] != 0x16:
                issues.append("invalid stop byte")
            body = data[4 : 4 + length_1]
            checksum = sum(body) & 0xFF
            if data[4 + length_1] != checksum:
                issues.append("checksum mismatch")
        elif data[-1] != 0x16:
            issues.append("missing/invalid final stop byte")

        if issues:
            return "real_world_negative", "long_invalid", "; ".join(issues)

        kind = "control" if length_1 == 3 else "long"
        return "real_world_wired", kind, f"valid {kind} frame"

    return (
        "wireless_or_aggregator",
        "non_wired_start",
        f"starts with 0x{start:02X}, not wired M-Bus frame start",
    )


def _iter_hex_files(root: Path) -> Iterable[Path]:
    yield from sorted(path for path in root.rglob("*.hex") if path.is_file())


def _read_zip(zip_path: Path) -> list[dict[str, object]]:
    with TemporaryDirectory() as tmpdir:
        tmp = Path(tmpdir)
        with zipfile.ZipFile(zip_path) as archive:
            archive.extractall(tmp)

        entries: list[dict[str, object]] = []
        for path in _iter_hex_files(tmp):
            data = _parse_hex_text(path.read_text(encoding="utf-8"))
            category, kind, notes = _classify(data)
            entries.append(
                {
                    "file": path.name,
                    "category": category,
                    "kind": kind,
                    "bytes": len(data),
                    "notes": notes,
                    "hex": _format_hex(data),
                }
            )
        return sorted(entries, key=lambda item: str(item["file"]))


def _write_jsonl(entries: list[dict[str, object]], output: Path) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", encoding="utf-8") as handle:
        for entry in entries:
            handle.write(json.dumps(entry, sort_keys=True, separators=(",", ":")))
            handle.write("\n")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("zip_path", type=Path, help="zip file containing .hex telegram fixtures")
    parser.add_argument(
        "--output",
        type=Path,
        default=_DEFAULT_OUTPUT,
        help=f"output JSONL fixture path, default: {_DEFAULT_OUTPUT}",
    )
    args = parser.parse_args(argv)

    if not args.zip_path.exists():
        parser.error(f"zip file not found: {args.zip_path}")

    entries = _read_zip(args.zip_path)
    _write_jsonl(entries, args.output)

    counts: dict[str, int] = {}
    for entry in entries:
        category = str(entry["category"])
        counts[category] = counts.get(category, 0) + 1

    print(f"wrote {len(entries)} entries to {args.output}")
    for category in sorted(counts):
        print(f"{category}: {counts[category]}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
