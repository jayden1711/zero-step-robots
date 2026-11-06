# zero-step-robots: PLAN (summary; the first session expands it for owner approval)

Question: can an LLM write a working robot controller's weights directly, with zero training steps?
Physics scores every attempt.

Builds on Takehi, Teoh, Zhang, Khattab (MIT CSAIL), "Sparks of Weight-Space Programming: LLMs can natively read &
write neural network weights," Nov 2, 2026. https://rikiyat.github.io/blog/weight-space-programming/
This project extends it to legged robots.

## Part A: write from scratch
The LLM writes **all weights** of small control networks from scratch, in increasing difficulty:
cartpole → hopper → small humanoid balance.

## Part B: edit an existing policy
The LLM edits an existing small walking policy (the distilled walker from humanoid-on-a-chip) so that it:
limps, walks backwards, or tolerates a sensor fault.

## Controls
- random weights
- zero weights
- the same LLM writing a normal Python controller (not weights)
- PPO

## Rules
- **Same information as PPO.** The model gets only what PPO gets: observation/action spec, reward
  definition, episode rules. No extra hints, demonstrations or privileged state.
- **Continuous scores over many episodes** (fixed seeds, many episodes per attempt), not pass/fail.
- **Every attempt is published**, failures included. No cherry-picking. Publishing happens only after the
  owner approves; until then everything stays in git-ignored `results/`.
- **LLM access:** through the owner's subscriptions by hand (prompt files the owner pastes, replies saved back)
  or local models on the NUC. No paid API calls.

## First stop point
1. Environments: cartpole and hopper (fixed versions, seeds, episode length).
2. Scoring harness: loads a weight file or a Python controller, runs N episodes, reports continuous scores.
3. Baselines for cartpole and hopper: random, zero, PPO, plus a reference Python controller to test the harness.
4. Prompt template: what the model is given (the same as PPO), the output format for weights, and the output
   format for a Python controller.

Then stop and report, before any LLM attempts.
