from __future__ import annotations

from pathlib import Path


_PROJECT_ROOT = Path(__file__).resolve().parents[1]
_RELEASE_NOTES = _PROJECT_ROOT / "docs" / "releases" / "2.0.0a1.md"


def test_v2_release_notes_exist_and_identify_prerelease():
    notes = _RELEASE_NOTES.read_text()

    assert "# pyMeterBus 2.0.0a1 release notes" in notes
    assert "first v2 prerelease" in notes
    assert "breaking rewrite" in notes
    assert "dependency-free default install" in notes


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

    assert "pymeterbus==2.0.0a1" in notes
    assert "Python 3.11" in notes
    assert "Python 3.12" in notes
    assert "Python 3.13" in notes
    assert "pymeterbus[serial]" in notes
    assert "pymeterbus[legacy]" in notes


def test_v2_release_notes_document_coverage_and_gaps():
    notes = _RELEASE_NOTES.read_text()

    assert "Implemented decoder coverage" in notes
    assert "Known gaps" in notes
    assert "Variable-data telegram header decoding" in notes
    assert "Fixed-data telegram strategy is not finalized" in notes
    assert "v2 model stability is still preview-level" in notes


def test_changelog_points_to_v2_release_notes():
    changelog = (_PROJECT_ROOT / "CHANGELOG.md").read_text()

    assert "## 2.0.0a1" in changelog
    assert "docs/releases/2.0.0a1.md" in changelog
