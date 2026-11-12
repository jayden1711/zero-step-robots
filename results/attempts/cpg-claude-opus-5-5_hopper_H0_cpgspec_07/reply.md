This is a hand-reasoned hopping controller; I couldn't simulate or tune it, so treat the parameters as an untested first guess.

**Conventions.** All joints use axis (0,−1,0). Positive torso angle means leaning back, and a positive joint angle swings the distal link forward. Positive a2 tilts the toe up and the upper body forward.

**Constraint that shapes the gait.** The hip range is [−150°, 0] and the torso must stay within ±0.2 rad. This rules out a knee-driven crouch, and the leg is far heavier than the torso, so the leg can't be swung during flight. The gait therefore comes from the ankle and foot:

- **Hip (a0):** a PD loop keeps the torso upright.
- **Knee (a1):** a PD loop holds the knee nearly straight (−0.05 rad).
- **Ankle balance (a2):** a PD loop controls how far the upper body's centre of mass sits ahead of the ankle (L, a linear function of the torso, hip and knee angles), with a set-point of 5 cm forward.
  - A velocity term leans the body further forward when torso x-velocity is below 0.8 m/s.
  - A weak term keeps the foot level in world frame.
- **Push-off:** a 2.2 Hz oscillator fires a one-sided toe-down push (up to 0.6) during about 30% of each cycle. The push lifts the heel and launches a short hop. Its reaction rotates the upper body backward, which places the foot ahead of the centre of mass for the next landing.
  - The oscillator starts at phase −3.0, so the first push comes about 0.25 s in, after the initial drop has settled.

```json
{"target": "cpg", "obs_dim": 11, "act_dim": 3, "hidden": 16,
 "oscillators": [{"name": "hop", "freq_hz": 2.2, "phase0": -3.0}],
 "couplings": [],
 "bias": {"a1": -0.15, "a2": -0.065},
 "units": [
   {"type": "linear", "name": "torso_pd_hip",
    "inputs": {"obs[1]": 4.0, "obs[7]": 0.3},
    "range": 2.0, "tol": 0.05, "to": {"a0": 1.0}},
   {"type": "linear", "name": "knee_hold",
    "inputs": {"obs[3]": -3.0, "obs[9]": -0.3},
    "range": 1.5, "tol": 0.05, "to": {"a1": 1.0}},
   {"type": "linear", "name": "ankle_balance",
    "inputs": {"obs[1]": 0.822, "obs[2]": 0.717, "obs[3]": 0.351, "obs[4]": -0.3,
               "obs[7]": 0.222, "obs[8]": 0.197, "obs[9]": 0.112, "obs[10]": -0.04,
               "obs[5]": -0.2},
    "range": 2.0, "tol": 0.05, "to": {"a2": 1.0}},
   {"type": "reflex", "name": "toe_push",
    "inputs": {"sin(hop)": 1.0}, "threshold": 0.6, "sharpness": 8.0,
    "to": {"a2": -0.3}}
 ]}
```

**How the biases break down:**

- **a1 = −0.15:** knee set-point term, −3 × 0.05.
- **a2 = −0.065,** the sum of three parts:
  - +0.075 from the balance set-point (1.5 × 0.05 m)
  - +0.16 from the velocity target (0.2 × 0.8 m/s)
  - −0.3 so that the push is 0 when off and −0.6 when on