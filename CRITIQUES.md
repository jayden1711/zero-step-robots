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
   PPO moving. (c) and (d) were written before the isolated rerun: the two LLM clips are contaminated Opus attempts and
   the addendum quotes pre-rerun Opus counts, so both are stale until regenerated (Reviewer recheck, R3). No claim of hopping or locomotion is made for any LLM attempt unless the table shows forward distance for
   it. **Limitation:** a standing score is not evidence of locomotion, and the post must say so beside every hopper
   number. A forward-speed-only metric, or a harder task (get from A to B), would separate these cases better and was not
   used, so as not to change the reward after seeing the results; this is stated as a limitation, not run.

**Named finding: "the LLM exploited the healthy reward."** When the prompt gives the reward and nothing about the goal,
LLM-written hopper policies that score highest by return are the ones that stand still: return at the value of surviving
1000 steps (+1 per step, so about 1000) and forward distance about zero. "Exploited" is shorthand, not a claim about
intent: in the replies themselves, most Opus and Sonnet attempts say they cannot test anything and choose a stand-still
design because an untested hop would probably fall early and lose the per-step bonus (a stated risk hedge under one
shot, no feedback; the prompt's scoring section also defines the score as total reward). This holds for
weights and for Python controllers, so it is not an artefact of the weight format. The comparison that tests whether it
is a prompt-framing effect is the hopper `goal` arm: the STRICT prompt plus one sentence stating that the goal is to move
forward as far as possible (forward distance), nothing else changed (so the scoring section still says the score is the
mean total reward, and the 1 m success rule is not given to the model), same models, modes and attempt indices, and the
same isolated runs for the rerun cells (the Sonnet strict weights comparison cell is from the earlier round, item 12).
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
   rather than swapped (`results/clips/README.md`). The existing clips predate the isolated rerun and show contaminated
   Opus attempts; `scripts/make_clips.py` now skips contaminated attempts, so the clips must be regenerated (and will
   show different attempts) before any use (Reviewer recheck, R3). All attempts will be published, not a selection.
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
12. **"The harness leaked information to the model."** Addressed in part; one exposure was found, fixed and rerun; what the
    model does see is listed here. Every `claude -p` call has all tools off, no MCP, no session persistence, no auto-memory,
    and runs in a fresh empty directory. **The exposure:** an earlier probe of the Opus model (`results/claude_isolation_probe_20261106T162104.json`)
    showed that an unrelated project's `CLAUDE.md` sat in `/tmp`, an ancestor of the then-temporary cwd, and was loaded as
    project instructions. The file is gone, so only the probe reply and the token counts (below) describe it; the probe
    reply says it was about a different project (a Jetson study). It was in the context of the Sonnet controller arm and all
    Opus arms (120 attempts). **Fix:** `scripts/run_pilot.py` now runs every call in a fresh empty directory under `/var/tmp`,
    refuses to run if the cwd or any ancestor holds `CLAUDE.md`, `CLAUDE.local.md` or `.claude`, and passes `--setting-sources
    project,local` so the user-level `~/.claude/CLAUDE.md` is not loaded. Each batch starts with an isolation probe whose last
    line must be `INSTRUCTION_FILES: none` (probe files: `results/claude_isolation_probe_<model>_*.json`; all probes made
    with the final flags report none). The exact flags and env are recorded per attempt (`meta.json`, `run.json`). The 120
    contaminated attempts are kept untouched, labelled `contaminated: /tmp/CLAUDE.md` in `meta.json`, excluded from every main
    table and listed in their own report section; they were rerun with the same prompts and attempt indices as ids ending
    `_iso2` (160 reruns in total with the 40 goal-arm attempts).
    **What the model still sees** (from the probes, which are the model's own self-report, not ground truth): the CLI's default
    system prompt (it names Read, Edit, Write, Glob, Grep and PowerShell although no tool is attached), environment metadata
    (platform, shell, "not a git repository", the temporary cwd path under `/var/tmp`), and a system reminder holding the
    logged-in account's email address (it cannot be switched off under subscription auth, so every
    output written to disk is redacted first and the runner fails loudly if an address survives; a search of `results/`
    finds none). No repo contents, results, memory or instruction file. The email is a possible identity cue; there is no
    sign it mattered, but it cannot be ruled out. Local models only receive the prompt through a local server API. Prompts
    do not contain results.
    **Not rerun, and why that is believed clean:** the 40 first-round Sonnet weights attempts (cartpole and hopper, strict and
    named; ids `claude_<task>_<arm>_weights_NN`) ran at 12:20 to 12:32 (UTC-6) on 2026-11-06, before the stray file existed,
    but also before `--setting-sources` was added, so a user-level `~/.claude/CLAUDE.md` could have been loaded; its mtime
    (18:34) postdates those runs, so what it said then is unknown [verify]. Independent evidence: total input tokens per call
    (`usage` in `run.json`) are the same, apart from the 21 tokens of the goal sentence, as in the rerun Sonnet goal-weights
    attempts that ran under the final flags, while the contaminated Sonnet and Opus calls carry about 830 extra tokens that the
    reruns do not (`results/reviewer/recheck_rerun.md`). So no extra instruction block was present. **Limitation:** probes are
    self-reports from one call per batch, the CLI's system prompt text is not recorded, and a `meta.json` `isolation` field
    written before this review says the probe found "no email"; the email was in fact present and redacted (the code string is
    now corrected; written files are not edited).
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
17. **"Models were compared at different times / model versions."** Limitation. All attempts ran on 2026-11-06 (UTC-6; the
    `created` stamps in `meta.json` are UTC, so the last reruns read 2026-11-07) with the model ids recorded per attempt.
    The Sonnet strict-weights cell ran about eight hours before the Sonnet goal-arm cells it is compared with, so a model
    change in between would look like a goal effect; later snapshots may also behave differently.
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

## Reviewer recheck (rerun)

A second fresh read, after the isolated rerun, of `CLAUDE.md`, `NUC_RULES.md`, README, PLAN, HANDOFF, this file, the runner
(`scripts/run_pilot.py`), the report generator, the clip and analysis scripts, the prompts, all 13 isolation probes, the
rerun logs, and the attempt directories. No new training and no new LLM attempts. Extra work was local only: recomputing
the hopper tables from raw `score.json` (`results/_scratch/recheck_finding.py`), token accounting from `run.json`
(`recheck_tokens.py`), probe readback (`recheck_probes.py`), contaminated-vs-rerun and strict-vs-goal counts with exact tests
(`recheck_compare.py`, output `results/reviewer/recheck_rerun.md`; numbers live there, not here), a clip-selection dry run
(`recheck_select.py`, no rendering), the test suite, and two single-attempt re-scores through `sim-run` (one process at a
time, load below 12). Branch note: this branch (`rerun`) was cut at `4883db9`; the earlier "Reviewer pass (2026-11-06)" is on
branch `prepost` (`6fd9fa0`) and is **not in this branch**, so its corrections to items 3, 4, 7, 9, 12, 18 and its sections
A to F are absent here until the branches are merged; this recheck does not repeat them.

### R-A. New claims traced

| claim | traces to | verdict |
|---|---|---|
| 120 attempts labelled contaminated; 160 rerun attempts (`_iso2`) | `results/attempts/*/meta.json`: exactly the Sonnet controller arm and every Opus arm are labelled; 160 `_iso2` ids; no duplicate (cell, index) in the clean set | holds |
| Hopper "Finding" table (standing / success counts, clean and contaminated) | recomputed from `score.json` independently of `pilot_report.py` | every count matches the report |
| Strict vs goal comparison | same recomputation | matches; the report states it as counts only |
| Contaminated attempts excluded from every main table | `scripts/pilot_report.py` splits on the `contaminated` label before any table, so stock, variant and finding tables are clean | holds for the report |
| Contaminated attempts excluded everywhere else | clip script, notable-attempt addendum, earlier fresh-seed re-scoring | **failed**, see R3 |
| "No LLM attempt travels 1 m" | true on the stock environment; **not true on every variant**: one Sonnet goal-arm weights attempt crosses 1 m on the heavy-torso variant (report, hopper variant tables) | say "on the stock environment" |
| Isolation: tools, MCP, memory, instruction files absent | all probes made with the final flags end `INSTRUCTION_FILES: none`; input-token accounting shows the ~830-token extra block of the contaminated runs is absent from the reruns | holds, with the limits in item 12 |
| Isolation: what IS in context | probes: default CLI system prompt, environment metadata, a system reminder with the account email (redacted on write; none found on disk) | now stated in item 12; was incomplete |
| Rerun and goal arm specified before their attempts existed | commit times: goal prompt, success rule and report code 18:17; isolation flags 19:09:46; first rerun attempt 19:10 (UTC-6) | holds (the flags commit is 18 s before the first rerun call) |
| One command reproduces a score | `python -m zsr.harness hopper --weights|--controller <attempt file>` reproduced a rerun weights and a rerun controller attempt to the last digit | holds for scoring; the replies are not reproducible (item 13) |
| Tests | 44 pass | holds |
| Success rule (mean forward distance of at least 1 m over 100 episodes) applied to every hopper arm | code and report header | holds; the rule was chosen after the standing finding (item 18) |

### R-B. Existing entries re-checked after the rerun

| # | Still true? | Classification honest? | Change |
|---|---|---|---|
| 1, 3 to 6, 8 to 11, 13 to 16, 19, 20 | yes (checked against files; item 9's 500-seed re-score is in `results/notable/analysis_data.json`; item 10's PPO settings in `zsr/ppo.py`; item 14's sampling in `scripts/run_pilot.py`; item 16's rlimits in `zsr/harness.py`) | yes | none |
| 2 | mostly; clips and addendum cited as evidence are stale (R3) | yes | cross-reference added |
| Named finding | the count claims hold; "exploited" over-read intent | wording was too strong | replaced by the replies' stated risk hedge, and the prompt's score definition added |
| 7 | the clip statement no longer true | yes | clip sentence rewritten |
| 12 | **partly wrong**: said the probe is refused if the output contains an email (the final code expects the email and redacts it); named the probe locations wrongly; listed the email but not the environment metadata; did not say the first-round Sonnet weights arm ran without `--setting-sources` | "addressed in part" was right | rewritten |
| 17 | incomplete: UTC/local dates, and the Sonnet strict-weights cell predates its goal-arm comparison by hours | yes | rewritten |
| 18 | true; the rerun and goal arm were specified before their attempts (R-A) | yes | none |

### R-C. Criticisms that were missing

1. **"The goal arm does not test whether the model can aim at distance."** The goal sentence is added to a prompt whose scoring
   section still says the score is the mean total reward, and the 1 m success rule is never shown. A model that follows the
   stated score and stands is behaving as told; "told the goal, still stood" overstates it. **Limitation, stated** (item 2).
   Extra experiment, not run (needs new LLM attempts, so the owner's go): an arm whose scoring section says the score is
   forward distance (not comparable with PPO's reward, so it must be labelled as a different task).
2. **"'Exploited' attributes intent."** The replies say what the model did and why: most attempts note that nothing can be
   tested and choose a stand-still design to avoid an early fall. That is a hedge under no feedback, not discovery of a
   loophole. **Addressed** (named finding reworded). Not tested: whether the same models would try to hop given a simulator.
3. **"Your clips and analysis still describe the contaminated runs."** True. The best and median clips are contaminated Opus
   attempts, and `results/notable/analysis.md` (addendum) and the fresh-seed re-scoring in `results/reviewer/` quote
   pre-rerun Opus counts and the old attempt totals. **Addressed in code, not in the files:** `scripts/make_clips.py` now skips
   contaminated attempts; a dry run (`results/_scratch/recheck_select.py`) shows the selection changes (the best-by-return
   attempt would now be a Sonnet goal-arm weights attempt, the cell median a failing one), so the clips must be rendered again
   and described from scratch before use. Rendering needs an ffmpeg with libx264 and was not done here. The stale local files
   carry a note. The three analysed weights attempts are Sonnet attempts from the clean first round and are unaffected.
4. **"The rerun may differ from the contaminated runs only by noise, so what did contamination change?"** Compared cell by
   cell on the same prompts: no difference that exceeds what two replicates of the same prompt show (cartpole ceilings
   identical; hopper standing counts differ by a few of ten, in either direction, between the contaminated and the rerun cell). So the contaminated
   file did not visibly change any conclusion, which is also not proof it had no effect (`results/reviewer/recheck_rerun.md`).
5. **"A few of ten is replicate noise."** The same observation cuts the other way: arm differences of a few attempts out of ten
   (strict vs named, strict vs goal) are no larger than the replicate-to-replicate spread. The one large strict-vs-goal gap
   (Opus weights) has an uncorrected exact p near conventional thresholds among four comparisons, and the others do not; the
   direction is fewer stand-still attempts and no successes, which the report reads as fewer survivors, not more hopping.
   **Limitation:** n of 10 per cell; descriptive only (item 8).
6. **"The probe is the model grading itself."** It is: a self-report from one call per batch. The independent evidence is
   token accounting (R-A) and the per-call ancestor check in the runner. The CLI's system prompt text is not recorded.
   **Limitation.**
7. **"The account email is in every call."** It is, and it identifies the account holder; hosted models might condition on it.
   It cannot be disabled under subscription auth, so it is a fixed condition of every Claude arm, redacted on write and
   absent from the repo and from `results/` (searched). **Limitation.** The local arms do not see it.
8. **"The first-round Sonnet weights arm ran with the older flags."** True (item 12): not rerun, no extra instruction block
   by token count, but the user-level file's earlier content cannot be checked [verify]. **Limitation.**
9. **"Success counts a forward fall."** Mean forward displacement of at least 1 m counts a policy that falls forward; the
   per-attempt lists let a reader see which attempts do. A time-on-feet-while-moving criterion would be stricter and was not
   added after seeing results. **Limitation.**
10. **"The goal arm exists for two models and one task."** Sonnet and Opus on hopper only; cartpole has no analogue and the local
    models were not given the arm. **Limitation.**

### R-D. Requested checks

- All attempts reported with medians and spreads: yes (`results/pilot_report.md`: n, unparsable, mean, median, IQR, min, max and
  the per-attempt list per cell; failures shown as `F`). The pooling rule is explicit: clean and contaminated are never mixed.
  The cell-level standing counts are counts, not rates with intervals; no cherry-picking found.
- Simulation stated plainly: README line 9, this file's header, report header, clip captions.
- Prior work: README lists it; unverifiable items are marked [verify] (the MIT post itself was supplied by the owner and cannot
  be checked offline [verify]).
- Neutral wording: the named finding was softened (R-C2). Quoted objections keep their wording.

### R-E. Changes made in this recheck

`CRITIQUES.md` (items 2, 7, 12, 17, the named finding, this section); `scripts/make_clips.py` (skips contaminated attempts);
`scripts/run_pilot.py` (the `isolation` string recorded in future `meta.json` files no longer says "no email"); `PLAN.md`
(isolation paragraph); `HANDOFF.md` (status). Local only: stale notes on the clips README, the notable addendum and the
earlier fresh-seed summary; `results/reviewer/recheck_rerun.md`; `results/_scratch/recheck_*.py`.

### R-F. Before any post

Merge or reconcile `prepost` and `rerun` (the earlier reviewer's corrections are only on `prepost`); regenerate the clips and
rewrite the notable addendum from the clean attempts; handle the git history; state "one reply, no execution, simulation" and
"stands still" beside every hopper number, "on the stock environment" beside the 1 m statement, and the goal-arm limit (R-C1);
the owner decides whether to run the distance-scored arm.
