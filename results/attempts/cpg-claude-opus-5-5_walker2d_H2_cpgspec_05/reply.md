I can't simulate this, so the numbers come from physical reasoning, not tuning.

**Hip structure.** Two linear terms are added together at each hip:

1. **Torso term.** The same world-frame torso PD goes on both hips (−1.5·(θ+0.25) − 0.08·θ̇). The two hips therefore apply a known net torque to the light torso and hold it at θ ≈ −0.25 rad, a slight backward lean. The hip limit q ≤ 0 means the leading foot can only get ahead of the hip if the torso leans back, which is why the lean is needed.
2. **Scissor term.** An equal and opposite PD on the inter-leg angle Δ = q_L − q_R tracks the rhythmic target Δ* ≈ 0.4·cos ψ, with a small phase lead. Because the two scissor torques cancel at the torso, the leg swing doesn't knock the torso over.

**Soft start.** Two identical oscillators (P and Q) start almost anti-phase and are pulled together by their coupling. Every rhythmic term uses cos P + cos Q or sin P + sin Q. The step amplitude therefore ramps from about 12% to full over roughly 1.5 s instead of lurching at t = 0. Cadence rises slightly with forward speed through obs[8] feedback on both oscillators.

**Knees.** A PD holds each knee straight against its joint limit. A phase-gated reflex flexes the swing knee to about −1 rad in mid-swing. The same reflex also tips the swing foot's toe up for clearance.

**Ankles.** Each foot tracks a mostly world-flat target, which acts as an ankle spring of about 300 Nm/rad on the shin angle. That is slightly stiffer than gravity's tipping effect. A small bias keeps the body leaning a little ahead of the ankle, and a speed term brakes (toe-down) when going fast.

```json
{"target": "cpg", "obs_dim": 17, "act_dim": 6, "hidden": 16,
 "oscillators": [
   {"name": "P", "freq_hz": 0.9, "phase0": 3.0208, "feedback": {"obs[8]": 1.0}},
   {"name": "Q", "freq_hz": 0.9, "phase0": 0.1208, "feedback": {"obs[8]": 1.0}}
 ],
 "couplings": [
   {"from": "P", "to": "Q", "weight": 1.0, "phase_lag": 0.0},
   {"from": "Q", "to": "P", "weight": 1.0, "phase_lag": 0.0}
 ],
 "bias": {"a0": -0.375, "a1": -1.35, "a2": 1.05, "a3": -0.375, "a4": -1.35, "a5": 1.05},
 "units": [
   {"type": "linear", "name": "hip_left_scissor_torso",
    "inputs": {"obs[5]": -2.5, "obs[2]": 2.5, "obs[14]": -0.25, "obs[11]": 0.25,
               "cos(P)": 0.5, "cos(Q)": 0.5, "sin(P)": -0.175, "sin(Q)": -0.175,
               "obs[1]": -1.5, "obs[10]": -0.08},
    "range": 3.0, "tol": 0.03, "to": {"a3": 1.0}},
   {"type": "linear", "name": "hip_right_scissor_torso",
    "inputs": {"obs[5]": 2.5, "obs[2]": -2.5, "obs[14]": 0.25, "obs[11]": -0.25,
               "cos(P)": -0.5, "cos(Q)": -0.5, "sin(P)": 0.175, "sin(Q)": 0.175,
               "obs[1]": -1.5, "obs[10]": -0.08},
    "range": 3.0, "tol": 0.03, "to": {"a0": 1.0}},
   {"type": "linear", "name": "knee_right_pd",
    "inputs": {"obs[3]": -3.0, "obs[12]": -0.2},
    "range": 4.0, "tol": 0.03, "to": {"a1": 1.0}},
   {"type": "linear", "name": "knee_left_pd",
    "inputs": {"obs[6]": -3.0, "obs[15]": -0.2},
    "range": 4.0, "tol": 0.03, "to": {"a4": 1.0}},
   {"type": "linear", "name": "foot_right_flat_spring",
    "inputs": {"obs[1]": 1.0, "obs[2]": -1.0, "obs[3]": -1.0, "obs[4]": -4.0,
               "obs[13]": -0.05, "obs[8]": -0.1},
    "range": 4.0, "tol": 0.03, "to": {"a2": 1.0}},
   {"type": "linear", "name": "foot_left_flat_spring",
    "inputs": {"obs[1]": 1.0, "obs[5]": -1.0, "obs[6]": -1.0, "obs[7]": -4.0,
               "obs[16]": -0.05, "obs[8]": -0.1},
    "range": 4.0, "tol": 0.03, "to": {"a5": 1.0}},
   {"type": "reflex", "name": "swing_right_knee_flex_toe_up",
    "inputs": {"sin(P)": 0.5, "sin(Q)": 0.5},
    "threshold": 0.3, "sharpness": 4.0, "to": {"a1": -1.65, "a2": 1.0}},
   {"type": "reflex", "name": "swing_left_knee_flex_toe_up",
    "inputs": {"sin(P)": -0.5, "sin(Q)": -0.5},
    "threshold": 0.3, "sharpness": 4.0, "to": {"a4": -1.65, "a5": 1.0}}
 ]}
```

**Main risks**, since this is untested:

- **Tracking lag.** The gait is timed by the oscillators, not by foot contact, so the body may not keep pace with the steps. If it lags, the likely failure is a backward stall over the leading heel.
- **Torso sign.** The torso feedback signs follow the stated convention that positive obs[1] means a forward lean. If that convention is wrong, the torso control is inverted and the robot will fall within the first second.