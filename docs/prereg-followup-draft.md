# Pre-registration DRAFT: warm-start value of zero-step designs (no LLM calls)

*Draft written 2026-11-15 (CST; 2026-11-16 UTC) on branch `writing-1116`. It is not in force until it is committed on its own (docs only)
and the owner or organizer accepts it. No code for it exists yet, and nothing below has been run. It extends, and does
not change, [the CPG track pre-registration](prereg-2026-11-09-cpg.md) and [the feedback-arm pre-registration](prereg-2026-11-10-cpg-feedback.md).
Their results stay reported exactly as they are.*

Derived numbers below (set sizes, power, compute) are computed by [`scripts/followup_numbers.py`](../scripts/followup_numbers.py)
from files in `results/`. Measured numbers link to their files.

## 1. Why

The CPG track scored zero-step designs against a binary bar. [0 of 120 one-reply attempts pass](../results/cpg_report.md#verdict-prereg-section-8)
3 m, and the best reach about 1 m ([1.08 m](../results/attempts/cpg-claude-opus-5-5_hopper_H0_cpgspec_06/score.json) on hopper).
With every attempt below the bar, the bar cannot say whether a zero-step design is *close* to working or no better than
noise. More LLM attempts against the same bar would most likely return more zeros, and the owner's rule is that no more
LLM attempts run.

This follow-up turns "zero-step success" into a measurable, continuous quantity. The question is **how much black-box
search a zero-step LLM design saves**, compared with a random design of the same family and with the LLM's own numbers
shuffled within its own structure. It uses only the designs that already exist and runs no model.

It also adds the Walker2d headroom test the track lacked: the search-tuned CPG [did not reach 3 m](../results/cpg/baselines/walker2d/tuned_cpg.score.json),
so a Walker2d failure may belong to the network rather than to the model.

A 6-design version of this comparison already exists. The feedback arm's random-search baseline from each Opus round-0
design passed [only where the start already passed](../results/cpg_feedback/rs/hopper/fromllm_claude-opus-5-5/). This
follow-up runs the same, already pre-registered proposer with a larger budget, over every zero-step design, with matched
controls.

## 2. Questions and hypotheses

- **Q1 (primary, hopper).** Starting from the LLM's zero-step designs, does a fixed black-box search reach the
  pre-registered 3 m pass more often within its budget than starting from random CPGs?
  H1: pass-within-budget rate L > R.
- **Q2 (secondary, hopper).** Is the gain in the LLM's specific numbers, or only in its choice of structure and scale?
  H2: rate L > P, where P keeps each LLM design's structure but permutes and sign-flips its numbers.
- **Q3 (secondary, Walker2d).** The same as Q1 and Q2, interpreted only if Stage B shows headroom (section 6).
- **Q4 (descriptive).** For each start set, the held-out distance curve over search effort, and the graded ladder:
  fraction of runs reaching 1.5, 3 and 5 m.

## 3. Start sets (per task)

All designs are specs in the `cpg-v1` spec language, compiled by the unchanged `circuitc` compiler.

- **L, LLM zero-step designs (n = [80 per task](../scripts/followup_numbers.py)):** the 60 one-reply designs of the CPG
  track (`results/attempts/cpg-claude-*_<task>_H{0,1,2}_cpgspec_NN/parsed.spec.json`) plus the 20 round-0 designs of the
  feedback arm (`results/attempts/fb-claude-*_<task>_H2_NN/r0/parsed.spec.json`). A round-0 design was written before the
  model saw any feedback, so it is zero-step. All 160 designs compiled in the original runs. Subgroups (model, hint
  level, set) are reported but never pooled differently after seeing results.
- **P, permuted LLM designs (n = 80 per task):** one per L design. Structure is kept: oscillator count and names,
  couplings present, the inputs of each unit, unit types, declared `range`/`tol`, `obs_dim`/`act_dim`/`hidden`. The
  numeric values are randomly permuted among the slots of the same kind *within that design*. The kinds are:
  (a) `freq_hz`; (b) `phase0` and coupling `phase_lag`; (c) coupling `weight`; (d) every gain (oscillator `feedback`
  gains, unit `inputs` gains, unit `to` weights); (e) `bias` values; (f) reflex `threshold` and `sharpness`. Each gain in
  kind (d) is then sign-flipped with probability 0.5. The RNG seed is the first 8 hex digits of SHA-256 of the L design's
  attempt id + `"/perm"`. P keeps the LLM's structure and its distribution of magnitudes but destroys which number goes
  where, and every sign.
- **R, random CPGs (n = 80 per task):** `random_cpg_spec(task, seed)` from `scripts/cpg_baselines.py`, the track's fixed
  distribution, unchanged, with seeds 1000..1079. These are disjoint from the 0..49 already scored in the track and the
  100..109 used by the feedback arm's random-search baseline.
- **H, hand-structure start (calibration only, n = 10 runs per task):** the unsearched hand start `x0` of
  `tuned_builder(task)` in `scripts/cpg_baselines.py` (the starting point of the tuned CPG before its search), with
  optimiser seeds 0..9. It is not compared with L. It shows whether the budget is enough from a known-reasonable
  structure.

## 4. The search (fixed; the proposer already pre-registered in the feedback arm)

- **Proposer:** `scripts/rs_proposer.py`, logic unchanged: a (1+1) hill climber. Each step perturbs every number of the
  best design so far (Gaussian, sd = 0.3 x |v| + 0.1; names, structure, dims and declared `range`/`tol` kept) and accepts
  the new design if its practice-seed mean d is higher. The practice seeds are seeds 0..9, scored with the same
  `zsr.feedback.summarize` code. A design that does not compile scores minus infinity.
- **Only change: the budget.** Each run gets 500 designs (5,000 practice episodes) instead of 6. The best-so-far design at
  **checkpoints 6, 25, 50, 100, 200 and 500** is scored once on the held-out seeds 10000..10099 with the unchanged
  harness. Checkpoint 6 replicates the feedback arm's baseline budget. Held-out scores are never used by the search.
- **One run per start.** The optimiser seed is the first 8 hex digits of SHA-256 of the start id, the same rule as the
  existing random-search-from-LLM runs.
- **Pass rule unchanged:** held-out mean d >= 3 m and >= 50 of 100 clean episodes.

Outcome per run: **T**, the first checkpoint whose best-so-far design passes, or "censored" if none does by 500. Also
recorded: the held-out mean d at every checkpoint, the practice-seed d of every design, and acceptances.

## 5. Bars (decided here, before any run)

**Primary (Q1, hopper):** the claim "zero-step LLM designs have measurable warm-start value on hopper" is made **if and
only if** both of the following hold:
1. the fraction of L runs passing by checkpoint 500 exceeds the fraction of R runs by at least 0.10 (10 percentage
   points), **and**
2. a one-sided Fisher exact test of L vs R on those counts gives p < 0.05.

If either fails, the report says **"no measurable warm-start value"** for that comparison, with both rates and the
interval.

- Power at n = 80 per arm ([computed](../scripts/followup_numbers.py)): 0.76 if the true rates are 25% vs 10%, 0.86 at
  20% vs 5%, 0.93 at 30% vs 10% or 15% vs 0%, and 0.47 at 20% vs 10%. The false-positive rate when L and R are equal at
  10% is 0.022. A true gain under about 10 points is likely to be missed. The report will say so.
- **Secondary (Q2):** the same two-part rule for L vs P, labelled secondary, with no multiplicity claim. Reading the
  outcomes together:
  - L > R and L > P: the LLM's specific numbers help search.
  - L > R and L ≈ P: its structure and scale help, its assignment does not.
  - L ≈ R: no measurable value.
  - L < R (one-sided test in the other direction, reported descriptively): the LLM's designs are *worse* starts, for
    example basins where the robot stands still, which the hill climber may not leave.
- **Fallback if the budget is too small (decided now):** if Stage 0 shows that fewer than 3 of 10 H runs pass on hopper
  by checkpoint 500, the binary primary would be mostly censored. The primary outcome then becomes the **held-out mean d
  at checkpoint 500**, L vs R, with a one-sided Mann-Whitney U at p < 0.05 **and** a difference in medians of at least
  0.5 m. The switch is made from Stage 0's result alone, before any L, P or R run, and is recorded in the report.
- Walker2d (Q3): the same rules, reported under "Walker2d", and interpreted as evidence about the model only if Stage B
  shows headroom.

## 6. Stages and order

0. **Calibration (hopper, then Walker2d):** the 10 H runs per task. This measures the simulation speed per task and
   applies the fallback rule above. No L, P or R run starts before Stage 0 is done for that task.
1. **Hopper:** L, P and R runs (240), interleaved by start index (L0, P0, R0, L1, ...) so a timebox cut leaves balanced
   arms.
2. **Stage B, Walker2d headroom:** the track's tuned-CPG CEM search (`cem` in `scripts/cpg_baselines.py`, same hand
   structure, same search and pick seeds), with the budget raised from 20,000 to **50,000 practice episodes**, 3 CEM
   seeds (0, 1, 2). Each search result is scored once on the held-out seeds. Headroom counts as **shown** if at least one
   of the 3 passes. If none does, the report says that headroom for `cpg-v1` on Walker2d is still not shown.
