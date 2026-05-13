# pyMeterBus

[![Build status](https://github.com/ganehag/pyMeterBus/actions/workflows/run-test.yml/badge.svg)](https://github.com/ganehag/pyMeterBus/actions/workflows/run-test.yml)
[![codecov](https://codecov.io/gh/ganehag/pyMeterBus/branch/master/graph/badge.svg?token=gHfokXGQ70)](https://codecov.io/gh/ganehag/pyMeterBus)
[![pypi](https://img.shields.io/pypi/pyversions/pyMeterBus)](https://pypi.org/project/pyMeterBus/)
[![GitHub issues](https://img.shields.io/github/issues/ganehag/pyMeterBus.svg)](https://github.com/ganehag/pyMeterBus/issues)
[![GitHub issues closed](https://img.shields.io/github/issues-closed/ganehag/pyMeterBus.svg)](https://github.com/ganehag/pyMeterBus/issues/?q=is%3Aissue+is%3Aclosed)
[![PyPI Status](https://img.shields.io/pypi/v/pyMeterBus.svg)](https://pypi.python.org/pypi/pyMeterBus/)

pyMeterBus is a Python decoder for M-Bus frames.

M-Bus, also called Meter-Bus, is a European metering protocol used for remote reading of heat, water, gas, electricity, and other consumption meters. pyMeterBus focuses on decoding complete frame bytes into structured Python objects and stable JSON-friendly exports.

## Current status

The `v2` decoder is the supported direction of the project. It is a breaking rewrite of the older object model and is intentionally small, explicit, and diagnostics-first.

The v2 package has no runtime dependencies. It does not import `pyserial`, YAML libraries, or crypto packages. It is byte-oriented: read a complete M-Bus frame with whatever transport you use, then pass those bytes to the decoder.

Transport is caller-owned. Serial adapters, sockets, HTTP gateways, files, and test fixtures are all just ways to obtain frame bytes.

If you are upgrading existing pyMeterBus code, read the [v1 to v2 migration guide](docs/migration-v1-to-v2.md) before changing production integrations.

## Requirements

Python 3.11 or newer.

Only actively supported Python versions are targeted.

## Install

From PyPI:

```shell
python -m pip install pyMeterBus
```

From a checkout:

```shell
python -m pip install .
```

For development:

```shell
python -m pip install -e .
```

## Common use cases

### Decode frame bytes in Python

```python
from meterbus.api import decode
from meterbus.export import to_json

raw = bytes.fromhex("E5")
result = decode(raw)

print(result.ok)
print(to_json(result, indent=2))
```

Output:

```json
{
  "diagnostics": [],
  "frame": {
    "diagnostics": [],
    "kind": "ack",
    "raw": "E5"
  },
  "ok": true,
  "raw": "E5",
  "telegram": null
}
```

For normal application code, use `decode()` and inspect `result.ok` and `result.diagnostics`. The decoder returns structured diagnostics rather than hiding malformed or unsupported data.

### Decode from the command line

```shell
python -m meterbus.cli.decode E5
```

After installation, the console script is available as:

```shell
pymeterbus-decode E5
```

Decode a binary frame file by converting it to one-line hex first:

```shell
python -m meterbus.cli.decode \
  --mode lenient \
  --view records \
  --indent 2 \
  "$(xxd -p -c 999999 frame.blob)"
```

### Decode serial data

A common use case is reading M-Bus frames from a serial adapter. pyMeterBus deliberately does not depend on `pyserial`, but it does document a recommended pattern: your application reads one complete frame, then passes those bytes to `decode()`.

See the [serial transport example](docs/serial-transport.md) for a complete frame reader and `pyserial` integration example.

The basic shape is:

```python
from meterbus.api import decode
from meterbus.model import DecodeMode

raw = read_complete_mbus_frame_from_your_transport()
result = decode(raw, mode=DecodeMode.LENIENT)
```

## Core concepts

### Export views

The decoder can export full results or smaller views for common workflows:

```shell
pymeterbus-decode --view full "$HEX"
pymeterbus-decode --view summary "$HEX"
pymeterbus-decode --view records "$HEX"
```

Use `full` while debugging protocol behavior. Use `records` when feeding readings into another system.

The same views are available from Python:

```python
from meterbus.api import decode
from meterbus.export import ExportView, to_dict

result = decode(raw)
records_payload = to_dict(result, view=ExportView.RECORDS)
```

### Decode modes and diagnostics

The CLI and Python API support three decode modes:

- `strict`: fail on malformed frames or record errors.
- `lenient`: preserve partially decoded data where possible.
- `compat`: compatibility-oriented lenient behavior.

Example:

```shell
pymeterbus-decode --mode lenient --indent 2 "$HEX"
```

For real-world meter collection, lenient mode is often more useful because meters may include manufacturer-specific data, filler bytes, malformed tails, or unsupported records.

See [diagnostics and decode modes](docs/diagnostics.md) for severity levels, common diagnostic categories, and ingestion guidance.

### Compact and format frames

pyMeterBus v2 recognizes EN 13757 compact and format frames. Compact frames do not carry DIF/VIF descriptors, so the decoder does not auto-expand them from hidden state.

Expansion is explicit: provide the matching format frame as a template.

```shell
pymeterbus-decode \
  --compact-template "$(xxd -p -c 999999 format-frame.blob)" \
  --indent 2 \
  "$(xxd -p -c 999999 compact-frame.blob)"
```

When a format template is supplied, pyMeterBus checks the Format Signature and validates the Full-Frame-CRC over the recovered application data.

## What is supported

The v2 decoder currently covers:

- ACK, short, control, and long frame decoding.
- Frame checksum validation.
- Variable-data headers and record decoding.
- DIF/DIFE parsing.
- VIF/VIFE parsing for the implemented standard tables.
- Variable-length values, dates, times, strings, integers, BCD, and floating-point values where implemented.
- Fixed-data telegram decoding.
- Format-frame descriptor parsing.
- Explicit compact-frame expansion with signature and Full-Frame-CRC validation.
- Structured diagnostics and stable JSON export.

Unsupported or manufacturer-specific data should be preserved with diagnostics where possible rather than guessed.

## What is not supported

The v2 decoder does not currently aim to provide:

- Serial communication helpers as part of the core package.
- Hidden transport state.
- Automatic compact-frame template caching.
- Encoding/transmission of M-Bus request or control frames.
- Full coverage of every manufacturer-specific extension.

Serial support belongs at the application or example layer: read complete frames using your preferred transport library, then call `decode(raw)`.

## Documentation

For normal use, start with the [v2 usage guide](docs/v2-usage.md). It covers installation assumptions, Python decoding, CLI decoding, export views, diagnostics, decode modes, fixed and variable data, and compact/format expansion.

If you are upgrading from older pyMeterBus code, start with the [v1 to v2 migration guide](docs/migration-v1-to-v2.md). It covers removed APIs, transport ownership, export changes, and practical upgrade steps.

Common entry points:

- Decode frames from Python: [v2 usage guide](docs/v2-usage.md#decode-a-frame)
- Decode frames from the command line: [CLI usage](docs/v2-usage.md#decode-from-the-command-line)
- Decode frames from serial data: [serial transport example](docs/serial-transport.md)
- Upgrade from v1: [migration guide](docs/migration-v1-to-v2.md)
- Export JSON or dictionaries: [export examples](docs/v2-usage.md#export-to-json)
- Understand diagnostics and lenient mode: [diagnostics and decode modes](docs/diagnostics.md)
- Expand compact frames with a format template: [compact and format frames](docs/v2-usage.md#compact-and-format-frames)

For contributors and maintainers:

- [architecture notes](docs/architecture.md)
- [data model](docs/data-model.md)
- [compact and format frame implementation review](docs/spec-review/compact-format-frames.md)
- [release checklist](docs/v2-release-checklist.md)

## Development

Run the v2 test suite:

```shell
bash scripts/test-v2.sh
```

Run a quick CLI smoke test:

```shell
python -m meterbus.cli.decode E5
```

Build smoke testing is available through:

```shell
bash scripts/smoke-build.sh
```

## Contributing

Contributions are welcome, but protocol changes need to be careful. M-Bus fields are tightly specified, and many real meters also contain manufacturer-specific data. A plausible decode is not good enough; changes should be backed by the standard, a real frame fixture, or both.

Good contributions usually do one of these things:

- Add support for a clearly identified standard field or table entry.
- Add a real-world frame fixture and the expected v2 output.
- Preserve unsupported data more accurately without guessing its meaning.
- Improve diagnostics, exports, documentation, or tests without widening the runtime dependency surface.

For decoder changes, prefer small pull requests. Include the raw frame bytes when possible, add focused tests, and explain which part of the standard or which known device behavior the change follows. If the behavior is uncertain, preserve raw bytes and emit diagnostics rather than silently inventing a meaning.

Please avoid:

- Adding runtime dependencies for core decoding.
- Adding hidden transport state or serial I/O to the core package.
- Adding automatic compact-frame template caches.
- Reintroducing the old pre-v2 object model into the v2 root API.
- Making broad rewrites at the same time as protocol behavior changes.

Before opening a pull request, run:

```shell
bash scripts/test-v2.sh
python -m meterbus.cli.decode E5
```

If your change affects packaging or console scripts, also run:

```shell
bash scripts/smoke-build.sh
```

## License

See [LICENSE](LICENSE).
