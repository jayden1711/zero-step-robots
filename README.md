# zero-step-robots

Can an LLM write a robot's brain by hand? Zero training steps: the model writes every weight, and physics scores it.

Builds on Takehi, Teoh, Zhang, Khattab (MIT CSAIL), ["Sparks of Weight-Space Programming: LLMs can natively read &
write neural network weights"](https://rikiyat.github.io/blog/weight-space-programming/) (Nov 2, 2026), and extends
it to legged robots.

Everything here is simulation (MuJoCo through Gymnasium); no real robot is involved.

Early stage; see [PLAN.md](PLAN.md). Objections and how each is handled: [CRITIQUES.md](CRITIQUES.md). Code is Apache-2.0 ([LICENSE](LICENSE)). Third-party code and models: [THIRD_PARTY.md](THIRD_PARTY.md).

## Layout

- `zsr/tasks.py`: the two tasks (cartpole = `InvertedPendulum-v5`, hopper = `Hopper-v5`), fixed seeds and episode length.
- `zsr/policy.py`: the weight-file format (one hidden layer of 16 tanh units, JSON).
- `zsr/harness.py`: scoring harness, one code path for every arm (`python -m zsr.harness <task> --weights f.json | --controller f.py`).
- `zsr/ppo.py`: PPO baseline (CPU), exports its actor to the weight format so it is scored by the same harness.
- `controllers/`: reference Python controllers used to test the harness.
- `scripts/run_baselines.py`: zero, random (10 seeds) and reference-controller arms.
- `prompts/`, `zsr/attempt.py`: the versioned prompt template, attempt directories, reply parsing and scoring.
- `zsr/variants.py`: modified-physics variants (pole length/mass, gravity, torso mass) scored for every arm.
- `scripts/`: `run_pilot.py` (LLM attempts, weights or controller mode), `run_local.sh` (local models via gpu-run),
  `score_pending.sh`, `score_variants.py`, `make_lqr.py`, `analyze_weights.py`, `pilot_report.py`, `run_circuit.sh`.
- `circuitc/`: circuit-spec compiler (spec to exact weights), see `docs/circuit-spec.md`.
- `Makefile`: one target per result (`make test|baselines|lqr|score|variants|report|circuit|notable|clips`).
- `tests/`: `pytest tests`.

Results are written to the git-ignored `results/`. Setup: `python3 -m venv .venv && .venv/bin/pip install -r requirements.txt`,
and run from the repo root with `PYTHONPATH=.` (or `pip install -e .`-style equivalents).

## Related work
- Takehi, Teoh, Zhang, Khattab (MIT CSAIL), "Sparks of Weight-Space Programming" (Nov 2, 2026), the approach this builds on.
- Lindner et al. (DeepMind), Tracr, arXiv 2301.05062: compiles programs to exact transformer weights; closest analogue for `circuitc/` [verify].
- Related, not yet checked against the sources, so cited by name only: RoboStriker (arXiv 2601.22517) [verify];
  URMA / MetaMorph [verify]; Text2Robot [verify].

