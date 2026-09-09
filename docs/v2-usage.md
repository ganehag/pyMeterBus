# pyMeterBus v2 usage

The v2 API is a structured decoder path built around explicit results, diagnostics, and deterministic export helpers.

v2 is a breaking rewrite. The package root is intentionally lightweight and focused on the v2 decode API. Legacy root-level imports from the older object model are no longer the supported public contract.

Use this guide if you want to decode M-Bus frames, inspect meter records, export JSON, or debug compact/format frames.

## Public imports

Preferred v2 imports:

```python
from meterbus import decode
from meterbus.api import decode
from meterbus.export import to_dict, to_json
from meterbus.model import DecodeMode
```

The package root exports only the small v2 decode surface:

```python
from meterbus import decode, decode_one, decode_one_frame
```

Do not rely on legacy symbols such as `TelegramLong`, `TelegramACK`, serial helpers, or wireless telegram classes being available from `import meterbus`. Import v2 APIs directly instead.

The default v2 package install has no runtime dependencies. The decoder is byte-oriented: bring your own transport, read raw M-Bus frame bytes, then pass those bytes to `decode()`.

## Mental model

Most callers should follow this flow:

1. Read bytes from a meter, file, socket, serial adapter, or test fixture.
2. Call `decode(raw)`.
3. Check `result.ok`.
4. Inspect `result.frame`, `result.telegram`, and `result.diagnostics`.
5. Export with `to_dict()` or `to_json()` if you need stable machine-readable output.

`decode()` is intentionally not a magic pipeline. It decodes one frame and reports what it knows. It does not maintain hidden compact-frame template caches, it does not silently expand compact frames, and it does not hide protocol diagnostics.

## Decode a frame

```python
from meterbus.api import decode

raw = bytes.fromhex("E5")
result = decode(raw)

assert result.ok is True
assert result.frame.kind.value == "ack"
assert result.telegram is None
```

`decode()` always returns a `DecodeResult`. It does not raise for ordinary decode failures. Check `result.ok` and inspect `result.diagnostics`. `result.ok` means that decoding produced no fatal diagnostic in the selected mode; it does not mean that `result.diagnostics` is empty.

ACK, short, and control frames do not contain application telegrams, so `result.telegram` is `None` for those frames.

## Decode one frame or telegram directly

The three entry points differ only in what they return and how they report an unusable result:

| API | Returns | Raises `DecodeError` when | Typical use |
| --- | --- | --- | --- |
| `decode()` | `DecodeResult` | Never for an ordinary protocol decode failure | Diagnostics-first ingestion and inspection |
| `decode_one_frame()` | `Frame` | The selected mode cannot produce a usable frame | Frame-only callers that prefer exceptions |
| `decode_one()` | `Telegram` | The selected mode is unsuccessful or the frame has no supported application telegram | Application-data callers that prefer exceptions |

```python
from meterbus.api import decode_one_frame, decode_one

frame = decode_one_frame(bytes.fromhex("E5"))
telegram = decode_one(long_frame_bytes)
```

`decode_one_frame()` returns a frame or raises `DecodeError`.

`decode_one()` returns an application telegram or raises `DecodeError` when decoding is unsuccessful in the selected mode or no telegram is available. For example, a fatal record error raises in strict mode, while lenient mode can return a partial telegram carrying an error diagnostic.

For most ingestion systems, `decode()` is the safer choice because it lets you log or store diagnostics without throwing away the raw result.

## Decode modes

```python
from meterbus.api import decode
from meterbus.model import DecodeMode

result = decode(bytes.fromhex("10 40 0B 00 16"), mode=DecodeMode.LENIENT)
```

Supported modes are:

- `DecodeMode.STRICT`: fail on malformed frames or record errors.
- `DecodeMode.LENIENT`: preserve partially decoded data where possible.
- `DecodeMode.COMPAT`: preserve partially decoded data where possible for compatibility-oriented workflows.

In lenient and compat modes, undecodable records can be preserved as `UnknownRecord` values with diagnostics instead of discarding the whole telegram. Such a result can have `ok=True` and still contain `error` diagnostics: `ok` specifically means there is no fatal diagnostic in that mode.

Use strict mode for tests and validation. Use lenient mode when you are collecting real-world meter data and prefer partial records plus diagnostics over a hard failure.

## Diagnostics

Diagnostics are structured. A diagnostic has a severity, code, message, optional byte offset, and optional context.

```python
result = decode(raw, mode=DecodeMode.LENIENT)

for diagnostic in result.diagnostics:
    print(diagnostic.severity.value, diagnostic.code, diagnostic.message)
```

Diagnostics have one owning layer. `result.frame.diagnostics` contains frame-envelope issues, while `result.telegram.diagnostics` contains application- and record-level issues. `result.diagnostics` is their ordered aggregate and is the normal top-level collection to inspect. A malformed record can also carry its own diagnostic when it is preserved as an `UnknownRecord`.

Typical handling is:

