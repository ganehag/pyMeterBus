# pyMeterBus fixture corpus

This directory is the seed for the pyMeterBus 2.0 golden fixture corpus.

Fixtures should describe protocol behavior independently from the old implementation. They should be readable by both Python tests and future non-Python implementations.

## Layout

```text
tests/fixtures/
  frames/
    ack.hex
    short.hex
    control.hex
    long_basic.hex
    invalid_start.hex

  telegrams/
    variable_data_humidity_temperature.hex
    variable_data_strings.hex

  expected/
    *.json
```

## Rules

1. Store raw telegram/frame bytes as uppercase hex with spaces allowed.
2. Expected output should be JSON and should not depend on Python object identities.
3. Fixtures should preserve raw bytes, diagnostics, and unknown fields where relevant.
4. Do not overwrite fixtures casually. If behavior changes, explain why in the commit message.
5. Future Zig/WASM implementations should be able to use the same fixtures.

## Seed source

The initial fixtures are copied from the existing test suite:

- `tests/test_frametype.py`
- `tests/test_variable_data_record.py`

A later task should extract expected JSON outputs from existing tests into `tests/fixtures/expected/`.
