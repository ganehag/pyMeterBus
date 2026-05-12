from __future__ import annotations

import importlib
import sys
from pathlib import Path

if sys.version_info >= (3, 11):
    import tomllib
else:  # pragma: no cover - Python < 3.11 fallback for supported package metadata
    import tomli as tomllib


_PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_decode_cli_package_entrypoint_is_configured():
    pyproject = tomllib.loads((_PROJECT_ROOT / "pyproject.toml").read_text())

    assert pyproject["project"]["scripts"]["pymeterbus-decode"] == "meterbus.cli.decode:main"


def test_decode_cli_package_entrypoint_target_is_importable():
    pyproject = tomllib.loads((_PROJECT_ROOT / "pyproject.toml").read_text())
    target = pyproject["project"]["scripts"]["pymeterbus-decode"]
    module_name, function_name = target.split(":")

    module = importlib.import_module(module_name)

    assert callable(getattr(module, function_name))
