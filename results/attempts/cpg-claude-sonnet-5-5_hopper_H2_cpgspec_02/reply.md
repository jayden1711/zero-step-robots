I could not run anything, so this is a conservative hand-designed spec rather than a tuned one.

- **Rhythm:** one 2 Hz oscillator drives the leg and foot with a sine, and the thigh with a cosine, so the thigh is a quarter-cycle out of phase with the leg.
- **Balance:** the thigh gets negative feedback on torso angle and angular velocity, with the angle term saturating at 1 near 0.2 rad of lean.
- **Bias:** a constant positive leg torque helps hold the body up.
- **Speed:** no explicit speed regulation, because I couldn't tune it blind.

```json
{"target": "cpg", "obs_dim": 11, "act_dim": 3, "hidden": 16,
 "oscillators": [{"name": "hop", "freq_hz": 2.0, "phase0": 0.0}],
 "couplings": [],
 "bias": {"a1": 0.3},
 "units": [
   {"type": "linear", "name": "balance", "inputs": {"obs[1]": 1.0, "obs[7]": 0.1},
    "range": 1.5, "tol": 0.05, "to": {"a0": -4.0}},
   {"type": "linear", "name": "push", "inputs": {"sin(hop)": 1.0},
    "range": 1.2, "tol": 0.02, "to": {"a1": 0.6, "a2": 0.3}},
   {"type": "linear", "name": "swing", "inputs": {"cos(hop)": 1.0},
    "range": 1.2, "tol": 0.02, "to": {"a0": 0.4}}
 ]}
```