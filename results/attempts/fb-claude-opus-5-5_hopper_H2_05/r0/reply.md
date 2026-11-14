Round 0 design: one 2 Hz hop oscillator, PD balance at the thigh, posture PD at each joint, and moderate rhythmic torques. Amplitudes are deliberately conservative so the first results show whether the rhythm moves the robot forward or knocks it over.

**How it works:**
- **Oscillator `hop`:** runs at 2.0 Hz, starting at phase 0.
- **Rhythm:**
  - `sin(hop)` drives the leg extension and compression: 0.45 to the leg joint and 0.35 to the foot.
  - `cos(hop)` drives the thigh swing, 90° out of phase with the push: 0.3 to the thigh.
- **Torso balance at the thigh:**
  - The thigh torque is a0 = −5·obs[1] − 0.5·obs[7] − 0.1·obs[5] + 0.2.
  - The +0.2 bias makes the controller hold a torso lean of about 0.04 rad forward, which drives forward motion.
  - The −0.1·obs[5] term reduces that lean as forward speed rises, which limits speed.
- **Posture:**
  - The leg and foot joints have weak PD pulls toward 0 (straight), so the rhythm moves them around a neutral pose.
  - The thigh has a lighter PD so it doesn't fight the balance term.

```json
{"target": "cpg", "obs_dim": 11, "act_dim": 3, "hidden": 16,
 "oscillators": [{"name": "hop", "freq_hz": 2.0, "phase0": 0.0}],
 "couplings": [],
 "bias": {"a0": 0.2},
 "units": [
   {"type": "linear", "name": "torso_balance", "inputs": {"obs[1]": -5.0, "obs[7]": -0.5, "obs[5]": -0.1},
    "range": 3.0, "tol": 0.05, "to": {"a0": 1.0}},
   {"type": "linear", "name": "thigh_posture", "inputs": {"obs[2]": -1.0, "obs[8]": -0.05},
    "range": 2.0, "tol": 0.05, "to": {"a0": 1.0}},
   {"type": "linear", "name": "leg_posture", "inputs": {"obs[3]": -2.0, "obs[9]": -0.1},
    "range": 3.0, "tol": 0.05, "to": {"a1": 1.0}},
   {"type": "linear", "name": "foot_posture", "inputs": {"obs[4]": -2.0, "obs[10]": -0.1},
    "range": 3.0, "tol": 0.05, "to": {"a2": 1.0}},
   {"type": "linear", "name": "push_rhythm", "inputs": {"sin(hop)": 1.0},
    "range": 1.0, "tol": 0.01, "to": {"a1": 0.45, "a2": 0.35}},
   {"type": "linear", "name": "swing_rhythm", "inputs": {"cos(hop)": 1.0},
    "range": 1.0, "tol": 0.01, "to": {"a0": 0.3}}
 ]}
```