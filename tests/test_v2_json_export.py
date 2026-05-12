from __future__ import annotations

import json

from meterbus.api import decode
from meterbus.export import to_dict, to_json
from tests.helpers.fixtures import load_hex_fixture


def test_to_json_exports_compact_json_string():
    result = decode(load_hex_fixture("frames/ack.hex").data)

    payload = to_json(result)

    assert isinstance(payload, str)
    assert "\n" not in payload
    assert json.loads(payload) == to_dict(result)


def test_to_json_exports_pretty_json_string_with_indent():
    result = decode(load_hex_fixture("frames/ack.hex").data)

    payload = to_json(result, indent=2)

    assert isinstance(payload, str)
    assert "\n" in payload
    assert "  \"diagnostics\"" in payload
    assert json.loads(payload) == to_dict(result)


def test_to_json_uses_stable_key_order():
    value = {"b": 2, "a": 1}

    assert to_json(value) == '{"a":1,"b":2}'


def test_to_json_exports_decoded_long_frame_result():
    result = decode(load_hex_fixture("frames/long_basic.hex").data)

    payload = json.loads(to_json(result))

    assert payload["ok"] is True
    assert payload["telegram"]["application_kind"] == "variable_data"
    assert len(payload["telegram"]["records"]) == 3
    assert payload["telegram"]["records"][0]["value"]["value"] == "64000449"
