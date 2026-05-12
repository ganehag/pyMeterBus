"""Decode M-Bus hex input and print JSON."""

from __future__ import annotations

import argparse
import sys

from meterbus.api import decode
from meterbus.export import ExportView, to_json
from meterbus.model import DecodeMode


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Decode an M-Bus frame from a hex string.")
    parser.add_argument("hex", help="Hex-encoded frame bytes, with or without spaces")
    parser.add_argument(
        "--mode",
        choices=[mode.value for mode in DecodeMode],
        default=DecodeMode.STRICT.value,
        help="Decode mode to use",
    )
    parser.add_argument(
        "--view",
        choices=[view.value for view in ExportView],
        default=ExportView.FULL.value,
        help="JSON export view to print",
    )
    parser.add_argument("--indent", type=int, default=None, help="Pretty-print JSON with this indentation")
    args = parser.parse_args(argv)

    try:
        raw = bytes.fromhex(args.hex)
    except ValueError as exc:
        print(f"invalid hex input: {exc}", file=sys.stderr)
        return 2

    result = decode(raw, mode=DecodeMode(args.mode))
    print(to_json(result, view=ExportView(args.view), indent=args.indent))
    return 0 if result.ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
