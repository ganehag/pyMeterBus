from __future__ import annotations

from pathlib import Path


_PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_readme_points_to_v2_usage_documentation():
    readme = (_PROJECT_ROOT / "README.md").read_text()

    assert "The `v2` decoder is the supported direction" in readme
    assert "no runtime dependencies" in readme
    assert "byte-oriented" in readme
    assert "docs/v2-usage.md" in readme
    assert "python -m meterbus.cli.decode" in readme
    assert "pymeterbus-decode" in readme


def test_v2_usage_doc_mentions_public_api_and_exports():
    usage = (_PROJECT_ROOT / "docs" / "v2-usage.md").read_text()

    assert "from meterbus import decode" in usage
    assert "from meterbus.api import decode" in usage
    assert "from meterbus.model import DecodeMode" in usage
    assert "from meterbus.export import to_dict" in usage
    assert "from meterbus.export import to_json" in usage
    assert "DecodeMode.STRICT" in usage
    assert "DecodeMode.LENIENT" in usage
    assert "DecodeMode.COMPAT" in usage


def test_v2_usage_doc_documents_root_api_break():
    usage = (_PROJECT_ROOT / "docs" / "v2-usage.md").read_text()

    assert "v2 is a breaking rewrite" in usage
    assert "package root exports only the small v2 decode surface" in usage
    assert "decode, decode_one, decode_one_frame" in usage
    assert "Do not rely on legacy symbols" in usage
    assert "dependency-free" in usage


def test_v2_usage_doc_mentions_cli_commands_and_exit_codes():
    usage = (_PROJECT_ROOT / "docs" / "v2-usage.md").read_text()

    assert "python -m meterbus.cli.decode" in usage
    assert "pymeterbus-decode" in usage
    assert "`0`: decode completed" in usage
    assert "`1`: decode completed" in usage
    assert "`2`: invalid CLI input" in usage
