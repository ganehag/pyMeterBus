#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BUILD_DIR="${ROOT_DIR}/build/smoke"
DIST_DIR="${BUILD_DIR}/dist"
VENV_DIR="${BUILD_DIR}/venv"

rm -rf "${BUILD_DIR}"
mkdir -p "${DIST_DIR}"

python -m pip install --upgrade pip build
python -m build --wheel --outdir "${DIST_DIR}" "${ROOT_DIR}"

WHEEL_PATH="$(find "${DIST_DIR}" -maxdepth 1 -name '*.whl' -print -quit)"
if [[ -z "${WHEEL_PATH}" ]]; then
  echo "no wheel produced" >&2
  exit 1
fi

python -m venv "${VENV_DIR}"
"${VENV_DIR}/bin/python" -m pip install --upgrade pip
"${VENV_DIR}/bin/python" -m pip install "${WHEEL_PATH}"

CLI_OUTPUT="$(${VENV_DIR}/bin/pymeterbus-decode E5)"
"${VENV_DIR}/bin/python" - <<'PY' "${CLI_OUTPUT}"
import json
import sys

payload = json.loads(sys.argv[1])
assert payload["ok"] is True
assert payload["frame"]["kind"] == "ack"
PY

"${VENV_DIR}/bin/python" - <<'PY'
from meterbus.api import decode
from meterbus.export import to_json

payload = to_json(decode(bytes.fromhex("E5")))
assert '"ok":true' in payload
assert '"kind":"ack"' in payload
PY
