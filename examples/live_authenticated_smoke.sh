#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

if [[ ! -d .venv ]]; then
  uv venv .venv >/dev/null 2>&1
fi

source .venv/bin/activate
uv pip install -e '.[dev]' >/dev/null 2>&1

export SOLARK_ENV_FILE="${SOLARK_ENV_FILE:-$HOME/.openclaw/workspace-energyops/secrets/solark-cloud.env}"
python scripts/live_smoke.py
