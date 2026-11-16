#!/usr/bin/env bash
# Warm-start study driver (docs/prereg-followup-draft.md section 6): two lanes, so at most 2 sim processes of this study.
#   scripts/warmstart_lanes.sh A|B [results_dir]
# Lane A: hopper H -> hopper LPR shard 0/2 -> walker2d H -> walker2d LPR shard 0/2
# Lane B: walker2d headroom seeds 0,1,2 -> (wait: hopper H complete) hopper LPR 1/2 -> (wait: walker2d H complete) walker2d LPR 1/2
# Every step is its own ~/projects/bin/sim-run process (registered, nice 10, one thread), cut at the stop time
# (prereg section 9: 2026-11-23 18:00 CST). Runs are resumable: rerunning the lane skips finished runs.
set -u
LANE=$1
RES=${2:-/home/jayden/projects/zero-step-robots/results}
PY=${PY:-/home/jayden/projects/zero-step-robots/.claude/worktrees/first-stop-point/.venv/bin/python}
cd "$(dirname "$(readlink -f "$0")")/.."
export PYTHONPATH=.
STOP=$(TZ=America/Chicago date -d '2026-11-23 18:00' +%s)

step() {  # step <args to warmstart.py>
  local left=$(( STOP - $(date +%s) ))
  if [ "$left" -le 0 ]; then echo "$(date -Is) stop time reached; not starting: $*"; exit 0; fi
  echo "$(date -Is) lane $LANE start: $*"
  timeout --signal=TERM "$left" ~/projects/bin/sim-run "$PY" scripts/warmstart.py "$@" --results "$RES"
  echo "$(date -Is) lane $LANE end (exit $?): $*"
}

wait_h() {  # wait until the 10 H runs of a task exist (lane A produces them)
  while [ "$(ls "$RES/warmstart/$1/H/"*.json 2>/dev/null | wc -l)" -lt 10 ]; do
    [ "$(date +%s)" -ge "$STOP" ] && { echo "stop time reached while waiting for $1 H"; exit 0; }
    sleep 60
  done
}

case "$LANE" in
  A) step run hopper H; step run hopper LPR --shard 0/2; step run walker2d H; step run walker2d LPR --shard 0/2 ;;
  B) for s in 0 1 2; do step headroom walker2d --seed "$s"; done
     wait_h hopper; step run hopper LPR --shard 1/2
     wait_h walker2d; step run walker2d LPR --shard 1/2 ;;
  *) echo "usage: $0 A|B [results_dir]" >&2; exit 2 ;;
esac
echo "$(date -Is) lane $LANE done"
