This is an untested design: I couldn't simulate it, so every gain is reasoned from the model's geometry rather than tuned.

**Rhythm.** One 2 Hz oscillator drives a stiff-legged ankle hop.
- **Push-off, sin(φ) > 0:** the foot presses its toe down (a2 < 0), which lifts the robot off the ground. At the same time the hip pushes the leg slightly backward (a0 < 0) to move the body forward.
- **Flight, sin(φ) < 0:** the toe lifts ready for landing, and the thigh swings the leg forward again.

**Balance.** A PD loop on the torso angle and angular velocity drives the hip: a0 = −3·(θ − θ_ref) − 0.075·ω. The gains are sized against the torso's inertia and the 0.008 s step so the discrete loop stays stable. The thigh can't swing forward of the torso, so I set the upright target slightly backward (θ_ref ≈ −0.05). That keeps the foot roughly under the hip and leaves room for corrections in both directions.

**Speed.** A small term in obs[5] tilts the hip command so the torso leans back as the robot speeds up, which places the foot further ahead and slows the next hop. It is centred near 0.5 m/s.

**Knee and foot.** The knee is held straight with a positive bias plus a spring term. A light spring-damper keeps the foot near neutral so each landing is roughly flat.

```json
{"target": "cpg", "obs_dim": 11, "act_dim": 3, "hidden": 16,
 "oscillators": [{"name": "hop", "freq_hz": 2.0, "phase0": 0.0}],
 "couplings": [],
 "bias": {"a0": -0.1, "a1": 0.4, "a2": 0.0},
 "units": [
   {"type": "linear", "name": "torso_balance_pd", "inputs": {"obs[1]": 1.0, "obs[7]": 0.025},
    "range": 0.5, "tol": 0.05, "to": {"a0": -3.0}},
   {"type": "linear", "name": "speed_regulation", "inputs": {"obs[5]": 1.0},
    "range": 3.0, "tol": 0.05, "to": {"a0": -0.1}},
   {"type": "linear", "name": "thigh_rhythm", "inputs": {"sin(hop)": 1.0},
    "range": 1.0, "tol": 0.02, "to": {"a0": -0.1}},
   {"type": "linear", "name": "ankle_pushoff_rhythm", "inputs": {"sin(hop)": 1.0},
    "range": 1.0, "tol": 0.02, "to": {"a2": -0.4}},
   {"type": "linear", "name": "foot_centering", "inputs": {"obs[4]": 1.0, "obs[10]": 0.07},
    "range": 1.5, "tol": 0.05, "to": {"a2": -0.3}},
   {"type": "linear", "name": "knee_hold_straight", "inputs": {"obs[3]": 1.0, "obs[9]": 0.05},
    "range": 1.0, "tol": 0.05, "to": {"a1": -1.0}}
 ]}
```