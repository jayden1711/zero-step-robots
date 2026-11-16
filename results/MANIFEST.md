
## MuJoCo versions (recorded 2026-11-07)
Owner rule: mujoco<4 in every venv (pinned with <venv>/mujoco-pin.txt and <venv>/pip.conf; uv venvs: pass -c <venv>/mujoco-pin.txt).

| venv | installed |
|---|---|
| `~/projects/zero-step-robots/.claude/worktrees/first-stop-point/.venv` | mujoco==3.17.0 |

## CPG track (2026-11-09, branch worktree-cpg)
| venv | installed |
|---|---|
| `.claude/worktrees/first-stop-point/.venv` (symlinked as `.claude/worktrees/cpg/.venv`) | mujoco==3.17.0, gymnasium==1.4.0 (Hopper-v5, Walker2d-v5) |
Outputs: `results/cpg/baselines/<task>/`, `results/cpg/ppo/<task>/`, `results/attempts/cpg-claude-*`, `results/cpg_report.md`, logs in `results/cpg/logs/`.

## Warm-start study (2026-11-16, branch writing-1116; prereg docs/prereg-followup-draft.md)
| venv | installed |
|---|---|
| `.claude/worktrees/first-stop-point/.venv` (used from `~/projects/wt/zero-step-robots-writing`) | mujoco==3.17.0, gymnasium==1.4.0 |
Outputs: `results/warmstart/<task>/{L,P,R,H}/*.json` (500 runs), `results/warmstart/walker2d/headroom/` (Stage B), `results/warmstart_report.md`. No MuJoCo 4.0 anywhere.
