# Criticisms a skeptical expert would raise, and how this repo answers them

No result numbers here. Numbers live in the git-ignored `results/` (paths below) until the owner approves publishing.
Each item is one of: **Addressed** (where), **Extra experiment** (what, and whether it was run), or **Limitation**
(stated up front). Everything is simulation (MuJoCo through Gymnasium); no real robot is involved anywhere.

Scope of the evidence: models claude-sonnet-5-5 and claude-opus-5-5 (subscription CLI), Qwen3-Coder-30B (4-bit GGUF) and
gpt-oss-20b (local, via llama.cpp); tasks cartpole (`InvertedPendulum-v5`) and hopper (`Hopper-v5`); two prompt arms
(STRICT, NAMED, plus a hopper-only GOAL arm for Sonnet and Opus); two output modes (weights, Python controller); ten attempts per model x task x arm x mode cell; baselines
zero, random, hand-written reference controller, LQR (cartpole), PPO; modified-physics variants; a circuit-compiler first compile.

Reproduction: every table is produced by a `make` target (see `Makefile`); attempt directories hold the raw prompt,
reply, parsed artefact, score, model id, CLI/server version, sampling settings, timing, seeds and prompt hash.
Main report: `results/pilot_report.md`. Clips: `results/clips/` (`make clips`).

## About the task and the reward

1. **"Cartpole is trivial."** Addressed, and stated plainly: cartpole (Gymnasium `InvertedPendulum-v5`) is an easy
   problem; a four-gain linear controller solves it, and the baselines show it (untuned LQR from the MuJoCo model,
   `scripts/make_lqr.py`; the hand-written reference, `controllers/cartpole_reference.py`; PPO). Cartpole results are a
   sanity floor and a check that the harness and weight format work, not evidence of capability. Table:
   `results/pilot_report.md`, cartpole sections, baseline rows. The more informative cartpole tables are the
   modified-physics variants (item 3).
2. **"On hopper it just learned to stand still."** / **"The reward rewards standing."** Both are correct, and the work
   says so. Hopper-v5 pays +1 per healthy step plus a forward-velocity term, so a policy that stays upright for 1000
   steps without moving scores near the maximum for standing, while a PPO policy that moves forward earns more per step
   but often falls before 1000 steps. Therefore: (a) every hopper table in `results/pilot_report.md` reports forward
   distance and forward speed next to the return, a count of attempts that travel at least 1 m (threshold fixed in the
   script), and the per-attempt return/distance pairs; (b) the do-nothing (zero-weights) baseline is in every hopper
   table (it falls early, so standing is better than nothing); (c) `results/notable/analysis.md` (addendum) states which
   attempts move forward; (d) the clips (`results/clips/README.md`) show the best and median LLM attempts standing, next to
   PPO moving. No claim of hopping or locomotion is made for any LLM attempt unless the table shows forward distance for
   it. **Limitation:** a standing score is not evidence of locomotion, and the post must say so beside every hopper
   number. A forward-speed-only metric, or a harder task (get from A to B), would separate these cases better and was not
   used, so as not to change the reward after seeing the results; this is stated as a limitation, not run.

**Named finding: "the LLM exploited the healthy reward."** When the prompt gives the reward and nothing about the goal,
LLM-written hopper policies that score highest by return are the ones that stand still: return at the value of surviving
1000 steps (+1 per step, so about 1000) and forward distance about zero. The model reads "reward = 1 while healthy + a
velocity term" and optimises the term that is cheap to get, which is what the scoring literally asks for. This holds for
weights and for Python controllers, so it is not an artefact of the weight format. The comparison that tests whether it
is a prompt-framing effect is the hopper `goal` arm: the STRICT prompt plus one sentence stating that the goal is to move
forward as far as possible (forward distance), nothing else changed, same models, modes, attempt indices and isolation.
Success for every hopper arm, old and new, is a mean forward distance of at least 1 m over the 100 scoring episodes;
the report shows return and distance side by side with the success count, and a "Finding" section comparing STRICT
with `goal` per model and mode (`results/pilot_report.md`; exact figures live there, not in git). Do not describe
standing as locomotion in any post, and describe the `goal` result only as measured there.
3. **"It memorised published solutions."** Addressed in part. Modified-physics variants (`zsr/variants.py`, chosen
   before any attempt was scored on them): pole length, pole mass and gravity for cartpole; torso mass for hopper.
   Every arm (baselines, every LLM attempt, compiled circuits) is scored on every variant by the same harness
   (`scripts/score_variants.py`, files in `results/variants/`, tables in `results/pilot_report.md`). The stock-model LQR is
   scored on the variants too, so how much a fixed controller transfers is visible, and a matched LQR per variant is the
   reference. **Limitation:** variants are single-parameter changes; they show whether stock-tuned numbers transfer, not that
   the model derived anything from physics. General control knowledge (PD structure) can come from training data; we do
   not claim otherwise, and we cannot tell recall from derivation from the outputs alone.
