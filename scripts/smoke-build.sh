#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BUILD_DIR="${ROOT_DIR}/build/smoke"
DIST_DIR="${BUILD_DIR}/dist"
BUILD_VENV_DIR="${BUILD_DIR}/build-venv"
INSTALL_VENV_DIR="${BUILD_DIR}/install-venv"

rm -rf "${BUILD_DIR}"
mkdir -p "${DIST_DIR}"

python -m venv "${BUILD_VENV_DIR}"
"${BUILD_VENV_DIR}/bin/python" -m pip install --upgrade pip build
"${BUILD_VENV_DIR}/bin/python" -m build --wheel --outdir "${DIST_DIR}" "${ROOT_DIR}"

WHEEL_PATH="$(find "${DIST_DIR}" -maxdepth 1 -name '*.whl' -print -quit)"
if [[ -z "${WHEEL_PATH}" ]]; then
  echo "no wheel produced" >&2
  exit 1
fi

python -m venv "${INSTALL_VENV_DIR}"
"${INSTALL_VENV_DIR}/bin/python" -m pip install --upgrade pip
"${INSTALL_VENV_DIR}/bin/python" -m pip install "${WHEEL_PATH}"

CLI_OUTPUT="$(${INSTALL_VENV_DIR}/bin/pymeterbus-decode E5)"
"${INSTALL_VENV_DIR}/bin/python" - <<'PY' "${CLI_OUTPUT}"
import json
import sys

payload = json.loads(sys.argv[1])
assert payload["ok"] is True
assert payload["frame"]["kind"] == "ack"
PY

"${INSTALL_VENV_DIR}/bin/python" - <<'PY'
from meterbus.api import decode
from meterbus.export import to_json

payload = to_json(decode(bytes.fromhex("E5")))
assert '"ok":true' in payload
assert '"kind":"ack"' in payload
PY
