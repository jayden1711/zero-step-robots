> STALE (reviewer recheck, rerun): this file (or its addendum / the Opus lines) was written before the isolated rerun and cites contaminated attempts (`contaminated: /tmp/CLAUDE.md`, mostly Opus). The Sonnet-only three-attempt analysis is unaffected. Do not use the affected parts as is; regenerate from the clean attempts. See CRITIQUES.md, 'Reviewer recheck (rerun)', R-C3.

# Notable hopper weight attempts: structure and robustness (local, not for git)

Simulation only (Gymnasium Hopper-v5 / MuJoCo). Data: `analysis_data.json` (script: `scripts/analyze_weights.py`;
rerun: `PYTHONPATH=. sim-run python scripts/analyze_weights.py results claude_hopper_named_weights_01
claude_hopper_strict_weights_04 claude_hopper_strict_weights_08`). Copies of the three attempt directories
(prompt, reply, parsed weights, score) are in this folder.

Selection note: the owner described two attempts at ~950-1000. Three claude-sonnet-5-5 hopper weight attempts are
in that range (named_01 = 999.1, strict_04 = 944.4, strict_08 = 999.9); all three are analysed. The other 17
claude hopper weight attempts scored 12-194 and are in the pilot report. These three were picked because they scored
high, so this file describes the best cases, not a typical attempt; the full distributions (including how many
attempts of each model and arm reach ~1000) are in `pilot_report.md`.

## What these networks are

All three are, in practice, **linear joint-space PD regulators that hold the stock standing pose**. They do not hop.

- **Mean forward distance over an episode is ~0** (|d| < 0.04 in all three). The return of ~1000 is the +1/step
  alive bonus over 1000 steps; the forward-speed term contributes nothing. They stand still for 1000 steps.
  The do-nothing (zero-weights) policy scores 148.5 on the same seeds because the hopper falls over; so holding
  the pose is a real difference from doing nothing, but it is not locomotion.
- **The tanh units never saturate.** Over 20 recorded episodes, no unit has |tanh| > 0.99 at any step. Every hidden
  unit's pre-activation stays small, so tanh(x) ~ x and the 16-unit network acts as one linear map.
  Evidence: a least-squares linear fit of the (unclipped) network output on the 11 observations has R^2 = 1.00
  for all three action channels in all three attempts, and the fitted linear policy, scored as its own policy,
  reproduces the return (999.1 / 929.4 / 999.9 vs 999.1 / 944.4 / 999.9 for the networks).
- **Most units are unused.** named_01: 3 non-zero hidden units, the other 13 rows of W1 and columns of W2 are zero.
  strict_08: same, 3 units. strict_04: 6 units, 10 zero.

## Inputs -> units -> actions (the mean Jacobian of action w.r.t. observation; obs index in brackets)

Hopper-v5 observation order: [0] torso height, [1] torso pitch, [2] thigh joint, [3] leg joint, [4] foot joint,
[5] x velocity, [6] z velocity, [7] torso angular velocity, [8] thigh joint velocity, [9] leg joint velocity,
[10] foot joint velocity. (Labels are mine, from the Gymnasium docs; the strict prompt did not name them.)

| attempt | thigh action | leg action | foot action |
|---|---|---|---|
| named_01 | -3.0 * obs[2] - 0.2 * obs[8] | -3.0 * obs[3] - 0.2 * obs[9] | -3.0 * obs[4] - 0.2 * obs[10] |
| strict_08 | -3.0 * obs[2] - 0.1 * obs[8] | -3.0 * obs[3] - 0.1 * obs[9] | -3.0 * obs[1] - 0.5 * obs[7] - 0.05 * obs[10] |
| strict_04 | -3.0 * obs[2] - 0.2 * obs[8] | -3.0 * obs[3] - 0.2 * obs[9] | -8.0 * obs[1] - 0.8 * obs[7] |

- **Sign pattern:** every gain is negative, i.e. negative feedback on joint angle (proportional) and joint velocity
  (derivative), driving each joint to 0 rad. Each hidden unit reads one joint angle and its velocity and feeds exactly
  one output (a diagonal / decoupled structure). The foot (ankle) action in strict_04 and strict_08 instead
  uses the torso pitch obs[1] and pitch rate obs[7].
