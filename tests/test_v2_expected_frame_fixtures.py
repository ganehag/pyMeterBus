from __future__ import annotations

import json
from pathlib import Path

import pytest

from meterbus.api import decode
from meterbus.export import to_dict
from tests.helpers.fixtures import fixture_root, iter_hex_fixtures


_EXPECTED_FRAME_ROOT = fixture_root() / "expected" / "frames"


def _load_expected(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


@pytest.mark.parametrize("fixture", iter_hex_fixtures("frames"), ids=lambda fixture: fixture.name)
def test_frame_fixture_matches_expected_export(fixture):
    expected_path = _EXPECTED_FRAME_ROOT / f"{fixture.name}.json"

    assert expected_path.exists(), f"missing expected fixture: {expected_path}"

    actual = to_dict(decode(fixture.data))
    expected = _load_expected(expected_path)

    assert actual == expected


def test_every_expected_frame_fixture_has_matching_hex_fixture():
    fixture_names = {fixture.name for fixture in iter_hex_fixtures("frames")}
    expected_names = {path.stem for path in _EXPECTED_FRAME_ROOT.glob("*.json")}

    assert expected_names == fixture_names
