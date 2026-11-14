# CPG track: findings (local, 2026-11-09 23:30 CST)

Verdict (prereg s8): **did not work** on Hopper-v5 or Walker2d-v5. 120/120 pre-registered Claude attempts ran
(Opus 5.5, Sonnet 5.5 x hopper, walker2d x H2, H1, H0 x 10); all compiled; 0 passed; no arm met the target.
Full tables: results/cpg_report.md.

- Best LLM attempt: hopper 1.08 m (Opus H0; Opus H2 1.07 m), walker2d 1.30 m (Opus H1). Fall-forward lunge baselines:
  0.74 m (hopper), 0.96 m (walker2d). Most LLM controllers fall within 0.1-2 s (median episode length per cell 7-221
  steps); the few full-length episodes stand still.
- Hints: H2 did not produce a pass. Post-hoc: torso-pitch->hip gain sign correct in 7/10 (Opus H2), 10/10 (Sonnet H2)
  vs 0-5/10 at H1/H0. Walker2d episode lengths rise with the hint level (H2 > H1 > H0), distance does not.
- Headroom: hopper tuned CPG (same cpg-v1 network, dev-seed search) passes: 3.27 m, 80/100 clean, but every episode ends
  in a fall after 3 m. Walker2d tuned CPG: 1.29 m, 0 clean -> headroom NOT shown for cpg-v1 on walker2d.
- PPO (1M steps, env reward, 16-unit MLP): hopper 12.7-17.5 m, walker2d 3.75-16.6 m mean d; all seeds pass.
- Necessity table holds on both tasks (every simple baseline < 1.5 m; 50 random CPGs: median < 0 m, none passes).
- Incidents: one Opus hopper timeout (kept as _try1, repeated once); one walker2d call aborted when an early-started
  batch was stopped (kept as _aborted1). Timeout raised 900 -> 1800 s after the first.
- Not run: local models (GPU queue; prereg made them conditional), any feedback/revision arm (not pre-registered).