3. **Walker2d:** L, P and R runs (240), interleaved as in step 1.
4. **Report:** `results/warmstart_report.md`, with the verdicts per section 5, all curves, every run listed, and
   `results/MANIFEST.md` updated.

## 7. Compute and resources

- **CPU only, no GPU, no model, no network.** Every run goes through `~/projects/bin/sim-run` (nice 10, one thread), at
  most 2 sim processes of this study at a time, and only while the NUC load is under 20. The GPU queue (other projects)
  is not touched.
- **Speed:** hopper runs at [about 16,700 steps/s](../scripts/followup_numbers.py) single-threaded, measured from a
  100-episode, 1000-step held-out scoring ([source](../results/attempts/fb-claude-opus-5-5_hopper_H2_08/score.json)).
  Walker2d speed is measured in Stage 0.
- **Worst case** (every episode lasts all 1000 steps): [about 5 min per run, about 41 CPU-h for all 500 runs, about 21 h
  wall on 2 slots](../scripts/followup_numbers.py); Stage B adds [about 2.5 CPU-h](../scripts/followup_numbers.py).
  Most designs fall within about 1.4 s ([median episode length per cell at most 175 steps](../scripts/writeup_numbers.py)),
  so the typical cost should be a fraction of that. Stage 0 gives the real figure.