```python
if not result.ok:
    # Log the raw frame and diagnostics.
    ...

if result.diagnostics:
    # Keep the decoded data, but preserve warnings/errors for later review.
    ...
```

Do not treat an empty `telegram.records` list as the only failure signal. Always look at `result.ok` and `result.diagnostics`.

## Export to dictionaries

```python
from meterbus.api import decode
from meterbus.export import to_dict

result = decode(bytes.fromhex("E5"))
payload = to_dict(result)

assert payload["ok"] is True
assert payload["frame"]["kind"] == "ack"
```

`to_dict()` produces JSON-friendly Python values. Bytes are rendered as uppercase hex strings, enums are rendered as their protocol-facing values, and most diagnostics are rendered as dictionaries.

## Export to JSON

```python
from meterbus.api import decode
from meterbus.export import to_json

result = decode(bytes.fromhex("E5"))
print(to_json(result))
print(to_json(result, indent=2))
```

`to_json()` wraps `to_dict()` and emits deterministic JSON with stable key ordering.

## Export views

The full export contains the complete decoded frame and telegram. For applications and shell pipelines, the smaller views are often easier to consume.

```python
from meterbus.export import ExportView, to_dict, to_json

summary = to_dict(result, view=ExportView.SUMMARY)
records = to_dict(result, view=ExportView.RECORDS)

print(to_json(result, view=ExportView.RECORDS, indent=2))
```

The views are:

- `full`: complete frame, telegram, raw data, diagnostics, and decoded records.
- `summary`: frame status and meter/header summary.
- `records`: flattened record-oriented output for normal meter readings.

Use `records` when feeding decoded readings into another system. Use `full` when debugging protocol behavior.

## Decode from the command line

During development or from a checkout:

```shell
python -m meterbus.cli.decode "E5"
python -m meterbus.cli.decode --indent 2 "E5"
python -m meterbus.cli.decode --mode lenient "10 40 0B 00 16"
```

After installation, the package entry point is:

```shell
pymeterbus-decode "E5"
pymeterbus-decode --indent 2 "E5"
pymeterbus-decode --mode lenient "10 40 0B 00 16"
```

For binary fixture files, convert to one-line hex first:

```shell
python -m meterbus.cli.decode \
  --mode lenient \
  --view records \
  --indent 2 \
  "$(xxd -p -c 999999 frame.blob)"
```

Exit codes:

- `0`: decode completed and `DecodeResult.ok` is true.
- `1`: decode completed and `DecodeResult.ok` is false, or compact expansion produced an error diagnostic.
- `2`: invalid CLI input, such as malformed hex.

The CLI writes the JSON decode result to stdout. CLI input errors are written to stderr.

## Serial and other transports

The v2 package does not import or depend on `pyserial`. This is intentional. Serial I/O, sockets, HTTP gateways, files, and test fixtures are transports; pyMeterBus v2 decodes bytes.

A serial application should read a complete M-Bus frame with its own transport code, then call the decoder:

```python
from meterbus.api import decode
from meterbus.model import DecodeMode

# Example shape only: use pyserial or another transport in your application.
raw = read_complete_mbus_frame_from_transport()
result = decode(raw, mode=DecodeMode.LENIENT)
```

This keeps the library dependency-free and avoids coupling protocol decoding to one I/O library. Future serial helpers should stay thin and optional: they should help callers collect complete frame bytes, not become a required runtime dependency for decoding.

## Variable-data telegrams

For long frames carrying CI `0x72` or `0x76`, the v2 decoder parses the variable-data header and then decodes records until it reaches filler bytes or an undecodable record.

```python
from meterbus.api import decode

raw = bytes.fromhex(
    "68 3D 3D 68 08 0B 72 21 00 00 00 B0 5C 02 1B "
    "12 00 00 00 0C 78 49 04 00 64 02 75 0A 00 "
    "01 FD 71 1E 2F 2F 0A 66 20 02 0A FB 1A 31 "
    "05 02 FD 97 1D 00 00 2F 2F 2F 2F 2F 2F 2F "
    "2F 2F 2F 2F 2F 2F 2F 2F DD 16"
)

result = decode(raw)
telegram = result.telegram

assert result.ok is True
assert telegram.header.manufacturer == "WEP"
assert len(telegram.records) == 3
```

The decoder preserves both the original application bytes and the trailing undecoded bytes:

```python
telegram.raw_application_data
telegram.undecoded_data
```

`CI 0x72` and `CI 0x76` differ in application-byte order. The decoder uses the CI mode bit when decoding values, including variable-length text.

## Working with decoded records

A normal variable-data record contains the parsed DIF/DIFE metadata, VIF/VIFE metadata, interpreted value, and record addressing fields.

```python
for record in telegram.records:
    print(record.vif.kind, record.value.value, record.value.unit)
```

For record-oriented JSON, prefer the records export view:

```python
from meterbus.export import ExportView, to_dict

payload = to_dict(result, view=ExportView.RECORDS)
for record in payload["records"]:
    print(record["kind"], record.get("value"), record.get("unit"))
```

