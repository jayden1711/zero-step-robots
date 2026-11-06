# HANDOFF: zero-step-robots
Status: round 2 prepared on branch `round2` (local, NOT pushed): local-model controller arms done and scored, variants, LQR, notable analysis, circuit compiler first compile, CRITIQUES.md; Claude arms (Sonnet controller, Opus both modes) waiting for the organizer
Next: organizer runs the commands under "Organizer: run these", then reads results/pilot_report.md and results/notable/analysis.md; no LLM spec attempts for the compiler until the owner says go
Updated: 2026-11-06

## Round 2 state (branch `round2`, committed locally, NOT pushed)
- Done by this session (all attempts logged under results/attempts/, scored; numbers only in git-ignored results/):
  Qwen3-Coder-30B and gpt-oss-20b Python-controller arms (40 attempts each, via gpu-run in 420 s chunks, scored through sim-run).
- Code added: `scripts/run_pilot.py` (`--mode weights|controller`, `--model`, `--max-seconds`; resumable), `scripts/run_local.sh`
  (mode + time budget), `zsr/variants.py` + `--variant` in the harness, `scripts/score_variants.py`, `scripts/make_lqr.py`,
  `scripts/analyze_weights.py`, `scripts/pilot_report.py` (now mode-aware, variant tables, do-nothing hopper baseline
  in every hopper table), `circuitc/` + `scripts/run_circuit.sh` + `docs/circuit-spec.md`, `Makefile`, `CRITIQUES.md`.
- Reports (local): `results/pilot_report.md`, `results/notable/analysis.md` (+ `analysis_data.json`), `results/circuit/`, `results/variants/`.
- Tests: `PYTHONPATH=. .venv/bin/python -m pytest tests` (27 pass).

## Organizer: run these
The session could not run `claude -p` (permission system refuses batches). From the `round2` worktree, in a shell where
`claude` is logged in (120 calls: Sonnet 5.5 controller arm, Opus 5.5 weights + controller arms, plus an Opus isolation probe).
Resumable: finished attempts are skipped, so just rerun after an interruption.

    cd /home/jayden/projects/zero-step-robots/.claude/worktrees/round2
    PY=/home/jayden/projects/zero-step-robots/.claude/worktrees/first-stop-point/.venv/bin/python \
      scripts/run_claude_round2.sh /home/jayden/projects/zero-step-robots/results

That script runs, in order:
1. `run_pilot.py probe --model claude-opus-5-5` (isolation probe)
2. `run_pilot.py claude --n 10 --model claude-sonnet-5-5 --mode controller`
3. `run_pilot.py claude --n 10 --model claude-opus-5-5 --mode weights`
4. `run_pilot.py claude --n 10 --model claude-opus-5-5 --mode controller`
5. `score_pending.sh` (sim-run), `score_variants.py` (sim-run, looped until it prints `complete`), `pilot_report.py`.
Attempt ids: `claude_<task>_<arm>_controller_NN` (Sonnet), `claude-opus-5-5_<task>_<arm>_{weights,controller}_NN` (Opus).
Afterwards: `make notable` is not needed again; read `results/pilot_report.md`.

## Decisions taken (round 2)
- Branch: the task text named `day-1106` first and `round2` in the owner's decisions; the earlier session had already
  started `round2`, so I continued there. The `day-1106` worktree is empty (at main) and can be removed.
- (c) Three, not two, Sonnet hopper weight attempts scored in the ~950-1000 range (named_01, strict_04, strict_08); all
  three are copied to results/notable/ and analysed. They are selected on score; the analysis says so.
- Variants (fixed before any attempt was scored on them): cartpole pole_long (length x2), pole_heavy (density x3),
  gravity_low (x0.5), gravity_high (x2); hopper torso_heavy (density x2), torso_light (density x0.5). Same reward,
  termination and seeds. Every arm, every attempt, is scored on every variant.
- LQR: Q = I, R = 1, no tuning, discrete Riccati solved by iteration in numpy (no scipy; installed nothing). One
  controller per variant plus the stock one, which is scored on all variants.
