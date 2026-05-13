# Compact and format frame review

This note is intentionally a design/review checkpoint, not an implementation.
Compact and format frames affect wireless M-Bus application decoding and should not be bolted onto the existing long-frame variable/fixed data decoder without a clean model.

## Source scope

Reviewed from the uploaded protocol PDFs already used during the v2 compliance pass:

- EN 13757-3:2018, especially the annex material describing full, compact, and format M-Bus frames.
- MBDOC48, for older explanatory wording and examples.
- EN 13757-2:2018, for lower/link-layer framing constraints where applicable.

The working conclusion is that compact/format frames are a separate application-layer variant, mainly relevant to wireless transmission, and should be modeled explicitly.

## What compact/format frames are

The current v2 decoder understands:

- frame envelope parsing,
- variable data telegrams using CI 72h/76h,
- fixed data telegrams using CI 73h/77h.

Compact/format support is different. It involves a relationship between at least two telegrams:

1. a format frame that describes the record layout, and
2. one or more compact frames that carry values using that prior layout.

That means compact decoding is not a pure stateless single-frame operation unless the caller supplies the format/template context.

## Implementation boundary

Do not decode compact frames by guessing record boundaries from payload bytes. That would defeat the point of the format frame and create silent misdecodes.

A safe implementation should introduce explicit types similar to:

```python
FormatDataTelegram
CompactDataTelegram
CompactFormatTemplate
```

The decoder should probably support two modes:

```python
decode(raw)
# Parses a format frame into a template-capable telegram.
# Parses a compact frame as a compact telegram but does not expand records without a template.

decode_compact(raw, template=template)
# Expands compact values using an explicit format template.
```

The exact public API should be decided before code is written.

## High-confidence requirements

### 1. CI recognition

Add tests first for recognizing the compact/format CI values from EN 13757-3 Annex G.

Expected behavior before full decode:

- known format frame CI returns a structured unsupported-or-partial telegram, not a generic long-frame-with-no-telegram result;
- known compact frame CI returns a structured unsupported-or-partial telegram, not a guessed variable-data telegram;
- unsupported compact expansion without a template should be explicit.

### 2. Template dependency

Compact frame expansion must require the corresponding format/template information.

Required behavior:

- no template: preserve payload and emit a clear diagnostic or unsupported feature result;
- wrong template: reject or diagnose; do not silently decode;
- matching template: expand records according to the format frame.

### 3. CRC/signature handling

The annex examples include CRC/signature behavior. Before decoding compact payloads, decide where this belongs:

- frame-level diagnostics,
- telegram-level diagnostics,
- template validation,
- or an unsupported marker.

Do not silently ignore CRC/signature bytes if the spec says they validate layout or compact-frame content.

### 4. Record layout reuse

A format frame should be parsed into record descriptors, not record values. The compact frame then supplies values for those descriptors.

This suggests separating:

- `DataRecord`: fully decoded record with DIF/VIF/value,
- `DataRecordDescriptor`: DIF/VIF metadata without value,
- compact value stream parsing against descriptors.

### 5. State management should remain caller-owned

The library should not hide a global cache of format frames. A hidden cache will be hard to reason about and hard to test. Prefer passing templates explicitly, or expose a small caller-owned context object.

Possible API:

```python
context = MeterBusDecodeContext()
context.add_format(decode(format_frame).telegram)
result = context.decode(compact_frame)
```

But a stateless `decode_compact(raw, template=...)` may be better for v2.

## Test plan

Start with tests that do not require full compact expansion:

1. Recognize a format frame CI.
2. Recognize a compact frame CI.
3. Return a clear diagnostic for compact frame without template.
4. Preserve raw compact payload.
5. Ensure compact/format CIs are not misclassified as variable-data CI 72h/76h or fixed-data CI 73h/77h.

Then add fixture-based tests from the PDFs:

6. Parse format frame into descriptors.
7. Expand one compact frame using the format descriptor.
8. Validate the example CRC/signature behavior if the example includes enough information.
9. Reject compact expansion with a mismatched template.
10. Round-trip full export/dict output for descriptor and expanded forms.

## Open questions before implementation

- Which exact CI values from Annex G should be supported first?
- Are compact/format frames in scope for wired M-Bus, wireless M-Bus only, or both in this project?
- Should the core `decode()` ever expand compact frames automatically?
- Where should compact-frame template identifiers live in the model?
- How should the CLI expose template-dependent decoding?

## Recommended branch sequence

1. `v2-compact-format-ci-recognition`
   - Add model shells and CI recognition only.
   - Preserve raw payload.
   - Add unsupported/template-required diagnostics.

2. `v2-format-frame-descriptors`
   - Decode format frames into descriptors.
   - No compact expansion yet.

3. `v2-compact-frame-expansion`
   - Add explicit template-based compact value expansion.

4. `v2-compact-format-cli`
   - Add CLI options for supplying a format/template frame.

## Additional PDF-backed compliance areas to investigate next

These are worth reviewing after compact/format framing is scoped:

- selection-for-readout DIF value and global readout request VIF handling;
- application reset subcodes and request telegrams, if v2 aims to encode/request as well as decode responses;
- fixed-data status and medium/unit edge cases beyond the examples already tested;
- manufacturer-specific VIF and DIF blocks where payload should be preserved rather than diagnosed;
- wireless-specific CI values that should be recognized but kept unsupported rather than silently ignored;
- link-layer ACK/error/control behavior from EN 13757-2 if v2 will support more than payload decoding.

## Current decision

Do not implement compact/format frame expansion until the project has at least one real fixture or PDF example encoded as a test. The first code branch should be CI recognition and safe preservation only.