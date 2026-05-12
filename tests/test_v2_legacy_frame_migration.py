from __future__ import annotations

from pathlib import Path


_PROJECT_ROOT = Path(__file__).resolve().parents[1]
_INVENTORY = _PROJECT_ROOT / "docs" / "v2-legacy-frame-migration.md"
_LEGACY_FRAME_ROOTS = (
    _PROJECT_ROOT / "tests" / "test-frames",
    _PROJECT_ROOT / "tests" / "error-frames",
    _PROJECT_ROOT / "tests" / "unsupported-frames",
)
_ALLOWED_SUFFIXES = {".blob", ".hex", ".xml"}


def _legacy_frame_paths() -> list[str]:
    paths: list[str] = []
    for root in _LEGACY_FRAME_ROOTS:
        for path in root.iterdir():
            if path.is_file() and (path.suffix in _ALLOWED_SUFFIXES or path.name.endswith(".blob.2")):
                paths.append(path.relative_to(_PROJECT_ROOT).as_posix())
    return sorted(paths)


def test_legacy_frame_migration_inventory_exists():
    inventory = _INVENTORY.read_text()

    assert "# v2 legacy frame fixture migration" in inventory
    assert "Migration rules" in inventory
    assert "Every legacy frame file must be classified" in inventory
    assert "First migration candidates" in inventory


def test_every_legacy_frame_file_is_classified_in_inventory():
    inventory = _INVENTORY.read_text()

    missing = [path for path in _legacy_frame_paths() if f"`{path}`" not in inventory]

    assert missing == []


def test_inventory_tracks_current_v2_canonical_frame_fixtures():
    inventory = _INVENTORY.read_text()
    fixture_root = _PROJECT_ROOT / "tests" / "fixtures" / "frames"

    missing = [
        path.relative_to(_PROJECT_ROOT).as_posix()
        for path in sorted(fixture_root.glob("*.hex"))
        if f"`{path.relative_to(_PROJECT_ROOT).as_posix()}`" not in inventory
    ]

    assert missing == []


def test_inventory_marks_migration_statuses_explicitly():
    inventory = _INVENTORY.read_text()

    assert "pending_review" in inventory
    assert "legacy_error_case" in inventory
    assert "unsupported_pending_review" in inventory
    assert "migrated" in inventory