4. **"It's just a controller in disguise."** Addressed. (a) The Python-controller arm: every model writes an ordinary
   Python controller on both tasks with the same prompts and attempt counts, scored by the same harness; weights and
   controller distributions sit side by side in the report. (b) Weight analysis of the high-scoring hopper attempts
   (`scripts/analyze_weights.py`, `results/notable/analysis.md`): they are linear PD posture-holds inside a tanh network
   that never saturates. The honest framing: the weight arm tests whether a model can *express* a known controller in
   weight space, not that it invented a new kind of control. **Limitation:** the analysis covers three attempts of one
   model, selected on score.
5. **"Only two simple tasks."** Limitation, stated up front. Humanoid and Part B (editing an existing policy) are not
   started and are not claimed.
6. **"Return rewards survival, not the behaviour you care about."** Addressed by item 2: distance, episode length and the
   fraction of full-length episodes are reported next to the return for hopper.

## About the evidence

7. **"Cherry-picked."** Addressed. Every attempt is logged and scored, failures included (`results/attempts/*/`); the
   report lists all attempts per cell with mean, median, IQR, min, max and the full per-attempt list, plus counts of
   unparsable replies and mid-episode crashes (`scripts/pilot_report.py`). The notable-attempts analysis is labelled as
   selected on score. The clips are one best and one median attempt chosen by a rule written in `scripts/make_clips.py`
   before viewing, each labelled with its rank; the best-by-return clip turned out to be a standing attempt and was kept
   rather than swapped (`results/clips/README.md`). All attempts will be published, not a selection.
8. **"Ten attempts per cell is small."** Limitation. Spreads are reported, no significance claims are made, and claims are
   descriptive ("in these attempts"). Extra experiment if wanted: more attempts for the local models are cheap (one
   command per arm, `make local-weights|local-controller`); not run, to keep the pre-specified size. Hosted-model arms
   are bounded by subscription use.
9. **"Scores are noisy or overfit to the evaluation seeds."** Addressed. 100 fixed episodes per score with reset seeds
   disjoint from any training seed; each attempt is scored once, with no selection among attempts. The three notable
   attempts were re-scored on 500 fresh seeds (`results/notable/analysis_data.json`); one of them degrades there, and the
   analysis says so. Extra experiment, cheap, not run: re-score all high-return hopper attempts on fresh seeds.
10. **"The PPO baseline is weak or untuned."** Limitation. PPO uses Stable-Baselines3 defaults with no tuning, 3 seeds and a
    fixed step budget (`results/baselines/ppo/*.log`). It is a reference for what a standard untuned learner gets, not
    state-of-the-art RL, and the post must not call it the best RL can do. It also uses training steps, which the LLM
    arms deliberately do not. On hopper its policies often fall before 1000 steps; return and distance are reported together.
11. **"Different arms see different information."** Addressed. The prompt carries only what PPO gets (observation/action
    spec, reward, episode rules); no hints, constants or example weights. Two arms: STRICT (raw numbers,
    `prompts/*_v2.md`) and NAMED (Gymnasium observation names, `prompts/*_v1.md`). Prompts are versioned, hashed per
    attempt (`meta.json`) and published verbatim. **Limitation:** NAMED gives more than PPO's raw numbers, which is why
    STRICT is the main comparison.
