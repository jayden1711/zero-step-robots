The round-0 failure was not a weak controller. The torso feedback had the wrong sign, so it made the lean worse instead of correcting it.

**Evidence:**
- Every episode followed the same path. The torso angle drifted steadily negative (−0.03, −0.09, then −0.19 rad) until it left the healthy range, and the thigh torque saturated (17% of steps).
- The +0.15 bias on a0 should have produced a slight positive torso angle. Instead the angle went negative right away.
- That means positive thigh torque *decreases* the torso angle. This fits the stated fact that negative thigh torque pitches the torso backward, but only if the backward direction is +obs[1].
- It also fits the model file. The `rooty` axis is (0, −1, 0), so a positive torso angle tips the top of the torso towards −x. The brief's "positive = forward lean" therefore appears reversed.
- With that reversal, a0 = −4·obs[1] − 0.5·obs[7] is positive feedback. Any small lean grows until the episode ends, which is exactly what we saw.

**Round 1 changes:**
- **Balance sign flipped:** a0 = +4·obs[1] + 0.6·obs[7]. If the torso pitches negative, the thigh torque goes negative, and that drives the torso angle back up.
- **Forward lean and speed regulation (new convention, forward lean = negative obs[1]):**
  - The target lean is about −0.05 rad. That needs a bias of −4·(−0.05) = +0.2 on a0.
  - A −0.1·obs[5] term shrinks the lean as speed rises.
- **Foot ankle strategy:**
  - With this convention, a positive foot angle means toe up, so a positive foot torque resists falling backward.
  - I added a small −0.25·obs[5] term to the foot.
- **Rhythm:** slightly stronger than round 0 (leg 0.6, foot 0.3, thigh swing 0.25) at the same 2 Hz. If the torso now holds, we also learn whether the robot actually hops.

This round mainly tests whether the sign diagnosis is right. If the torso then drifts positive instead, the original convention was correct and something else caused the fall.

```json
{"target": "cpg", "obs_dim": 11, "act_dim": 3, "hidden": 16,
 "oscillators": [{"name": "cpg", "freq_hz": 2.0, "phase0": 0.0}],
 "couplings": [],
 "bias": {"a0": 0.2},
 "units": [
   {"type": "linear", "name": "torso_balance", "inputs": {"obs[1]": 4.0, "obs[7]": 0.6, "obs[5]": -0.1},
    "range": 4.0, "tol": 0.05, "to": {"a0": 1.0}},
   {"type": "linear", "name": "thigh_rhythm", "inputs": {"cos(cpg)": 0.25},
    "range": 0.4, "tol": 0.02, "to": {"a0": 1.0}},
   {"type": "linear", "name": "leg_pd", "inputs": {"obs[3]": -2.0, "obs[9]": -0.2},
    "range": 4.0, "tol": 0.05, "to": {"a1": 1.0}},
   {"type": "linear", "name": "leg_rhythm", "inputs": {"sin(cpg)": 0.6},
    "range": 0.7, "tol": 0.02, "to": {"a1": 1.0}},
   {"type": "linear", "name": "foot_pd", "inputs": {"obs[4]": -2.0, "obs[10]": -0.2},
    "range": 4.0, "tol": 0.05, "to": {"a2": 1.0}},
   {"type": "linear", "name": "foot_balance", "inputs": {"obs[5]": -0.25},
    "range": 2.5, "tol": 0.05, "to": {"a2": 1.0}},
   {"type": "linear", "name": "foot_rhythm", "inputs": {"sin(cpg)": 0.3},
    "range": 0.4, "tol": 0.02, "to": {"a2": 1.0}}
 ]}
```