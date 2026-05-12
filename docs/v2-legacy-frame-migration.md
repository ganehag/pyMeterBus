# v2 legacy frame fixture migration

The legacy repository contains a valuable frame corpus under `tests/test-frames`, `tests/error-frames`, and `tests/unsupported-frames`.

These files are currently not referenced by the focused v2 test suite. They should not be deleted casually. They should be migrated deliberately into canonical v2 fixtures, preserved as explicit error cases, or documented as unsupported with a reason.

## Migration rules

- Every legacy frame file must be classified.
- Migrated frames must live under `tests/fixtures/frames/` with matching expected exports under `tests/fixtures/expected/frames/` where full-frame export is supported.
- Unsupported frames must stay listed with a reason.
- Do not bulk-promote old frames without checking whether the old expectation depends on legacy behavior.
- Prefer small migration slices: valid frames first, then explicit error frames, then unsupported/wireless/fixed-data cases.

## Current v2 canonical frame fixtures

These already participate in the v2 expected-frame export tests.

| Path | Status | Notes |
| --- | --- | --- |
| `tests/fixtures/frames/ack.hex` | migrated | ACK frame fixture. |
| `tests/fixtures/frames/control.hex` | migrated | Control frame fixture. |
| `tests/fixtures/frames/invalid_start.hex` | migrated | Invalid frame-start fixture. |
| `tests/fixtures/frames/long_basic.hex` | migrated | Long variable-data fixture. |
| `tests/fixtures/frames/short.hex` | migrated | Short frame fixture. |

## Legacy test frames pending review

These are the main legacy corpus. Each should be decoded or triaged one by one.

| Path | Status | Notes |
| --- | --- | --- |
| `tests/test-frames/abb_f95.blob` | pending_review | Legacy corpus frame. |
| `tests/test-frames/abb_xxx.blob` | pending_review | Legacy corpus frame. |
| `tests/test-frames/abb_xxx.hex` | pending_review | Legacy hex frame; likely easy first migration candidate. |
| `tests/test-frames/abb_xxx.xml` | pending_review | Legacy expected/sidecar data; inspect before migration. |
| `tests/test-frames/allmess_cf50.blob` | pending_review | Legacy corpus frame. |
| `tests/test-frames/amt_meter.blob` | pending_review | Legacy corpus frame. |
| `tests/test-frames/amt_meter.hex` | pending_review | Legacy hex frame; likely easy first migration candidate. |
| `tests/test-frames/EDC.blob` | pending_review | Legacy corpus frame. |
| `tests/test-frames/electricity-meter-1.blob` | pending_review | Legacy corpus frame. |
| `tests/test-frames/electricity-meter-2.blob` | pending_review | Legacy corpus frame. |
| `tests/test-frames/els_falcon.blob` | pending_review | Legacy corpus frame. |
| `tests/test-frames/Elster-F2.blob` | pending_review | Legacy corpus frame. |
| `tests/test-frames/els_tmpa_telegramm1.blob` | pending_review | Legacy corpus frame. |
| `tests/test-frames/elv_temp_humid.blob` | pending_review | Legacy corpus frame. |
| `tests/test-frames/emh_diz.blob` | pending_review | Legacy corpus frame. |
| `tests/test-frames/frame1.blob` | pending_review | Legacy corpus frame. |
| `tests/test-frames/frame2.blob` | pending_review | Legacy corpus frame. |
| `tests/test-frames/gmc_emmod206.blob` | pending_review | Legacy corpus frame. |
| `tests/test-frames/invalid_length2.blob` | pending_review | Legacy error-ish frame; may become explicit v2 diagnostic fixture. |
| `tests/test-frames/invalid_length.blob` | pending_review | Legacy error-ish frame; may become explicit v2 diagnostic fixture. |
| `tests/test-frames/kamstrup_multical_601.blob` | pending_review | Legacy corpus frame. |
| `tests/test-frames/manual_frame2.blob` | pending_review | Manual legacy frame. |
| `tests/test-frames/manual_frame3.blob` | pending_review | Manual legacy frame. |
| `tests/test-frames/manual_frame7.blob` | pending_review | Manual legacy frame. |
| `tests/test-frames/nzr_dhz_5_63.blob` | pending_review | Legacy corpus frame. |
| `tests/test-frames/premature_end_of_data1.blob` | pending_review | Legacy error-ish frame; may become explicit v2 diagnostic fixture. |
| `tests/test-frames/premature_end_of_data2.blob` | pending_review | Legacy error-ish frame; may become explicit v2 diagnostic fixture. |
| `tests/test-frames/premature_end_of_dif1.blob` | pending_review | Legacy error-ish frame; may become explicit v2 diagnostic fixture. |
| `tests/test-frames/premature_end_of_dif2.blob` | pending_review | Legacy error-ish frame; may become explicit v2 diagnostic fixture. |
| `tests/test-frames/premature_end_of_var_vif1.blob` | pending_review | Legacy error-ish frame; may become explicit v2 diagnostic fixture. |
| `tests/test-frames/premature_end_of_vif1.blob` | pending_review | Legacy error-ish frame; may become explicit v2 diagnostic fixture. |
| `tests/test-frames/rel_padpuls2.blob` | pending_review | Legacy corpus frame. |
| `tests/test-frames/rel_padpuls3.blob` | pending_review | Legacy corpus frame. |
| `tests/test-frames/siemens_rvd_235.hex` | pending_review | Legacy hex frame; likely easy first migration candidate. |
| `tests/test-frames/svm_f22_telegram1.blob` | pending_review | Legacy corpus frame. |
| `tests/test-frames/too_long_var_vif.blob` | pending_review | Legacy error-ish frame; may become explicit v2 diagnostic fixture. |
| `tests/test-frames/too_many_dife.blob` | pending_review | Legacy error-ish frame; may become explicit v2 diagnostic fixture. |
| `tests/test-frames/too_many_vife.blob` | pending_review | Legacy error-ish frame; may become explicit v2 diagnostic fixture. |
| `tests/test-frames/too_short_header.blob` | pending_review | Legacy error-ish frame; may become explicit v2 diagnostic fixture. |
| `tests/test-frames/WEP-indoor.blob` | pending_review | Legacy corpus frame. |
| `tests/test-frames/wmbus-converted.blob` | pending_review | Wireless/converted frame candidate; inspect before promoting. |

