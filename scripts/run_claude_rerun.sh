#!/usr/bin/env bash
# Organizer: isolated rerun of the contaminated round-2 Claude arms plus the new hopper `goal` arm (160 `claude -p`
# calls, 2 isolation probes), then scoring, variants and the report. Resumable: finished attempts are skipped, so
# rerun the same command after any interruption. Run from the repo root.
# usage: PY=<python> scripts/run_claude_rerun.sh RESULTS_DIR
# Every call runs in a fresh empty dir under /var/tmp with --setting-sources project,local; run_pilot.py refuses to run
# if any ancestor has CLAUDE.md, CLAUDE.local.md or .claude, and every batch starts with the isolation probe (refused
# if it reports an instruction file or its output has an email).
set -uo pipefail
RES=$1; PY=${PY:-python3}; export PYTHONPATH=$PWD
S=claude-sonnet-5-5; O=claude-opus-5-5
SFX=_iso2

wait_load() { while [ "$(cut -d' ' -f1 /proc/loadavg | cut -d. -f1)" -ge 20 ]; do echo "load >= 20, waiting"; sleep 60; done; }

"$PY" scripts/mark_contaminated.py "$RES"
# 1. isolation probes: READ the replies (results/claude_isolation_probe_<model>_*.json); they must show no instruction file
"$PY" scripts/run_pilot.py probe --results "$RES" --model $S || exit 1
"$PY" scripts/run_pilot.py probe --results "$RES" --model $O || exit 1
# 2. rerun of the 120 contaminated attempts: same prompts, same attempt indices, new ids with suffix _iso2
"$PY" scripts/run_pilot.py claude --results "$RES" --n 10 --model $S --mode controller --arms strict,named --suffix $SFX
"$PY" scripts/run_pilot.py claude --results "$RES" --n 10 --model $O --mode weights    --arms strict,named --suffix $SFX
"$PY" scripts/run_pilot.py claude --results "$RES" --n 10 --model $O --mode controller --arms strict,named --suffix $SFX
# 3. hopper goal arm (strict prompt + one goal sentence), Sonnet and Opus, weights and controller
for M in $S $O; do for MODE in weights controller; do
  "$PY" scripts/run_pilot.py claude --results "$RES" --n 10 --model $M --mode $MODE --arms goal --suffix $SFX
done; done
# 4. scoring (sim-run, one at a time), variants (loop until complete), report
wait_load
scripts/score_pending.sh "$RES"
until wait_load; ~/projects/bin/sim-run "$PY" scripts/score_variants.py "$RES" --max-seconds 500 | grep -q '^complete'; do :; done
"$PY" scripts/pilot_report.py "$RES"
