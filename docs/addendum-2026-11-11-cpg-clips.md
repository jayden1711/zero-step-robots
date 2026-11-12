# Addendum 2026-11-11: clips of the CPG feedback arm (render plan, fixed before viewing)

Written 2026-11-11 (CST) on the organizer's request, before any of these clips is rendered or viewed. No training, no
LLM call, no new attempt: every clip replays an existing design's compiled `cpg-v1` weights from `results/`.

## What is rendered (5 designs x 3 seeds = 15 clips)

| # | design | why it is included |
|---|---|---|
| 1 | `fb-claude-opus-5-5_hopper_H2_08`, round 5 (its final, scored design) | passing LLM design |
| 2 | `fb-claude-opus-5-5_hopper_H2_03`, round 5 (its final, scored design) | passing LLM design (passed already at round 0) |
| 3 | the Opus Walker2d feedback attempt whose round-5 held-out mean d is the **lower median** of its 10 attempts (5th lowest; ties broken by attempt id), its round-5 design | a failing LLM design, picked by rank, not by viewing |
| 4 | the hopper search-tuned CPG (`results/cpg/baselines/hopper/tuned_cpg.spec.json`) | baseline for #1 and #2 |
| 5 | the Walker2d search-tuned CPG (`results/cpg/baselines/walker2d/tuned_cpg.spec.json`) | baseline for #3 |

- **Seeds:** the first 3 held-out scoring seeds by index: **10000, 10001, 10002**, for every design. (Held-out = never
  shown to the model; these are the first three of the 100 scoring episodes.)
- **Camera and format:** the environment's default tracking camera, 640x480, every 4th simulation step at 31 fps; one
  full episode per clip (up to 1000 steps, about 8 s; after a fall the last frame is held to the same length).
- **Caption on every frame:** SIMULATION (no real robot), task, design id and round, how it was selected, episode seed,
  the design's held-out score (mean d to the last healthy step, clean-episode count, over the 100 scoring episodes),
  and a live step / distance counter with the episode state (running, fell at step N, or 1000 steps reached).
- **Software:** MuJoCo 3.17.0 (mujoco<4, as in `results/MANIFEST.md`), Gymnasium 1.4.0, software EGL (no GPU),
  single-threaded libx264 encoder, run through `~/projects/bin/sim-run`.
- **Output:** `results/clips_cpg/` (git-ignored): the 15 mp4 files, `selection.json` (selected ids and per-episode
  numbers) and `README.md`. All 15 are kept and listed, whatever they show; none is dropped or re-rendered with other seeds.
- Script: `scripts/make_cpg_clips.py`, committed with or after this file and before rendering.

## Correction 2026-11-11 (before the second render): camera

The first render used Gymnasium's default render camera. In Gymnasium 1.4.0 that camera does **not** follow the robot
(the default config names a body but the camera stays fixed), so in the hopper clips the robot walks out of the frame.
I saw this while checking frames of the first render; nothing else in the plan changes. Second render: the `track`
camera defined in both model files (`hopper.xml`, `walker2d.xml`: mode `trackcom`, 3 m to the side), which follows the
centre of mass. Same 5 designs, same seeds 10000-10002, same length and captions; all 15 clips re-rendered. The first
render is kept unchanged in `results/clips_cpg/_render1_fixed_camera/` and is not to be used. The earlier
`results/clips/` (2026-11-07) used the same default camera; that is noted in its README, and it was not re-rendered.
