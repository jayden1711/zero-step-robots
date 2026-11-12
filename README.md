# zero-step-robots

Can an LLM write a robot's brain by hand? Zero training steps: the model writes every weight, and physics scores it.

## Result: a pre-registered negative / partial result

**Target** (pre-registered before any attempt): Claude writes, with no training, the parameters of an oscillator (CPG)
network controller that moves Gymnasium MuJoCo `Hopper-v5` and `Walker2d-v5` at least 3 m forward without falling,
on 100 held-out episodes; a model meets the target when at least 5 of its 10 attempts pass.

| arm | Hopper-v5 | Walker2d-v5 |
|---|---|---|
| One reply, no feedback, 3 hint levels (Opus 5.5 and Sonnet 5.5, 10 attempts per cell) | 0 of 60 attempts pass (best 1.08 m) | 0 of 60 (best 1.30 m) |
| Feedback: 5 revisions from a fixed practice-episode summary (H2 hint) | **Opus: 2 of 10 pass** (6.42 m and 6.90 m); Sonnet 0 of 10 (best 0.96 m) | 0 of 20 (best 0.97 m); Opus got worse with feedback |
| Random-search proposer, same 6-design budget, random start | 0 of 10 (best 0.48 m) | 0 of 10 |
| Hand-built CPG (structure by hand, parameters by search on practice seeds) | **passes** (3.27 m, 80 of 100 episodes >= 3 m) | does not pass (1.29 m) |
| PPO, 1M environment steps, 16-unit MLP (upper reference) | passes (12.7 to 17.5 m) | passes (3.75 to 16.6 m) |

- **No arm met the pre-registered target on either task.** On hopper, 2 of 10 Opus attempts with feedback pass; one of
  them hops for all 1000 steps in every held-out episode. One of the two already passed before any feedback.
