This is a gated, SIMBICON-style walker on a single phase oscillator. It uses 13 of the 16 hidden units. I couldn't run it, so it is untested.

**Sign conventions.** All joints rotate about the −y axis. Working that through gives:
- A positive thigh angle swings the leg forward.
- A negative knee angle bends the knee the human way.
- A positive foot angle lifts the toes.
- A positive torso angle leans the torso backward.

The thigh joint is limited to −150°…0°, so the hip cannot flex forward of the torso line. To get room for forward foot placement, the torso is held leaned back at about 0.4 rad. The legs are mostly below that torso mass, so the centre of mass moves only about 1 cm.

**Controller design:**
- **Phase.** One oscillator runs at 0.76 Hz plus 1 rad/s per m/s of forward speed, so the robot steps faster when it moves faster. The right leg swings around φ ≈ −0.7 and the left leg half a cycle later.
- **Swing hip (gated, 2 units per leg).** Each hip runs a PD on the thigh's angle in the world frame. The target is 0.1 + 0.15·v − 0.4·(stance-leg world angle), which places the foot further forward when moving fast or falling forward.
  - The gate is built from tanh(x+g) + tanh(x−g), with g = M(1 ∓ cos(φ+0.7)). This passes the PD only during that leg's swing window, with no extra compensating units.
- **Stance hip (gated, 2 units per leg).** A torso-pitch PD toward 0.4 rad, gated to the opposite window. One weak, always-on torso PD on both hips covers double support.
- **Knees (1 unit each).** A PD toward 0.1 − 0.8·cos(φ+0.9). In stance the target is above zero, so the knee stays locked against its limit. In early swing it flexes to about −0.7 rad for ground clearance.
- **Ankles (1 unit each).** A PD that keeps the foot flat in the world frame, with a small toes-up offset that fades with speed. This gives a gentle forward push from standing and resists going faster than about 1 m/s.

```json
{"target": "cpg", "obs_dim": 17, "act_dim": 6, "hidden": 16,
 "oscillators": [{"name": "gait", "freq_hz": 0.76, "phase0": -2.0, "feedback": {"obs[8]": 1.0}}],
 "units": [
  {"type": "reflex", "name": "R_swing_A", "inputs": {"obs[1]": -4.2, "obs[2]": -3.0, "obs[5]": -1.2, "obs[8]": 0.45, "obs[10]": -0.3, "obs[11]": -0.3, "cos(gait)": -1.0707, "sin(gait)": 0.9019}, "threshold": -1.7, "sharpness": 1.0, "to": {"a0": 0.35}},
  {"type": "reflex", "name": "R_swing_B", "inputs": {"obs[1]": -4.2, "obs[2]": -3.0, "obs[5]": -1.2, "obs[8]": 0.45, "obs[10]": -0.3, "obs[11]": -0.3, "cos(gait)": 1.0707, "sin(gait)": -0.9019}, "threshold": 1.1, "sharpness": 1.0, "to": {"a0": 0.35}},
  {"type": "reflex", "name": "L_swing_A", "inputs": {"obs[1]": -4.2, "obs[5]": -3.0, "obs[2]": -1.2, "obs[8]": 0.45, "obs[10]": -0.3, "obs[14]": -0.3, "cos(gait)": 1.0707, "sin(gait)": -0.9019}, "threshold": -1.7, "sharpness": 1.0, "to": {"a3": 0.35}},
  {"type": "reflex", "name": "L_swing_B", "inputs": {"obs[1]": -4.2, "obs[5]": -3.0, "obs[2]": -1.2, "obs[8]": 0.45, "obs[10]": -0.3, "obs[14]": -0.3, "cos(gait)": -1.0707, "sin(gait)": 0.9019}, "threshold": 1.1, "sharpness": 1.0, "to": {"a3": 0.35}},
  {"type": "reflex", "name": "R_stance_torso_A", "inputs": {"obs[1]": 3.0, "obs[10]": 0.12, "cos(gait)": 0.7648, "sin(gait)": -0.6442}, "threshold": 0.2, "sharpness": 1.0, "to": {"a0": 0.5}},
  {"type": "reflex", "name": "R_stance_torso_B", "inputs": {"obs[1]": 3.0, "obs[10]": 0.12, "cos(gait)": -0.7648, "sin(gait)": 0.6442}, "threshold": 2.2, "sharpness": 1.0, "to": {"a0": 0.5}},
  {"type": "reflex", "name": "L_stance_torso_A", "inputs": {"obs[1]": 3.0, "obs[10]": 0.12, "cos(gait)": -0.7648, "sin(gait)": 0.6442}, "threshold": 0.2, "sharpness": 1.0, "to": {"a3": 0.5}},
  {"type": "reflex", "name": "L_stance_torso_B", "inputs": {"obs[1]": 3.0, "obs[10]": 0.12, "cos(gait)": 0.7648, "sin(gait)": -0.6442}, "threshold": 2.2, "sharpness": 1.0, "to": {"a3": 0.5}},
  {"type": "reflex", "name": "torso_always", "inputs": {"obs[1]": 3.0, "obs[10]": 0.12}, "threshold": 1.2, "sharpness": 1.0, "to": {"a0": 0.25, "a3": 0.25}},
  {"type": "reflex", "name": "R_knee", "inputs": {"obs[3]": -4.0, "obs[12]": -0.24, "cos(gait)": -1.989, "sin(gait)": 2.507}, "threshold": -0.4, "sharpness": 1.0, "to": {"a1": 1.0}},
  {"type": "reflex", "name": "L_knee", "inputs": {"obs[6]": -4.0, "obs[15]": -0.24, "cos(gait)": 1.989, "sin(gait)": -2.507}, "threshold": -0.4, "sharpness": 1.0, "to": {"a4": 1.0}},
  {"type": "reflex", "name": "R_ankle", "inputs": {"obs[1]": -1.5, "obs[2]": -1.5, "obs[3]": -1.5, "obs[4]": -1.5, "obs[10]": -0.03, "obs[11]": -0.03, "obs[12]": -0.03, "obs[13]": -0.03, "obs[8]": -0.15}, "threshold": -0.15, "sharpness": 1.0, "to": {"a2": 0.8}},
  {"type": "reflex", "name": "L_ankle", "inputs": {"obs[1]": -1.5, "obs[5]": -1.5, "obs[6]": -1.5, "obs[7]": -1.5, "obs[10]": -0.03, "obs[14]": -0.03, "obs[15]": -0.03, "obs[16]": -0.03, "obs[8]": -0.15}, "threshold": -0.15, "sharpness": 1.0, "to": {"a5": 0.8}}
 ]}
```