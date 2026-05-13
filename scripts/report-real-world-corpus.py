#!/usr/bin/env python3
"""Report decode quality for an imported real-world M-Bus corpus.

Input is the JSONL file produced by `scripts/import-real-world-corpus.py`.
The report is intentionally dependency-free and is meant for release-readiness
triage: it shows which real-world frames decode cleanly, which only decode in
lenient/compat mode, and which expose diagnostics or unsupported areas.
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any

from meterbus.api import decode
from meterbus.model import DecodeMode


_DEFAULT_CORPUS = Path("tests/fixtures/real_world_corpus.jsonl")
_FIELDNAMES = [
    "file",
    "category",
    "kind",
    "bytes",
    "frame_kind",
    "ci",
    "telegram_kind",
    "manufacturer",
    "medium",
    "records",
    "undecoded_bytes",
    "strict_ok",
    "lenient_ok",
    "compat_ok",
    "strict_diagnostics",
    "lenient_diagnostics",
    "compat_diagnostics",
    "notes",
]


def _parse_hex(text: str) -> bytes:
    return bytes.fromhex("".join(text.split()))


def _load_entries(path: Path) -> list[dict[str, Any]]:
    entries: list[dict[str, Any]] = []
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        try:
            entry = json.loads(line)
        except json.JSONDecodeError as exc:
            raise ValueError(f"invalid JSONL at {path}:{line_number}: {exc}") from exc
        entries.append(entry)
    return entries


def _diagnostic_codes(result: Any) -> str:
    return ";".join(diagnostic.code for diagnostic in result.diagnostics)


def _frame_kind(result: Any) -> str:
    if result.frame is None:
        return ""
    kind = getattr(result.frame, "kind", "")
    return getattr(kind, "value", str(kind))


def _ci(result: Any) -> str:
    if result.frame is None:
        return ""
    value = getattr(result.frame, "ci", None)
    if value is None:
        return ""
    return f"0x{value:02X}"


def _telegram_kind(result: Any) -> str:
    telegram = result.telegram
    if telegram is None:
        return ""
    return getattr(telegram, "application_kind", type(telegram).__name__)


def _manufacturer(result: Any) -> str:
    telegram = result.telegram
    header = getattr(telegram, "header", None)
    return str(getattr(header, "manufacturer", "") or "")


def _medium(result: Any) -> str:
    telegram = result.telegram
    header = getattr(telegram, "header", None)
    value = getattr(header, "medium", "")
    return "" if value is None else str(value)


def _record_count(result: Any) -> str:
    telegram = result.telegram
    records = getattr(telegram, "records", None)
    if records is None:
        counters = getattr(telegram, "counters", None)
        if counters is None:
            return ""
        return str(len(counters))
    return str(len(records))


def _undecoded_bytes(result: Any) -> str:
    telegram = result.telegram
    undecoded_data = getattr(telegram, "undecoded_data", None)
    if undecoded_data is None:
        return ""
    return str(len(undecoded_data))


def build_rows(entries: list[dict[str, Any]]) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for entry in entries:
        raw = _parse_hex(str(entry["hex"]))
        strict = decode(raw, mode=DecodeMode.STRICT)
        lenient = decode(raw, mode=DecodeMode.LENIENT)
        compat = decode(raw, mode=DecodeMode.COMPAT)

        metadata_source = lenient if lenient.frame is not None else strict
        rows.append(
            {
                "file": str(entry.get("file", "")),
                "category": str(entry.get("category", "")),
                "kind": str(entry.get("kind", "")),
                "bytes": str(entry.get("bytes", len(raw))),
                "frame_kind": _frame_kind(metadata_source),
                "ci": _ci(metadata_source),
                "telegram_kind": _telegram_kind(metadata_source),
                "manufacturer": _manufacturer(metadata_source),
                "medium": _medium(metadata_source),
                "records": _record_count(metadata_source),
                "undecoded_bytes": _undecoded_bytes(metadata_source),
                "strict_ok": str(strict.ok).lower(),
                "lenient_ok": str(lenient.ok).lower(),
                "compat_ok": str(compat.ok).lower(),
                "strict_diagnostics": _diagnostic_codes(strict),
                "lenient_diagnostics": _diagnostic_codes(lenient),
                "compat_diagnostics": _diagnostic_codes(compat),
                "notes": str(entry.get("notes", "")),
            }
        )
    return rows


def write_csv(rows: list[dict[str, str]], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=_FIELDNAMES)
        writer.writeheader()
        writer.writerows(rows)


def write_markdown(rows: list[dict[str, str]], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    total = len(rows)
    categories = Counter(row["category"] for row in rows)
    strict_ok = sum(1 for row in rows if row["strict_ok"] == "true")
    lenient_ok = sum(1 for row in rows if row["lenient_ok"] == "true")
    compat_ok = sum(1 for row in rows if row["compat_ok"] == "true")

    lines = [
        "# Real-world M-Bus corpus decode report",
        "",
        f"Total entries: {total}",
        "",
        "## Summary",
        "",
        "| Metric | Count |",
        "| --- | ---: |",
        f"| strict ok | {strict_ok} |",
        f"| lenient ok | {lenient_ok} |",
        f"| compat ok | {compat_ok} |",
    ]
    for category, count in sorted(categories.items()):
        lines.append(f"| {category} | {count} |")

    lines.extend(
        [
            "",
            "## Entries",
            "",
            "| File | Category | Kind | CI | Manufacturer | Records | Strict | Lenient | Compat | Diagnostics |",
            "| --- | --- | --- | --- | --- | ---: | --- | --- | --- | --- |",
        ]
    )

    for row in rows:
        diagnostics = row["lenient_diagnostics"] or row["strict_diagnostics"] or row["compat_diagnostics"]
        lines.append(
            "| {file} | {category} | {kind} | {ci} | {manufacturer} | {records} | {strict_ok} | {lenient_ok} | {compat_ok} | {diagnostics} |".format(
                file=row["file"],
                category=row["category"],
                kind=row["kind"],
                ci=row["ci"],
                manufacturer=row["manufacturer"],
                records=row["records"] or "0",
                strict_ok=row["strict_ok"],
                lenient_ok=row["lenient_ok"],
                compat_ok=row["compat_ok"],
                diagnostics=diagnostics,
            )
        )

    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def print_summary(rows: list[dict[str, str]]) -> None:
    categories = Counter(row["category"] for row in rows)
    strict_ok = sum(1 for row in rows if row["strict_ok"] == "true")
    lenient_ok = sum(1 for row in rows if row["lenient_ok"] == "true")
    compat_ok = sum(1 for row in rows if row["compat_ok"] == "true")

    print(f"entries: {len(rows)}")
    print(f"strict ok: {strict_ok}")
    print(f"lenient ok: {lenient_ok}")
    print(f"compat ok: {compat_ok}")
    for category, count in sorted(categories.items()):
        print(f"{category}: {count}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--corpus",
        type=Path,
        default=_DEFAULT_CORPUS,
        help=f"input JSONL corpus path, default: {_DEFAULT_CORPUS}",
    )
    parser.add_argument("--csv", type=Path, help="optional CSV report output path")
    parser.add_argument("--markdown", type=Path, help="optional Markdown report output path")
    args = parser.parse_args(argv)

    if not args.corpus.exists():
        parser.error(
            f"corpus file not found: {args.corpus}; run scripts/import-real-world-corpus.py first"
        )

    rows = build_rows(_load_entries(args.corpus))
    if args.csv is not None:
        write_csv(rows, args.csv)
    if args.markdown is not None:
        write_markdown(rows, args.markdown)
    print_summary(rows)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
