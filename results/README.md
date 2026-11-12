# results/ (published 2026-11-11 with the owner's approval)

Every attempt of every arm is here, failures included: 640 attempts in `attempts/` (the 40 feedback-arm attempts hold
6 rounds each), plus 2 kept transport failures. Simulation only (MuJoCo
3.17.0 through Gymnasium 1.4.0, `MANIFEST.md`); no real robot.

## Start here
- `cpg_feedback_report.md`, `cpg_feedback_findings.md`: the CPG feedback arm (prereg `docs/prereg-2026-11-10-cpg-feedback.md`).
- `cpg_report.md`, `cpg_findings.md`: the CPG track without feedback, with baselines and the necessity table
  (prereg `docs/prereg-2026-11-09-cpg.md`).
- `pilot_report.md`: the earlier arms (raw weights and Python controllers; cartpole and hopper; Claude Sonnet/Opus,
  Qwen3-Coder-30B, gpt-oss-20b; strict, named and goal prompts; physics variants).
- `clips_cpg/`: the **pre-registered clip set** (`docs/addendum-2026-11-11-cpg-clips.md`; designs and seeds fixed before
  rendering). `clips/`: the earlier clips (2026-11-07; their camera does not follow the robot, see the note there).

## Layout
- `attempts/<id>/`: one directory per attempt: `prompt.md`, `meta.json` (model, interface, prompt hashes, flags,
  contamination label), `run.json` (raw CLI or server output, token use), `reply.md`, the parsed artefact
  (`parsed.weights.json`, `parsed.controller.py`, or `parsed.spec.json` + `parsed.cpg.json` + `compile_report.json`) and
  `score.json` (100 scoring episodes, per-episode numbers). Ids:
  - `claude_*`, `claude-opus-5-5_*`, `qwen3-coder-30b_*`, `gpt-oss-20b_*`: earlier arms; `_iso2` = the isolated rerun.
    The 120 attempts labelled `contaminated` in `meta.json` (an unrelated project's instruction file was in context) are
    kept, excluded from the main tables, and listed separately in `pilot_report.md` (CRITIQUES.md item 12).
  - `cpg-claude-*_<task>_H{0,1,2}_cpgspec_NN`: CPG track, one reply each.
  - `fb-claude-*_<task>_H2_NN/r0..r5/`: feedback arm, one subdirectory per round (prompt with the full history, reply,
    the dev-seed summary the model saw in `feedback.txt`, and that round's held-out score, which the model never saw);
    the attempt's `score.json` is round 5's.
  - `*_try1`, `*_aborted1`: transport failures (no reply), kept with a `NOTE.md`, listed in the reports, not attempts.
- `baselines/`, `cpg/baselines/`, `cpg/ppo/`: zero, random, reference controllers, tuned CPGs, PPO scores.
- `cpg_feedback/rs/`: the random-search proposer baselines. `variants/`: modified-physics scores. `circuit/`, `notable/`,
  `reviewer/`, `pilot/`: compiler fixtures, the notable-weights analysis, reviewer rechecks, pilot probes.
- `claude_isolation_probe_*.json`: the isolation probes run before each Claude batch.

## Not included, and why
- Agent scratch and moved-aside files (`_scratch/`, `_trash/`) and run logs (`*.log`): working files, not results; every
  number in the reports is recomputed from the attempt directories by the scripts in `scripts/`.
- PPO weight files (`*_ppo_seed*.weights.json`): trained checkpoints are kept out of git by the repo rules; their scores
  are here, and `zsr/ppo.py` retrains them (SB3 defaults, fixed seeds).
- `clips/_old_contaminated/` and `clips_cpg/_render1_fixed_camera/`: superseded renders marked "not to be used" (the
  first shows contaminated attempts, the second used a camera that does not follow the robot).

The account email that the Claude CLI places in every call's context was replaced by `[redacted-email]` before any file
was written (CRITIQUES.md item 12).
