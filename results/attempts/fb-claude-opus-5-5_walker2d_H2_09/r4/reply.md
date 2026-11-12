# Round 4 design

## What the round 0–3 data show

Two facts explain all four failures.

**1. Hip torque mostly rotates the torso, not the leg.**
- The torso is light: about 3.5 kg, with roughly 0.2 kg·m² of inertia about the hip.
- Each leg is heavy: about 9.5 kg, with roughly 3 kg·m² of inertia about the hip.
- So a torque at either hip mostly spins the torso. This is why the thighs barely moved in rounds 2 and 3, even with large actions.
- In round 3, the swing-leg torques were only half compensated at the stance hip. Their reaction tipped the torso back to about −0.3 rad.

**2. Leaning back makes the robot walk backward.**
- The thigh cannot pass in front of the torso line.
- When the torso leans back, both legs point forward in the world frame.
- With the feet ahead of the centre of mass, every design was pushed backward at about −0.7 m/s until it fell.

## Changes in round 4: split the hips into a common mode and a differential mode

**Common mode (τR + τL) holds the torso.**
- One shared PD unit sends the same command to both hips.
- The lean target is θ* = 0.05 − 0.25·v.
  - At low speed the torso leans slightly forward, so the feet land slightly behind the hip and the robot falls forward into the gait.
  - At higher speed it leans back, so the feet land ahead and brake (Raibert-style speed regulation).
- The command is −1.5·θ − 0.1·θ̇ − 0.375·v + 0.075.

**Differential mode (τR − τL) scissors the legs.**
- It is a PD on qR − qL toward a target of 0.5·sin φ, sent as +1 to a0 and −1 to a3.
- The reaction torques on the torso cancel exactly, so moving the legs no longer disturbs the torso.
- No stance/swing gating is needed.

**One oscillator at 0.85 Hz** sets the rhythm for both legs. The left leg uses the antiphase of the same oscillator, so no coupling is needed.

**Knees** keep the round-3 PD and flexion reflex. The left-leg reflex uses the opposite sign of the same oscillator. **Feet** are unchanged. The design uses 8 units.

```json
{"target": "cpg", "obs_dim": 17, "act_dim": 6, "hidden": 16,
 "oscillators": [
   {"name": "P", "freq_hz": 0.85, "phase0": 0.0}
 ],
 "bias": {"a0": 0.075, "a3": 0.075, "a1": -0.85, "a4": -0.85},
 "units": [
   {"type": "linear", "name": "torso_pd", "inputs": {"obs[1]": -1.5, "obs[10]": -0.1, "obs[8]": -0.375},
    "range": 2.5, "tol": 0.05, "to": {"a0": 1.0, "a3": 1.0}},
   {"type": "linear", "name": "scissor", "inputs": {"obs[2]": -1.0, "obs[5]": 1.0, "obs[11]": -0.15, "obs[14]": 0.15, "sin(P)": 0.5},
    "range": 2.0, "tol": 0.05, "to": {"a0": 1.0, "a3": -1.0}},
   {"type": "linear", "name": "knee_R", "inputs": {"obs[3]": -3.0, "obs[12]": -0.15},
    "range": 3.0, "tol": 0.05, "to": {"a1": 1.0}},
   {"type": "linear", "name": "knee_L", "inputs": {"obs[6]": -3.0, "obs[15]": -0.15},
    "range": 3.0, "tol": 0.05, "to": {"a4": 1.0}},
   {"type": "reflex", "name": "knee_flex_R", "inputs": {"cos(P)": 0.921, "sin(P)": -0.389},
    "threshold": 0.3, "sharpness": 6.0, "to": {"a1": -0.9}},
   {"type": "reflex", "name": "knee_flex_L", "inputs": {"cos(P)": -0.921, "sin(P)": 0.389},
    "threshold": 0.3, "sharpness": 6.0, "to": {"a4": -0.9}},
   {"type": "linear", "name": "foot_R", "inputs": {"obs[4]": -0.5, "obs[13]": -0.03},
    "range": 1.5, "tol": 0.05, "to": {"a2": 1.0}},
   {"type": "linear", "name": "foot_L", "inputs": {"obs[7]": -0.5, "obs[16]": -0.03},
    "range": 1.5, "tol": 0.05, "to": {"a5": 1.0}}
 ]}
```