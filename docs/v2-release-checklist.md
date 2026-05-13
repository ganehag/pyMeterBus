# pyMeterBus v2 release checklist

This checklist tracks what should be true before cutting a v2 preview release or merging v2 into the main release path.

The current v2 branch is useful, tested, documented, and intentionally dependency-free. It is a breaking rewrite focused on decoding complete M-Bus frame bytes into structured models, diagnostics, and stable exports.

## Current baseline

- [x] Structured `DecodeResult` API.
- [x] Frame decoder for ACK, short, control, and long frames.
- [x] Frame checksum validation and frame-level diagnostics.
- [x] Variable-data telegram header decoder for CI `0x72` and CI `0x76`.
- [x] Fixed-data telegram decoder.
- [x] DIF/DIFE parser.
- [x] Expanded base VIF/VIFE parser.
- [x] Fixed-length value decoder.
- [x] Semantic variable-length value decoder for clear text and BCD cases.
- [x] Single-record decoder.
- [x] Telegram record loop.
- [x] Record-level VIF scaling.
- [x] Date, time, and datetime interpretation for implemented formats.
- [x] Lenient and compat `UnknownRecord` preservation.
- [x] `to_dict()` export.
- [x] `to_json()` export.
- [x] Full, summary, and records export views.
- [x] `python -m meterbus.cli.decode` CLI.
- [x] Installed `pymeterbus-decode` entry point.
- [x] CLI compact-template expansion path.
- [x] Format-frame descriptor parsing.
- [x] Explicit compact-frame expansion using caller-supplied format descriptors.
- [x] Compact Format Signature validation.
- [x] Compact Full-Frame-CRC validation over recovered application data.
- [x] EN 13757 CRC helper.
- [x] v2 usage documentation.
- [x] v2-focused README.
- [x] Focused v2 test script.
- [x] Focused v2 GitHub Actions workflow.
- [x] Dependency-free default install.
- [x] No runtime optional dependency groups in package metadata.
- [x] Lightweight root package exports for the v2 decode API.
- [x] Explicit v2 prerelease version: `2.0.0a1`.

## Protocol coverage gaps

- [ ] Add more manufacturer-specific or real-world fixture coverage.
- [ ] Expand extension VIF table coverage where the standard gives exact semantics.
- [ ] Decide how to represent unsupported/enhanced VIFs long term.
- [ ] Add more date/time edge cases from real meters.
- [ ] Add more variable-length value examples from real devices.
- [ ] Validate DIF/DIFE storage, tariff, and subunit interpretation against more real telegrams.
- [ ] Add real compact/format frame captures if available; current coverage is synthetic and spec-shaped.
- [ ] Decide whether wireless-specific CI values should be modeled explicitly or preserved as unsupported telegrams.

## Compatibility decisions

- [x] Treat v2 as a breaking rewrite rather than a drop-in legacy-compatible release.
- [x] Make root package exports v2-focused: `decode`, `decode_one`, and `decode_one_frame`.
- [x] Do not guarantee legacy classes or serial helpers from `import meterbus`.
- [x] Keep v2 decode/export/CLI usable from a dependency-free default install.
- [x] Keep serial transport outside the core package.
- [x] Remove stale legacy optional dependency metadata.
- [x] Remove stale serial console entry points.
- [x] Remove legacy pre-v2 implementation modules and tests from the v2 branch.
- [ ] Decide whether `meterbus.load()` should remain unavailable, be reintroduced as a v2 compatibility wrapper, or live only in a separate legacy branch.
- [ ] Decide whether v2 models are public stable API or still preview API.
- [ ] Decide whether root package exports should also expose `to_dict` and `to_json`.
- [ ] Decide strict/lenient/compat semantics for all known non-fatal frame issues.
- [ ] Document any intentional differences from legacy parsed values that users are likely to notice.

## Packaging and release

- [x] Choose a preview version scheme: `2.0.0a1`.
- [x] Set `requires-python` to the tested support window.
- [x] Keep package runtime dependencies empty.
- [x] Keep only the supported `pymeterbus-decode` console script.
- [x] Add release notes for the v2 preview.
- [ ] Confirm package classifiers match the tested Python versions before publishing.
- [ ] Verify editable install and wheel install both expose `pymeterbus-decode`.
- [ ] Build package artifacts from a clean checkout.
- [ ] Install the built wheel in a fresh virtual environment.
- [ ] Run `pymeterbus-decode "E5"` from the installed wheel.

## CI and quality gates

- [ ] Keep `bash scripts/test-v2.sh` passing locally.
- [ ] Keep `.github/workflows/test-v2.yml` passing for Python 3.11, 3.12, and 3.13.
- [ ] Keep build smoke workflow passing.
- [ ] Decide whether v2 CI should run on `master` after merge.
- [ ] Add coverage thresholds only after the v2 API surface stabilizes.

## Documentation

- [x] README is v2-focused and links to detailed docs.
- [x] Document the v2 root API contract and dependency-free default install.
- [x] Document byte-oriented transport ownership.
- [x] Document CLI command and exit codes.
- [x] Document compact/format expansion from Python and CLI.
- [x] Document full, summary, and records export views.
- [ ] Expand `docs/v2-usage.md` with real-world examples as fixtures grow.
- [ ] Document common diagnostics and what users should do with them.
- [ ] Document strict, lenient, and compat mode differences with examples.
- [ ] Revisit older docs such as `PacketFormat.md` and `WirelessMBusUSB.md` for v2 relevance.

## Merge strategy

- [ ] Prefer keeping `v2` as the integration branch until the preview API is intentionally frozen.
- [ ] Merge `v2` into `master` only when CI, docs, and packaging choices are clear.
- [ ] If releasing before merging to `master`, publish as a clearly marked prerelease from `v2`.
- [ ] Avoid squashing the v2 branch history unless the project explicitly wants a compact public history.

## Final preview release checks

- [ ] `git switch v2 && git pull origin v2`.
- [ ] `bash scripts/test-v2.sh`.
- [ ] `bash scripts/smoke-build.sh`.
- [ ] Build package artifacts from a clean checkout.
- [ ] Install the built wheel in a fresh virtual environment.
- [ ] Run `pymeterbus-decode "E5"` from the installed wheel.
- [ ] Smoke-test at least one long variable-data telegram fixture.
- [ ] Smoke-test compact expansion with the synthetic template fixture or a real capture if available.
- [ ] Review README, `docs/v2-usage.md`, and release notes together.