## Legacy error frames pending review

These should become explicit v2 diagnostic/error fixtures if their behavior is still relevant.

| Path | Status | Notes |
| --- | --- | --- |
| `tests/error-frames/application_busy.blob` | legacy_error_case | Review expected v2 diagnostic behavior. |
| `tests/error-frames/buffer_too_long.blob` | legacy_error_case | Review expected v2 diagnostic behavior. |
| `tests/error-frames/error.blob` | legacy_error_case | Review expected v2 diagnostic behavior. |
| `tests/error-frames/premature_end_of_record.blob` | legacy_error_case | Review expected v2 diagnostic behavior. |
| `tests/error-frames/too_many_difes.blob` | legacy_error_case | Review expected v2 diagnostic behavior. |
| `tests/error-frames/too_many_readouts.blob` | legacy_error_case | Review expected v2 diagnostic behavior. |
| `tests/error-frames/too_many_records.blob` | legacy_error_case | Review expected v2 diagnostic behavior. |
| `tests/error-frames/too_many_vifes.blob` | legacy_error_case | Review expected v2 diagnostic behavior. |
| `tests/error-frames/unimplemented_ci.blob` | legacy_error_case | Review expected v2 diagnostic behavior. |
| `tests/error-frames/unspecified_error.blob` | legacy_error_case | Review expected v2 diagnostic behavior. |

## Legacy unsupported frames pending review

These are already marked unsupported in the legacy layout. Keep that signal, but re-check each one against v2 goals.

| Path | Status | Notes |
| --- | --- | --- |
| `tests/unsupported-frames/gabriel-wmbus.blob` | unsupported_pending_review | Wireless/unsupported candidate; inspect before promoting. |
| `tests/unsupported-frames/gabriel-wmbus.blob.2` | unsupported_pending_review | Wireless/unsupported candidate; inspect before promoting. |
| `tests/unsupported-frames/manual_frame1.blob` | unsupported_pending_review | Manual unsupported frame. |
| `tests/unsupported-frames/manual_frame4.blob` | unsupported_pending_review | Manual unsupported frame. |
| `tests/unsupported-frames/manual_frame5.blob` | unsupported_pending_review | Manual unsupported frame. |
| `tests/unsupported-frames/manual_frame6.blob` | unsupported_pending_review | Manual unsupported frame. |
| `tests/unsupported-frames/rvd235.blob` | unsupported_pending_review | Unsupported legacy frame. |
| `tests/unsupported-frames/siemens_rvd235.blob` | unsupported_pending_review | Unsupported legacy frame. |
| `tests/unsupported-frames/svm_f22_telegram2.blob` | unsupported_pending_review | Unsupported legacy frame. |

## First migration candidates

Start with the legacy `.hex` files because they should be easiest to normalize into v2 fixture files:

- `tests/test-frames/abb_xxx.hex`
- `tests/test-frames/amt_meter.hex`
- `tests/test-frames/siemens_rvd_235.hex`

Then inspect `.blob` files and convert only those that are unambiguous raw byte frames.