- **On hopper the representation is not the limit:** the hand-built CPG of the same network passes, so the gap is in the
  LLM-written controllers. On Walker2d the hand-built CPG did not pass within its budget, so headroom for the CPG network
  there was not shown (PPO's plain 16-unit network does pass).
- Every attempt is reported, failures included: all prompts, replies, compiled designs and per-episode scores are in
  [`results/`](results/) (see [`results/README.md`](results/README.md)). Earlier arms (raw-weight and Python-controller
  attempts on cartpole and hopper, several models) are in [`results/pilot_report.md`](results/pilot_report.md); their
  main finding is that the best-scoring hopper "controllers" stood still to collect the per-step survival reward.
- Pre-registration, in order: [PLAN.md addendum 2026-11-09](PLAN.md) (distance target),
  [docs/prereg-2026-11-09-cpg.md](docs/prereg-2026-11-09-cpg.md) (CPG track),
  [docs/prereg-2026-11-10-cpg-feedback.md](docs/prereg-2026-11-10-cpg-feedback.md) (feedback arm),
  [docs/addendum-2026-11-11-cpg-clips.md](docs/addendum-2026-11-11-cpg-clips.md) (clips). Each was committed before the
  runs it governs; git history shows the order.
- Clips: [`results/clips_cpg/`](results/clips_cpg/), the **pre-registered clip set** (designs and seeds fixed before
  rendering, including a failing design and the hand-built baselines). Objections and limits: [CRITIQUES.md](CRITIQUES.md).
  Short abstract: [docs/abstract.md](docs/abstract.md).

Builds on Rikiya Takehi, Jayden Teoh, Alex Zhang, Omar Khattab (MIT CSAIL), ["Sparks of Weight-Space Programming: LLMs
can natively read & write neural network weights"](https://rikiyat.github.io/blog/weight-space-programming/) (blog post,
Nov 2, 2026; a blog-stage result, not peer-reviewed), and extends it to legged-robot locomotion.

Everything here is simulation (MuJoCo 3.17.0 through Gymnasium 1.4.0); no real robot is involved. The LLM arms used
Claude through the subscription CLI (`claude -p`, isolated: no tools, empty working directory); no paid API.

Plan and history: [PLAN.md](PLAN.md). Code is Apache-2.0 ([LICENSE](LICENSE)). Third-party code and models: [THIRD_PARTY.md](THIRD_PARTY.md).

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
- CPG track (`docs/prereg-2026-11-09-cpg.md`): `zsr/cpg.py` (oscillator network format `cpg-v1`), `circuitc/cpg.py`
  (spec target `cpg`), prompts `prompts/*_v3.md`, `scripts/cpg_baselines.py`, `scripts/run_claude_cpg.sh`,
  `scripts/cpg_report.py`. Tasks now include `walker2d` (`Walker2d-v5`).
- `Makefile`: one target per result (`make test|baselines|lqr|score|variants|report|circuit|notable|clips`).
- `tests/`: `pytest tests`.

Results are in `results/` (published 2026-11-11; new runs write there too, and `results/` stays in `.gitignore` so new files are not added by accident). Setup: `python3 -m venv .venv && .venv/bin/pip install -r requirements.txt`,
and run from the repo root with `PYTHONPATH=.` (or `pip install -e .`-style equivalents).

## Related work
Citations checked by web search on 2026-11-09 unless marked TO VERIFY.

- Rikiya Takehi, Jayden Teoh, Alex Zhang, Omar Khattab (MIT CSAIL), "Sparks of Weight-Space Programming: LLMs can
  natively read & write neural network weights", blog post, 2026-11-02,
  https://rikiyat.github.io/blog/weight-space-programming/ (logs: github.com/RikiyaT/lm_understand-logs). A blog-stage
  result, not peer-reviewed; the authors call the results early. A general LLM reads
  raw network weights and edits them from a plain-language goal, with no gradient descent, on language models. It does
  not cover writing a controller's weights for physical locomotion; that is the slice this repo tests.
- Yujin Tang et al. (Google DeepMind), "SayTap: Language to Quadrupedal Locomotion", CoRL 2023 (PMLR v229),
  arXiv:2306.07580. The LLM writes foot-contact patterns and a trained RL controller executes them; here there is no
  trained controller.
- Yen-Jen Wang, Bike Zhang, Jianyu Chen, Koushil Sreenath, "Prompt a Robot to Walk with Large Language Models"
  (Prompt2Walk), IEEE CDC 2024, arXiv:2309.09969. The LLM outputs joint targets every step from
  few-shot prompts (LLM in the loop), not network weights.
- Yecheng Jason Ma et al., "Eureka: Human-Level Reward Design via Coding Large Language Models", ICLR 2024,
  arXiv:2310.12931. The contrast: the LLM writes reward code and RL (in NVIDIA Isaac Gym) trains the policy; here the LLM writes the policy
  weights (or controller) directly, with no training.
- Wenhao Yu, Fei Xia et al. (Google), "Language to Rewards for Robotic Skill Synthesis", CoRL 2023, arXiv:2306.08647.
  The LLM writes reward code and MuJoCo MPC optimises the actions.
- David Lindner et al., "Tracr: Compiled Transformers as a Laboratory for Interpretability", NeurIPS 2023,
  arXiv:2301.05062 (code: github.com/google-deepmind/tracr). Programs compiled into exact transformer weights; the
  closest analogue of `circuitc/`.
- Auke Jan Ijspeert, "Central pattern generators for locomotion control in animals and robots: a review", Neural
  Networks 21(4):642-653, 2008, doi:10.1016/j.neunet.2008.03.014. Background for the CPG track.
- Junzhi Yu, Min Tan, Jian Chen, Jianwei Zhang, "A Survey on CPG-Inspired Control Models and System Implementation",
  IEEE Transactions on Neural Networks and Learning Systems 25(3):441-456, 2014, doi:10.1109/TNNLS.2013.2280596.
- TO VERIFY (not searched): other work where an LLM designs CPG or gait parameters, beyond SayTap; RoboStriker
  (arXiv 2601.22517); URMA / MetaMorph; Text2Robot. Named here as leads only.
