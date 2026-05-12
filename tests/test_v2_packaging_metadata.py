from __future__ import annotations

import sys
from configparser import ConfigParser
from pathlib import Path

if sys.version_info >= (3, 11):
    import tomllib
else:  # pragma: no cover - Python < 3.11 fallback for supported package metadata
    import tomli as tomllib


_PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_setup_cfg_uses_modern_metadata_keys():
    parser = ConfigParser()
    parser.read(_PROJECT_ROOT / "setup.cfg")

    assert parser["metadata"]["description_file"] == "README.md"
    assert "description-file" not in parser["metadata"]


def test_pyproject_uses_modern_license_metadata():
    pyproject = tomllib.loads((_PROJECT_ROOT / "pyproject.toml").read_text())

    assert pyproject["build-system"]["requires"] == ["setuptools>=77.0"]
    assert pyproject["project"]["license"] == "BSD-3-Clause"
    assert "License :: OSI Approved :: BSD License" not in pyproject["project"]["classifiers"]
