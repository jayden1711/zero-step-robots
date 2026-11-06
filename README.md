# zero-step-robots

Can an LLM write a robot's brain by hand? Zero training steps: the model writes every weight, and physics scores it.

Builds on Takehi, Teoh, Zhang, Khattab (MIT CSAIL), ["Sparks of Weight-Space Programming: LLMs can natively read &
write neural network weights"](https://rikiyat.github.io/blog/weight-space-programming/) (Nov 2, 2026), and extends
it to legged robots.

Early stage; see [PLAN.md](PLAN.md). Code is Apache-2.0 ([LICENSE](LICENSE)). Third-party code and models: [THIRD_PARTY.md](THIRD_PARTY.md).

## Layout

- `zsr/tasks.py`: the two tasks (cartpole = `InvertedPendulum-v5`, hopper = `Hopper-v5`), fixed seeds and episode length.
- `zsr/policy.py`: the weight-file format (one hidden layer of 16 tanh units, JSON).
- `zsr/harness.py`: scoring harness, one code path for every arm (`python -m zsr.harness <task> --weights f.json | --controller f.py`).
- `zsr/ppo.py`: PPO baseline (CPU), exports its actor to the weight format so it is scored by the same harness.
- `controllers/`: reference Python controllers used to test the harness.
- `scripts/run_baselines.py`: zero, random (10 seeds) and reference-controller arms.
- `prompts/`, `zsr/attempt.py`: the versioned prompt template, attempt directories, reply parsing and scoring.
- `tests/`: `pytest tests`.

Results are written to the git-ignored `results/`. Setup: `python3 -m venv .venv && .venv/bin/pip install -r requirements.txt`,
and run from the repo root with `PYTHONPATH=.` (or `pip install -e .`-style equivalents).
