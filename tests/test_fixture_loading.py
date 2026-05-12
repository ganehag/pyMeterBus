from pathlib import Path

import pytest

from tests.helpers.fixtures import (
    HexFixture,
    fixture_root,
    iter_hex_fixtures,
    load_hex_fixture,
    parse_hex_fixture_text,
)


def test_fixture_root_exists():
    root = fixture_root()

    assert root.exists()
    assert root.name == "fixtures"


def test_parse_hex_fixture_text_accepts_whitespace_and_comments():
    data = parse_hex_fixture_text("""
        E5
        # Short frame follows
        10 08 0B 13 16
    """)

    assert data == b"\xE5\x10\x08\x0B\x13\x16"


def test_parse_hex_fixture_text_rejects_malformed_tokens():
    with pytest.raises(ValueError, match="invalid hex byte token"):
        parse_hex_fixture_text("E5 100")

    with pytest.raises(ValueError, match="invalid hex byte token"):
        parse_hex_fixture_text("E5 GG")


def test_load_hex_fixture_returns_named_fixture():
    fixture = load_hex_fixture("frames/ack.hex")

    assert isinstance(fixture, HexFixture)
    assert fixture.name == "ack"
    assert fixture.path == fixture_root() / Path("frames/ack.hex")
    assert fixture.data == b"\xE5"
    assert fixture.hex == "E5"


def test_iter_hex_fixtures_loads_frame_fixtures_in_name_order():
    fixtures = iter_hex_fixtures("frames")
    names = [fixture.name for fixture in fixtures]

    assert names == sorted(names)
    assert names == [
        "ack",
        "control",
        "invalid_start",
        "long_basic",
        "short",
    ]
    assert all(fixture.data for fixture in fixtures)


def test_iter_hex_fixtures_loads_telegram_fixtures():
    fixtures = iter_hex_fixtures("telegrams")
    names = [fixture.name for fixture in fixtures]

    assert names == [
        "variable_data_humidity_temperature",
        "variable_data_strings",
    ]
    assert all(fixture.data.startswith(b"\x68") for fixture in fixtures)
