# Criticisms a skeptical expert would raise, and how this repo answers them

No result numbers here. Numbers live in the git-ignored `results/` (paths below) until the owner approves publishing.
Each item is one of: **Addressed** (where), **Extra experiment** (what, and whether it was run), or **Limitation**
(stated up front). Everything is simulation (MuJoCo through Gymnasium); no real robot is involved anywhere.

Reproduction: every table is produced by a `make` target (see `Makefile`); attempt directories hold the raw prompt,
reply, parsed artefact, score, model id, CLI/server version, sampling settings, timing, seeds and prompt hash.

## About the task

1. **"Cartpole is trivial."** Addressed, and stated plainly: cartpole (Gymnasium `InvertedPendulum-v5`) is an easy
   problem; a four-gain linear controller solves it. A linear baseline is in every cartpole table: an LQR computed from
   the MuJoCo model (`scripts/make_lqr.py`, Q = I, R = 1, untuned) and the hand-tuned linear reference
   (`controllers/cartpole_reference.py`). Cartpole results are a sanity floor, not evidence of capability. Table:
   `results/pilot_report.md`, cartpole sections, baseline rows.
2. **"A return near 1000 on hopper just means it stands; that isn't hopping."** Addressed. Every hopper table carries a
   median forward-distance column, the do-nothing (zero-weights) baseline, and the PPO baseline that does move forward.
   `results/notable/analysis.md` shows the high-scoring hopper attempts hold a pose and do not hop. No claim of
   locomotion is made for them.
3. **"It memorised published solutions."** Addressed in part. Modified-physics variants (`zsr/variants.py`): pole length,
   pole mass and gravity for cartpole; torso mass for hopper. Every arm (baselines, every LLM attempt, compiled circuits)
   is scored on every variant by the same harness (`scripts/score_variants.py`, files in `results/variants/`, tables in
   `results/pilot_report.md`). A stock-model LQR is scored on the variants too, so its transfer is visible. The variants
   were written before any attempt was scored on them. **Limitation:** variants are single-parameter changes; they
   show whether stock-tuned numbers transfer, not that the model derived anything from physics. General control
   knowledge (PD structure) can still come from training data; we do not claim otherwise.
4. **"It's just a controller in disguise."** Addressed. (a) The Python-controller arm: every model writes a normal Python
   controller on both tasks with the same prompts and attempt counts, scored by the same harness; weights and
   controller distributions are side by side in the report. (b) The weight analysis of the high-scoring attempts
   (`scripts/analyze_weights.py`, `results/notable/analysis.md`): they are in fact linear PD controllers inside a tanh
   network that never saturates, and the analysis says so. The honest framing is that the weight arm tests whether a
   model can *express* a known controller in weight space, not that it invented a new kind of control.
5. **"Only two simple tasks."** Limitation, stated up front. Humanoid and Part B (editing an existing policy) are not
   started and are not claimed.

## About the evidence

6. **"Cherry-picked."** Addressed. Every attempt is logged and scored, failures included (`results/attempts/*/`);
   the report lists all attempts per cell with mean, median, IQR, min, max and the full per-attempt list, plus counts of
   unparsable replies and mid-episode crashes (`scripts/pilot_report.py`). The notable-attempts analysis is explicitly
   labelled as selected on score and describes best cases only.
7. **"Ten attempts per cell is small."** Limitation. Spreads are reported and no significance claims are made; the
   claims are descriptive ("in these 10 attempts"). *Extra experiment* if wanted: more attempts for the local models are
   cheap (one command per arm via `make local-weights|local-controller`); not run, to keep the pre-specified size.
   Hosted-model arms are bounded by subscription use.
8. **"Scores are noisy/overfit to the evaluation seeds."** Addressed. 100 fixed episodes per score with reset seeds
   disjoint from any training seed; there is no selection among attempts, each attempt is scored once. The three notable
   attempts were rerun on 500 fresh seeds (`results/notable/analysis_data.json`); one of them degrades there, which the
   analysis reports.
9. **"The PPO baseline is weak or untuned."** Limitation. PPO uses Stable-Baselines3 defaults with no tuning, 3 seeds, a
   fixed step budget (recorded in `results/baselines/ppo/*.log`). It is a reference for "what a standard untuned
   learner gets", not a state-of-the-art RL result, and the post must not call it the best RL can do. It also uses
   training steps, which the LLM arms deliberately do not.
10. **"Different arms see different information."** Addressed. The prompt carries only what PPO gets (observation/action
    spec, reward, episode rules); no hints, constants or example weights. Two arms: STRICT (raw numbers, `prompts/*_v2.md`)
    and NAMED (Gymnasium observation names, `prompts/*_v1.md`). Prompts are versioned, hashed per attempt
    (`meta.json`), and published verbatim with the results. **Limitation:** the NAMED arm gives more than PPO's raw
    numbers; that is why STRICT is the main comparison.
11. **"The harness leaked information to the model."** Addressed for the hosted model that has tools: `claude -p` runs
    with an empty fresh cwd outside any repo, tools disabled, no MCP, no session persistence, memory off, and a probe
    asked it to list tools/files/instructions it could see (`results/pilot/claude_isolation_probe_*.json`; a second
    probe is requested for the Opus model in `scripts/run_claude_round2.sh`). **Limitation:** the probe reply showed
    the account email address and a system prompt that names tools; no repo, memory or project instructions appeared. The
    local models only ever receive the prompt through a local server API. Prompts do not contain results.
12. **"Hosted-model runs aren't reproducible."** Limitation. The `claude -p` CLI exposes no sampling settings or seed;
    results will vary between runs and between model snapshots. We record raw output, CLI version, reported model id and
    date for each attempt, so the logged runs are auditable, not exactly repeatable. Local runs record seed, sampling
    parameters and server version, but llama.cpp output is not guaranteed bit-identical across hardware.
13. **"Local models are quantised and small, so this says little about LLMs in general."** Limitation. Qwen3-Coder-30B
    runs as a 4-bit GGUF and gpt-oss-20b as MXFP4 with vendor-recommended sampling; results describe those builds only.
    Token limits and reasoning effort differ per model and are recorded in `run.json`.
14. **"Comparing a subscription CLI model and local models is apples to oranges."** Limitation, stated in the report
    header: interface, sampling and context differ per model. The comparison that is controlled is within-model
    (weights vs Python controller, STRICT vs NAMED).
15. **"Return rewards survival, not the thing you care about."** Addressed: the return is the task's own reward, and
    distance, episode length and the fraction of full-length episodes are reported next to it for hopper.
16. **"Generated code was executed."** Limitation. LLM-written Python controllers run in the harness process with CPU and
    memory rlimits; that is not a sandbox. They are only run through `sim-run` on the NUC, replies are kept, and crashes
    are scored and logged. Do not run untrusted controllers elsewhere.

## About the method track

17. **"The circuit-compiler spec is just a controller written in another notation."** Limitation, stated up front: the
    compiler is deterministic code, and a compiled spec is only as capable as the spec. What it measures is whether
    expressing a design as a spec and compiling it removes the weight-arithmetic errors. So far only two spec fixtures
    written by the repo author (not an LLM) have been compiled, as tests of the compiler; **no claim is made about LLM
    spec writing** until those attempts are run. Exactness is tested per primitive (`tests/test_circuitc.py`); a `linear`
    primitive is exact only within a declared range and tolerance, and the compiler says so.
18. **"No novelty relative to prior work."** Limitation. This builds on the MIT weight-space post and related work
    listed in `README.md`; the contribution, if any, is the controlled comparison across arms and tasks, not the
    idea of writing weights by hand.

