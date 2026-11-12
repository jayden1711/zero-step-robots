#!/usr/bin/env bash
# PPO upper reference for the CPG track (prereg s5): rescore the existing hopper PPO weights with the new metric,
# then train Walker2d PPO (SB3 defaults, 16-unit actor, 1M steps, seeds 0..2). Each step one sim-run process.
set -euo pipefail
cd "$(dirname "$0")/.."
RES=${1:-/home/jayden/projects/zero-step-robots/results}
PY=${PY:-.venv/bin/python}
mkdir -p "$RES/cpg/ppo/hopper" "$RES/cpg/ppo/walker2d"
for s in 0 1 2; do
  PYTHONPATH=. ~/projects/bin/sim-run "$PY" -m zsr.harness hopper --weights "$RES/baselines/ppo/hopper_ppo_seed$s.weights.json" \
    --out "$RES/cpg/ppo/hopper/hopper_ppo_seed$s.score.json" > /dev/null
done
for s in 0 1 2; do
  [ -f "$RES/cpg/ppo/walker2d/walker2d_ppo_seed$s.score.json" ] && continue
  PYTHONPATH=. ~/projects/bin/sim-run "$PY" -m zsr.ppo walker2d --seed $s --outdir "$RES/cpg/ppo/walker2d"
done
