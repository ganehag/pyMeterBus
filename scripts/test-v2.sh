#!/usr/bin/env bash
set -euo pipefail

python -m pytest \
  tests/test_v2_docs_usage.py \
  tests/test_v2_package_entrypoint.py \
  tests/test_v2_cli_decode.py \
  tests/test_v2_json_export.py \
  tests/test_v2_error_records.py \
  tests/test_v2_variable_length_values.py \
  tests/test_v2_date_time_values.py \
  tests/test_v2_vif_table.py \
  tests/test_v2_scaled_values.py \
  tests/test_v2_record_loop.py \
  tests/test_v2_record_decoder.py \
  tests/test_v2_value_decoder.py \
  tests/test_v2_vif_parser.py \
  tests/test_v2_dif_parser.py \
  tests/test_v2_variable_header_decoder.py \
  tests/test_v2_expected_frame_fixtures.py \
  tests/test_v2_dict_export.py \
  tests/test_v2_decode_api.py \
  tests/test_v2_frame_decoder.py \
  tests/test_v2_model.py \
  tests/test_fixture_loading.py
