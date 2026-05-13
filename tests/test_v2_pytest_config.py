from __future__ import annotations

from pathlib import Path

import tomllib


_PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_pytest_config_has_no_unused_asyncio_options():
    pyproject = tomllib.loads((_PROJECT_ROOT / "pyproject.toml").read_text())

    pytest_config = pyproject.get("tool", {}).get("pytest", {}).get("ini_options", {})
    assert "asyncio_default_fixture_loop_scope" not in pytest_config
