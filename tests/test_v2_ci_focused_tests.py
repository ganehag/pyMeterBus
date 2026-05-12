from __future__ import annotations

from pathlib import Path


_PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_v2_focused_test_script_lists_v2_suite():
    script = (_PROJECT_ROOT / "scripts" / "test-v2.sh").read_text()

    assert "python -m pytest" in script
    assert "tests/test_v2_decode_api.py" in script
    assert "tests/test_v2_cli_decode.py" in script
    assert "tests/test_v2_docs_usage.py" in script
    assert "tests/test_fixture_loading.py" in script


def test_v2_ci_workflow_uses_focused_test_script():
    workflow = (_PROJECT_ROOT / ".github" / "workflows" / "test-v2.yml").read_text()

    assert "bash scripts/test-v2.sh" in workflow
    assert "actions/setup-python@v5" in workflow
    assert '"3.11"' in workflow
    assert '"3.12"' in workflow
    assert '"3.13"' in workflow