Values may be integers, decimals, strings, dates, datetimes, or raw/preserved data depending on the DIF/VIF combination. Decimal values are exported as strings to avoid losing precision in JSON.

## Fixed-data telegrams

For long frames carrying fixed-data CIs, the v2 decoder parses the fixed-data header, medium/unit field, and the two fixed counters.

```python
from meterbus.api import decode

result = decode(raw_fixed_data_frame)
telegram = result.telegram

for counter in telegram.counters:
    print(counter.index, counter.value, counter.unit, counter.scaled_value)
```

Fixed-data counters expose both the raw BCD value and `scaled_value` when the medium/unit field defines a multiplier. Historic counter units can inherit the first counter's unit metadata where the standard says "same but historic".

## Compact and format frames

EN 13757 compact frames do not carry DIF/VIF descriptors. They carry value bytes plus a Format Signature and Full-Frame-CRC. To decode values safely, you need the matching format frame or equivalent descriptors.

The v2 decoder therefore does **not** auto-expand compact frames from `decode()`. It recognizes and preserves them. Expansion is explicit.

### Decode a format frame

```python
from meterbus.api import decode
from meterbus.model import FormatDataTelegram

format_result = decode(format_frame_bytes)
assert isinstance(format_result.telegram, FormatDataTelegram)

for descriptor in format_result.telegram.descriptors:
    print(descriptor.index, descriptor.dif, descriptor.vif)
```

A format frame contains descriptor metadata only: DIF/DIFE plus VIF/VIFE. It contains no values.

### Decode a compact frame

```python
from meterbus.api import decode
from meterbus.model import CompactDataTelegram

compact_result = decode(compact_frame_bytes)
assert isinstance(compact_result.telegram, CompactDataTelegram)

print(compact_result.telegram.format_signature)
print(compact_result.telegram.full_frame_crc)
print(compact_result.telegram.compact_data)
```

A compact frame is preserved until you supply the matching template.

### Expand a compact frame in Python

```python
from meterbus.codec.compact import expand_compact_telegram

expansion = expand_compact_telegram(
    compact_result.telegram,
    format_result.telegram,
)

if expansion.diagnostics:
    for diagnostic in expansion.diagnostics:
        print(diagnostic.code, diagnostic.message)

for record in expansion.records:
    print(record.vif.kind, record.value.value, record.value.unit)
```

When passed a full `FormatDataTelegram`, expansion checks that the compact frame's Format Signature matches the format frame's Format Signature. If expansion consumes all compact value bytes, it also reconstructs the recovered full application data and validates the compact frame's Full-Frame-CRC.

If you already matched the template yourself, you can pass descriptors directly:

```python
expansion = expand_compact_telegram(
    compact_result.telegram,
    format_result.telegram.descriptors,
)
```

Passing descriptors directly skips signature and CRC validation. This is useful for low-level tooling, but application code should usually pass the full `FormatDataTelegram`.

### Expand a compact frame from the CLI

```shell
python -m meterbus.cli.decode \
  --compact-template "$(xxd -p -c 999999 format-frame.blob)" \
  --indent 2 \
  "$(xxd -p -c 999999 compact-frame.blob)"
```

The output contains the normal compact-frame decode result plus a `compact_expansion` object:

```json
{
  "compact_expansion": {
    "records": [],
    "undecoded_data": "",
    "diagnostics": [],
    "recovered_application_data": ""
  }
}
```

If the Format Signature or Full-Frame-CRC does not match, the CLI still prints JSON but exits with code `1`.

## Common use cases

### Debug a single captured frame

```shell
python -m meterbus.cli.decode --mode lenient --indent 2 "$HEX"
```

Use this when you want to see every parsed field and any diagnostics.

### Extract readings for another system

```shell
python -m meterbus.cli.decode --mode lenient --view records "$HEX"
```

This produces a smaller JSON object with meter identity and decoded records.

### Decode many frames in Python

```python
from meterbus.api import decode
from meterbus.export import to_dict
from meterbus.model import DecodeMode

for raw in frames:
    result = decode(raw, mode=DecodeMode.LENIENT)
    payload = to_dict(result, view="records")
    store(payload)
```

Keep the diagnostics. Real-world meter data often contains manufacturer-specific data, filler, malformed tails, or unsupported records.

### Investigate unsupported data

Use full export and lenient mode:

```shell
python -m meterbus.cli.decode --mode lenient --view full --indent 2 "$HEX"
```

Look for `diagnostics`, `undecoded_data`, `UnknownRecord`, and VIF kinds such as `unknown_extension` or manufacturer-specific records.

## Notes

The v2 API is intentionally boring: decode first, inspect diagnostics, export with `to_dict()` or `to_json()`. Protocol coverage will continue to grow in small tested slices.

When behavior is not implemented, the preferred v2 behavior is to preserve raw bytes and emit diagnostics rather than guessing. This matters for M-Bus because many fields are tightly specified and some device data is manufacturer-specific.