- Local arms ran in 420 s chunks in the foreground (no background jobs), GPU only through gpu-run, one model at a time.
- Compiler: JSON spec with two primitives (`linear` with declared range/tolerance, `reflex`) plus bias; oscillators
  and anything else are compile errors. The two fixtures in `circuitc/examples/` were written by me as compiler tests;
  they are not LLM outputs and are labelled that way in the report. No LLM wrote a spec.
- Related work in README: only items relevant to this repo are cited; PicoGPT, vla.cpp, Hirundo, CrowdStrike and
  Booz Allen are not cited (not relevant here). RoboStriker, URMA/MetaMorph and Text2Robot are cited by name and
  marked [verify] (no web check). THIRD_PARTY.md rows for llama.cpp and the models are marked [verify] where upstream
  sources/licences were not checked.
- `scripts/pilot_report.py` previously keyed cells without the mode and would have mixed weights and controller
  attempts; fixed.
- Not done: nothing pushed; no changes outside the repo and results/.


## Pilot run state (day-1106 branch, NOT pushed)
- Runner code: `scripts/run_pilot.py`, `scripts/run_local.sh`, `scripts/score_pending.sh`. Results go to `/home/jayden/projects/zero-step-robots/results/` (git-ignored; baselines live there too).
  `cd <repo>/.claude/worktrees/day-1106 && <python> scripts/run_pilot.py claude --results /home/jayden/projects/zero-step-robots/results --n 10 --model claude-sonnet-5-5`
  (use `/home/jayden/projects/zero-step-robots/.claude/worktrees/first-stop-point/.venv/bin/python` as the python). Resumable: finished attempts are skipped.
- **Qwen3-Coder-30B arm: DONE and scored** (40 attempts, all logged in results/attempts/; interim `results/pilot_report.md` built by `scripts/pilot_report.py <results>`; rerun it after the other arms). Command used: `PY=<that python> scripts/run_local.sh qwen3-coder-30b /home/jayden/projects/zero-step-robots/results` was queued via gpu-run (waits up to 12 h). The GPU lock was still held by robot-framing-test's llama-server (its pilot had finished; the server was idle). Not touched. If the queued job is gone, re-run the command.
- **gpt-oss-20b arm: DONE and scored** (40 attempts, served via gpu-run after robot-framing-test released the GPU; reasoning effort medium).
- Scoring (after replies exist): `PY=<python> scripts/score_pending.sh /home/jayden/projects/zero-step-robots/results` (sequential, through sim-run).
- Codex CLI / Gemini CLI arms skipped (owner decision, see PLAN.md).

## What exists
- `zsr/` package: tasks (cartpole = InvertedPendulum-v5, hopper = Hopper-v5, 1000 steps), weight format
  (16-tanh MLP JSON), harness, PPO, attempt/prompt/reply-parsing tooling. `tests/` (11 pass): `pytest tests`.
- Prompt template v1 in `prompts/`; `python -m zsr.attempt prompt <task> <weights|controller>` prints a prompt,
  `new` creates `results/attempts/<id>/` with prompt.md + meta.json (prompt hash, model, interface), `score` parses
  `reply.md` and scores it (failures are scored and kept).
- Baselines (zero, random x10 seeds, reference Python controller, PPO x3 seeds per task) are all scored with the
  same harness (100 episodes, seeds 10000..10099). Files: `results/baselines/*.score.json` and
  `results/baselines/ppo/` in the MAIN checkout (git-ignored). Numbers deliberately not quoted here.
- Venv: `.venv` in the worktree (git-ignored); recreate with requirements.txt. Run with `PYTHONPATH=.`.

## Things to know
- The PPO weights score full marks on cartpole through the harness, which confirms the weight export is lossless.
- The hopper reference controller is weak by design (random-search linear policy, harness test only, not an arm to
  beat). It overfit its 5 search episodes.
- Python controllers run in the harness process with rlimits (4 GB, 3600 s CPU); that is not a sandbox. Run LLM code
  only through sim-run on the NUC.
