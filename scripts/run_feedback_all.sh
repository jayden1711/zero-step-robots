#!/usr/bin/env bash
# CPG feedback arm, prereg order (docs/prereg-2026-11-10-cpg-feedback.md s10): per task, Opus and Sonnet streams side
# by side (one call at a time each), then RS-from-LLM for that task; hopper first, then walker2d.
set -uo pipefail
cd "$(dirname "$0")/.."
RES=${1:-/home/jayden/projects/zero-step-robots/results}
PY=${PY:-.venv/bin/python}
mkdir -p "$RES/cpg_feedback/logs"
for task in hopper walker2d; do
  for model in claude-opus-5-5 claude-sonnet-5-5; do
    PYTHONPATH=. "$PY" scripts/run_feedback.py --model "$model" --task "$task" --level H2 --n 10 --results "$RES" \
      > "$RES/cpg_feedback/logs/fb_${model}_${task}.log" 2>&1 &
  done
  wait
  for model in claude-opus-5-5 claude-sonnet-5-5; do
    PYTHONPATH=. ~/projects/bin/sim-run "$PY" scripts/rs_proposer.py fromllm "$task" --model "$model" \
      >> "$RES/cpg_feedback/logs/rs_fromllm_${task}.log" 2>&1
  done
done
