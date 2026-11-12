This is an untested blind design, so it may not pass. The reasoning behind it:

**Geometry.** The hips can only extend (thigh angle ≤ 0 relative to the torso). So the swing foot can land ahead of the hip only when the torso leans back. With the swing thigh driven to its 0 limit, foot placement ahead of the hip is about −(torso angle). Speed is therefore regulated through torso lean: the faster the robot goes, the further back the torso is held, so the foot lands further ahead and the robot slows down. This is a SIMBICON-like foot-placement rule.

**Rhythm.** There are two oscillators at 0.9 Hz, coupled to stay π apart. Phase 0 is mid-stance and π is mid-swing.
- **Thighs:** PD control toward a target of −0.2 − 0.25·sin φ. In stance the thigh sweeps back to −0.45; in swing it returns to the 0 limit.
- **Knees:** PD control toward a target of −0.35 + 0.78·cos φ − 0.33·sin φ. The joint limit at 0 rectifies this, so the knee is straight in stance. In swing it flexes to about −1.1, with the peak early in swing.
- **Ankles:** a soft PD toward flat, plus a gated plantarflex push-off in late stance. The push-off also starts the robot moving from rest.

**Balance.** Torso feedback must act only at the stance hip, because at the swing hip the reaction has the opposite sign. Each leg uses a pair of tanh units. Their arguments are 2·(e ± C·(1−cos φ)), where e = torso angle + 0.075·torso angular velocity + 0.25·forward speed. Summed, the pair gives about −2e at mid-stance and almost 0 in swing, with no constant offset.

```json
{"target": "cpg", "obs_dim": 17, "act_dim": 6, "hidden": 16,
 "oscillators": [
   {"name": "R", "freq_hz": 0.9, "phase0": 0.0},
   {"name": "L", "freq_hz": 0.9, "phase0": 3.14159}
 ],
 "couplings": [
   {"from": "R", "to": "L", "weight": 1.5, "phase_lag": 3.14159},
   {"from": "L", "to": "R", "weight": 1.5, "phase_lag": 3.14159}
 ],
 "bias": {"a0": -0.6, "a1": -0.7, "a2": -0.2, "a3": -0.6, "a4": -0.7, "a5": -0.2},
 "units": [
   {"type": "linear", "name": "R_thigh_pd", "inputs": {"sin(R)": -0.75, "obs[2]": -3.0, "obs[11]": -0.25}, "range": 2.5, "tol": 0.05, "to": {"a0": 1.0}},
   {"type": "linear", "name": "L_thigh_pd", "inputs": {"sin(L)": -0.75, "obs[5]": -3.0, "obs[14]": -0.25}, "range": 2.5, "tol": 0.05, "to": {"a3": 1.0}},
   {"type": "linear", "name": "R_knee_pd", "inputs": {"cos(R)": 1.56, "sin(R)": -0.66, "obs[3]": -2.0, "obs[12]": -0.12}, "range": 2.5, "tol": 0.05, "to": {"a1": 1.0}},
   {"type": "linear", "name": "L_knee_pd", "inputs": {"cos(L)": 1.56, "sin(L)": -0.66, "obs[6]": -2.0, "obs[15]": -0.12}, "range": 2.5, "tol": 0.05, "to": {"a4": 1.0}},
   {"type": "linear", "name": "R_foot_pd", "inputs": {"obs[4]": -0.6, "obs[13]": -0.03}, "range": 1.5, "tol": 0.05, "to": {"a2": 1.0}},
   {"type": "linear", "name": "L_foot_pd", "inputs": {"obs[7]": -0.6, "obs[16]": -0.03}, "range": 1.5, "tol": 0.05, "to": {"a5": 1.0}},
   {"type": "reflex", "name": "R_bal_a", "inputs": {"obs[1]": 1.0, "obs[10]": 0.075, "obs[8]": 0.25, "cos(R)": -0.8}, "threshold": -0.8, "sharpness": 2.0, "to": {"a0": -0.5}},
   {"type": "reflex", "name": "R_bal_b", "inputs": {"obs[1]": 1.0, "obs[10]": 0.075, "obs[8]": 0.25, "cos(R)": 0.8}, "threshold": 0.8, "sharpness": 2.0, "to": {"a0": -0.5}},
   {"type": "reflex", "name": "L_bal_a", "inputs": {"obs[1]": 1.0, "obs[10]": 0.075, "obs[8]": 0.25, "cos(L)": -0.8}, "threshold": -0.8, "sharpness": 2.0, "to": {"a3": -0.5}},
   {"type": "reflex", "name": "L_bal_b", "inputs": {"obs[1]": 1.0, "obs[10]": 0.075, "obs[8]": 0.25, "cos(L)": 0.8}, "threshold": 0.8, "sharpness": 2.0, "to": {"a3": -0.5}},
   {"type": "reflex", "name": "R_pushoff", "inputs": {"sin(R)": 0.878, "cos(R)": 0.479}, "threshold": 0.7, "sharpness": 5.0, "to": {"a2": -0.2}},
   {"type": "reflex", "name": "L_pushoff", "inputs": {"sin(L)": 0.878, "cos(L)": 0.479}, "threshold": 0.7, "sharpness": 5.0, "to": {"a5": -0.2}}
 ]}
```