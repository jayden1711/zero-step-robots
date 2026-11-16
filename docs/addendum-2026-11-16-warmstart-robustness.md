# Addendum 2026-11-16: robustness of the hopper warm-start result (no LLM calls)

Written 2026-11-16 (CST) on the organizer's GO (09:0x CST), **before any code or run of this addendum exists**. It is
committed on its own (docs only) before anything below is built or run. It extends
[the warm-start pre-registration](prereg-followup-draft.md) (call it "the warm-start prereg"), whose results stay
reported exactly as they are ([`results/warmstart_report.md`](../results/warmstart_report.md)). Anything that addendum
does not change still holds: tasks, `cpg-v1`, compiler, harness, practice seeds 0..9, held-out seeds 10000..10099, pass
rule, start sets L, P, R, H, MuJoCo 3.17.0 (mujoco<4) and Gymnasium 1.4.0.

## 1. Questions

- **Q1, optimiser replication (confirmatory, hopper).** The warm-start result
  ([L 39 of 80 vs R 2 of 80 passing by 500 designs](../results/warmstart_report.md#hopper)) came from one optimiser, a
  (1+1) hill climber. Does it hold with a different black-box optimiser at the same budget?
- **Q2, what makes a good start (hopper).** Which features of a zero-step LLM design, fixed below, predict that a search
  started from it passes?

## 2. What I have already seen (disclosure)

While writing up the warm-start study I computed these pass-by-500 counts for the hill-climber L runs on hopper:
- by model: Opus 23 of 40, Sonnet 16 of 40;
- by hint level: H0 7 of 20, H1 5 of 20, H2 27 of 40;
- by source: one-reply designs 23 of 60, feedback round-0 designs 16 of 20.

I have **not** looked at pass rates by pitch-to-hip gain sign, by starting distance or by oscillator count, on any run.
Features F3 and F4 below were therefore suggested by data I have seen. Testing them on the new optimiser's runs is a
test on new data of a pattern already observed, and it is labelled that way.

## 3. Q1: the CEM replication

- **Starts:** exactly the warm-start prereg's hopper sets: L (80), P (80, same permutation seeds), R (80, seeds
  1000..1079) and H (10, the hand start).
- **Search vector:** every numeric value of the start spec that `rs_proposer.perturb` changes, in the same traversal
  order. That is every number except `obs_dim`, `act_dim`, `hidden`, `range` and `tol`. Structure, names and declared
  ranges are fixed.
- **Optimiser:** the cross-entropy method, with diagonal Gaussian, population 20, and the 5 best as elites. The initial
  sd per value is 0.3 x |v| + 0.1 (the hill climber's perturbation scale). After each generation the mean becomes the
  elite mean and the sd becomes 0.8 x elite sd + 0.2 x previous sd (the update rule of the track's `cem`). Generation 1
  contains the start itself plus 19 samples. Designs that do not compile score minus infinity and are never elites
  unless fewer than 5 compile.
- **Budget, matched:** 25 generations x 20 = **500 designs = 5,000 practice episodes**, the same as the hill climber.
  The best-so-far design (by practice mean d over every design evaluated) is scored once on the held-out seeds at
  **checkpoints 20, 100, 200 and 500 designs**.
- **Seeds:** the optimiser seed is the first 8 hex digits of SHA-256 of `"cem/" + start id`. For H it is `"cem/hand_s<k>"`.
- **Bars, the same as the warm-start prereg's primary and secondary:**
  - Q1 primary: the result **replicates** if and only if the L pass-by-500 rate exceeds R by at least 10 points **and** a
    one-sided Fisher exact test gives p < 0.05.
  - Secondary: L vs P under the same rule.
  - Fallback: if fewer than 3 of 10 H runs pass by 500, the outcome is the held-out mean d at 500, compared with a
    one-sided Mann-Whitney U at p < 0.05 and a median gap of at least 0.5 m.
- **Combined reading:**
  - Replicates under CEM: "the warm-start value is not specific to the hill climber".
  - Does not replicate: "the hopper result is optimiser-dependent". The report says this plainly and the write-up is
    amended to say so.

## 4. Q2: predictors

Features of each L start design, all computable from files that already exist:

| id | feature | source | seen before? |
|---|---|---|---|
| F1 | pitch-to-hip net gain sign correct (gain < 0) | `pitch_gain` in `scripts/cpg_report.py`, applied to the start spec | no |
| F2 | the start's own held-out mean d >= 0.5 m | the original attempt's `score.json` (`r0/score.json` for feedback round-0 designs) | no |
| F3 | hint level H2 (vs H0 or H1) | attempt id | yes (section 2) |
| F4 | model Opus (vs Sonnet) | attempt id | yes (section 2) |
| F5 | two or more oscillators (vs one) | start spec | no |

- **Confirmatory test, on the CEM L runs (new data):** for each feature, a two-sided Fisher exact test of pass by 500
  against feature yes/no, with Holm-Bonferroni over the 5 features at a family-wise alpha of 0.05. A feature
  "predicts" only if it survives Holm. The report gives the pass rate in each group and the odds ratio.
- **Exploratory, labelled as such:** the same table on the hill-climber L runs, which are already finished and whose
  F3/F4 counts I have seen.
- No other feature is tested. No feature, threshold or grouping is changed after the CEM results are seen.

## 5. Compute

CPU only, through `~/projects/bin/sim-run` (nice 10, one thread), at most 2 processes of this study at a time. There is
no GPU, no model and no network. Measured cost for the hill-climber runs on hopper was a median of 15 to 38 s per run
per set ([`results/warmstart_report.md`](../results/warmstart_report.md#hopper)). CEM evaluates the same number of
designs, so the expectation is 250 runs x about 30 s = about 2 CPU-h, about 1 h wall on 2 slots. The worst case (every
episode at 1000 steps) is about 21 CPU-h, as in the warm-start prereg. Output is under 20 MB, in
`results/warmstart_cem/hopper/{L,P,R,H}/` and `results/warmstart_cem_report.md`.

## 6. Order and stop rule

1. This file committed (docs only).
2. Code (`scripts/warmstart_cem.py`, `scripts/warmstart_cem_report.py`) and tests committed.
3. H runs, then L, P, R interleaved by index, in 2 shards.
4. Report, then a write-up amendment.

No run after **2026-11-23 18:00 CST**. Unfinished sets are reported with their actual n. Any change needs a further
dated addendum before the affected runs.
