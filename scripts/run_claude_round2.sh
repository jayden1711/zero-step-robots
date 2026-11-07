#!/usr/bin/env bash
# SUPERSEDED by scripts/run_claude_rerun.sh (the round-2 runs it started were contaminated by /tmp/CLAUDE.md). Kept for the record.
# Organizer: Claude arms of round 2 (120 `claude -p` calls), then scoring, variants and the report. Resumable: finished
# attempts are skipped, so rerun after any interruption. Run from the repo root.
# usage: PY=<python> scripts/run_claude_round2.sh RESULTS_DIR
set -uo pipefail
RES=$1; PY=${PY:-python3}; export PYTHONPATH=$PWD
S=claude-sonnet-5-5; O=claude-opus-5-5
"$PY" scripts/run_pilot.py probe --results "$RES" --model $O   # isolation probe for the Opus calls (Sonnet probe is in the pilot results)
"$PY" scripts/run_pilot.py claude --results "$RES" --n 10 --model $S --mode controller
"$PY" scripts/run_pilot.py claude --results "$RES" --n 10 --model $O --mode weights
"$PY" scripts/run_pilot.py claude --results "$RES" --n 10 --model $O --mode controller
scripts/score_pending.sh "$RES"
until ~/projects/bin/sim-run "$PY" scripts/score_variants.py "$RES" --max-seconds 500 | grep -q '^complete'; do :; done
"$PY" scripts/pilot_report.py "$RES"
