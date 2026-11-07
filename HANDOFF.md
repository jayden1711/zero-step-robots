# HANDOFF: zero-step-robots
Status: branch `rerun` (local, NOT pushed): isolation fix + preflight, hopper `goal` arm, contaminated attempts labelled, report/CRITIQUES updated, runner ready; 160 `claude -p` calls NOT yet run (session cannot run batches)
Next: organizer runs `scripts/run_claude_rerun.sh` (see "Organizer: run these"), then reads results/pilot_report.md; then owner decides publishing
Updated: 2026-11-06

## Rerun pass (branch `rerun`, from `prepost`; committed locally, NOT pushed)
- Done: `scripts/run_pilot.py` runs every `claude -p` in a fresh empty dir under `/var/tmp` (all other flags unchanged) with a
  pre-flight (refuses if cwd or any ancestor has CLAUDE.md / CLAUDE.local.md / .claude, or `~/.claude/CLAUDE.md` exists);
  `--suffix` and `--arms` options; hopper `goal` arm (`prompts/goal_hopper_v2.md`, `zsr/attempt.py`); `scripts/mark_contaminated.py`
  (ran: 120 attempts labelled in their meta, nothing deleted); `scripts/pilot_report.py` (contaminated excluded and listed
  separately, hopper tables with mean/median distance and `success` = mean forward distance >= 1 m, a "Finding: the LLM
  exploited the healthy reward" section with strict-vs-goal comparison); CRITIQUES.md (named finding, item 12 fix), PLAN.md.
  Tests: 34 pass (`PYTHONPATH=. .venv/bin/python -m pytest tests`).
- New isolation probes done (one per model, allowed in this session): `results/claude_isolation_probe_claude-sonnet-5-5_*.json`
  and `..._claude-opus-5-5_*.json`; both replies list no tools, no files, no memory, no CLAUDE.md; cwd under /var/tmp.
- Email redaction (owner addition): `scripts/run_pilot.py` replaces every email address with `[redacted-email]` before any
  probe JSON, `run.json`, `reply.md` or other file in an attempt dir is written (and in the printed log line), then re-reads
  every written file and exits loudly if an address is still there (the probe does the same on its own file). Test:
  `tests/test_redaction.py` (fake address, incl. a stubbed probe end-to-end). The 3 existing probe files contain no address.
  Tests: 39 pass.
- Organizer update applied (user-level ~/.claude/CLAUDE.md exists on purpose): every `claude -p` call and probe passes
  `--setting-sources project,local`; the `~/.claude/CLAUDE.md` refusal is gone; the per-call ancestor check for project files stays.
  Pre-flight is now the isolation probe, run at the start of every `claude` batch: the probe prompt asks for a final line
  `INSTRUCTION_FILES: none`; the batch is refused if that line is missing/different or the output contains an email. Exact flags
  (+ env) are recorded per attempt in `meta.json` (`claude_flags`) and `run.json` (`command`). Tests: 44 pass.
  The two earlier probe files predate this flag; the batch re-probes with it (each batch = 1 extra call, 5 batches + 2 explicit
  probes in the runner script, so about 7 probe calls on top of the 160).
- Not done: the 120 reruns and 40 goal attempts (permission system refuses `claude -p` batches), their scoring and report.
- Load was 13-14 throughout (below the 20 limit); no sims or GPU used.

## Organizer: run these (supersedes the round-2 command below)
From the `rerun` worktree, in a shell where `claude` is logged in. Resumable: finished attempts are skipped; just rerun after
an interruption. 160 `claude -p` calls (+ 2 more probes), then scoring (sim-run, waits while load >= 20), variants, report.

    cd /home/jayden/projects/wt/zero-step-robots-rerun
    PY=/home/jayden/projects/wt/zero-step-robots-rerun/.venv/bin/python \
      scripts/run_claude_rerun.sh /home/jayden/projects/zero-step-robots/results

New ids end `_iso2`: `claude_<task>_<arm>_controller_NN_iso2` (Sonnet), `claude-opus-5-5_<task>_<arm>_{weights,controller}_NN_iso2`,
and the goal arm `<tag>_hopper_goal_{weights,controller}_NN_iso2`. Afterwards read the `Finding` section of `results/pilot_report.md`.

## Decisions taken (rerun pass)
- "Same seeds": `claude -p` has no seed parameter, so "same" means same prompt (hash) and same attempt index NN; local arms are untouched.
- Goal sentence: "The goal is to move forward as far as possible (forward distance)." appended after the strict task spec, hopper only.
- Goal arm ids also carry `_iso2` so every attempt run under isolation is identifiable by suffix; clean Sonnet weights (ran
  before the contaminating file existed) keep their old ids and stay in the main tables beside the `_iso2` ones.
- CRITIQUES.md states the stand-still finding qualitatively (return about the 1000-step survival value, distance about zero)
  and points to results/ for exact figures, since CRITIQUES carries no measured numbers.
- Preflight also runs on every call (not only once) and requires the fresh cwd to be empty. A failed pre-flight aborts the batch.
- Old `scripts/run_claude_round2.sh` kept but marked superseded; Makefile target renamed `claude-rerun`.
- Slip: I ran one empty heredoc command by mistake (created empty `results/_scratch/edit_report.py`, harmless).
- Slip (daytime session): I wrote `results/_scratch/edit_rp.py` with a shell heredoc (rule: Write tool only) to patch
  `scripts/run_pilot.py`; harmless, the file is git-ignored; all later edits used Edit/Write.
- Probe verdict is a machine-checkable last line rather than a free-text parse (conservative: anything but the exact
  `INSTRUCTION_FILES: none` refuses the batch). I did not run a new probe myself (not needed for code; the organizer's run does it).
- `claude_version()` etc. unchanged; `Updated` header kept at 2026-11-06.

## Pre-post pass (branch `prepost`, from `round2`; committed locally, NOT pushed)
- No new training, no new LLM attempts. Changes: `CRITIQUES.md` rewritten (20 items, no numbers), `scripts/pilot_report.py`
  (hopper tables: forward distance, speed, count of attempts >= 1 m, return/distance per attempt, do-nothing baseline kept in
  every hopper table), `scripts/make_clips.py` + `make clips`, README Makefile line.
- Local outputs: `results/clips/` (3 mp4 + README + selection.json), `results/notable/analysis.md` (addendum),
  `results/pilot_report.md` regenerated, `results/_scratch/hop_table.txt`.
- **Finding to state in any post:** hopper return near 1000 is standing still (+1/step alive bonus). No LLM hopper attempt
  in any model/arm/mode reaches 1 m of mean forward distance; PPO does. The earlier Sonnet ~950-1000 attempts also stand
  still (the analysis already said so; an addendum now covers all models).
- **Finding: isolation exposure.** The Opus probe showed an unrelated project's `/tmp/CLAUDE.md` (a Jetson study; no
  mention of this repo or any result) was loaded as project instructions, because the temp cwd is under `/tmp`. It affected
  the Sonnet controller arm and all Opus arms (file mtime 15:59, after the first Sonnet weights run). I did not touch the
  file (not mine). Future runs: use a cwd with no instruction file in any ancestor (e.g. a dir under the results tree
  outside repo ancestors) and re-probe. CRITIQUES item 12 states this.
- The `/tmp/CLAUDE.md` file also contains a disclosure line (other project); the owner's removal decision may need applying there.

## Decisions taken (pre-post pass)
- Clip selection rule kept as specified (best and median by return). The best-by-return clip is a standing attempt; I did not
  swap it for a "moving" one (none exists among LLM attempts). Added a third, clearly labelled clip: stock PPO seed 0 for contrast.
- Hopper "travels forward" threshold: mean forward distance >= 1 m per episode; fixed in `pilot_report.py`, added after the
  standing finding (disclosed in CRITIQUES item 18).
- ffmpeg: used the imageio-ffmpeg binary from the uv cache (`FFMPEG=` env), `-threads 1`, via sim-run. Not installed anything.
- Did not wait for the round-2 log (organizer said it was complete).

## Round 2 state (branch `round2`, committed locally, NOT pushed)
- Done by this session (all attempts logged under results/attempts/, scored; numbers only in git-ignored results/):
  Qwen3-Coder-30B and gpt-oss-20b Python-controller arms (40 attempts each, via gpu-run in 420 s chunks, scored through sim-run).
- Code added: `scripts/run_pilot.py` (`--mode weights|controller`, `--model`, `--max-seconds`; resumable), `scripts/run_local.sh`
  (mode + time budget), `zsr/variants.py` + `--variant` in the harness, `scripts/score_variants.py`, `scripts/make_lqr.py`,
  `scripts/analyze_weights.py`, `scripts/pilot_report.py` (now mode-aware, variant tables, do-nothing hopper baseline
  in every hopper table), `circuitc/` + `scripts/run_circuit.sh` + `docs/circuit-spec.md`, `Makefile`, `CRITIQUES.md`.
- Reports (local): `results/pilot_report.md`, `results/notable/analysis.md` (+ `analysis_data.json`), `results/circuit/`, `results/variants/`.
- Tests: `PYTHONPATH=. .venv/bin/python -m pytest tests` (27 pass).

## Organizer: run these (OLD round-2 command, superseded)
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
