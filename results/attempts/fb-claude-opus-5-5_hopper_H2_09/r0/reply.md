This first design holds the hopper upright and adds a gentle hop rhythm. It does not try to be fast yet. The rhythm amplitudes are kept moderate, so the round-0 results should mostly show whether the sign conventions and the balance loop are right.

**Oscillator.** One oscillator, `hop`, runs at 2.5 Hz.

**Thigh (a0): torso balance.** The thigh torque is −4·(obs[1] + 0.15·obs[7]). This opposes both the torso tilt and its rate. A bias of +0.12 shifts the balance point to a slight forward lean of about 0.03 rad, which is meant to produce forward drift. There is also a weak hold that keeps the thigh angle near 0, and a small cos-phase swing (0.3) for the flight phase.

**Leg (a1) and foot (a2): posture hold plus rhythm.** Each joint has a stiff hold that keeps its angle near 0 and damps its speed. On top of that, sin(hop) adds an extension push of 0.5 at the leg and 0.3 at the foot. This means the push-off happens a quarter cycle after the thigh swing.

**What I'll adjust next round:**
- If the robot falls forward or backward quickly, I'll fix the lean bias and balance gains.
- If it stands but doesn't move, I'll increase the rhythm amplitudes and the lean.
- If it falls in an oscillating way, I'll lower the frequency or change the phase relationship between the joints.

```json
{"target": "cpg", "obs_dim": 11, "act_dim": 3, "hidden": 16,
 "oscillators": [{"name": "hop", "freq_hz": 2.5, "phase0": 0.0}],
 "bias": {"a0": 0.12},
 "units": [
   {"type": "linear", "name": "torso_pd", "inputs": {"obs[1]": 1.0, "obs[7]": 0.15},
    "range": 2.0, "tol": 0.02, "to": {"a0": -4.0}},
   {"type": "linear", "name": "thigh_hold", "inputs": {"obs[2]": 1.0, "obs[8]": 0.1},
    "range": 3.0, "tol": 0.02, "to": {"a0": -0.5}},
   {"type": "linear", "name": "thigh_swing", "inputs": {"cos(hop)": 1.0},
    "range": 1.2, "tol": 0.01, "to": {"a0": 0.3}},
   {"type": "linear", "name": "leg_hold", "inputs": {"obs[3]": 1.0, "obs[9]": 0.1},
    "range": 3.0, "tol": 0.02, "to": {"a1": -2.0}},
   {"type": "linear", "name": "foot_hold", "inputs": {"obs[4]": 1.0, "obs[10]": 0.1},
    "range": 2.0, "tol": 0.02, "to": {"a2": -2.0}},
   {"type": "linear", "name": "pushoff", "inputs": {"sin(hop)": 1.0},
    "range": 1.2, "tol": 0.01, "to": {"a1": 0.5, "a2": 0.3}}
 ]}
```