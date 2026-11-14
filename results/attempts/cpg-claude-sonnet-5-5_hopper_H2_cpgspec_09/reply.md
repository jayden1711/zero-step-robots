This spec is untested, since I can't run anything here. It uses one 2 Hz oscillator for the hop cycle, with the thigh, leg and foot driven by `sin(phase)` and torso-angle feedback on the thigh.

- **Rhythm:** In the first half of each cycle (`sin` positive) the leg extends and the foot pushes. The thigh torque is negative in that half, so it doesn't swing the leg forward during push-off. In the second half the leg flexes and the thigh swings forward for the next landing.
- **Balance:** The thigh gets `-4*obs[1] - 0.5*obs[7]`, which opposes forward lean and rotation.
- **Forward speed:** A constant +0.2 thigh bias sets a slight forward lean target, equivalent to a torso angle of about 0.05 rad.

```json
{"target": "cpg", "obs_dim": 11, "act_dim": 3, "hidden": 16,
 "oscillators": [{"name": "hop", "freq_hz": 2.0, "phase0": 3.5}],
 "couplings": [],
 "bias": {"a0": 0.2, "a1": 0.2},
 "units": [
   {"type": "linear", "name": "rhythm", "inputs": {"sin(hop)": 1.0},
    "range": 1.2, "tol": 0.05, "to": {"a0": -0.3, "a1": 0.8, "a2": 0.3}},
   {"type": "linear", "name": "balance", "inputs": {"obs[1]": -4.0, "obs[7]": -0.5},
    "range": 3.0, "tol": 0.05, "to": {"a0": 1.0}}
 ]}
```