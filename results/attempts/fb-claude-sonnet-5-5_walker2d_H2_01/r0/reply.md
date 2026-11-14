This is the round-0 design: two antiphase oscillators drive thigh and knee torques, with torso-angle and angular-velocity feedback on both thighs. I could not run it, so the amplitudes, frequency and gains are untested first guesses.

- **Oscillators:** `R` and `L` start half a cycle apart and are coupled with a pi lag in both directions, so they settle in antiphase. I set the frequency to 1.2 Hz.
- **Thigh torque:** `-0.6*sin(phase)`. It is negative while sin > 0 (stance, thigh swings back) and positive in swing.
- **Knee torque:** `+0.5*sin(phase)`. It flexes the knee during swing and extends it in stance.
- **Balance:** `-(obs[1] + 0.1*obs[10])` goes to both thighs. A forward lean or forward pitch rate then gives a negative thigh torque, which pitches the torso back.
- **Feet:** left unpowered for now.

```json
{"target": "cpg", "obs_dim": 17, "act_dim": 6, "hidden": 16,
 "oscillators": [
  {"name": "R", "freq_hz": 1.2, "phase0": 0.0},
  {"name": "L", "freq_hz": 1.2, "phase0": 3.14159}
 ],
 "couplings": [
  {"from": "R", "to": "L", "weight": 3.0, "phase_lag": 3.14159},
  {"from": "L", "to": "R", "weight": 3.0, "phase_lag": 3.14159}
 ],
 "bias": {},
 "units": [
  {"type": "linear", "name": "right_leg_rhythm", "inputs": {"sin(R)": 1.0},
   "range": 1.0, "tol": 0.02, "to": {"a0": -0.6, "a1": 0.5}},
  {"type": "linear", "name": "left_leg_rhythm", "inputs": {"sin(L)": 1.0},
   "range": 1.0, "tol": 0.02, "to": {"a3": -0.6, "a4": 0.5}},
  {"type": "linear", "name": "torso_balance", "inputs": {"obs[1]": 1.0, "obs[10]": 0.1},
   "range": 1.5, "tol": 0.05, "to": {"a0": -1.0, "a3": -1.0}}
 ]}
```