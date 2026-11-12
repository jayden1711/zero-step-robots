# Clips (local, git-ignored). SIMULATION only: MuJoCo Hopper-v5 through Gymnasium, no real robot.

> **Note 2026-11-11 (camera):** these clips use Gymnasium 1.4.0's default render camera, which does not follow the robot.
> A robot that moves forward (the PPO clip, and any moving attempt) leaves the frame after about 2 m; the captions'
> distance counters stay correct. Not re-rendered. The CPG clips in `../clips_cpg/` use the model's own tracking camera.

Re-rendered 2026-11-07 from CLEAN attempts only (the `contaminated` attempts are never selected or ranked; 200 clean hopper
attempts, 197 scored, 3 without a score). The earlier clips, which showed contaminated Opus attempts, are kept
unchanged in `_old_contaminated/` and are not to be used.

Made by `scripts/make_clips.py` (rerun: `FFMPEG=<ffmpeg with libx264> PYTHONPATH=. sim-run <python> scripts/make_clips.py results`).
Software EGL rendering (no GPU), single-threaded libx264 encoder, run through sim-run. Full numbers in `selection.json`.
No training and no new LLM attempts: every clip replays existing weights or controllers from `results/attempts/` or
`results/baselines/ppo/`.

Same for all four clips: 640x480, the environment's default tracking camera, first evaluation seed (10000, not chosen),
1000 steps shown as 250 frames (every 4th step) at 31 fps (about 8 s). After an episode ends the last frame is held.
Every frame's caption: SIMULATION, label, model, mode, arm, attempt id, rank (by return and by distance among the 197 clean
scored hopper attempts, plus rank within its cell), episode seed, the attempt's score (mean return AND mean forward distance
over the 100 scoring episodes, seeds 10000-10099), and a live step / return / distance counter with the episode state.

## How each clip was chosen (rules fixed in the script before any clip was viewed; no cherry-picking)

| clip | attempt | rule | result |
|---|---|---|---|
| `hopper_a_best.mp4` | claude_hopper_goal_weights_09_iso2 (claude-sonnet-5-5, weights, goal arm) | highest stock mean return among all clean Claude hopper weights attempts, any arm | mean return 1015, mean distance 0.13 m; rank 4/197 by return, 22/197 by distance; 1 of 10 in its cell |
| `hopper_b_median.mp4` | claude_hopper_goal_weights_02_iso2 (same cell) | attempt in (a)'s model/mode/arm cell whose mean return is closest to the cell median (78.4; ties: lower id) | mean return 65, mean distance 0.16 m; falls at step 36 in this episode; rank 96/197 by return; 6 of 10 in its cell |
| `hopper_c_goal_best.mp4` | claude_hopper_goal_controller_03_iso2 (claude-sonnet-5-5, controller, goal arm) | highest mean forward distance among all 40 clean goal-arm attempts, any model and mode | mean return 382, mean distance 0.91 m; rank 1/197 by distance, 62/197 by return; falls at step 283 in this episode |
| `hopper_d_ppo_seed0.mp4` | stock PPO seed 0 (baseline, unranked) | the first seed, not chosen by score | mean return 2191, mean distance 12.70 m; falls at step 433 in this episode |

## What the clips show

- (a) is a hopper that **stands still**: 1000 steps, forward distance about 0.14 m, and a return of about 1016 that is almost all
  the +1 healthy bonus. 'Best by return' among Claude weights attempts is therefore a standing attempt, as in the earlier
  finding that the LLM exploited the healthy reward. In (a)'s cell, 2 of 10 attempts stand (00 and 09); the others fall early.
- (b) is the cell median by the stated rule, and it is a failing attempt that falls almost at once. So the median of this
  cell is not a standing attempt, unlike (a).
- (c) is the best forward mover of any clean LLM attempt: under 1 m in the episode and on average, then it falls. Far below PPO.
- (d) PPO moves forward about 9 m in this episode and also falls before the time limit (9% of its scoring episodes reach full length).
- Single-episode numbers (seed 10000) differ from the 100-episode means; the caption shows the means, the live counter shows the episode.
- Selection by return (a, b) and by distance (c) was kept as specified, not swapped for a rule that looks better.
