Round 3 hopped but pitched forward while airborne. In flight, the thigh-torque reaction on the torso has the opposite sign to the one on the ground, so my strong balance gains pushed the torso further over. For round 4 I'm lowering the balance gains and the thigh rhythm and bias, keeping the thigh angle feedback to stop the backward drift. I'm also raising the leg extension bias a little to reduce the sinking seen in round 0.

```json
{"target": "cpg", "obs_dim": 11, "act_dim": 3, "hidden": 16,
 "oscillators": [{"name": "hop", "freq_hz": 2.5, "phase0": 0.0}],
 "couplings": [],
 "bias": {"a0": 0.05, "a1": 0.4},
 "units": [
  {"type": "linear", "name": "balance", "inputs": {"obs[1]": 2.5, "obs[7]": 0.25, "obs[2]": 1.5, "obs[8]": 0.15},
   "range": 8.0, "tol": 0.05, "to": {"a0": -1.0}},
  {"type": "linear", "name": "sin_drive", "inputs": {"sin(hop)": 1.0},
   "range": 1.0, "tol": 0.01, "to": {"a1": 0.6, "a2": 0.25}},
  {"type": "linear", "name": "cos_drive", "inputs": {"cos(hop)": 1.0},
   "range": 1.0, "tol": 0.01, "to": {"a0": 0.2}}
 ]}
```