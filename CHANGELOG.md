# Changelog

## 2.0.0a2

Second v2 prerelease.

Highlights:

- Full v2 test gate now runs the complete `tests` directory.
- Packaging and workflow tests were aligned with the dependency-free v2 package policy.
- Added and linked the v1-to-v2 migration guide.
- Added and linked diagnostics and decode-mode documentation.
- Production PyPI publishing is now manual-only and guarded by an `origin/master` containment check.
- TestPyPI remains the prerelease rehearsal path for non-master tags.
- Updated GitHub Actions to current documented major versions for checkout, setup-python, upload-artifact, and download-artifact.
- No Dependabot configuration was added.

Full release notes: docs/releases/2.0.0a2.md

## 2.0.0a1

First v2 prerelease.

Highlights:

- Breaking rewrite.
- Structured decoder API.
- Deterministic dictionary and JSON exports.
- CLI decode entry point.
- Dependency-free default install.
- Python 3.11, 3.12, and 3.13 support metadata.

Full release notes: docs/releases/2.0.0a1.md
