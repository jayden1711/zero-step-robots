# HANDOFF: zero-step-robots
Status: pilot partly run: Qwen3-Coder-30B arm done and scored (40 attempts); Claude arm refused by permissions (command below); gpt-oss arm queued behind robot-framing-test's GPU server
Next: owner runs the Claude command below; check gpt-oss arm finished (else re-run its command), then score_pending.sh + pilot_report.py; read results/pilot_report.md and stop
Updated: 2026-11-06

## Pilot run state (day-1106 branch, NOT pushed)
- Runner code: `scripts/run_pilot.py`, `scripts/run_local.sh`, `scripts/score_pending.sh`. Results go to `/home/jayden/projects/zero-step-robots/results/` (git-ignored; baselines live there too).
- **Claude arm: launching it from this session was denied by the permission system, so it was not worked around.** Isolation probe (`claude -p`, empty cwd, no tools) did run; saved as `results/pilot/claude_isolation_probe_*.json`. Run the 40 attempts yourself:
  `cd <repo>/.claude/worktrees/day-1106 && <python> scripts/run_pilot.py claude --results /home/jayden/projects/zero-step-robots/results --n 10 --model claude-sonnet-5-5`
  (use `/home/jayden/projects/zero-step-robots/.claude/worktrees/first-stop-point/.venv/bin/python` as the python). Resumable: finished attempts are skipped.
- **Qwen3-Coder-30B arm: DONE and scored** (40 attempts, all logged in results/attempts/; interim `results/pilot_report.md` built by `scripts/pilot_report.py <results>`; rerun it after the other arms). Command used: `PY=<that python> scripts/run_local.sh qwen3-coder-30b /home/jayden/projects/zero-step-robots/results` was queued via gpu-run (waits up to 12 h). The GPU lock was still held by robot-framing-test's llama-server (its pilot had finished; the server was idle). Not touched. If the queued job is gone, re-run the command.
- **gpt-oss-20b arm:** GGUF now present with SHA-256 in `~/models/SHA256SUMS.wiif`. Queued via gpu-run behind robot-framing-test's gptoss server (not touched); may not have started. Command: `scripts/run_local.sh gpt-oss-20b <results>`.
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
