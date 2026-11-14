I can't run anything, so this controller is an untested best guess based on how Hopper-v5 behaves.

- **Posture:** the thigh torque is a PD law on torso pitch, with a bias that holds a slight forward lean. That lean is meant to turn balancing into forward travel.
- **Hopping:** a single 2.5 Hz oscillator drives the leg joint around a positive extension bias, which should produce rhythmic hops.
- **Foot:** the foot torque is a mild feedback on torso pitch. I'm unsure of its sign convention, so the gain is kept small.

```json
{"target": "cpg", "obs_dim": 11, "act_dim": 3, "hidden": 16,
 "oscillators": [{"name": "hop", "freq_hz": 2.5, "phase0": 0.0}],
 "couplings": [],
 "bias": {"a0": 0.2, "a1": 0.4},
 "units": [
   {"type": "linear", "name": "pitch_pd", "inputs": {"obs[1]": -5.0, "obs[7]": -0.5},
    "range": 3.0, "tol": 0.05, "to": {"a0": 1.0}},
   {"type": "linear", "name": "hop_leg", "inputs": {"sin(hop)": 1.0},
    "range": 1.0, "tol": 0.05, "to": {"a1": 0.5}},
   {"type": "linear", "name": "foot_pitch", "inputs": {"obs[1]": -1.0, "obs[7]": -0.1},
    "range": 3.0, "tol": 0.05, "to": {"a2": 1.0}}
 ]}
```