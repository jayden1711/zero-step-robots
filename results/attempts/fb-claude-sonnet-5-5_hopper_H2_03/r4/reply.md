Round 3 fell backward because the knee buckled: the leg torque stayed near zero for too long. For round 4 I go back to the stable round-1 base, with a strong positive leg torque and the same balance gains on thigh and foot. Instead of a sustained bend, I add one short crouch dip per cycle, which should be too brief to buckle the knee. After the dip the leg goes to full extension, which should push the robot off the ground.

```json
{"target": "cpg", "obs_dim": 11, "act_dim": 3, "hidden": 16,
 "oscillators": [{"name": "hop", "freq_hz": 2.0, "phase0": 0.0}],
 "couplings": [],
 "bias": {"a0": 0.1, "a1": 0.45},
 "units": [
  {"type": "linear", "name": "balance", "inputs": {"obs[1]": -8.0, "obs[7]": -0.8},
   "range": 10.0, "tol": 0.05, "to": {"a0": 1.0, "a2": 1.0}},
  {"type": "reflex", "name": "crouch_gate", "inputs": {"cos(hop)": 1.0},
   "threshold": -0.7, "sharpness": 8.0, "to": {"a1": 0.55}}
 ]}
```