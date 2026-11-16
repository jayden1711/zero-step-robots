# Addendum 2026-11-16 (b): is the balance-feedback sign causal? (no LLM calls)

Written 2026-11-16 (CST), after the robustness addendum's results and **before any code or run of this addendum**.
It is committed on its own (docs only) on branch `signfix-1116`, which is kept separate from the publish set on main.
Everything in [the warm-start prereg](prereg-followup-draft.md) and [the robustness addendum](addendum-2026-11-16-warmstart-robustness.md)
stays as reported.

## 1. Question

In both optimisers, hopper starts whose torso-pitch-to-hip net gain has the correcting sign (< 0) pass far more often:
[32 of 50 vs 2 of 30 under CEM](../results/warmstart_cem_report.md#predictors-cem-runs-confirmatory-holm-over-5-at-005).
That is a correlation. **Does flipping only that sign, in the designs that have it wrong, raise the pass rate?**

## 2. Already known (disclosure)

For the 30 wrong-sign L designs I know the pass-by-500 counts of the original runs:
[2 of 30 under CEM](../results/warmstart_cem_report.md#predictors-cem-runs-confirmatory-holm-over-5-at-005) and
[4 of 30 under the hill climber](../results/warmstart_cem_report.md#predictors-hill-climber-runs-exploratory-f3f4-counts-were-seen-before-this-addendum).
Nothing has been computed for the repaired designs.

## 3. The intervention

- **Designs:** the hopper L designs with `pitch_gain(spec) >= 0` (`scripts/cpg_report.py`). Expected n = 30, which
  follows from the counts above.
- **Repair (S):** in every unit whose `to` weight on `a0` (thigh) is nonzero, multiply the `obs[1]` input gain, if
  present, by -1. Nothing else changes. If the repaired net gain is still >= 0 (for example when the only pitch input
  is zero), the design is listed as "not repairable" and counted as an S failure in the primary test.
- **Search:** both optimisers, unchanged. The hill climber is `warmstart.run` with 500 designs. CEM is
  `warmstart_cem.run`, 25 x 20. Optimiser seeds are SHA-256 of `"signfix/" + start id` and `"signfix-cem/" + start id`.
  Same practice and held-out seeds, same checkpoints, same pass rule.
- **Also reported:** each repaired design's own held-out d with no search (one scoring).

## 4. Bars (fixed now)

- **Primary (CEM):** pass by 500 for S vs the original L run on the same 30 designs, as paired outcomes. "The sign is
  causal for search success" if and only if S passes in at least 6 more designs than the original (a 20-point gain on
  n = 30) **and** a one-sided exact McNemar test (binomial on the discordant pairs) gives p < 0.05.
- **Secondary:** the same rule for the hill climber.
- **Reading:**
  - Primary met: one sign flip recovers much of the gap.
  - Not met: the sign is a marker of better designs, not their cause, at least for this repair.

## 5. Compute, order, stop

CPU only via `sim-run`, at most 2 processes. 60 runs at about 30-60 s each, so under 1 CPU-h. Output is under 5 MB in
`results/warmstart_signfix/hopper/{cem,hc}/`. Order: this file, then code and tests, then the runs, then the report
(`results/warmstart_signfix_report.md`). Stop: 2026-11-23 18:00 CST.
