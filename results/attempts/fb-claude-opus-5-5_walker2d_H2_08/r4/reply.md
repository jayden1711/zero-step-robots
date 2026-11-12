# Round 4: back to the round-2 signs, with a torso target the hip limits allow

## What round 3 showed

Round 3 confirmed that its sign flip was wrong. The robot never touched the ground (0 touchdowns in 0.06 s), so only internal hip torques acted. The bias and the flipped feedback drove the hip torque sum negative. In 0.06 s the thighs went to about −1.0 rad and the torso to −0.97 rad. With no ground contact, angular momentum is conserved, so the heavy legs stayed nearly fixed in space while the light torso rotated. That means:

- The leg's angle from vertical is q_thigh − θ, with foot-forward positive. This is the original spec convention.
- A negative hip torque pitches the torso backward.
- So the rounds 0–2 feedback sign (−k·θ) was the stabilising one. My Newton argument in round 3 was wrong.

## The real constraint

The thigh range is [−2.62, 0], and a negative thigh angle swings the leg backward. So a foot can only be ahead of the hip if the torso leans back: foot-forward angle = q − θ ≤ −θ.

In round 2, the torso target was a forward lean of about +0.1. That target is unreachable with the legs near vertical. As a result:

- The sum unit saturated at +1 (66% of steps).
- Both thighs were pinned at their 0 limit.
- The whole robot tipped back as one rigid stick.

The fix is a slight backward-lean target: θ_d = −0.1 − 0.2·v. This keeps the hip joints off their limit, and the extra lean at speed puts the swing foot further forward, which brakes.

## Changes from round 2

- **Torso unit (sum to both hips):** the command is −θ − 0.06·θ̇ − 0.2·v − 0.1 (the −0.1 is in the a0 and a3 biases). The signs are those of round 2, the target is new, and the gains are moderate.
- **Scissor unit:** round 2's signs (round 3 had flipped them). The per-leg foot-forward target is 0.2·cos φ. Feedforward is −0.2·sin φ per leg (the stance leg pushes back and the swing leg pulls forward). Damping is raised to 0.25.
- **Foot units:** round 2's level-foot signs. A positive foot torque (toe up) with the foot planted tips the body forward. So I add an ankle speed loop, 0.2·(0.6 − v), through a +0.12 bias and a −0.2·obs[8] gain. It counters the backward drift seen in every round so far. Push-off amplitude is 0.2.
- **Unchanged:** knees, oscillators (1 Hz, antiphase coupling), and start phases π/2 and 3π/2.

```json
{"target": "cpg", "obs_dim": 17, "act_dim": 6, "hidden": 16,
 "oscillators": [
   {"name": "R", "freq_hz": 1.0, "phase0": 1.5708},
   {"name": "L", "freq_hz": 1.0, "phase0": 4.7124}
 ],
 "couplings": [
   {"from": "R", "to": "L", "weight": 4.0, "phase_lag": 3.14159},
   {"from": "L", "to": "R", "weight": 4.0, "phase_lag": 3.14159}
 ],
 "bias": {"a0": -0.1, "a1": -0.375, "a2": 0.12, "a3": -0.1, "a4": -0.375, "a5": 0.12},
 "units": [
   {"type": "linear", "name": "torso_balance",
    "inputs": {"obs[1]": -1.0, "obs[10]": -0.06, "obs[8]": -0.2},
    "range": 2.0, "tol": 0.05, "to": {"a0": 1.0, "a3": 1.0}},
   {"type": "linear", "name": "hip_scissor",
    "inputs": {"obs[2]": -2.0, "obs[5]": 2.0, "obs[11]": -0.25, "obs[14]": 0.25, "cos(R)": 0.4, "cos(L)": -0.4, "sin(R)": -0.4, "sin(L)": 0.4},
    "range": 4.0, "tol": 0.05, "to": {"a0": 0.5, "a3": -0.5}},
   {"type": "linear", "name": "R_knee",
    "inputs": {"obs[3]": -1.5, "obs[12]": -0.1, "sin(R)": 0.83, "cos(R)": 0.35},
    "range": 2.5, "tol": 0.05, "to": {"a1": 1.0}},
   {"type": "linear", "name": "L_knee",
    "inputs": {"obs[6]": -1.5, "obs[15]": -0.1, "sin(L)": 0.83, "cos(L)": 0.35},
    "range": 2.5, "tol": 0.05, "to": {"a4": 1.0}},
   {"type": "linear", "name": "R_foot",
    "inputs": {"obs[1]": 0.4, "obs[2]": -0.4, "obs[3]": -0.4, "obs[4]": -0.4, "obs[13]": -0.02, "obs[8]": -0.2, "sin(R)": -0.141, "cos(R)": 0.141},
    "range": 1.5, "tol": 0.05, "to": {"a2": 1.0}},
   {"type": "linear", "name": "L_foot",
    "inputs": {"obs[1]": 0.4, "obs[5]": -0.4, "obs[6]": -0.4, "obs[7]": -0.4, "obs[16]": -0.02, "obs[8]": -0.2, "sin(L)": -0.141, "cos(L)": 0.141},
    "range": 1.5, "tol": 0.05, "to": {"a5": 1.0}}
 ]}
```

## What I'll check next

- **Still tipping backward:** raise the ankle speed bias, or make the torso target less negative.
- **Falling forward, with speed rising:** raise the obs[8] gain in the torso unit.
- **Thighs pinned at 0 again:** lean the torso target further back.