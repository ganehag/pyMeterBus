from __future__ import annotations

from pathlib import Path


_PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_readme_points_to_v2_usage_documentation():
    readme = (_PROJECT_ROOT / "README.md").read_text()

    assert "The `v2` decoder is the supported direction" in readme
    assert "prerelease line" in readme
    assert "no runtime dependencies" in readme
    assert "byte-oriented" in readme
    assert "docs/getting-started.md" in readme
    assert "docs/v2-usage.md" in readme
    assert "python -m meterbus.cli.decode" in readme
    assert "pymeterbus-decode" in readme


def test_readme_documents_dependency_and_transport_boundaries():
    readme = (_PROJECT_ROOT / "README.md").read_text()

    assert "does not import `pyserial`" in readme
    assert "dependency-update tooling" in readme
    assert "Transport is caller-owned" in readme
    assert "Wireless M-Bus decoding" in readme
    assert "Silent acceptance of aggregator-stripped" in readme
    assert "Do not rely on the wired decoder to guess frame boundaries" in readme


def test_readme_documents_real_world_corpus_workflow():
    readme = (_PROJECT_ROOT / "README.md").read_text()

    assert "Real-world wired M-Bus corpus regression checks" in readme
    assert "scripts/import-real-world-corpus.py" in readme
    assert "scripts/report-real-world-corpus.py" in readme
    assert "valid wired frames, malformed wired-looking frames, and wireless/aggregator-looking payloads separate" in readme


def test_getting_started_guide_is_practical_for_non_developers():
    guide = (_PROJECT_ROOT / "docs" / "getting-started.md").read_text()

    assert "need to get M-Bus data decoded" in guide
    assert "pyMeterBus v2 does not talk to meters by itself" in guide
    assert "python -m pip install --pre pyMeterBus" in guide
    assert "pymeterbus-decode E5" in guide
    assert "pymeterbus-decode --mode lenient --indent 2 \"$HEX\"" in guide
    assert "$(xxd -p -c 999999 frame.blob)" in guide
    assert "For most practical use, start with `lenient`" in guide


def test_getting_started_guide_documents_common_failure_paths():
    guide = (_PROJECT_ROOT / "docs" / "getting-started.md").read_text()

    assert "Invalid start byte" in guide
    assert "Length mismatch" in guide
    assert "Checksum mismatch" in guide
    assert "No records decoded" in guide
    assert "pyMeterBus v2 will not silently guess missing headers" in guide
    assert "pyMeterBus does not include serial communication helpers" in guide
    assert "v2 is not a drop-in replacement" in guide
    assert "What to include when asking for help" in guide


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
