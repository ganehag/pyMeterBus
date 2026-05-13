# Release process

pyMeterBus releases are automated through GitHub Actions.

The release workflow is tag-driven. Pushing a version tag runs the v2 test matrix, runs the build smoke test matrix, builds the source and wheel distributions, checks the distributions, publishes to PyPI using Trusted Publishing, and creates a GitHub Release with the built artifacts attached.

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

## PyPI Trusted Publishing setup

The workflow uses PyPI Trusted Publishing. Do not add a PyPI token to repository secrets unless there is a specific reason to avoid Trusted Publishing.

Configure the PyPI project with a trusted publisher matching:

```text
Repository: ganehag/pyMeterBus
Workflow: .github/workflows/publish.yml
Environment: pypi
```

The workflow has `id-token: write` permission and publishes from the `pypi` GitHub environment.

## Release notes

Every release must have a matching release note file:

```text
docs/releases/<version>.md
```

For example:

```text
docs/releases/2.0.0a1.md
```

The GitHub Release body is created from that file.

## Dry run

Use the manual workflow dispatch dry run before pushing a tag.

In GitHub Actions, run `Publish release` manually and leave `publish` set to `false`.

The dry run builds and checks the distributions but does not publish to PyPI and does not create a GitHub Release.

## Prerelease from v2

For a v2 prerelease:

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

The workflow will then publish to PyPI and create a GitHub Release.

## Post-release verification

After the workflow succeeds, verify installation in a fresh environment:

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

If PyPI publishing succeeds but GitHub Release creation fails, do not re-upload the same distribution to PyPI. Re-run or repair only the GitHub Release step manually.

If PyPI publishing succeeds with a bad artifact, do not delete and replace the same version on PyPI. Publish a new version instead.

## Branch strategy

For `2.0.0a1`, release from `v2` before making `master` the v2 default branch.

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

Do not mix the prerelease with the default-branch migration unless you intentionally want to make v2 the public default at the same time.
