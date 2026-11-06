# zero-step-robots: Claude rules

**Read `~/projects/NUC_RULES.md` first.** It covers Quatern priority, sim-run/gpu-run, the results policy and publishing.

Can an LLM write a robot's brain by hand? Plan: PLAN.md. State: HANDOFF.md.

- **First stop point:** environments, scoring harness, PPO and Python-controller baselines for cartpole and
  hopper, and the prompt template. Then stop and report. **No LLM attempts before the owner says go.**
- **No paid APIs.** No API keys, no SDK calls to hosted models. LLM attempts happen one of two ways:
  (a) the session writes a prompt file to `results/attempts/<id>/prompt.md`, the owner pastes it into their
  subscription by hand and saves the reply as `reply.md`; or (b) a local model on the NUC, served through
  `~/projects/bin/gpu-run`.
- **Fairness:** the prompt contains only what PPO gets (obs/action spec, reward, episode rules). Never add
  hints, tuned constants or example weights. Keep the prompt template versioned and record its hash per attempt.
- **Scoring:** continuous, many episodes, fixed seeds, the same harness for every arm (random, zero, Python
  controller, PPO, LLM-written weights).
- **Every attempt is logged,** failures included (prompt, reply, parsed weights, scores, model + interface).
  Never delete or skip a failed attempt. All of it stays in git-ignored `results/` until the owner approves
  publishing, and then all of it is published, not a selection.
- **Compute:** sims through `~/projects/bin/sim-run` (max 4 processes, one thread each). PPO on the GPU only via
  `gpu-run`; CPU PPO is fine for cartpole/hopper.
- **Part B** depends on humanoid-on-a-chip's distilled walker. Don't start Part B until that exists and the
  owner says go. Don't copy code from the private robot-arena-sim.
- **Public repo, Apache-2.0.** Code only. Confirm the "Sparks of Weight-Space Programming" citation (authors,
  link) before any public write-up. Nothing goes public without the owner's go-ahead.
