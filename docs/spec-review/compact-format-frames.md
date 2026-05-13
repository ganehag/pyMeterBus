# Compact and format frame review

This note records the design reasoning and current implementation status for compact and format frames in the v2 decoder. It is intentionally engineering context, not user-facing usage documentation. For user-facing examples, see `docs/v2-usage.md`.

## Source scope

Reviewed from the protocol PDFs used during the v2 compliance pass:

- EN 13757-3:2018, especially Annex G for full, compact, and format M-Bus frames.
- MBDOC48, for older explanatory wording and examples.
- EN 13757-2:2018, for lower/link-layer framing constraints where applicable.

The working conclusion remains that compact/format frames are a separate application-layer variant and must be modeled explicitly.

## What compact/format frames are

A normal full M-Bus frame carries the data record descriptors and values together:

```text
DIF/VIF + value bytes
```

Compact/format support separates those concerns:

1. a format frame carries the record layout, and
2. one or more compact frames carry only values using that layout.

That means compact decoding is not a safe single-frame operation unless the caller supplies matching format/template context.

## Current implementation status

The v2 decoder now implements the safe subset of this model:

- recognizes full, compact, and format frame CI variants currently in scope;
- parses format frames into descriptor records;
- parses compact frames into a compact telegram with Format Signature, Full-Frame-CRC, and compact payload bytes;
- does not automatically expand compact frames from `decode()`;
- expands compact frames only through explicit caller-supplied descriptors or a `FormatDataTelegram`;
- validates the Format Signature when a `FormatDataTelegram` is supplied;
- reconstructs recovered application data during successful expansion;
- validates Full-Frame-CRC over the recovered application data;
- exposes compact expansion through the CLI with `--compact-template`.

This keeps template ownership caller-visible and avoids hidden global state.

## Key implementation boundary

Do not decode compact frames by guessing record boundaries from payload bytes. That would defeat the purpose of the format frame and create silent misdecodes.

The current implementation follows this boundary:

```python
decode(raw)
# Parses a format frame into a FormatDataTelegram.
# Parses a compact frame into a CompactDataTelegram.
# Does not expand compact records without a template.

expand_compact_telegram(compact_telegram, format_telegram)
# Checks Format Signature.
# Expands values according to format descriptors.
# Validates Full-Frame-CRC if expansion is complete.
```

Descriptor-only expansion is still available for low-level callers that have already matched template context themselves, but application code should normally pass the full `FormatDataTelegram`.

## High-confidence requirements and status

### 1. CI recognition

Status: implemented for the v2 compact/format scope.

Known compact and format CIs are modeled separately instead of being misclassified as variable-data or fixed-data telegrams.

### 2. Template dependency

Status: implemented.

A compact frame is preserved as compact data until a caller supplies format descriptors or a `FormatDataTelegram`. Expansion without explicit template state is not attempted.

### 3. CRC/signature handling

Status: implemented for explicit expansion with a `FormatDataTelegram`.

The Format Signature must match. If expansion consumes all compact value bytes, the recovered full application data is checked against the compact frame's Full-Frame-CRC.

### 4. Record layout reuse

Status: implemented.

Format frames produce descriptors. Compact expansion combines descriptor bytes with compact value bytes to create expanded `DataRecord` instances and recovered application data.

### 5. State management remains caller-owned

Status: implemented by omission.

There is no hidden global format cache. The caller supplies the template explicitly. A future caller-owned context object could still be added, but it should be explicit and testable.

## Test coverage

Current coverage includes:

- compact and format CI recognition;
- format frame descriptor parsing;
- compact frame parsing and payload preservation;
- explicit compact expansion from descriptors;
- signature mismatch rejection when using a `FormatDataTelegram`;
- Full-Frame-CRC mismatch diagnostics;
- compact CLI expansion with `--compact-template`;
- preservation of undecoded compact tails and truncated values.

## Remaining gaps

- Add real compact/format frame captures if available. Current compact expansion tests are synthetic and spec-shaped.
- Verify byte order of Format Signature and Full-Frame-CRC against real devices.
- Decide whether a caller-owned context object is useful enough to add.
- Document common compact-frame diagnostics in the user docs after real captures exist.
- Decide whether additional Annex G CI variants should be recognized as explicit unsupported telegrams.

## Current decision

Keep compact expansion explicit. Do not add hidden template caches. Do not auto-expand compact frames in `decode()`.

The safe public path is:

```python
format_result = decode(format_frame_bytes)
compact_result = decode(compact_frame_bytes)
expansion = expand_compact_telegram(compact_result.telegram, format_result.telegram)
```

The safe CLI path is:

```shell
pymeterbus-decode \
  --compact-template "$(xxd -p -c 999999 format-frame.blob)" \
  "$(xxd -p -c 999999 compact-frame.blob)"
```

## Additional PDF-backed compliance areas to investigate next

These are worth reviewing after the current v2 preview stabilizes:

- selection-for-readout DIF value and global readout request VIF handling;
- application reset subcodes and request telegrams, if v2 aims to encode/request as well as decode responses;
- fixed-data status and medium/unit edge cases beyond the examples already tested;
- manufacturer-specific VIF and DIF blocks where payload should be preserved rather than diagnosed;
- wireless-specific CI values that should be recognized but kept unsupported rather than silently ignored;
- link-layer ACK/error/control behavior from EN 13757-2 if v2 will support more than payload decoding.