- **Disk:** each run stores its practice-score history and the 6 checkpoint specs and scores (no per-step traces), tens
  of kB per run, well under 100 MB in all. `df` is checked before starting, against the NUC's 50 GB free floor.
- **Software:** the project venv as pinned, MuJoCo 3.17.0 (mujoco<4 via `mujoco-pin.txt`) and Gymnasium 1.4.0, the same
  as every earlier result ([`results/MANIFEST.md`](../results/MANIFEST.md)). No MuJoCo 4.0 anywhere in this study.

## 8. What stays fixed, and what would need an addendum

Fixed: tasks, `cpg-v1`, compiler, harness, practice and held-out seeds, pass rule, proposer logic, start sets, budgets,
checkpoints, bars and order. Any change needs a further dated addendum committed before the affected runs. Nothing from
this study is fed to any model, and no LLM is called. The results do not re-score or replace any earlier verdict.

## 9. Stop rule

Runs end at **2026-11-23 18:00 CST** (the project timebox), whatever the state. Unfinished sets are reported with their
actual n and marked incomplete. Thanks to the interleaving, a partial set still compares L, P and R at equal n.

## 10. Code to write before any run (committed after this file, before Stage 0)

- `scripts/warmstart.py`: start-set builders (L from the attempt dirs, P as defined in section 3, R and H), the 500-design
  run using `rs_proposer.perturb`/`dev_score` with checkpoint scoring, and resumable per-run JSON in
  `results/warmstart/<task>/<set>/<id>.json`.
- `scripts/warmstart_report.py`: the tables, the tests of section 5, and the curves.
- Tests: P preserves structure exactly and changes no fixed field; the permutation is deterministic per id; the
  6-design checkpoint of an L run reproduces the existing RS-from-LLM proposer's acceptance logic given the same seed; R
  seeds are disjoint from 0..49 and 100..109.

## 11. Excluded on purpose

- **New LLM attempts of any kind** (owner rule).
- **A hand-written analytic controller** (for example a Raibert-style hopper controller) as a "zero-step human" baseline.
  It would be written in this session, by an LLM, so it would be an LLM attempt under another name.
- **A larger or different optimiser** (CMA-ES etc.). One proposer, already pre-registered, keeps the comparison simple.
  A different optimiser would answer a different question.
