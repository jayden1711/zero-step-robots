Round 0 shows that the balance loop has the wrong sign. In every episode the torso pitched steadily toward negative angles and eventually fell. As it did, the feedback term −obs[1] grew positive, so the thigh torques kept getting pushed further positive. The thigh rhythm unit was at the action limit about 33% of the time.

That points to a positive-feedback loop. With a foot on the ground, a thigh torque τ applies −τ to the torso about the shared axis. So a positive thigh torque drives obs[1] down, and the stabilising feedback has to have the **same** sign as obs[1].

This fits my reading of the XML from round 0, where every joint axis is (0, −1, 0). Under that reading, a **negative** torso angle means leaning forward, which matches the forward falls with "height too low".

**Changes in round 1:**

- **Balance at both thighs:** the feedback is now +1.0·obs[1] + 0.15·obs[10] − 0.05·obs[8] (it was −obs[1] − 0.1·obs[10] − 0.1·obs[8]).
  - A thigh bias of +0.1 makes the torso settle at about −0.1 rad, a slight forward lean under this convention.
  - At higher speed, the obs[8] term shifts the target toward upright.
- **Knee:** the torque is now 0.5·cos φ − 0.25·sin φ.
  - The knee is extended through stance (φ ≈ 0) and flexed through swing, with peak flexion at φ ≈ 2.7.
  - Before, the knee flexed during mid-stance, which collapsed the supporting leg. I removed the knee bias.
- **Frequency:** lowered slightly to 0.9 Hz.
- **Unchanged:** the thigh rhythm (−0.6·cos φ: back in stance, forward in swing), the foot holds and the antiphase coupling.

```json
{"target": "cpg", "obs_dim": 17, "act_dim": 6, "hidden": 16,
 "oscillators": [
   {"name": "R", "freq_hz": 0.9, "phase0": 0.0},
   {"name": "L", "freq_hz": 0.9, "phase0": 3.14159}
 ],
 "couplings": [
   {"from": "R", "to": "L", "weight": 2.0, "phase_lag": 3.14159},
   {"from": "L", "to": "R", "weight": 2.0, "phase_lag": 3.14159}
 ],
 "bias": {"a0": 0.1, "a3": 0.1},
 "units": [
   {"type": "linear", "name": "R_thigh_rhythm", "inputs": {"cos(R)": 1.0},
    "range": 1.0, "tol": 0.02, "to": {"a0": -0.6}},
   {"type": "linear", "name": "R_knee_rhythm", "inputs": {"cos(R)": 0.5, "sin(R)": -0.25},
    "range": 0.6, "tol": 0.02, "to": {"a1": 1.0}},
   {"type": "linear", "name": "L_thigh_rhythm", "inputs": {"cos(L)": 1.0},
    "range": 1.0, "tol": 0.02, "to": {"a3": -0.6}},
   {"type": "linear", "name": "L_knee_rhythm", "inputs": {"cos(L)": 0.5, "sin(L)": -0.25},
    "range": 0.6, "tol": 0.02, "to": {"a4": 1.0}},
   {"type": "linear", "name": "torso_balance_speed", "inputs": {"obs[1]": 1.0, "obs[10]": 0.15, "obs[8]": -0.05},
    "range": 2.5, "tol": 0.05, "to": {"a0": 1.0, "a3": 1.0}},
   {"type": "linear", "name": "R_foot_hold", "inputs": {"obs[4]": 1.0},
    "range": 1.0, "tol": 0.05, "to": {"a2": -1.0}},
   {"type": "linear", "name": "L_foot_hold", "inputs": {"obs[7]": 1.0},
    "range": 1.0, "tol": 0.05, "to": {"a5": -1.0}}
 ]}
```