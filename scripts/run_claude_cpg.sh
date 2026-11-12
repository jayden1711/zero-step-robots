#!/usr/bin/env bash
# CPG track, Claude arms (docs/prereg-2026-11-09-cpg.md section 6). Usage: run_claude_cpg.sh <task> [RESULTS]
# Per model: one isolation probe, then 10 attempts per level in the order H2, H1, H0. Resumable: attempts that
# have a reply.md are skipped. Then every new reply is compiled and scored through sim-run, and the report rebuilt.
set -euo pipefail
cd "$(dirname "$0")/.."
task=$1
RES=${2:-/home/jayden/projects/zero-step-robots/results}
PY=${PY:-.venv/bin/python}
deadline=$(date -d '2026-11-23 18:00 CST' +%s)
[ "$(date +%s)" -lt "$deadline" ] || { echo "past the prereg stop time (2026-11-23 18:00 CST): no new LLM calls"; exit 1; }
for model in claude-opus-5-5 claude-sonnet-5-5; do
  PYTHONPATH=. "$PY" scripts/run_pilot.py claude --results "$RES" --model "$model" --tag "cpg-$model" \
    --mode cpgspec --tasks "$task" --arms H2,H1,H0 --n 10 --timeout 1800 || echo "WARNING: $model batch ended with failed calls (logged; see above)"
done
for d in "$RES"/attempts/cpg-claude-*_"$task"_H?_cpgspec_[0-9][0-9]; do  # renamed transport failures are skipped
  [ -f "$d/score.json" ] && continue
  PYTHONPATH=. ~/projects/bin/sim-run "$PY" -m zsr.attempt score "$(basename "$d")" --results "$RES" > /dev/null
done
PYTHONPATH=. "$PY" scripts/cpg_report.py "$RES"
