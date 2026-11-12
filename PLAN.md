# zero-step-robots: PLAN (summary; the first session expands it for owner approval)

Question: can an LLM write a working robot controller's weights directly, with zero training steps?
Physics scores every attempt.

Builds on Takehi, Teoh, Zhang, Khattab (MIT CSAIL), "Sparks of Weight-Space Programming: LLMs can natively read &
write neural network weights," Nov 2, 2026. https://rikiyat.github.io/blog/weight-space-programming/
This project extends it to legged robots.

## Part A: write from scratch
The LLM writes **all weights** of small control networks from scratch, in increasing difficulty:
cartpole → hopper → small humanoid balance.

## Part B: edit an existing policy
The LLM edits an existing small walking policy (the distilled walker from humanoid-on-a-chip) so that it:
limps, walks backwards, or tolerates a sensor fault.

## Controls
- random weights
- zero weights
- the same LLM writing a normal Python controller (not weights)
- PPO

## Rules
- **Same information as PPO.** The model gets only what PPO gets: observation/action spec, reward
  definition, episode rules. No extra hints, demonstrations or privileged state.
- **Continuous scores over many episodes** (fixed seeds, many episodes per attempt), not pass/fail.
- **Every attempt is published**, failures included. No cherry-picking. Publishing happens only after the
  owner approves; until then everything stays in git-ignored `results/`.
- **LLM access:** through the owner's subscriptions by hand (prompt files the owner pastes, replies saved back)
  or local models on the NUC. No paid API calls.

## First stop point
1. Environments: cartpole and hopper (fixed versions, seeds, episode length).
2. Scoring harness: loads a weight file or a Python controller, runs N episodes, reports continuous scores.
3. Baselines for cartpole and hopper: random, zero, PPO, plus a reference Python controller to test the harness.
4. Prompt template: what the model is given (the same as PPO), the output format for weights, and the output
   format for a Python controller.

Then stop and report, before any LLM attempts.

## First-stop-point design (for owner approval)
- **Tasks:** cartpole = Gymnasium `InvertedPendulum-v5` (continuous force, so weights can output it directly),
  hopper = `Hopper-v5`. 1000-step episodes. Versions pinned in `requirements.txt` / THIRD_PARTY.md.
- **Policy format:** one hidden layer, 16 tanh units, raw observations, clipped linear output (97 numbers for
  cartpole, 243 for hopper). PPO uses the same actor shape, so its weights export losslessly and go through the
  identical harness.
- **Scoring:** 100 episodes, reset seeds 10000..10099 (training seeds stay below 10000), deterministic policy.
  Reports mean/SEM/median/min/max return, mean length, fraction of full-length episodes, forward distance, and
  faults (a crashing controller keeps the reward earned before the crash, and the fault is logged).
- **Arms:** zero weights, random weights (10 seeds, std 1/sqrt(fan_in)), reference Python controllers (harness
  test only), PPO (3 seeds per task, SB3 defaults, CPU), then LLM-written weights and LLM-written Python.
- **Prompt (v1, arm NAMED):** task spec + reward + episode rules + output format only; no hints, constants or examples.
  The observation components are named as in the Gymnasium docs (needed to state the reward). Each attempt
  records the sha256 of the rendered prompt and of its component files. Replies are parsed from the last fenced
  block; unparsable or invalid replies are scored as failures and kept.

## Prompt arms (owner decision, 2026-11-06)
Two prompt arms, each versioned; every attempt records its arm, prompt version and prompt hash in `meta.json`.
- **STRICT = prompt v2 (main comparison).** Raw numbers only, the same information PPO gets: observation and action
  dimensions and bounds, step time, initial-state noise, and the reward/termination rules written in terms of
  observation indices (`obs[1]`). No sensor names, no robot or environment description.
- **NAMED = prompt v1 (second arm).** Same, plus the Gymnasium observation names and a description of the robot.
- **GOAL (hopper only, owner decision 2026-11-06).** The STRICT prompt plus one sentence (`prompts/goal_hopper_v2.md`)
  stating that the goal is to move forward as far as possible (forward distance); nothing else changed. Sonnet and
  Opus, weights and controller, 10 attempts each. Success for every hopper arm = mean forward distance >= 1 m over the
  100 scoring episodes; return and forward distance are always reported together.
- Files: `prompts/*_v2.md` (strict), `prompts/*_v1.md` (named). `python -m zsr.attempt new ... --arm strict|named|goal`
  (default strict). Never edit a released prompt file; a change is a new version.
