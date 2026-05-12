from __future__ import annotations

from pathlib import Path


_PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_v2_release_checklist_covers_release_decision_areas():
    checklist = (_PROJECT_ROOT / "docs" / "v2-release-checklist.md").read_text()

    assert "# pyMeterBus v2 release checklist" in checklist
    assert "## Protocol coverage gaps" in checklist
    assert "## Compatibility decisions" in checklist
    assert "## Packaging and release" in checklist
    assert "## CI and quality gates" in checklist
    assert "## Documentation" in checklist
    assert "## Merge strategy" in checklist
    assert "## Final preview release checks" in checklist


def test_v2_release_checklist_mentions_core_release_paths():
    checklist = (_PROJECT_ROOT / "docs" / "v2-release-checklist.md").read_text()

    assert "v2" in checklist
    assert "master" in checklist
    assert "prerelease" in checklist
    assert "pymeterbus-decode" in checklist
    assert "bash scripts/test-v2.sh" in checklist


def test_v2_release_checklist_mentions_preview_version():
    checklist = (_PROJECT_ROOT / "docs" / "v2-release-checklist.md").read_text()

    assert "2.0.0a1" in checklist
    assert "Explicit v2 prerelease version" in checklist
    assert "Choose a preview version scheme" in checklist
