The controller below has not been run or simulated, so expect it to need tuning. Its structure follows SIMBICON-style walking: torso control at the stance hip, a world-frame target at the swing hip, a straight stance knee and an ankle spring.

**How it works**

- **Rhythm:** There are two oscillators, R and L, coupled with a lag of π.
  - The base frequency is 0.9 Hz. Forward speed obs[8] feeds back at 1.5 rad/s per m/s, so faster walking means faster stepping.
  - Phase convention for each leg: p in (0, π) is stance, with sin p > 0. p in (π, 2π) is swing.
  - R starts at mid-stance and L at mid-swing, which matches the upright starting pose.
- **Phase gating without multiplication:** A pair of reflex units, tanh(e + M(1−g)) + tanh(e − M(1−g)), gives about 2·tanh(e) when the gate g = 1. When g ≤ 0, the two terms almost cancel. This is how each hip gets feedback only in the right phase:
  - **Stance hip (gate g = sin p):** torso feedback. Hip torque ≈ tanh(−2.5·θ − 0.25·ω − 0.625·v + 0.2). The target lean is θ_des = 0.08 − 0.25·v: the torso leans back as speed rises.
    - Because the hip can only swing the thigh backward (range [−2.62, 0]), leaning back is what lets the swing foot land ahead of the body. So the lean is the speed and foot-placement regulator, as the hint suggests.
  - **Swing hip (gate g = −sin p):** a PD controller toward a world-frame thigh target, with joint target = world target + torso angle (obs[1]).
    - The world target is φ* = −0.28 + 0.3·cos(p + 0.5) + 0.1·v.
    - The gains are Kp = 2 and Kd = 0.4.
- **Knee:** a PD controller (Kp 2, Kd 0.2) toward −0.45 − cos(p − p₀), with flexion peaking just before mid-swing.
  - During stance the target is above 0, so the knee is pushed into its 0 limit and stays locked straight.
  - The −0.45 offset is applied through the action bias.
- **Foot:** an ankle spring toward 0, with torque −1.2·q − 0.03·q̇ − 0.5·(v − 0.8).
  - The spring resists the shin rolling forward, which shifts the centre of pressure toward the toes and gives push-off.
  - Below 0.8 m/s it tips the body forward; above that it brakes.

```json
{"target": "cpg", "obs_dim": 17, "act_dim": 6, "hidden": 16,
 "oscillators": [
   {"name": "R", "freq_hz": 0.9, "phase0": 1.5708, "feedback": {"obs[8]": 1.5}},
   {"name": "L", "freq_hz": 0.9, "phase0": 4.7124, "feedback": {"obs[8]": 1.5}}
 ],
 "couplings": [
   {"from": "R", "to": "L", "weight": 1.0, "phase_lag": 3.1416},
   {"from": "L", "to": "R", "weight": 1.0, "phase_lag": 3.1416}
 ],
 "bias": {"a1": -0.9, "a2": 0.4, "a4": -0.9, "a5": 0.4},
 "units": [
   {"type": "reflex", "name": "hip_swing_R_plus",
    "inputs": {"obs[1]": 2.0, "obs[2]": -2.0, "obs[11]": -0.4, "obs[8]": 0.2, "cos(R)": 0.5266, "sin(R)": 0.7124},
    "threshold": -0.44, "sharpness": 1.0, "to": {"a0": 0.5}},
   {"type": "reflex", "name": "hip_swing_R_minus",
    "inputs": {"obs[1]": 2.0, "obs[2]": -2.0, "obs[11]": -0.4, "obs[8]": 0.2, "cos(R)": 0.5266, "sin(R)": -1.2876},
    "threshold": 1.56, "sharpness": 1.0, "to": {"a0": 0.5}},
   {"type": "reflex", "name": "torso_stance_R_plus",
    "inputs": {"obs[1]": -2.5, "obs[10]": -0.25, "obs[8]": -0.625, "sin(R)": -1.0},
    "threshold": -1.2, "sharpness": 1.0, "to": {"a0": 0.5}},
   {"type": "reflex", "name": "torso_stance_R_minus",
    "inputs": {"obs[1]": -2.5, "obs[10]": -0.25, "obs[8]": -0.625, "sin(R)": 1.0},
    "threshold": 0.8, "sharpness": 1.0, "to": {"a0": 0.5}},
   {"type": "linear", "name": "knee_R",
    "inputs": {"cos(R)": 0.591, "sin(R)": 1.9106, "obs[3]": -2.0, "obs[12]": -0.2},
    "range": 4.0, "tol": 0.05, "to": {"a1": 1.0}},
   {"type": "linear", "name": "foot_R",
    "inputs": {"obs[4]": -1.2, "obs[13]": -0.03, "obs[8]": -0.5},
    "range": 2.5, "tol": 0.05, "to": {"a2": 1.0}},
   {"type": "reflex", "name": "hip_swing_L_plus",
    "inputs": {"obs[1]": 2.0, "obs[5]": -2.0, "obs[14]": -0.4, "obs[8]": 0.2, "cos(L)": 0.5266, "sin(L)": 0.7124},
    "threshold": -0.44, "sharpness": 1.0, "to": {"a3": 0.5}},
   {"type": "reflex", "name": "hip_swing_L_minus",
    "inputs": {"obs[1]": 2.0, "obs[5]": -2.0, "obs[14]": -0.4, "obs[8]": 0.2, "cos(L)": 0.5266, "sin(L)": -1.2876},
    "threshold": 1.56, "sharpness": 1.0, "to": {"a3": 0.5}},
   {"type": "reflex", "name": "torso_stance_L_plus",
    "inputs": {"obs[1]": -2.5, "obs[10]": -0.25, "obs[8]": -0.625, "sin(L)": -1.0},
    "threshold": -1.2, "sharpness": 1.0, "to": {"a3": 0.5}},
   {"type": "reflex", "name": "torso_stance_L_minus",
    "inputs": {"obs[1]": -2.5, "obs[10]": -0.25, "obs[8]": -0.625, "sin(L)": 1.0},
    "threshold": 0.8, "sharpness": 1.0, "to": {"a3": 0.5}},
   {"type": "linear", "name": "knee_L",
    "inputs": {"cos(L)": 0.591, "sin(L)": 1.9106, "obs[6]": -2.0, "obs[15]": -0.2},
    "range": 4.0, "tol": 0.05, "to": {"a4": 1.0}},
   {"type": "linear", "name": "foot_L",
    "inputs": {"obs[7]": -1.2, "obs[16]": -0.03, "obs[8]": -0.5},
    "range": 2.5, "tol": 0.05, "to": {"a5": 1.0}}
 ]}
```