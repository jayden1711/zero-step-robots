# Round 4: ankle push forward, no backward speed loop at the hips, higher knee lift

## Why the robot keeps drifting backward

**1. The feet point forward from the ankle.** Each foot runs from the ankle about 0.2 m toward +x. Standing upright puts the centre of mass over the heel edge of the support, so the robot tips backward unless the ankles push it forward. Round 3's ankle offset (+0.1 rad) helped: it survived 4.7 s instead of about 1.5 s. It was not enough to overcome the backward tipping.

**2. Hip torque with the feet planted moves the hips backward.** A positive thigh torque pitches the torso forward, but it also rotates the planted legs about the feet and moves the hips toward −x. Round 3 fed speed into the thighs (−0.6·velocity). When the robot drifted backward, this commanded more positive thigh torque, which pushed the hips further back. That is positive feedback on the drift.

**3. The swing foot dragged.** Each foot was on the ground 87–88% of the time, and the knees only flexed to about −0.45 to −0.78 rad.

## Changes for round 4

- **Speed control moves from the hips to the ankles.**
  - Foot torque = 0.32 − 2·(foot angle) − 0.1·(foot angular velocity) − 0.3·(forward speed).
  - With a foot planted, a positive foot torque tilts the shank forward and pushes the body forward. At standstill this pushes harder, and it eases off once the robot moves forward at about 0.4 m/s.
  - In swing, the same positive torque lifts the toes, which helps the foot clear the ground.
- **Thighs:** the forward-speed term is removed. Everything else is the same as round 3:
  - target −0.25 − 0.25·cos φ, with gains Kp 1 and Kd 0.1;
  - torso feedback −4·(torso angle − 0.05) − 0.5·(torso angular velocity).
- **Knees:** torque = 0.2 − 0.8·sin(φ + 0.67).
  - The knee flexes harder, with a peak of −0.6, from late stance through early swing (centred near φ ≈ 0.9).
  - It straightens before touchdown and is held straight through stance (peak +1.0).
- **Oscillator frequency goes from 1.0 to 1.2 Hz.** Quicker steps catch the body more often.

```json
{"target": "cpg", "obs_dim": 17, "act_dim": 6, "hidden": 16,
 "oscillators": [
   {"name": "R", "freq_hz": 1.2, "phase0": 1.5708},
   {"name": "L", "freq_hz": 1.2, "phase0": 4.71239}
 ],
 "couplings": [
   {"from": "R", "to": "L", "weight": 2.0, "phase_lag": 3.14159},
   {"from": "L", "to": "R", "weight": 2.0, "phase_lag": 3.14159}
 ],
 "bias": {"a0": -0.05, "a3": -0.05, "a1": 0.2, "a4": 0.2, "a2": 0.32, "a5": 0.32},
 "units": [
   {"type": "linear", "name": "R_thigh",
    "inputs": {"cos(R)": -0.25, "obs[2]": -1.0, "obs[11]": -0.1, "obs[1]": -4.0, "obs[10]": -0.5},
    "range": 3.0, "tol": 0.05, "to": {"a0": 1.0}},
   {"type": "linear", "name": "L_thigh",
    "inputs": {"cos(L)": -0.25, "obs[5]": -1.0, "obs[14]": -0.1, "obs[1]": -4.0, "obs[10]": -0.5},
    "range": 3.0, "tol": 0.05, "to": {"a3": 1.0}},
   {"type": "linear", "name": "R_knee",
    "inputs": {"sin(R)": -0.63, "cos(R)": -0.5, "obs[12]": -0.05},
    "range": 1.5, "tol": 0.05, "to": {"a1": 1.0}},
   {"type": "linear", "name": "L_knee",
    "inputs": {"sin(L)": -0.63, "cos(L)": -0.5, "obs[15]": -0.05},
    "range": 1.5, "tol": 0.05, "to": {"a4": 1.0}},
   {"type": "linear", "name": "R_foot",
    "inputs": {"obs[4]": -2.0, "obs[13]": -0.1, "obs[8]": -0.3},
    "range": 2.5, "tol": 0.05, "to": {"a2": 1.0}},
   {"type": "linear", "name": "L_foot",
    "inputs": {"obs[7]": -2.0, "obs[16]": -0.1, "obs[8]": -0.3},
    "range": 2.5, "tol": 0.05, "to": {"a5": 1.0}}
 ]}
```