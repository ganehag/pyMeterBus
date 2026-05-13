"""Decode M-Bus hex input and print JSON."""

from __future__ import annotations

import argparse
import json
import sys

from meterbus.api import decode
from meterbus.codec.compact import expand_compact_telegram
from meterbus.export import ExportView, to_dict, to_json
from meterbus.model import CompactDataTelegram, DecodeMode, FormatDataTelegram, Severity


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
    parser.add_argument(
        "--compact-template",
        help="Hex-encoded M-Bus Format frame used to expand a Compact frame",
    )
    parser.add_argument("--indent", type=int, default=None, help="Pretty-print JSON with this indentation")
    args = parser.parse_args(argv)

    try:
        raw = bytes.fromhex(args.hex)
    except ValueError as exc:
        print(f"invalid hex input: {exc}", file=sys.stderr)
        return 2

    mode = DecodeMode(args.mode)
    result = decode(raw, mode=mode)
    if args.compact_template is None:
        print(to_json(result, view=ExportView(args.view), indent=args.indent))
        return 0 if result.ok else 1

    try:
        template_raw = bytes.fromhex(args.compact_template)
    except ValueError as exc:
        print(f"invalid compact template hex input: {exc}", file=sys.stderr)
        return 2

    template_result = decode(template_raw, mode=mode)
    if not isinstance(template_result.telegram, FormatDataTelegram):
        print("compact template must decode to an M-Bus Format frame", file=sys.stderr)
        return 1

    if not isinstance(result.telegram, CompactDataTelegram):
        print("compact template can only be used when the input decodes to an M-Bus Compact frame", file=sys.stderr)
        return 1

    expansion = expand_compact_telegram(result.telegram, template_result.telegram)
    payload = to_dict(result, view=ExportView(args.view))
    if not isinstance(payload, dict):
        payload = {"result": payload}
    payload["compact_expansion"] = to_dict(
        {
            "records": expansion.records,
            "undecoded_data": expansion.undecoded_data,
            "diagnostics": expansion.diagnostics,
            "recovered_application_data": expansion.recovered_application_data,
        }
    )
    print(json.dumps(payload, indent=args.indent))

    expansion_has_error = any(diagnostic.severity is Severity.ERROR for diagnostic in expansion.diagnostics)
    return 0 if result.ok and template_result.ok and not expansion_has_error else 1


if __name__ == "__main__":
    raise SystemExit(main())
