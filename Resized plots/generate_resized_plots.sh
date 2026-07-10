#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

if command -v python3.12 >/dev/null 2>&1; then
  PYTHON_BIN="$(command -v python3.12)"
elif [ -x /opt/anaconda3/bin/python3.12 ]; then
  PYTHON_BIN="/opt/anaconda3/bin/python3.12"
else
  PYTHON_BIN="python3"
fi

PYTHONPYCACHEPREFIX="${PYTHONPYCACHEPREFIX:-/private/tmp/masterthesis_pycache}" \
  "$PYTHON_BIN" "Resized plots/generate_resized_plots.py"
