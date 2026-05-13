# Diagnostics and decode modes

pyMeterBus v2 is diagnostics-first. The decoder should not silently invent meaning for malformed, incomplete, unsupported, or manufacturer-specific data. It should return the best structured result it can and explain uncertainty through diagnostics.

Most application code should call `decode()` and inspect the returned `DecodeResult`:

```python
from meterbus import decode
from meterbus.model import DecodeMode

result = decode(raw, mode=DecodeMode.LENIENT)

if not result.ok:
    for diagnostic in result.diagnostics:
        print(diagnostic.severity, diagnostic.code, diagnostic.message)
```

## Severity levels

Diagnostics use severity levels to separate hard failures from recoverable uncertainty.

| Severity | Meaning | Typical application response |
| --- | --- | --- |
| `fatal` | The decoder cannot safely produce the requested structure in the selected mode. | Reject the frame, log the raw bytes, and inspect transport/framing. |
| `error` | Something is wrong, but lenient/compat decoding may still preserve partial data. | Keep raw bytes and diagnostics; use decoded data cautiously. |
| `warning` | Decode completed, but extra or unusual data was observed. | Usually safe to ingest if your application accepts partial/provisional data. |
| `info` | Non-problematic explanatory diagnostic. | Log only when debugging. |

For strict validation, treat any non-empty diagnostics as worth investigating. For production ingestion, a small number of known warnings may be acceptable if raw bytes are preserved.

## Decode modes

### `strict`

Use strict mode for tests, validation tools, and cases where you want malformed data rejected early.

Strict mode should fail on malformed frame structure, invalid checksums, invalid stop bytes, incompatible length fields, and record errors that make the result unsafe to treat as a clean decode.

```python
from meterbus import decode
from meterbus.model import DecodeMode

result = decode(raw, mode=DecodeMode.STRICT)
assert result.ok
```

### `lenient`

Use lenient mode for real-world meter collection where some meters may include manufacturer-specific records, filler bytes, malformed tails, unsupported extension data, or otherwise useful partial payloads.

Lenient mode aims to preserve decoded structure and raw undecoded data where possible. The presence of a decoded telegram does not mean every byte was fully understood. Always inspect diagnostics.

```python
result = decode(raw, mode=DecodeMode.LENIENT)
if result.telegram is not None:
    process_records(result.telegram.records)
```

### `compat`

Compat mode is compatibility-oriented lenient behavior. It exists to help ingestion workflows preserve data, not to recreate the v1 object model.

Do not assume compat mode will produce legacy classes, legacy import paths, or legacy parsed values. If you depend on exact v1 behavior, keep using the v1 line until you have v2 fixtures proving the behavior you need.

## Common diagnostics

Exact diagnostic codes may expand over time, but these categories are important for application behavior.

| Code/category | Common cause | Recommended response |
| --- | --- | --- |
| `empty_input` | No bytes were passed to the decoder. | Fix caller/transport code. This is not meter data. |
| `unsupported_input_type` | Caller passed a value that cannot be converted to bytes. | Pass `bytes`, `bytearray`, `memoryview`, or a list/tuple of byte values. |
| `invalid_start_byte` | Frame does not begin with a known M-Bus start byte. | Check frame boundary detection and transport buffering. |
| `length_mismatch` | Frame length fields disagree or do not match the supplied byte count. | Check whether the frame is truncated, concatenated, or over-read. |
| `truncated_frame` | Too few bytes are present for the frame type. | Treat as transport/framing failure. Preserve raw bytes for debugging. |
| `invalid_repeated_start_byte` | Long/control frame repeated start byte is not `0x68`. | Treat as malformed frame or bad frame boundary. |
| `invalid_stop_byte` | Frame does not end with expected `0x16`. | Check frame boundary, truncation, or corruption. |
| `checksum_mismatch` | Computed checksum differs from the frame checksum. | Reject in strict mode. In lenient mode, keep diagnostics and use data only if your application tolerates corruption risk. |
| unsupported CI/telegram | The frame is structurally valid but the application telegram type is not implemented. | Preserve raw frame and diagnostics. Add fixture coverage before implementing support. |
| unsupported or enhanced VIF | Record metadata uses a VIF/VIFE path that v2 does not yet model semantically. | Preserve the record and raw metadata; avoid guessing the unit or meaning. |
| unknown or malformed record | A record cannot be decoded completely. | In lenient/compat mode, preserve unknown record data and diagnostics for later analysis. |

## Practical ingestion guidance

For production ingestion, prefer this pattern:

1. Read exactly one complete frame from your transport.
2. Decode in `lenient` mode.
3. Store the raw frame bytes.
4. Store diagnostics with the decoded payload.
5. Process records only if `result.ok` is true or if your application explicitly accepts the diagnostic codes observed.

For test fixtures and protocol development, prefer strict mode first. Add lenient-mode expectations only when you are deliberately preserving partial data.

## When to add a fixture

Add a raw-frame fixture whenever you find one of these situations:

- a real meter produces a diagnostic you want to accept;
- a manufacturer-specific field needs to be preserved more clearly;
- a new VIF/VIFE entry is implemented;
- strict and lenient behavior differ in a way users may notice;
- v1 and v2 parse the same telegram differently.

A plausible decode is not enough. Prefer raw bytes plus expected structured output so future changes cannot silently alter behavior.
