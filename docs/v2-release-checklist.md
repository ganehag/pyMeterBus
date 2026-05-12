# pyMeterBus v2 release checklist

This checklist tracks what should be true before cutting a v2 preview or merging the v2 work into the main release path.

The current v2 branch is useful, tested, and documented enough for preview use. It is not yet a complete protocol replacement for the legacy API.

## Current baseline

- [x] Structured `DecodeResult` API.
- [x] Frame decoder for ACK, short, control, and long frames.
- [x] Variable-data telegram header decoder for CI `0x72`.
- [x] DIF/DIFE parser.
- [x] Expanded base VIF/VIFE parser.
- [x] Fixed-length value decoder.
- [x] Semantic variable-length value decoder for clear ASCII and BCD cases.
- [x] Single-record decoder.
- [x] Telegram record loop.
- [x] Record-level VIF scaling.
- [x] Date and datetime interpretation.
- [x] Lenient and compat `UnknownRecord` preservation.
- [x] `to_dict()` export.
- [x] `to_json()` export.
- [x] `python -m meterbus.cli.decode` CLI.
- [x] Installed `pymeterbus-decode` entry point.
- [x] v2 usage documentation.
- [x] Focused v2 test script.
- [x] Focused v2 GitHub Actions workflow.

## Protocol coverage gaps

- [ ] Confirm fixed-data telegram handling strategy.
- [ ] Expand extension VIF tables beyond the current first-extension basics.
- [ ] Add more manufacturer-specific or real-world fixture coverage.
- [ ] Decide how to represent unsupported/enhanced VIFs long term.
- [ ] Add more date/time edge cases from real meters.
- [ ] Add more variable-length value examples from real devices.
- [ ] Validate DIF/DIFE storage, tariff, and subunit interpretation against real telegrams.

## Compatibility decisions

- [ ] Decide whether v2 remains a parallel API or becomes the default decode path.
- [ ] Decide whether `meterbus.load()` should eventually wrap v2 or remain legacy-only.
- [ ] Decide whether v2 models are public stable API or still preview API.
- [ ] Decide whether root package exports should expose `decode`, `to_dict`, and `to_json`.
- [ ] Decide strict/lenient/compat semantics for all known non-fatal frame issues.
- [ ] Document any intentional differences from legacy parsed values.

## Packaging and release

- [ ] Choose a preview version scheme, for example `2.0.0a1`, `2.0.0b1`, or `1.x` with v2 preview APIs.
- [ ] Update package classifiers if Python support has changed.
- [ ] Confirm `requires-python` matches the tested support window.
- [ ] Confirm optional dependencies are not needed for the v2 decoder path.
- [ ] Verify editable install and wheel install both expose `pymeterbus-decode`.
- [ ] Add changelog or release notes for the v2 preview.

## CI and quality gates

- [ ] Keep `bash scripts/test-v2.sh` passing locally.
- [ ] Keep `.github/workflows/test-v2.yml` passing for Python 3.11, 3.12, and 3.13.
- [ ] Decide whether the full legacy suite must pass before v2 preview releases.
- [ ] Decide whether v2 CI should run on `master` after merge.
- [ ] Add coverage thresholds only after the v2 API surface stabilizes.

## Documentation

- [ ] Keep README v2 section concise and link to detailed docs.
- [ ] Expand `docs/v2-usage.md` with real-world examples as fixtures grow.
- [ ] Document common diagnostics and what users should do with them.
- [ ] Document strict, lenient, and compat mode differences with examples.
- [ ] Document the CLI command and exit codes in release notes.

## Merge strategy

- [ ] Prefer keeping `v2` as the integration branch until the preview API is intentionally frozen.
- [ ] Merge `v2` into `master` only when CI, docs, and packaging choices are clear.
- [ ] If releasing before merging to `master`, publish as a clearly marked prerelease from `v2`.
- [ ] Avoid squashing the v2 branch history unless the project explicitly wants a compact public history.

## Final preview release checks

- [ ] `git switch v2 && git pull origin v2`.
- [ ] `bash scripts/test-v2.sh`.
- [ ] Build package artifacts from a clean checkout.
- [ ] Install the built wheel in a fresh virtual environment.
- [ ] Run `pymeterbus-decode "E5"` from the installed wheel.
- [ ] Smoke-test at least one long variable-data telegram fixture.
- [ ] Review README, `docs/v2-usage.md`, and changelog/release notes together.
