# LLM agent workflow for pyMeterBus 2.0

This document defines how coding agents should work on the 2.0 rewrite.

The important rule is: do not ask an agent to rewrite pyMeterBus in one step. Give it small tasks with stable acceptance criteria.

## Universal constraints

Every agent task should include these constraints:

```text
Do not broaden the task.
Do not redesign public models unless this task explicitly updates the model spec.
Do not change fixtures unless this task is explicitly about fixtures.
Do not add transport code to core modules.
Do not import pySerial from model or codec modules.
Do not discard unknown bytes.
Do not use float for scaled protocol values in the core model.
Do not silently swallow decoding errors; return diagnostics.
Do not configure global logging from library code.
```

## Task 0: Design scaffold

Goal: add documentation and fixture structure only.

Deliverables:

```text
docs/architecture.md
docs/data-model.md
docs/agent-workflow.md
tests/fixtures/README.md
tests/fixtures/frames/*.hex
tests/fixtures/telegrams/*.hex
```

Acceptance:

```text
- no production code changed;
- docs describe architecture and model boundaries;
- fixture directories exist;
- seed frames are copied from current tests.
```

## Task 1: Fixture extraction

Goal: convert existing tests into stable fixture files.

Prompt:

```text
Extract raw frames and expected outputs from the current tests into fixture files.
Do not change production code.
Do not invent new behavior.
Add a fixture loader for tests.
```

Acceptance:

```text
- current tests still pass;
- ACK, short, control, long, invalid, and variable-data examples exist as fixtures;
- expected JSON captures current behavior where already tested.
```

## Task 2: Model layer

Goal: implement model dataclasses and enums.

Prompt:

```text
Implement meterbus.model according to docs/data-model.md.
Do not implement decoding yet.
Do not import transport, serial, CLI, or export modules.
```

Acceptance:

```text
- type checker passes;
- model tests pass;
- model modules have no pySerial dependency;
- model objects preserve raw bytes where specified.
```

## Task 3: Frame decoder

Goal: implement ACK, short, control, and long frame decoding.

Prompt:

```text
Implement FrameDecoder for ACK, short, control, and long frames.
Use direct byte inspection.
Preserve raw bytes.
Return diagnostics.
Support strict and lenient mode.
```

Acceptance:

```text
- frame fixture tests pass;
- checksum mismatch behavior is tested;
- truncated frame behavior is tested;
- arbitrary bytes do not crash lenient mode.
```

## Task 4: Variable data header parser

Goal: parse variable-data long-frame headers.

Prompt:

```text
Implement parsing of variable data header from long-frame application bytes.
Preserve raw header bytes.
Return diagnostics for unsupported or short data.
```

Acceptance:

```text
- long frame fixture parses header;
- identification number, manufacturer, version, medium, access number, status, and signature are represented where available.
```

## Task 5: DIB parser

Goal: parse Data Information Blocks.

Prompt:

```text
Implement Data Information Block parsing for behavior currently covered by fixtures.
Preserve extension bytes.
Represent unknown or unsupported DIB values with diagnostics in lenient mode.
```

Acceptance:

```text
- function tests pass;
- storage number behavior matches current tests;
- more_records_follow behavior matches current tests.
```

## Task 6: VIB parser

Goal: parse Value Information Blocks.

Prompt:

```text
Implement Value Information Block parsing for behavior currently covered by fixtures.
Use Decimal for multipliers and scaled values.
Preserve custom VIF bytes.
```

Acceptance:

```text
- %RH records pass;
- temperature records pass;
- seconds duration record passes;
- fabrication number record passes;
- software version record passes;
- energy Wh accumulation records pass.
```

## Task 7: Record decoder

Goal: decode variable data records.

Prompt:

```text
Implement variable data record decoding using the DIB and VIB parsers.
Return DataRecord or UnknownRecord.
Never discard raw record bytes.
```

Acceptance:

```text
- all extracted variable-data record fixtures pass;
- string value fixtures pass;
- binary-like hex string fixtures pass;
- Decimal path avoids binary float artifacts.
```

## Task 8: Export layer

Goal: implement dict and JSON export.

Prompt:

```text
Implement to_dict and to_json for the 2.0 model.
Implement a v1 compatibility export mode that matches existing test expectations.
```

Acceptance:

```text
- current expected record JSON tests pass in compatibility mode;
- 2.0 export includes raw bytes and diagnostics;
- export code does not mutate model objects.
```

## Task 9: Compatibility wrapper

Goal: implement `meterbus.load(data)` on top of the new decoder.

Prompt:

```text
Implement meterbus.load(data) using the new decoder.
Preserve old accepted input types.
Preserve old exception behavior where practical.
```

Acceptance:

```text
- old frame type tests pass or are intentionally migrated;
- deprecation behavior is tested;
- old input forms still work in compatibility mode.
```

## Task 10: Transport layer

Goal: rebuild serial/RFC2217/session behavior on top of the codec.

Prompt:

```text
Implement transport/session code on top of encoder and decoder.
Do not duplicate frame parsing logic.
Do not configure global logging.
```

Acceptance:

```text
- request frame generation matches existing behavior;
- receive behavior is covered with a fake transport;
- core modules still have no pySerial import.
```

## Review rule

Each task should be reviewed as a small pull request or commit. If an agent produces broad rewrites, revert the task and rerun it with narrower instructions.
