# Round 5 (final)

## Where things stand

- **Round 3** is the best so far: 1.48 m in every practice episode. It cannot pass (that needs 3 m), and it fell at 1.53 s for one reason: the forward speed ran away. x rose by 0.10, 0.11, 0.12, 0.14 and then 0.18 m per 0.1 s. The torso pitched forward and outran the leg, which was left trailing at −1.04 rad, until the height dropped below 0.7 m.
- **Round 4** failed for a different reason than I intended. Its backward fall came at 0.2–0.3 s, when speed was still low, so the stronger speed feedback was not the cause. The cause was the start-up balance: the a0 bias went from +0.09 to −0.12, and the stiffer thigh PD pulled the hip negative. Negative thigh torque pitches the torso back, and it tipped over.

## Design for round 5

I keep round 3 exactly as it was for its first second, then add a brake that acts only at high speed.

- **The base is round 3 unchanged.** The biases, gains and rhythm are the same, so the start-up and the first second of the gait should repeat what survived.
- **A new speed-brake reflex on obs[5]**, with threshold 1.5 m/s and sharpness 4:
  - It sends −0.15·tanh(…) to a0 and −0.10·tanh(…) to a2.
  - The biases are lowered by 0.15 on a0 and 0.10 on a2, so the reflex's output at low speed is cancelled.
  - Net effect: about 0 below 1 m/s (at most −0.03 at 1.2 m/s). Toward 2 m/s it adds up to −0.3 on the thigh and −0.2 on the ankle. That pitches the torso back and stops the runaway that ended round 3.

## Risk

This is not guaranteed. If the brake is too weak, I expect roughly the same 1.5 m as round 3. If it fires during the early fast phase, it could tip the robot backward, as in round 4.

Resubmitting round 3 would lock in about 1.48 m, but it cannot pass. This is the smallest change that targets round 3's known failure, so I judged it the better final bet.

```json
{"target": "cpg", "obs_dim": 11, "act_dim": 3, "hidden": 16,
 "oscillators": [{"name": "hop", "freq_hz": 2.0, "phase0": 0.0}],
 "bias": {"a0": -0.06, "a1": -0.6, "a2": 0.05},
 "units": [
   {"type": "linear", "name": "torso_balance", "inputs": {"obs[1]": -4.0, "obs[7]": -0.5, "obs[5]": -0.2},
    "range": 3.5, "tol": 0.05, "to": {"a0": 1.0}},
   {"type": "linear", "name": "thigh_pd", "inputs": {"obs[2]": -1.0, "obs[8]": -0.1},
    "range": 2.5, "tol": 0.05, "to": {"a0": 1.0}},
   {"type": "linear", "name": "thigh_rhythm", "inputs": {"sin(hop)": 0.3},
    "range": 0.5, "tol": 0.02, "to": {"a0": 1.0}},
   {"type": "linear", "name": "leg_pd", "inputs": {"obs[3]": -2.0, "obs[9]": -0.2},
    "range": 4.0, "tol": 0.05, "to": {"a1": 1.0}},
   {"type": "linear", "name": "leg_rhythm", "inputs": {"cos(hop)": 0.6},
    "range": 0.9, "tol": 0.02, "to": {"a1": 1.0}},
   {"type": "linear", "name": "ankle_balance", "inputs": {"obs[1]": -2.5, "obs[7]": -0.4, "obs[5]": -0.125},
    "range": 3.0, "tol": 0.05, "to": {"a2": 1.0}},
   {"type": "linear", "name": "foot_pd", "inputs": {"obs[4]": -0.5, "obs[10]": -0.05},
    "range": 2.0, "tol": 0.05, "to": {"a2": 1.0}},
   {"type": "linear", "name": "foot_rhythm", "inputs": {"cos(hop)": 0.25},
    "range": 0.4, "tol": 0.02, "to": {"a2": 1.0}},
   {"type": "reflex", "name": "speed_brake", "inputs": {"obs[5]": 1.0}, "threshold": 1.5,
    "sharpness": 4.0, "to": {"a0": -0.15, "a2": -0.1}}
 ]}
```