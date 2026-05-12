from __future__ import annotations

import sys
from pathlib import Path

if sys.version_info >= (3, 11):
    import tomllib
else:  # pragma: no cover - Python < 3.11 fallback for supported package metadata
    import tomli as tomllib


_PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_asyncio_fixture_loop_scope_is_explicit():
    pyproject = tomllib.loads((_PROJECT_ROOT / "pyproject.toml").read_text())

    assert pyproject["tool"]["pytest"]["ini_options"]["asyncio_default_fixture_loop_scope"] == "function"
