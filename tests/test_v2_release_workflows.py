from __future__ import annotations

from pathlib import Path


_PROJECT_ROOT = Path(__file__).resolve().parents[1]
_WORKFLOWS = _PROJECT_ROOT / ".github" / "workflows"


def test_production_pypi_workflow_is_manual_only():
    workflow = (_WORKFLOWS / "publish-pypi.yml").read_text()

    assert "workflow_dispatch:" in workflow
    assert "push:" not in workflow
    assert "tags:" not in workflow
    assert "pypa/gh-action-pypi-publish@release/v1" in workflow


def test_production_pypi_workflow_requires_master_containment():
    workflow = (_WORKFLOWS / "publish-pypi.yml").read_text()

    assert "git fetch origin master --prune" in workflow
    assert 'git merge-base --is-ancestor "${GITHUB_SHA}" "origin/master"' in workflow
    assert "This commit is not contained in origin/master" in workflow


def test_testpypi_workflow_accepts_prerelease_tags_but_rejects_master():
    workflow = (_WORKFLOWS / "publish-testpypi.yml").read_text()

    assert "push:" in workflow
    assert "tags:" in workflow
    assert '"v*"' in workflow
    assert "repository-url: https://test.pypi.org/legacy/" in workflow
    assert "This commit is contained in origin/master" in workflow
