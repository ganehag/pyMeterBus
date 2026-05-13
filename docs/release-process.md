# Release process

pyMeterBus releases are automated through GitHub Actions.

The release flow intentionally uses two separate publishing workflows. This keeps the OpenID Connect trust boundary narrow: TestPyPI trusts only the TestPyPI workflow, and production PyPI trusts only the production PyPI workflow.

The policy is strict:

- non-master release tests publish to TestPyPI only;
- production releases publish to real PyPI only from commits contained in `master`;
- only real PyPI releases create a public GitHub Release.

This lets prerelease work from `v2` validate the packaging path without risking the production PyPI project.

## Workflows

### TestPyPI workflow

```text
.github/workflows/publish-testpypi.yml
```

Use this for prereleases and release tests from `v2` or any other non-master branch.

It:

- runs the v2 test matrix on Python 3.11, 3.12, and 3.13;
- runs the build smoke matrix on Python 3.11, 3.12, and 3.13;
- builds source and wheel distributions;
- runs `twine check`;
- publishes to TestPyPI when `publish=true` or when a non-master tag is pushed;
- refuses to publish if the commit is contained in `origin/master`.

### PyPI workflow

```text
.github/workflows/publish-pypi.yml
```

Use this only for production releases from `master`.

It:

- runs the v2 test matrix on Python 3.11, 3.12, and 3.13;
- runs the build smoke matrix on Python 3.11, 3.12, and 3.13;
- builds source and wheel distributions;
- runs `twine check`;
- publishes to real PyPI when `publish=true` or when a master tag is pushed;
- refuses to publish if the commit is not contained in `origin/master`;
- creates a GitHub Release from `docs/releases/<version>.md` and attaches the built artifacts.

## Tag format

Both workflows accept tags matching:

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

## Trusted Publishing setup

Use PyPI Trusted Publishing. Do not add PyPI tokens to repository secrets unless there is a specific reason to avoid Trusted Publishing.

Configure the TestPyPI project with a trusted publisher matching:

```text
Repository: ganehag/pyMeterBus
Workflow: .github/workflows/publish-testpypi.yml
Environment: testpypi
```

Configure the real PyPI project with a trusted publisher matching:

```text
Repository: ganehag/pyMeterBus
Workflow: .github/workflows/publish-pypi.yml
Environment: pypi
```

The environment names are not merely cosmetic. They should be configured under the repository settings with appropriate protection rules. This is especially important if some maintainers have commit access but should not have production PyPI publishing access.

## Release notes

Every release must have a matching release note file:

```text
docs/releases/<version>.md
```

For example:

```text
docs/releases/2.0.0a1.md
```

For production PyPI releases from `master`, the GitHub Release body is created from that file.

TestPyPI releases do not create a public GitHub Release.

## Dry runs

Both workflows can be run manually with `publish=false`.

A dry run builds and checks the distributions but does not publish to TestPyPI/PyPI and does not create a GitHub Release.

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

Because this tag is on `v2` and not contained in `master`, `publish-testpypi.yml` publishes to TestPyPI only. `publish-pypi.yml` also sees the tag, but refuses to publish because the commit is not contained in `origin/master`.

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

Because this tag is contained in `master`, `publish-pypi.yml` publishes to real PyPI and creates a GitHub Release. `publish-testpypi.yml` also sees the tag, but refuses to publish because the commit is contained in `origin/master`.

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

If a workflow fails before publishing, fix the issue, delete the local and remote tag if needed, then create a new tag after the fix.

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
