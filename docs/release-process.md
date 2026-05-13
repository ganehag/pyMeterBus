# Release process

pyMeterBus releases are automated through GitHub Actions.

The release workflow is tag-driven. Pushing a version tag runs the v2 test matrix, runs the build smoke test matrix, builds the source and wheel distributions, checks the distributions, and publishes according to branch policy.

The policy is strict:

- tags whose commit is contained in `master` publish to the real PyPI project;
- tags or manual publish runs from any other branch publish to TestPyPI only;
- only real PyPI releases create a public GitHub Release.

This lets prerelease work from `v2` validate the full packaging path without risking the production PyPI project.

## Release workflow

The workflow lives at:

```text
.github/workflows/publish.yml
```

It runs on tags matching:

```text
v*
```

For example:

```text
v2.0.0a1
v2.0.0
v2.0.1
```

The tag must match the package version from `meterbus.__version__`. For example, if the package version is `2.0.0a1`, the release tag must be `v2.0.0a1`.

## Publishing targets

### TestPyPI

Use TestPyPI for releases from `v2`, feature branches, and manual publish runs that are not based on `master`.

The workflow publishes to TestPyPI when the tagged commit is not contained in `origin/master`.

### PyPI

Use real PyPI only for releases from `master`.

The workflow publishes to PyPI only when the tagged commit is contained in `origin/master`.

## Trusted Publishing setup

The workflow uses Trusted Publishing. Do not add PyPI tokens to repository secrets unless there is a specific reason to avoid Trusted Publishing.

Configure the real PyPI project with a trusted publisher matching:

```text
Repository: ganehag/pyMeterBus
Workflow: .github/workflows/publish.yml
Environment: pypi
```

Configure the TestPyPI project with a trusted publisher matching:

```text
Repository: ganehag/pyMeterBus
Workflow: .github/workflows/publish.yml
Environment: testpypi
```

The workflow has `id-token: write` permission and publishes from either the `pypi` or `testpypi` GitHub environment.

## Release notes

Every release must have a matching release note file:

```text
docs/releases/<version>.md
```

For example:

```text
docs/releases/2.0.0a1.md
```

For real PyPI releases from `master`, the GitHub Release body is created from that file.

TestPyPI releases do not create a public GitHub Release.

## Dry run

Use the manual workflow dispatch dry run before pushing a tag.

In GitHub Actions, run `Publish release` manually and leave `publish` set to `false`.

The dry run builds and checks the distributions but does not publish to PyPI/TestPyPI and does not create a GitHub Release.

## TestPyPI prerelease from v2

For a v2 prerelease test publication:

```shell
git switch v2
git pull origin v2

bash scripts/test-v2.sh
bash scripts/smoke-build.sh
```

Confirm the version:

```shell
python - <<'PY'
import meterbus
print(meterbus.__version__)
PY
```

Confirm the release notes exist:

```shell
ls docs/releases/2.0.0a1.md
```

Create and push the tag:

```shell
git tag -a v2.0.0a1 -m "pyMeterBus 2.0.0a1"
git push origin v2.0.0a1
```

Because this tag is on `v2` and not contained in `master`, the workflow publishes to TestPyPI only.

## PyPI release from master

For a real PyPI release, first ensure the release commit is on `master`.

```shell
git switch master
git pull origin master

bash scripts/test-v2.sh
bash scripts/smoke-build.sh
```

Create and push the tag from `master`:

```shell
git tag -a v2.0.0 -m "pyMeterBus 2.0.0"
git push origin v2.0.0
```

Because this tag is contained in `master`, the workflow publishes to real PyPI and creates a GitHub Release.

## Post-TestPyPI verification

After a TestPyPI workflow succeeds, verify installation in a fresh environment:

```shell
python -m venv /tmp/pymeterbus-testpypi-check
/tmp/pymeterbus-testpypi-check/bin/python -m pip install --upgrade pip
/tmp/pymeterbus-testpypi-check/bin/python -m pip install \
  --index-url https://test.pypi.org/simple/ \
  --extra-index-url https://pypi.org/simple/ \
  --pre pyMeterBus
/tmp/pymeterbus-testpypi-check/bin/pymeterbus-decode E5
```

## Post-PyPI verification

After a real PyPI workflow succeeds, verify installation in a fresh environment:

```shell
python -m venv /tmp/pymeterbus-release-check
/tmp/pymeterbus-release-check/bin/python -m pip install --upgrade pip
/tmp/pymeterbus-release-check/bin/python -m pip install --pre pyMeterBus
/tmp/pymeterbus-release-check/bin/pymeterbus-decode E5
```

Expected output includes:

```json
{"diagnostics":[],"frame":{"diagnostics":[],"kind":"ack","raw":"E5"},"ok":true,"raw":"E5","telegram":null}
```

## Failure handling

If the workflow fails before publishing, fix the issue, delete the local and remote tag if needed, then create a new tag after the fix.

If a TestPyPI publication succeeds but has bad metadata, publish a new version. Do not rely on replacing the same version.

If PyPI publishing succeeds but GitHub Release creation fails, do not re-upload the same distribution to PyPI. Re-run or repair only the GitHub Release step manually.

If PyPI publishing succeeds with a bad artifact, do not delete and replace the same version on PyPI. Publish a new version instead.

## Branch strategy

For `2.0.0a1`, publish from `v2` to TestPyPI before making `master` the v2 default branch.

A later branch move can be done separately:

```shell
git fetch origin
git switch master
git pull origin master
git branch v1
git push origin v1
git merge --no-ff origin/v2
git push origin master
```

Do not mix the TestPyPI prerelease with the default-branch migration unless you intentionally want to make v2 the public default at the same time.
