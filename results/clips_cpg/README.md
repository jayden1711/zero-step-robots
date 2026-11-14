# CPG clips (local, git-ignored). SIMULATION only: MuJoCo 3.17.0 through Gymnasium 1.4.0; no real robot.

Plan fixed before rendering: `docs/addendum-2026-11-11-cpg-clips.md` (commit 4e8c3df), with the camera correction
(commit 4e541d7). Script: `scripts/make_cpg_clips.py`. No training, no LLM call, no new attempt: each clip replays a
design's existing compiled `cpg-v1` weights; before rendering, the script checks that the replay reproduces the stored
held-out episodes exactly.

Same for all 15: held-out scoring seeds 10000, 10001, 10002 (the first three by index, chosen before viewing); the
model's `track` camera (follows the centre of mass); 640x480; every 4th step at 31 fps (about 8 s per 1000-step episode;
after a fall the last frame is held); software EGL, no GPU; single-threaded libx264; run through sim-run. Every frame
shows SIMULATION, the design id and round, why it was selected, its held-out score over all 100 scoring episodes, and a
live step / distance counter with the episode state.

The failing Walker2d design was picked by rank (lower median, 5th lowest of 10, of the Opus Walker2d feedback attempts'
round-5 held-out mean d), not by viewing. Ranking (attempt index: mean d): 08: -6.57, 05: -2.35, 02: -2.02, 07: -1.70, 06: -1.23, 04: -0.97, 00: 0.03, 03: 0.06, 01: 0.77, 09: 0.83.

| file | design | why | held-out score (mean d, eps >= 3 m) | seed | this episode: d | this episode: end |
|---|---|---|---|---|---|---|
| `hopper_opus_fb08_r5_seed10000.mp4` | fb-claude-opus-5-5_hopper_H2_08 round 5 | passing LLM design (feedback arm) | 6.90 m, 100/100 | 10000 | 6.89 m | 1000 steps, no fall |
| `hopper_opus_fb08_r5_seed10001.mp4` | fb-claude-opus-5-5_hopper_H2_08 round 5 | passing LLM design (feedback arm) | 6.90 m, 100/100 | 10001 | 6.90 m | 1000 steps, no fall |
| `hopper_opus_fb08_r5_seed10002.mp4` | fb-claude-opus-5-5_hopper_H2_08 round 5 | passing LLM design (feedback arm) | 6.90 m, 100/100 | 10002 | 6.90 m | 1000 steps, no fall |
| `hopper_opus_fb03_r5_seed10000.mp4` | fb-claude-opus-5-5_hopper_H2_03 round 5 | passing LLM design (feedback arm; passed at round 0) | 6.42 m, 100/100 | 10000 | 7.01 m | fell at step 920 |
| `hopper_opus_fb03_r5_seed10001.mp4` | fb-claude-opus-5-5_hopper_H2_03 round 5 | passing LLM design (feedback arm; passed at round 0) | 6.42 m, 100/100 | 10001 | 6.80 m | fell at step 904 |
| `hopper_opus_fb03_r5_seed10002.mp4` | fb-claude-opus-5-5_hopper_H2_03 round 5 | passing LLM design (feedback arm; passed at round 0) | 6.42 m, 100/100 | 10002 | 5.76 m | fell at step 754 |
| `walker2d_opus_fb_lowermedian_r5_seed10000.mp4` | fb-claude-opus-5-5_walker2d_H2_06 round 5 | failing LLM design: lower median of Opus walker2d feedback attempts (rank rule) | -1.23 m, 0/100 | 10000 | -1.24 m | fell at step 182 |
| `walker2d_opus_fb_lowermedian_r5_seed10001.mp4` | fb-claude-opus-5-5_walker2d_H2_06 round 5 | failing LLM design: lower median of Opus walker2d feedback attempts (rank rule) | -1.23 m, 0/100 | 10001 | -1.23 m | fell at step 182 |
| `walker2d_opus_fb_lowermedian_r5_seed10002.mp4` | fb-claude-opus-5-5_walker2d_H2_06 round 5 | failing LLM design: lower median of Opus walker2d feedback attempts (rank rule) | -1.23 m, 0/100 | 10002 | -1.22 m | fell at step 182 |
| `hopper_tuned_cpg_seed10000.mp4` | hopper search-tuned CPG (baseline) | baseline: structure by hand, parameters by search on dev seeds | 3.27 m, 80/100 | 10000 | 3.20 m | fell at step 346 |
| `hopper_tuned_cpg_seed10001.mp4` | hopper search-tuned CPG (baseline) | baseline: structure by hand, parameters by search on dev seeds | 3.27 m, 80/100 | 10001 | 3.25 m | fell at step 373 |
| `hopper_tuned_cpg_seed10002.mp4` | hopper search-tuned CPG (baseline) | baseline: structure by hand, parameters by search on dev seeds | 3.27 m, 80/100 | 10002 | 3.02 m | fell at step 320 |
| `walker2d_tuned_cpg_seed10000.mp4` | walker2d search-tuned CPG (baseline) | baseline: structure by hand, parameters by search on dev seeds | 1.29 m, 0/100 | 10000 | 1.29 m | fell at step 220 |
| `walker2d_tuned_cpg_seed10001.mp4` | walker2d search-tuned CPG (baseline) | baseline: structure by hand, parameters by search on dev seeds | 1.29 m, 0/100 | 10001 | 1.29 m | fell at step 220 |
| `walker2d_tuned_cpg_seed10002.mp4` | walker2d search-tuned CPG (baseline) | baseline: structure by hand, parameters by search on dev seeds | 1.29 m, 0/100 | 10002 | 1.35 m | fell at step 218 |

What they show (from the numbers above; read with the clips):
- Opus #08 (round 5) hops forward for the full 1000 steps on all three seeds (about 6.9 m each), torso upright.
- Opus #03 (round 5) covers 5.8-7.0 m on these seeds and then falls (steps 754-920); it reaches 3 m well before the
  fall, which is what the pre-registered metric counts.
- The hopper search-tuned CPG reaches about 3.0-3.25 m and falls at steps 320-373 on these seeds.
- The failing Opus Walker2d design moves backward about 1.2 m and falls at step 182 on every seed.
- The Walker2d search-tuned CPG moves about 1.3 m and falls at about step 220.

`_render1_fixed_camera/` holds the first render (Gymnasium's default camera, which does not follow the robot): kept,
not to be used.