- The worktree is `.claude/worktrees/first-stop-point`; merge or cherry-pick the branch to main when happy, then push.

## Decisions taken overnight
- Cartpole uses Gymnasium `InvertedPendulum-v5` (continuous action) rather than discrete `CartPole-v1`, so weights
  can emit a force directly. Conservative: standard, documented env.
- Prompt names the observation components (from Gymnasium docs) because the reward definition refers to them. This
  is arguably slightly more than PPO's raw numbers; drop the names if you want strict parity.
- Same 16-unit tanh architecture is given to the LLM and used by PPO (PPO also has a separate 64x64 value net,
  which is training-only and not part of the policy).
- PPO: SB3 default hyperparameters, no tuning (cartpole 100k steps, hopper 1M steps, 3 seeds). Scored once; not
  re-run or picked from.
- Ran at most 2 sim processes of my own at a time because other projects had sims running.
- No attempt directories were created under results/attempts/ (tests used a temp dir).
- Installed Python packages into a project venv from PyPI (pip worked, no blocks).

## Day 1106 (branch `day-1106`, committed locally, NOT pushed)
- Added prompt v2 (STRICT: raw numbers, reward in terms of `obs[i]`, no names) as `prompts/*_v2.md`; v1 is now the
  NAMED arm, unchanged. `zsr/attempt.py` takes `--arm strict|named` (default strict); meta.json records arm, prompt
  version and hashes. Tests (12) cover: no sensor names in strict prompts, distinct hashes, arm recorded.
- PLAN.md records both arms. No attempt directories were created.
- Venv for this branch: reuse `../first-stop-point/.venv` (run with `PYTHONPATH=.`) or recreate from requirements.txt.

## Blocked: what is needed to start LLM attempts
1. **PLAN.md names no LLMs and no attempt counts**, so I could not follow "the LLMs and attempt counts PLAN.md
   specifies". Please write: which models, via which interface, and N attempts per (model, task, mode, arm).
2. Hand-pasted subscription models: nothing needed from me but the list; I will generate prompt files with
   `python -m zsr.attempt new <id> <task> <mode> --model M --interface 'subscription UI (pasted by hand)' --arm ...`
   and you paste each `prompt.md`, save `reply.md`, then `... score <id>`.
3. Local model: only `~/models/Qwen3-Coder-30B-A3B-Instruct-Q4_K_M.gguf` is present. It is served via gpu-run
   (~10.2 GB resident), but the GPU lock is currently held by robot-framing-test for hours, so no GPU work was done.
   Whether Qwen3-Coder counts as one of the planned LLMs is your call. No download needed for it.
4. No API keys or paid spend are involved in any of the above.

## Decisions taken (day 1106)
- STRICT prompt keeps the generic sentence "every position and velocity is perturbed by a small uniform random
  amount" (initial-state noise, part of the episode rules); no sensor is named.
- STRICT hopper reward states that the forward term v is the change of an *unobserved* x coordinate over the step
  and that obs[5] is a related but non-identical instantaneous reading. Conservative: accurate to the environment,
  without telling the model which physical quantity obs[5] is.
- STRICT also drops the Gymnasium/MuJoCo env names and robot description (they would leak the semantics).
- Branch renamed from the tool default to `day-1106`.
- Did not pick an LLM or attempt count myself, did not run the local model, did not create any attempt dirs.

## Decisions taken (day-1106)
- Pilot uses weights mode only (Python-controller mode not in the owner's pilot spec).
- Claude model pinned to `claude-sonnet-5-5` explicitly (not the session default); auto-memory disabled via env for the probe and runs. The probe reply still showed the account email and a system prompt that names tools; no repo, memory or instructions leaked.
- Local sampling: vendor-recommended settings, seed 1000+attempt index; gpt-oss at reasoning effort medium (same as robot-framing-test).
- Did not stop or contact robot-framing-test's idle server holding the GPU lock.
- Did not retry the denied Claude launch with other wrappers.
