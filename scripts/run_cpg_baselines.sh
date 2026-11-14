#!/usr/bin/env bash
# One task's CPG baselines in sequence, each step one sim-run process. Usage: run_cpg_baselines.sh <task>
set -euo pipefail
cd "$(dirname "$0")/.."
task=$1
PY=${PY:-.venv/bin/python}
for cmd in necessity randcpg tuned; do
  PYTHONPATH=. ~/projects/bin/sim-run "$PY" scripts/cpg_baselines.py "$cmd" "$task"
done
