I can't run anything here, so this controller is untested and the gains are educated guesses. It has one 2 Hz oscillator driving the hop, and the torso angle and angular velocity feed back to the thigh. A small negative thigh bias tilts the torso slightly forward to produce forward speed.

```json
{"target": "cpg", "obs_dim": 11, "act_dim": 3, "hidden": 16,
 "oscillators": [{"name": "hop", "freq_hz": 2.0, "phase0": 0.0}],
 "couplings": [],
 "bias": {"a0": -0.1, "a1": 0.1},
 "units": [
   {"type": "linear", "name": "balance", "inputs": {"obs[1]": 5.0, "obs[7]": 0.5},
    "range": 3.0, "tol": 0.05, "to": {"a0": 1.0}},
   {"type": "linear", "name": "swing", "inputs": {"cos(hop)": 1.0},
    "range": 1.0, "tol": 0.05, "to": {"a0": 0.3}},
   {"type": "linear", "name": "push_leg", "inputs": {"sin(hop)": 1.0},
    "range": 1.0, "tol": 0.05, "to": {"a1": 0.5}},
   {"type": "linear", "name": "push_foot", "inputs": {"sin(hop)": 1.0},
    "range": 1.0, "tol": 0.05, "to": {"a2": 0.2}}
 ]}
```