12. **"The harness leaked information to the model."** Addressed in part, with one disclosed exposure. `claude -p` runs
    with a fresh empty temporary cwd outside any repo, tools disabled, no MCP, no session persistence, auto-memory off;
    probes asked the model to list what it could see (`results/pilot/claude_isolation_probe_*.json` for Sonnet;
    `results/claude_isolation_probe_20261106T162104.json` for Opus). The Sonnet probe showed no project files. **The
    Opus probe showed that a `CLAUDE.md` belonging to an unrelated project sat in `/tmp`, an ancestor of the temporary
    cwd, and was loaded as project instructions. It concerns a different project (a Jetson timing study), mentions neither
    this repo, hopper, cartpole, weights nor any result, but it was in the context of the attempts that ran after that file
    appeared (the Sonnet controller arm and all Opus arms; the first Sonnet weights arm ran before the file existed, by
    file and attempt timestamps).** Not claimed to be harmless beyond what its contents show. **Fix (branch `rerun`):**
    `scripts/run_pilot.py` now runs every `claude -p` call in a fresh empty directory under `/var/tmp`, with a pre-flight
    that refuses to run if the cwd or any ancestor holds `CLAUDE.md`, `CLAUDE.local.md` or `.claude`; every call also
    passes `--setting-sources project,local`, so a user-level `~/.claude/CLAUDE.md` is not loaded. Each batch first runs the
    isolation probe and is refused if the probe reports any instruction file or its output contains an email address.
    The exact flags are recorded per attempt (`meta.json`, `run.json`). Probe files are in
    `results/claude_isolation_probe_<model>_*.json`. The 120 contaminated attempts are kept untouched, labelled `contaminated: /tmp/CLAUDE.md` in
    their `meta.json`, excluded from every main table and listed in their own report section; they were rerun with the
    same prompts and attempt indices as ids ending `_iso2`. Also, the account email address and a system
    prompt naming tools were visible to the model. No repo contents, results or memory were. Local models only receive the
    prompt through a local server API. Prompts do not contain results. **Limitation** as above.
13. **"Hosted-model runs aren't reproducible."** Limitation. The CLI exposes no sampling settings or seed; results vary
    between runs and between model snapshots. We record raw output, CLI version, reported model id and date per attempt,
    so runs are auditable, not exactly repeatable. Local runs record seed, sampling parameters and server version, but
    llama.cpp output is not guaranteed bit-identical across hardware.
14. **"Local models are quantised and small, so this says little about LLMs in general."** Limitation. Qwen3-Coder-30B runs
    as a 4-bit GGUF and gpt-oss-20b as MXFP4 with vendor-recommended sampling; results describe those builds only. Token
    limits and reasoning effort differ per model and are recorded in `run.json`.
15. **"A subscription CLI model and local models are not comparable."** Limitation, stated in the report header:
    interface, sampling and context differ per model. The controlled comparisons are within-model (weights vs Python
    controller, STRICT vs NAMED) and against the baselines.
16. **"Generated code was executed."** Limitation. LLM-written Python controllers run in the harness process with CPU and
    memory rlimits; that is not a sandbox. They are run only through `sim-run` on the NUC, replies are kept, crashes are
    scored and logged. Do not run untrusted controllers elsewhere.
17. **"Models were compared at different times / model versions."** Limitation. Attempts ran on 2026-11-06 with the model
    ids recorded per attempt; later snapshots may behave differently.
18. **"Variants and thresholds were tuned after seeing results."** Addressed. Variant parameters, the 1 m "travels"
    threshold, the scoring seeds, and the clip selection rule are fixed in code that predates the corresponding results,
    and git history shows when. The 1 m threshold was added to the report after the standing finding, so it is
    post-hoc in time; it is a coarse floor, not tuned, and the per-attempt distances are listed so readers can apply
    their own. The `goal` arm and the isolated rerun were specified (2026-11-06) before any of their attempts existed.

## About the method track

19. **"The circuit-compiler spec is just a controller written in another notation."** Limitation, stated up front: the
    compiler is deterministic code, and a compiled spec is only as capable as the spec. What it measures is whether
    expressing a design as a spec and compiling it removes weight-arithmetic errors. So far only two spec fixtures written
    by the repo author (not an LLM) have been compiled, as tests of the compiler; **no claim is made about LLM spec
    writing** until those attempts are run. The hopper fixture holds the pose and does not hop. Exactness is tested per
    primitive (`tests/test_circuitc.py`); a `linear` primitive is exact only within a declared range and tolerance.
20. **"No novelty relative to prior work."** Limitation. This builds on the MIT weight-space post and related work in
    `README.md`; the contribution, if any, is the controlled comparison across arms, tasks and modes with all attempts
    logged, not the idea of writing weights by hand. Some references are marked [verify] because they could not be
    checked offline.