- **Isolation (fixed 2026-11-06).** Every `claude -p` call runs in a fresh empty dir under `/var/tmp`; a pre-flight
  refuses to run if any ancestor of the cwd has `CLAUDE.md`, `CLAUDE.local.md` or `.claude`; calls pass
  `--setting-sources project,local` (no user-level settings or CLAUDE.md), and each batch starts with an isolation
  probe whose last line must be `INSTRUCTION_FILES: none`. (The account email in the session context is expected and is
  redacted before anything is written.) The first-round Sonnet weights arm predates `--setting-sources` and was not rerun
  (see CRITIQUES.md item 12). Attempts that ran with an unrelated `/tmp/CLAUDE.md` loaded are labelled
  `contaminated` in their meta, kept, excluded from main tables, and rerun with ids ending `_iso2`.

## Pilot (owner decisions, 2026-11-06)
Models: subscription CLIs and local models only, no API keys.
- **Claude via `claude -p`**, one reply per attempt, matching the MIT setup. Each call runs with cwd = a fresh empty
  temp dir outside any repo, all tools disabled (`--tools ""`), no MCP servers (`--strict-mcp-config`), no session
  persistence, a fresh context per attempt (no --continue/--resume), auto-memory off. It cannot see the repo or run
  code. Before the pilot, one probe call asks it to list its tools and any files/instructions it can see; the reply is
  saved in `results/pilot/` as evidence of isolation. CLI version and model id are recorded per attempt.
- **GPT via Codex CLI, Gemini via Gemini CLI: SKIPPED.** Codex on the owner's Mac is logged in with an API key, not a
  subscription; Gemini CLI is not installed.
- **Local open baselines:** gpt-oss-20b and Qwen3-Coder-30B (GGUFs in `~/models`), served with llama.cpp through
  `gpu-run`, one at a time, queued behind other GPU jobs. gpt-oss reuses robot-framing-test's download once its
  SHA-256 is recorded in `~/models/SHA256SUMS.wiif`.
- **Size:** 10 attempts per model x task (cartpole, hopper) x arm (strict, named), weights mode. Same prompt text for
  every model. Python-controller mode is not part of the pilot.
- **Logged per attempt** in `results/attempts/<id>/`: rendered prompt + sha256 (`prompt.md`, `meta.json`), raw reply
  (`reply.md`, plus `run.json` with the raw CLI/server output), parse result and score (`score.json`),
  model/version, timing, sampling settings. Local models use the vendor-recommended sampling settings, a fixed seed
  per attempt index; the `claude -p` CLI exposes no sampling settings (defaults).
- Runner: `scripts/run_pilot.py` (and `scripts/run_local.sh` for the local models). The pilot ends with
  `results/pilot_report.md` (local); then stop.

## Round 2 (owner decisions, 2026-11-06)
- **Python-controller arm for every model on both tasks** (the key comparison): same isolation, same 10 attempts per
  model x task x arm (STRICT and NAMED), same scoring harness. Controllers run only through `sim-run` with the rlimits.
- **Claude Opus 5.5 (`claude-opus-5-5`) alongside Sonnet 5.5 (`claude-sonnet-5-5`)**, 10 attempts per task and arm,
  weights and controller modes. The Claude runs are done by the organizer (`scripts/run_claude_round2.sh`); local
  models run through `gpu-run`.
- **Modified-physics variants** (`zsr/variants.py`) of both tasks; every arm is scored on them.
- **Baselines added:** cartpole LQR (`scripts/make_lqr.py`); the do-nothing (zero-weights) policy is in every hopper table.
- **Notable attempts:** the high-scoring hopper weight attempts get a structural and robustness analysis
  (`scripts/analyze_weights.py`); local only.
- **Circuit-compiler track** (`docs/circuit-compiler-track.md`, `docs/circuit-spec.md`, `circuitc/`): first working
  compile on both tasks; no LLM spec attempts yet.
- **Criticism-proofing:** `CRITIQUES.md` lists the objections and the evidence or limitation for each. Every number in a
  future post must trace to a file under `results/` and a `make` target.


## Addendum 2026-11-09: raised target (owner decision)

Source: the owner's hard-target audit (approved 2026-11-09, about 00:45 CST, relayed by the organizer). Standing owner rule: a target must be
hard enough that a skeptical expert would be impressed, simple baselines must fail it meaningfully, the task must force the interesting
behavior, and there must be a learning signal (partial credit or a curriculum).

