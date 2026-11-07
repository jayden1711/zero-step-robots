#!/usr/bin/env bash
# Score every attempt under RESULTS/attempts that has a reply.md but no score.json, one at a time through sim-run.
# usage: PY=<python> scripts/score_pending.sh RESULTS_DIR
# Exits non-zero if any attempt failed to score (every pending attempt must end with a non-empty score.json).
set -uo pipefail
RES=$1; PY=${PY:-python3}; HERE=$(cd "$(dirname "$0")/.." && pwd)
cd "$HERE"
nfail=0
for d in "$RES"/attempts/*/; do
  id=$(basename "$d")
  [ -f "$d/reply.md" ] && [ ! -f "$d/score.json" ] || continue
  PYTHONPATH="$HERE" ~/projects/bin/sim-run "$PY" -m zsr.attempt score "$id" --results "$RES" > "$d/score.stdout" 2>&1
  rc=$?
  if [ "$rc" -ne 0 ] || [ ! -s "$d/score.json" ]; then
    echo "score failed: $id (rc=$rc)"
    nfail=$((nfail + 1))
  fi
done
[ "$nfail" -eq 0 ] || { echo "$nfail attempt(s) failed to score" >&2; exit 1; }
