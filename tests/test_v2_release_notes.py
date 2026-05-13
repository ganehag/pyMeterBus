from __future__ import annotations

from pathlib import Path

import meterbus


_PROJECT_ROOT = Path(__file__).resolve().parents[1]
_RELEASE_VERSION = meterbus.__version__
_RELEASE_NOTES = _PROJECT_ROOT / "docs" / "releases" / f"{_RELEASE_VERSION}.md"


def test_v2_release_notes_exist_and_identify_prerelease():
    notes = _RELEASE_NOTES.read_text()

    assert f"# pyMeterBus {_RELEASE_VERSION} release notes" in notes
    assert "v2 prerelease" in notes
    assert "breaking" in notes.lower()
    assert "dependency-free" in notes


def test_v2_release_notes_document_public_api_and_cli():
    notes = _RELEASE_NOTES.read_text()

    assert "from meterbus import decode" in notes
    assert "from meterbus.api import decode" in notes
    assert "from meterbus.export import to_dict, to_json" in notes
    assert "from meterbus.model import DecodeMode" in notes
    assert "pymeterbus-decode" in notes
    assert "python -m meterbus.cli.decode" in notes


def test_v2_release_notes_document_packaging_and_python_support():
    notes = _RELEASE_NOTES.read_text()

    assert f"pymeterbus=={_RELEASE_VERSION}" in notes
    assert "Python 3.11" in notes
    assert "Python 3.12" in notes
    assert "Python 3.13" in notes
    assert "default install is intentionally dependency-free" in notes
    assert "Serial transport is caller-owned" in notes


def test_v2_release_notes_document_coverage_and_gaps():
    notes = _RELEASE_NOTES.read_text()

    assert "Implemented decoder coverage" in notes
    assert "Known gaps" in notes
    assert "Variable-data telegram header decoding" in notes
    assert "Fixed-data telegram decoding" in notes
    assert "v2 model stability is still preview-level" in notes


def test_changelog_points_to_current_v2_release_notes():
    changelog = (_PROJECT_ROOT / "CHANGELOG.md").read_text()

    assert f"## {_RELEASE_VERSION}" in changelog
    assert f"docs/releases/{_RELEASE_VERSION}.md" in changelog