**Ordering.** This addendum is committed before any attempt toward the target below. No run toward it starts before this commit (its hash is
recorded in `~/projects/worklane-notes/addenda-2026-11-09.md`). Every earlier arm and its result stays reported exactly as it was:
- pilot;
- round 2;
- strict, named and goal arms;
- the isolated rerun;
- the circuit-compiler first compiles;
- return-based tables;
- the 1 m goal-arm success rule.

### Target and success bar
- **Hopper, scored on distance.** `Hopper-v5` (pinned version, 1000-step episodes, the existing 100 scoring episodes). The score is the
  **mean forward distance**, not return.
  - An attempt **passes at >= 3 m**.
  - This closes the stand-still game: a controller that collects the healthy reward without moving scores 0 m.
- **Walker2d**, added under the same rule: `Walker2d-v5` (the version is pinned in `requirements.txt` and `THIRD_PARTY.md` at the code
  commit that adds it). It uses the same episode length and scoring-episode count, and an attempt passes at a mean forward distance
  of >= 3 m.
- **Arm result.** An arm (model x task x mode x hint level) **meets the target** when **at least 5 of its 10 attempts pass**. The best
  attempt is reported separately and never stands in for the arm.
- Return is still reported next to distance in every table.

### Necessity table (produced and committed to `results/` before any claim on this target)
- **Rows, on both tasks, same scoring episodes:**
  - the zero-weights (do-nothing) policy;
  - a random policy;
  - the highest-return stand-still attempt from the earlier hopper arms (the healthy-reward exploit);
  - a fall-forward controller (a single fixed lunge);
  - an open-loop sinusoid gait whose amplitude, frequency and phase are tuned on dev seeds only.
- **Columns:** mean, median and min forward distance, return, and full-length episode fraction.
- **Rule:** each simple baseline must fail the 3 m bar meaningfully, with a mean below 1.5 m (half the bar).
- PPO, trained on the default reward at the existing budget, is reported as an upper reference, not as a baseline that must fail.
- If the open-loop gait passes 3 m, that is reported and the bar is raised by a further dated addendum before any claim is made.

### Learning signal
- **Partial credit = mean forward distance** (continuous, negative allowed). It is reported for every attempt, so near-misses are
  visible.
- **Curriculum through circuit-spec gait hints** (`docs/circuit-spec.md`, `circuitc/`). The hint levels are fixed text, frozen with a
  SHA-256 in `prompts/` before the first attempt:
  - **H0**: no hint (the goal prompt with the distance objective);
  - **H1**: the circuit-spec template with a named oscillator / phase structure for the gait;
  - **H2**: H1 plus admissible ranges for frequency and joint amplitudes.
- Every arm runs at each level in that order. The result is the lowest level at which the arm meets the target, plus the partial-credit
  curve over the levels.

### What changes and what stays
- **Changes:**
  - hopper scoring for this target (distance, not return);
  - Walker2d-v5 is added, with its actor shape for weights mode taken from the env;
  - the hint-level prompts;
  - the necessity table.
- **Stays:**
  - isolation (fresh empty dir under `/var/tmp` with the pre-flight check);
  - models and attempt counts;
  - sampling as before;
  - the scoring harness and rlimits;
  - controllers through `sim-run`, local models through `gpu-run`;
  - the contamination labelling;
  - CRITIQUES tracking.

## Addendum 2026-11-09 (b): CPG track (owner decision)
Pre-registration in [docs/prereg-2026-11-09-cpg.md](docs/prereg-2026-11-09-cpg.md), committed before any code, prompt,
baseline or attempt of the track. The LLM writes an oscillator / CPG network through `circuitc` (format `cpg-v1`);
target: Hopper-v5, then Walker2d-v5, at least 3 m forward without falling; hint levels H2 -> H1 -> H0; timebox ends 2026-11-23.
Result (2026-11-09): all 120 pre-registered Claude attempts ran; the target was not met (see CRITIQUES.md, CPG track;
numbers in `results/cpg_report.md`).

## Addendum 2026-11-10: CPG feedback arm (owner decision)
Pre-registration in [docs/prereg-2026-11-10-cpg-feedback.md](docs/prereg-2026-11-10-cpg-feedback.md), committed before any
code, prompt, baseline or attempt of the arm: the model revises its cpg-v1 design 5 times from a fixed dev-seed rollout
summary; round-5 design scored on held-out seeds; baselines: the no-feedback arm and random-search proposers with the same
budget. The no-feedback result stays as reported.
Result (2026-11-10): all 240 pre-registered calls ran; the arm-level target was not met on either task, but 2 of 10 Opus
hopper attempts pass the 3 m bar (see CRITIQUES.md, CPG feedback arm; numbers in `results/cpg_feedback_report.md`).
