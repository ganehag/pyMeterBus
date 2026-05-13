from __future__ import annotations

from pathlib import Path

import tomllib

import meterbus


_PROJECT_ROOT = Path(__file__).resolve().parents[1]


def _pyproject() -> dict:
    return tomllib.loads((_PROJECT_ROOT / "pyproject.toml").read_text())


def test_legacy_setup_cfg_has_been_removed():
    assert not (_PROJECT_ROOT / "setup.cfg").exists()


def test_pyproject_uses_modern_license_metadata():
    pyproject = _pyproject()

    assert pyproject["build-system"]["requires"] == ["setuptools>=77.0"]
    assert pyproject["project"]["license"] == "BSD-3-Clause"
    assert "License :: OSI Approved :: BSD License" not in pyproject["project"]["classifiers"]


def test_pyproject_uses_dynamic_runtime_version():
    pyproject = _pyproject()

    assert "version" not in pyproject["project"]
    assert pyproject["project"]["dynamic"] == ["version"]
    assert pyproject["tool"]["setuptools"]["dynamic"]["version"] == {"attr": "meterbus.__version__"}
    assert meterbus.__version__.startswith("2.0.0")
    assert (_PROJECT_ROOT / "docs" / "releases" / f"{meterbus.__version__}.md").exists()


def test_v2_python_support_metadata_matches_ci_matrix():
    pyproject = _pyproject()
    classifiers = pyproject["project"]["classifiers"]

    assert pyproject["project"]["requires-python"] == ">=3.11"
    assert "Programming Language :: Python :: 3.11" in classifiers
    assert "Programming Language :: Python :: 3.12" in classifiers
    assert "Programming Language :: Python :: 3.13" in classifiers
    assert "Programming Language :: Python :: 3.6" not in classifiers
    assert "Programming Language :: Python :: 3.7" not in classifiers
    assert "Programming Language :: Python :: 3.8" not in classifiers
    assert "Programming Language :: Python :: 3.9" not in classifiers
    assert "Programming Language :: Python :: 3.10" not in classifiers


def test_v2_default_install_has_no_runtime_dependencies_or_optional_groups():
    pyproject = _pyproject()

    assert pyproject["project"]["dependencies"] == []
    assert "optional-dependencies" not in pyproject["project"]


def test_removed_legacy_dependencies_are_not_packaged():
    pyproject = _pyproject()
    project = pyproject["project"]
    dependency_text = "\n".join(project.get("dependencies", []))

    assert "simplejson" not in dependency_text
    assert "pyserial" not in dependency_text
    assert "pyaml" not in dependency_text
    assert "pyyaml" not in dependency_text
    assert "pycryptodome" not in dependency_text
