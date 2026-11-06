#!/usr/bin/env bash
# Score every attempt under RESULTS/attempts that has a reply.md but no score.json, one at a time through sim-run.
# usage: PY=<python> scripts/score_pending.sh RESULTS_DIR
set -uo pipefail
RES=$1; PY=${PY:-python3}; HERE=$(cd "$(dirname "$0")/.." && pwd)
cd "$HERE"
for d in "$RES"/attempts/*/; do
  id=$(basename "$d")
  [ -f "$d/reply.md" ] && [ ! -f "$d/score.json" ] || continue
  PYTHONPATH="$HERE" ~/projects/bin/sim-run "$PY" -m zsr.attempt score "$id" --results "$RES" > "$d/score.stdout" 2>&1 \
    || echo "score failed: $id"
done