- **Implementation of the gain:** the models picked small W1 scales with large W2 scales (strict_08: W1 entries 0.3 /
  0.01 / 0.05, W2 = 10; strict_04: W2 = -3, -1, -8, -4; named_01: W1 = 3 and W2 = -1) so that tanh stays in its
  linear range. The product W2*W1 is the effective gain listed above.
- **Saturation of the output:** the action clip at +-1 is essentially never hit (0.0% for strict_08 and named_01,
  at most 0.3% of steps for one channel of strict_04). Raw action std is 0.001-0.01 for the two ~1000 attempts:
  the controller almost never acts, because the stock initial pose is already close to its set point.
- **The reply's own description matches the measurement** (strict_08's reply states hip/knee PD to zero, ankle
  pitch feedback, tanh kept near linear); the numbers above come from the weights, not from the reply text.

## Can it be explained as a known controller?

Yes: a decoupled joint-space PD (proportional-derivative) posture-hold, plus an ankle-from-pitch term in two of the
three. It is a textbook linear controller, expressed in a tanh network that is operated in its linear region. The
network structure adds nothing a linear policy lacks on the states it visits (R^2 = 1.00). Whether the model "wrote
a PD controller in weights" or "wrote weights that happen to be linear" is not distinguishable from the weights;
the reply text says the former.

It is not a hopping gait. Nothing here tests locomotion.

## Robustness

- **500 episodes, fresh seeds 20000..20499** (stock Hopper-v5): named_01 999.1 (SEM 0.03, all 500 full length);
  strict_08 1000.0 (SEM 0.03, all full length); strict_04 917.8 (SEM 10.4, 88.4% of episodes full length,
  worst episode 201.7). strict_04's original 100-episode score (944.4) sits inside its sampling spread but above the
  500-episode mean; it is the least reliable of the three. The other two do not fail in 500 episodes.
- **Modified torso mass** (`results/variants/`, 100 episodes, seeds 10000..10099): torso density x2 and x0.5.
  named_01 998.6 / 999.2, strict_08 999.9 / 999.9, strict_04 991.8 / 995.5. These hold-the-pose controllers do not
  depend on the exact torso mass, as expected from a stabilising PD law on a mass that is already supported by
  stiff joints.
- **Not tested:** pushes/disturbances larger than the stock reset noise (<= 0.005), different reset noise
  scales, sensor noise, other terrains. A controller that is this passive may fail under them. Not claimed.

## Limits of this analysis

- Three attempts from one model; no statement about other models or about success rates (see the pilot report).
- "Known controller" is a classification of three numeric structures, not a proof about why the LLM chose them.
- Observation labels are from the Gymnasium documentation and are my reading; the numeric structure does not depend
  on them.

## Addendum (2026-11-06, after round 2): which hopper attempts move forward?

Checked against the final scores of all 160 hopper attempts (all models, modes, arms), `results/pilot_report.md`
(hopper tables now carry forward distance and speed next to every return) and `results/_scratch/hop_table.txt`.

- The three Sonnet attempts above stand still; this analysis already said so (mean forward distance ~0, |d| < 0.04 m).
  Nothing in it needs retracting. The sentence "holding the pose is a real difference from doing nothing" is about
  falling (zero weights fall after ~150 steps); it is not about locomotion.
- The Opus 5.5 hopper attempts that score ~999-1000 (strict weights 9 of 10, named weights 8 of 10, controller arms
  5-9 of 10) are the same kind: mean forward distance ~0 for every one of them. The best-scoring attempt overall for
  a Claude hopper (claude-opus-5-5_hopper_strict_weights_04, ~999.9) stands still for 1000 steps.
  qwen3-coder-30b (named controller, 6 of 10) and gpt-oss-20b (named controller, 3 of 10) also reach ~990-999 by
  standing.
- Not one of the 160 hopper attempts reaches 1 m of mean forward distance per episode. The largest (~0.85 m) is an
  attempt that falls forward within ~90 steps. The three PPO seeds travel an order of magnitude or more further (and
  fall before 1000 steps on most episodes). So: **no LLM attempt, in any arm, produced hopping**; the near-1000 returns
  are the +1/step alive bonus.
- Because the reward pays +1 per healthy step, the best score for "stand" is near the maximum while PPO's return is
  higher only through forward motion; a return near 1000 and a return of 2000-3000 are different behaviours, not
  different degrees of the same one. Clips of both: `results/clips/` (README there).
