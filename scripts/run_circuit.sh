#!/usr/bin/env bash
# Compile the circuit fixtures and score them with the standard harness. Output (local): RESULTS/circuit/<task>_<name>/
# usage: PY=<python> scripts/run_circuit.sh RESULTS_DIR      (run from the repo root)
set -euo pipefail
RES=$1; PY=${PY:-python3}
for spec in circuitc/examples/*.json; do
  name=$(basename "$spec" .json); task=${name%%_*}; d="$RES/circuit/$name"; mkdir -p "$d"
  cp "$spec" "$d/spec.json"
  PYTHONPATH=. "$PY" -m circuitc "$spec" "$d/weights.json" > "$d/compile_report.json"
  PYTHONPATH=. ~/projects/bin/sim-run "$PY" -m zsr.harness "$task" --weights "$d/weights.json" --out "$d/score.json" > /dev/null
  echo "$name: $("$PY" -c "import json;s=json.load(open('$d/score.json'));print('mean_return',round(s['mean_return'],1),'frac_full',s['frac_full_length'])")"
done
