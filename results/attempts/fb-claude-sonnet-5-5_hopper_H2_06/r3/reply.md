Round 3 is a guess from the round 0 to 2 results, since all three fell backward in about 0.3 s. Two changes:

- **Foot feedback:** the negative gain in round 2 made the backward drift worse (d went from about +0.02 to -0.08), so I'm flipping it to positive.
- **Knee bend:** I added a constant negative leg bias so the knee flexes. Earlier runs show the thigh pinned at its 0 rad limit, where balance torque on it does nothing, and a bent knee should get it off that limit.

```json
{"target": "cpg", "obs_dim": 11, "act_dim": 3, "hidden": 16,
 "oscillators": [{"name": "hop", "freq_hz": 2.0, "phase0": 0.0}],
 "couplings": [],
 "bias": {"a1": -0.3},
 "units": [
  {"type": "linear", "name": "rhythm", "inputs": {"cos(hop)": 1.0},
   "range": 1.5, "tol": 0.02, "to": {"a0": 0.1, "a1": 0.3}},
  {"type": "linear", "name": "balance", "inputs": {"obs[1]": -5.0, "obs[7]": -0.5},
   "range": 4.0, "tol": 0.02, "to": {"a0": 1.0, "a2": 0.6}}
 ]}
```