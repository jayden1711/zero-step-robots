# CPG feedback arm: findings (local, 2026-11-10 17:40 CST)

Prereg: docs/prereg-2026-11-10-cpg-feedback.md (f4e08e6); code/prompts frozen af807e4. 240/240 calls ran, 0 transport
failures; every round scored on held-out seeds. Full tables: results/cpg_feedback_report.md.

**Verdict (prereg s6): did not work at the arm level on either task.** No model x task cell reached 5 of 10 passing
attempts. The H0 stage was conditional on an H2 cell meeting the target and was not run.

But for the first time in this project, LLM-written controllers pass the 3 m bar:
- Hopper, Opus 5.5 with feedback: **2 of 10 attempts pass** (round-5 designs: 6.42 m and 6.90 m held-out mean d,
  100/100 clean episodes each); 4 of 10 reach >= 1.5 m. Arm mean 1.92 m, median 1.27 m.
  - fb-..._hopper_H2_08: rounds 0-1 near 0 m (round 1 stood still: foot on the ground 99% of steps, 1 touchdown). The
    model read that contact pattern, diagnosed "no flight phase", raised the leg rhythm and added a push-off; round 2 hopped
    (5.43 m), rounds 3-5 improved to 6.90 m with **all 100 held-out episodes running the full 1000 steps without a fall**:
    a sustained hop, better than the search-tuned CPG baseline (3.27 m, falls in every episode).
  - fb-..._hopper_H2_03: **passed already at round 0, before any feedback** (6.12 m, 79% full-length), with the v4fb
    template; revisions kept it in the 4.7-6.4 m range; round 5 = 6.42 m.
- Hopper, Sonnet 5.5 with feedback: 0/10 pass; distances cluster near 0.9-1.0 m (best 0.96 m); median rose from 0.38 m
  (round 0) to 0.94 m (round 5).
- Walker2d: 0/20 pass. Sonnet improved with feedback (median 0.68 m at round 5 vs ~0 at round 0; best 0.97 m). **Opus got
  worse with feedback**: round-5 median -1.10 m (moves backward), below its own round 0 (-0.81 m) and the no-feedback arm.
- Baselines with the same 6-design budget: RS-random 0/20 pass (hopper best 0.48 m). RS-from-LLM: hopper Opus 1/10 (the
  run starting from the 6.12 m round-0 design), Sonnet 0/10; walker2d 0/20. So on hopper, Opus's own revisions produced
  one pass that random revision from the same starts did not (attempt 08), and otherwise matched it.
- No-feedback reference (track H2): 0/10 per cell. The feedback arm's round-0 control: Opus hopper 1/10 pass (above).
  One pass in 10 vs 0 in 10 is not a measurable difference; the no-feedback verdict stays as reported.
- Dev (practice) and held-out means agree closely for every passing design: no sign of overfitting to the dev seeds.
- Budget: 240 calls; ~2.86M input tokens (incl. cache), ~1.74M output tokens. CPU only via sim-run. Wall: ~4.5 h.
