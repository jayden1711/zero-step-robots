This is a phase-clocked compass-gait controller, designed by reasoning about the dynamics. I couldn't simulate it, so I can't say how well it will score.

**Assumed sign conventions.** All hinge axes in this model are (0,−1,0). From that I derived:
- Thigh and knee angles below 0 move the foot backward.
- A positive torso angle means leaning back.
- A positive foot angle means toe up.

The gait only works if these are right. Because the hips can only extend, the legs can only alternate around vertical if the torso leans back a little.

**How each joint is controlled:**
- **Hips, difference between legs:** one oscillator at 0.9 Hz sets a target for q_R − q_L of 0.6·sin φ. Opposite torques on the two hips track it. These torques cancel on the torso, so they only move the legs.
- **Hips, common part:** the same PD term goes to both hips. It holds the torso at 0.35 rad back, using the stance leg against the ground. A weak term keeps the mean hip angle near −0.35.
- **Knees:** stance knees are pushed straight against the joint limit. While a leg swings forward (a phase-advanced cosine window), a reflex bends its knee to about −0.6 rad and lifts the toe.
- **Ankles:** a soft PD holds the foot flat. A phase-gated reflex pushes off at the end of each stance. Its window shrinks as forward speed rises, which limits speed.
- **Start:** the initial phase lifts the right leg while the left one pushes off. Leaning the torso back makes the feet push against the ground, which gives the first forward impulse.

```json
{"target": "cpg", "obs_dim": 17, "act_dim": 6, "hidden": 16,
 "oscillators": [{"name": "clk", "freq_hz": 0.9, "phase0": 0.0}],
 "couplings": [],
 "bias": {"a0": -0.42, "a3": -0.42, "a1": -0.4, "a4": -0.4, "a2": -0.15, "a5": -0.15},
 "units": [
   {"type": "linear", "name": "hip_scissor", "inputs": {"obs[2]": -2.0, "obs[5]": 2.0, "obs[11]": -0.15, "obs[14]": 0.15, "sin(clk)": 1.2},
    "range": 2.0, "tol": 0.05, "to": {"a0": 1.0, "a3": -1.0}},
   {"type": "linear", "name": "torso_balance", "inputs": {"obs[1]": 1.0, "obs[10]": 0.1, "obs[2]": -0.1, "obs[5]": -0.1},
    "range": 2.0, "tol": 0.05, "to": {"a0": 1.0, "a3": 1.0}},
   {"type": "linear", "name": "knee_pd_R", "inputs": {"obs[3]": -2.0, "obs[12]": -0.15},
    "range": 2.0, "tol": 0.05, "to": {"a1": 1.0}},
   {"type": "linear", "name": "knee_pd_L", "inputs": {"obs[6]": -2.0, "obs[15]": -0.15},
    "range": 2.0, "tol": 0.05, "to": {"a4": 1.0}},
   {"type": "linear", "name": "ankle_pd_R", "inputs": {"obs[4]": -0.4, "obs[13]": -0.03},
    "range": 1.0, "tol": 0.05, "to": {"a2": 1.0}},
   {"type": "linear", "name": "ankle_pd_L", "inputs": {"obs[7]": -0.4, "obs[16]": -0.03},
    "range": 1.0, "tol": 0.05, "to": {"a5": 1.0}},
   {"type": "reflex", "name": "swing_flex_R", "inputs": {"cos(clk)": 0.878, "sin(clk)": -0.479},
    "threshold": 0.2, "sharpness": 5.0, "to": {"a1": -0.6, "a2": 0.15}},
   {"type": "reflex", "name": "swing_flex_L", "inputs": {"cos(clk)": -0.878, "sin(clk)": 0.479},
    "threshold": 0.2, "sharpness": 5.0, "to": {"a4": -0.6, "a5": 0.15}},
   {"type": "reflex", "name": "pushoff_R", "inputs": {"cos(clk)": -0.707, "sin(clk)": -0.707, "obs[8]": -0.15},
    "threshold": 0.7, "sharpness": 6.0, "to": {"a2": -0.3}},
   {"type": "reflex", "name": "pushoff_L", "inputs": {"cos(clk)": 0.707, "sin(clk)": 0.707, "obs[8]": -0.15},
    "threshold": 0.7, "sharpness": 6.0, "to": {"a5": -0.3}}
 ]}
```