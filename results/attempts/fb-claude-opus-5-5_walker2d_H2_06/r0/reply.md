This first design uses PD tracking of a rhythmic gait, with torso balance and a small speed correction added on top. Two oscillators are locked half a cycle apart. One choice matters most, and the round-0 results should test it.

**Sign assumption.** Walker2d's root pitch joint (`rooty`) turns about the same axis as every leg joint, `0 -1 0`. With that axis, a positive thigh torque applies the opposite torque to the torso, so it drives obs[1] *down*. The brief states that a positive obs[1] means a forward lean. The joint axes imply the opposite: positive obs[1] tilts the top of the torso towards −x. I followed the axis algebra:
- Upright feedback is `+K·obs[1]` and `+K·obs[10]` at the hips.
- The world angle of each leg is `obs[1] + thigh angle`.

This differs from the hint's "opposes the sign of obs[1]". If the torso goes over within the first few dozen steps, flipping this sign is the first thing I'll change.

**Gait (0.8 Hz):**
- **Thighs:** each thigh tracks a target angle measured relative to the world: −0.05 + 0.22·cos φ. The foot lands at about +0.17 rad (ahead of the hip) and pushes back to −0.27 rad.
- **Torso lean:** the thigh joint cannot go above 0 (in front of the torso line). The torso is therefore held at obs[1] ≈ 0.2, which by the axis convention above is a slight backward lean. This lets the feet land ahead of the hip without pressing into that limit.
- **Knees:** each knee tracks −0.3 + 0.5·sin(φ + 0.63). It is straight from foot strike through mid-stance, bends up to 0.8 rad early in the swing, and straightens again before the next strike.
- **Speed correction:** the hip targets shift with (obs[8] − 0.6) to rein in speed. A positive shift brakes through the stance leg.
- **Ankles:** a soft PD controller holds each ankle near 0.
- **Startup phases:** the right leg starts at mid-stance and the left at mid-swing.

```json
{"target": "cpg", "obs_dim": 17, "act_dim": 6, "hidden": 16,
 "oscillators": [
   {"name": "R", "freq_hz": 0.8, "phase0": 1.5708},
   {"name": "L", "freq_hz": 0.8, "phase0": 4.7124}
 ],
 "couplings": [
   {"from": "R", "to": "L", "weight": 2.0, "phase_lag": 3.14159},
   {"from": "L", "to": "R", "weight": 2.0, "phase_lag": 3.14159}
 ],
 "bias": {"a0": -0.365, "a1": -0.6, "a3": -0.365, "a4": -0.6},
 "units": [
   {"type": "linear", "name": "hip_R",
    "inputs": {"cos(R)": 0.33, "obs[1]": -0.5, "obs[2]": -1.5, "obs[10]": -0.03, "obs[11]": -0.15, "obs[8]": 0.15},
    "range": 2.0, "tol": 0.03, "to": {"a0": 1.0}},
   {"type": "linear", "name": "knee_R",
    "inputs": {"sin(R)": 0.8, "cos(R)": 0.58, "obs[3]": -2.0, "obs[12]": -0.12},
    "range": 3.0, "tol": 0.03, "to": {"a1": 1.0}},
   {"type": "linear", "name": "ankle_R",
    "inputs": {"obs[4]": -0.4, "obs[13]": -0.02},
    "range": 1.0, "tol": 0.03, "to": {"a2": 1.0}},
   {"type": "linear", "name": "hip_L",
    "inputs": {"cos(L)": 0.33, "obs[1]": -0.5, "obs[5]": -1.5, "obs[10]": -0.03, "obs[14]": -0.15, "obs[8]": 0.15},
    "range": 2.0, "tol": 0.03, "to": {"a3": 1.0}},
   {"type": "linear", "name": "knee_L",
    "inputs": {"sin(L)": 0.8, "cos(L)": 0.58, "obs[6]": -2.0, "obs[15]": -0.12},
    "range": 3.0, "tol": 0.03, "to": {"a4": 1.0}},
   {"type": "linear", "name": "ankle_L",
    "inputs": {"obs[7]": -0.4, "obs[16]": -0.02},
    "range": 1.0, "tol": 0.03, "to": {"a5": 1.0}}
 ]}
```

Each hip unit combines three terms:
- leg-angle PD tracking: Kp = 1.5 and Kd = 0.15 (in action units, 1 = 100 N·m)
- torso feedback: Kb = 1.0 on (obs[1] − 0.2) and Kbd = 0.12 on obs[10]
- the speed term on obs[8]

The constant parts of the targets are moved into `bias`, because linear units have no constant input. Ten of the 16 hidden units are still free for later rounds, for example phase-gated stance/swing reflexes or oscillator phase feedback.