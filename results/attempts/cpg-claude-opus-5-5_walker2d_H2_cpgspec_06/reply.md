This is a single oscillator driving both legs half a cycle apart, with PD-style joint servos and balance feedback added on top. I couldn't run or test it, so the gains below come from hand estimates of the robot's masses and inertias, not from simulation.

**How the controller works:**

- **One oscillator, both legs.** The left leg uses the right leg's phase plus π, so its cos and sin weights are simply negated. Antiphase is therefore exact and needs no coupling.
- **Cadence follows speed.** The base frequency is 0.6 Hz, plus 3 rad/s of phase rate per m/s of forward speed. At about 0.8 m/s the stride rate is about 1 Hz, so the legs step faster if the body starts falling forward.
- **Thigh servo (one unit per leg).** Each thigh unit computes `4*(q_des - q) - 0.12*q̇ - 0.5*(β - β_des) - 0.03*ω`, where β is the torso angle and ω its angular velocity:
  - The thigh target is `q_des = -0.275 + 0.225*cos(phase)`, with the constant part in the bias.
  - The target torso lean is β_des ≈ -0.25. Because thigh angles can only be ≤ 0, leaning the torso back is the only way to put the landing foot about 0.2 rad ahead of the hip.
  - On a stance leg the joint stiffness also stabilises the torso. The damping is kept low enough for the stiff torso loop to stay stable at 8 ms steps.
- **Knee servo (one unit per leg).** It holds the knee near -0.1 (almost straight) in stance with gains 1.5 and 0.1.
- **Swing reflex (one unit per leg).** It flexes the knee by about 0.9 rad from just before lift-off until about 0.7 rad of phase before landing. It also lifts the toe during swing.
- **Ankle servo (one unit per leg).** It holds the foot near flat and adds speed feedback, `-0.1*(vx - 0.7)`: toes press down to brake when too fast and lift to tip the body forward when too slow.
- **Start-up.** The phase starts at π/2: the right leg is in mid-stance and the left leg in mid-swing, so walking begins with one step.

```json
{"target": "cpg", "obs_dim": 17, "act_dim": 6, "hidden": 16,
 "oscillators": [{"name": "osc", "freq_hz": 0.6, "phase0": 1.5708, "feedback": {"obs[8]": 3.0}}],
 "couplings": [],
 "bias": {"a0": -1.225, "a1": -0.8, "a2": 0.17, "a3": -1.225, "a4": -0.8, "a5": 0.17},
 "units": [
   {"type": "linear", "name": "thigh_R", "inputs": {"obs[2]": -4.0, "obs[11]": -0.12, "cos(osc)": 0.9, "obs[1]": -0.5, "obs[10]": -0.03},
    "range": 3.0, "tol": 0.05, "to": {"a0": 1.0}},
   {"type": "linear", "name": "thigh_L", "inputs": {"obs[5]": -4.0, "obs[14]": -0.12, "cos(osc)": -0.9, "obs[1]": -0.5, "obs[10]": -0.03},
    "range": 3.0, "tol": 0.05, "to": {"a3": 1.0}},
   {"type": "linear", "name": "knee_R", "inputs": {"obs[3]": -1.5, "obs[12]": -0.1},
    "range": 2.5, "tol": 0.05, "to": {"a1": 1.0}},
   {"type": "linear", "name": "knee_L", "inputs": {"obs[6]": -1.5, "obs[15]": -0.1},
    "range": 2.5, "tol": 0.05, "to": {"a4": 1.0}},
   {"type": "linear", "name": "foot_R", "inputs": {"obs[4]": -0.4, "obs[13]": -0.02, "obs[8]": -0.1},
    "range": 1.2, "tol": 0.05, "to": {"a2": 1.0}},
   {"type": "linear", "name": "foot_L", "inputs": {"obs[7]": -0.4, "obs[16]": -0.02, "obs[8]": -0.1},
    "range": 1.2, "tol": 0.05, "to": {"a5": 1.0}},
   {"type": "reflex", "name": "swing_R", "inputs": {"sin(osc)": -0.878, "cos(osc)": -0.479}, "threshold": 0.2,
    "sharpness": 4.0, "to": {"a1": -0.65, "a2": 0.1}},
   {"type": "reflex", "name": "swing_L", "inputs": {"sin(osc)": 0.878, "cos(osc)": 0.479}, "threshold": 0.2,
    "sharpness": 4.0, "to": {"a4": -0.65, "a5": 0.1}}
 ]}
```