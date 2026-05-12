from __future__ import annotations

import importlib.util
import sys
from configparser import ConfigParser
from pathlib import Path

if sys.version_info >= (3, 11):
    import tomllib
else:  # pragma: no cover - Python < 3.11 fallback for supported package metadata
    import tomli as tomllib


_PROJECT_ROOT = Path(__file__).resolve().parents[1]


def _load_meterbus_version() -> str:
    spec = importlib.util.spec_from_file_location(
        "meterbus_version_check",
        _PROJECT_ROOT / "meterbus" / "__init__.py",
    )
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.__version__


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


def test_pyproject_uses_dynamic_runtime_version():
    pyproject = tomllib.loads((_PROJECT_ROOT / "pyproject.toml").read_text())

    assert pyproject["project"]["version"] == "0.0.0"
    assert pyproject["tool"]["setuptools"]["dynamic"]["version"] == {"attr": "meterbus.__version__"}
    assert _load_meterbus_version() == "2.0.0a1"


def test_v2_default_install_has_no_runtime_dependencies():
    pyproject = tomllib.loads((_PROJECT_ROOT / "pyproject.toml").read_text())

    assert pyproject["project"]["dependencies"] == []


def test_legacy_dependencies_are_available_as_extras_without_simplejson():
    pyproject = tomllib.loads((_PROJECT_ROOT / "pyproject.toml").read_text())
    extras = pyproject["project"]["optional-dependencies"]

    assert "json" not in extras
    assert extras["serial"] == ["pyserial"]
    assert extras["yaml"] == ["pyaml"]
    assert extras["crypto"] == ["pycryptodome"]
    assert extras["legacy"] == ["pyserial", "pyaml", "pycryptodome"]
    assert extras["all"] == ["pyserial", "pyaml", "pycryptodome"]


def test_simplejson_is_not_a_packaged_dependency():
    pyproject = tomllib.loads((_PROJECT_ROOT / "pyproject.toml").read_text())
    extras = pyproject["project"]["optional-dependencies"]

    assert "simplejson" not in pyproject["project"]["dependencies"]
    assert all("simplejson" not in dependencies for dependencies in extras.values())
