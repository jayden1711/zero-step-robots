# Round 2: lower the balance gains

## What round 1 showed

- **The sign fix was correct.** Round 0 drifted slowly and monotonically negative, which is the signature of positive feedback. Round 1 behaved differently: the torso tipped positive (+0.055), then swung to −0.2 within about 0.1 s. That is a fast, growing oscillation, not a drift. So positive thigh torque does lower obs[1], and the brief's "positive = forward lean" is reversed, as the model file's `rooty` axis (0, −1, 0) indicates.
- **The gains were far too high.** Hopper's actuators have a gear ratio of 200, so an action of 1 means about 200 N·m.
  - Kp = 4 gives about 800 N·m/rad.
  - Kd = 0.6 gives about 120 N·m·s/rad.
  - The torque is held for 0.008 s per step. At that gain the damping term overshoots within one step: it reverses the angular velocity and makes it larger, so the loop goes unstable.
  - The thigh saturating on 10% of steps and the balance unit saturating on 4% fit this.

## Round 2 changes

- **Balance gains cut sharply:** a0 = 1.2·obs[1] + 0.12·obs[7] − 0.05·obs[5] + 0.06.
  - The bias sets a target lean of −0.05 rad, which is forward in the corrected convention.
  - The speed term lowers a0 as speed rises, which reduces the forward lean.
- **Rhythm reduced:** thigh 0.15, leg 0.4, foot 0.15, at the same 2 Hz. The external periodic hip torque was probably helping drive the torso oscillation, so this round prioritises staying upright.
- **Foot speed damping halved** to −0.12·obs[5]. Positive foot torque raises the toe and pitches the body forward.
- **Leg PD unchanged.** It kept the leg near straight, which is fine for now.

If this survives, round 3 will increase the rhythm and lean for speed. If the torso still oscillates fast, I'll cut the gains further. If it drifts slowly, I'll raise Kp.

```json
{"target": "cpg", "obs_dim": 11, "act_dim": 3, "hidden": 16,
 "oscillators": [{"name": "cpg", "freq_hz": 2.0, "phase0": 0.0}],
 "couplings": [],
 "bias": {"a0": 0.06},
 "units": [
   {"type": "linear", "name": "torso_balance", "inputs": {"obs[1]": 1.2, "obs[7]": 0.12, "obs[5]": -0.05},
    "range": 2.0, "tol": 0.05, "to": {"a0": 1.0}},
   {"type": "linear", "name": "thigh_rhythm", "inputs": {"cos(cpg)": 0.15},
    "range": 0.25, "tol": 0.02, "to": {"a0": 1.0}},
   {"type": "linear", "name": "leg_pd", "inputs": {"obs[3]": -2.0, "obs[9]": -0.2},
    "range": 4.0, "tol": 0.05, "to": {"a1": 1.0}},
   {"type": "linear", "name": "leg_rhythm", "inputs": {"sin(cpg)": 0.4},
    "range": 0.5, "tol": 0.02, "to": {"a1": 1.0}},
   {"type": "linear", "name": "foot_pd", "inputs": {"obs[4]": -2.0, "obs[10]": -0.2},
    "range": 4.0, "tol": 0.05, "to": {"a2": 1.0}},
   {"type": "linear", "name": "foot_balance", "inputs": {"obs[5]": -0.12},
    "range": 1.5, "tol": 0.05, "to": {"a2": 1.0}},
   {"type": "linear", "name": "foot_rhythm", "inputs": {"sin(cpg)": 0.15},
    "range": 0.25, "tol": 0.02, "to": {"a2": 1.0}}
 ]}
```