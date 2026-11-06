# HANDOFF: zero-step-robots
Status: first stop point reached (envs, harness, baselines, prompt template v1 built and tested); no LLM attempts made
Next: owner reviews PLAN.md "First-stop-point design" and the baseline scores in results/baselines/, then says go (or not) for LLM attempts
Updated: 2026-11-06

## What exists (branch `worktree-first-stop-point`, commit 62fd835 plus this handoff; NOT pushed)
- `zsr/` package: tasks (cartpole = InvertedPendulum-v5, hopper = Hopper-v5, 1000 steps), weight format
  (16-tanh MLP JSON), harness, PPO, attempt/prompt/reply-parsing tooling. `tests/` (11 pass): `pytest tests`.
- Prompt template v1 in `prompts/`; `python -m zsr.attempt prompt <task> <weights|controller>` prints a prompt,
  `new` creates `results/attempts/<id>/` with prompt.md + meta.json (prompt hash, model, interface), `score` parses
  `reply.md` and scores it (failures are scored and kept).
- Baselines (zero, random x10 seeds, reference Python controller, PPO x3 seeds per task) are all scored with the
  same harness (100 episodes, seeds 10000..10099). Files: `results/baselines/*.score.json` and
  `results/baselines/ppo/` in the MAIN checkout (git-ignored). Numbers deliberately not quoted here.
- Venv: `.venv` in the worktree (git-ignored); recreate with requirements.txt. Run with `PYTHONPATH=.`.

## Things to know
- The PPO weights score full marks on cartpole through the harness, which confirms the weight export is lossless.
- The hopper reference controller is weak by design (random-search linear policy, harness test only, not an arm to
  beat). It overfit its 5 search episodes.
- Python controllers run in the harness process with rlimits (4 GB, 3600 s CPU); that is not a sandbox. Run LLM code
  only through sim-run on the NUC.
- The worktree is `.claude/worktrees/first-stop-point`; merge or cherry-pick the branch to main when happy, then push.

## Decisions taken overnight
- Cartpole uses Gymnasium `InvertedPendulum-v5` (continuous action) rather than discrete `CartPole-v1`, so weights
  can emit a force directly. Conservative: standard, documented env.
- Prompt names the observation components (from Gymnasium docs) because the reward definition refers to them. This
  is arguably slightly more than PPO's raw numbers; drop the names if you want strict parity.
- Same 16-unit tanh architecture is given to the LLM and used by PPO (PPO also has a separate 64x64 value net,
  which is training-only and not part of the policy).
- PPO: SB3 default hyperparameters, no tuning (cartpole 100k steps, hopper 1M steps, 3 seeds). Scored once; not
  re-run or picked from.
- Ran at most 2 sim processes of my own at a time because other projects had sims running.
- No attempt directories were created under results/attempts/ (tests used a temp dir).
- Installed Python packages into a project venv from PyPI (pip worked, no blocks).
