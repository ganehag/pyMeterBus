from __future__ import annotations

from pathlib import Path


_PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_build_smoke_script_builds_and_installs_wheel():
    script = (_PROJECT_ROOT / "scripts" / "smoke-build.sh").read_text()

    assert '"${BUILD_VENV_DIR}/bin/python" -m build --wheel' in script
    assert "python -m venv" in script
    assert "BUILD_VENV_DIR" in script
    assert "INSTALL_VENV_DIR" in script
    assert "pymeterbus-decode E5" in script
    assert "from meterbus.api import decode" in script
    assert "from meterbus.export import to_json" in script


def test_build_smoke_script_does_not_install_build_into_system_python():
    script = (_PROJECT_ROOT / "scripts" / "smoke-build.sh").read_text()

    assert "python -m pip install --upgrade pip build" not in script
    assert '"${BUILD_VENV_DIR}/bin/python" -m pip install --upgrade pip build' in script
    assert '"${INSTALL_VENV_DIR}/bin/python" -m pip install "${WHEEL_PATH}"' in script


def test_build_smoke_script_asserts_default_install_has_no_legacy_dependencies():
    script = (_PROJECT_ROOT / "scripts" / "smoke-build.sh").read_text()

    assert "metadata.distributions()" in script
    assert "pyserial" in script
    assert "pyaml" in script
    assert "simplejson" in script
    assert "pycryptodome" in script
    assert "unexpected default dependency installed" in script


def test_build_smoke_workflow_uses_smoke_script():
    workflow = (_PROJECT_ROOT / ".github" / "workflows" / "build-smoke.yml").read_text()

    assert "bash scripts/smoke-build.sh" in workflow
    assert "actions/setup-python@v6" in workflow
    assert '"3.11"' in workflow
    assert '"3.12"' in workflow
    assert '"3.13"' in workflow
