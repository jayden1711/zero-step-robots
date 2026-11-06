# One command per result. Results go to the git-ignored results/ directory. Heavy runs go through sim-run / gpu-run.
PY ?= .venv/bin/python
R  ?= $(CURDIR)/results
export PYTHONPATH := $(CURDIR)
SIM = ~/projects/bin/sim-run

.PHONY: clips test baselines lqr score variants report circuit notable local-controller local-weights claude-round2
test:            ; $(PY) -m pytest tests -q
baselines:       ; $(SIM) $(PY) scripts/run_baselines.py --out $(R)/baselines
lqr:             ; $(SIM) $(PY) scripts/make_lqr.py $(R)/baselines/lqr
score:           ; PY=$(PY) scripts/score_pending.sh $(R)
variants:        ; $(SIM) $(PY) scripts/score_variants.py $(R) --max-seconds 500   # rerun until it prints "complete"
report:          ; $(PY) scripts/pilot_report.py $(R)
circuit:         ; PY=$(PY) scripts/run_circuit.sh $(R)
notable:         ; $(SIM) $(PY) scripts/analyze_weights.py $(R) claude_hopper_named_weights_01 claude_hopper_strict_weights_04 claude_hopper_strict_weights_08
# local models: M=qwen3-coder-30b|gpt-oss-20b; runs inside gpu-run, 420 s chunks, rerun until it stops printing "time budget"
local-controller: ; PY=$(PY) scripts/run_local.sh $(M) $(R) controller 420
local-weights:    ; PY=$(PY) scripts/run_local.sh $(M) $(R) weights 420
claude-round2:   ; PY=$(PY) scripts/run_claude_round2.sh $(R)
clips:          ; FFMPEG=$(FFMPEG) $(SIM) $(PY) scripts/make_clips.py $(R)   # FFMPEG = an ffmpeg binary with libx264; needs MUJOCO_GL=egl-capable libs
