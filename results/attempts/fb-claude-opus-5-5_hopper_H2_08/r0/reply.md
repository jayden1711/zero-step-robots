Round 0 is a conservative baseline. The aim is to stay upright for the full 1000 steps and creep forward. Later rounds can raise the hop amplitude once I see how it fails.

**Design**
- **Oscillator:** one 2 Hz oscillator, `hop`.
- **Torso balance at the thigh:** `a0 = -2.0·(obs[1] - 0.05) - 0.3·obs[7]`. The 0.05 rad target lean, written as bias +0.1, is what drives forward speed. A weak thigh-angle term keeps the hip from drifting.
- **Leg posture hold:** proportional-derivative (PD) control holds the leg joint near straight with a slight bend, and holds the foot near neutral. The leg term is `-1.5·(obs[3] + 0.1)`, written as bias -0.15.
- **Rhythm:**
  - `cos(hop)` drives leg compression and extension (a1) and foot push-off (a2).
  - `sin(hop)` drives the thigh swing (a0), so the thigh runs a quarter cycle ahead of the leg.
  - Amplitudes are moderate (0.3–0.4), so the posture loops dominate at first.

```json
{"target": "cpg", "obs_dim": 11, "act_dim": 3, "hidden": 16,
 "oscillators": [{"name": "hop", "freq_hz": 2.0, "phase0": 0.0}],
 "couplings": [],
 "bias": {"a0": 0.1, "a1": -0.15},
 "units": [
   {"type": "linear", "name": "torso_pd", "inputs": {"obs[1]": -2.0, "obs[7]": -0.3},
    "range": 2.0, "tol": 0.05, "to": {"a0": 1.0}},
   {"type": "linear", "name": "thigh_posture", "inputs": {"obs[2]": -0.5, "obs[8]": -0.05},
    "range": 1.5, "tol": 0.05, "to": {"a0": 1.0}},
   {"type": "linear", "name": "leg_pd", "inputs": {"obs[3]": -1.5, "obs[9]": -0.1},
    "range": 2.0, "tol": 0.05, "to": {"a1": 1.0}},
   {"type": "linear", "name": "foot_pd", "inputs": {"obs[4]": -1.5, "obs[10]": -0.1},
    "range": 2.0, "tol": 0.05, "to": {"a2": 1.0}},
   {"type": "linear", "name": "rhythm_cos", "inputs": {"cos(hop)": 1.0},
    "range": 1.0, "tol": 0.02, "to": {"a1": 0.4, "a2": 0.3}},
   {"type": "linear", "name": "rhythm_sin", "inputs": {"sin(hop)": 1.0},
    "range": 1.0, "tol": 0.02, "to": {"a0": 0.3}}
 ]}
```