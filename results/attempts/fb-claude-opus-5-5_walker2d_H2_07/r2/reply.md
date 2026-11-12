Round 1 showed that my sign flip was wrong. Your stated convention holds.

**What the data shows**
- **The torso sign follows your convention.** In round 1 the robot fell in 0.06 s, before either foot touched the ground.
  - The flipped feedback pushed the thighs to −1 (right thigh saturated 62% of steps), and obs[1] fell from −0.005 to below −1.
  - So a negative thigh torque drives obs[1] negative, and a negative obs[1] means a backward lean.
  - That is a positive-feedback loop, so round 0's sign (−obs[1]) was the stabilising one. My reading of the XML was wrong.
- **Round 0 fell backward because of its knee phasing, not the balance sign.** Its knee flexed during φ ∈ (0, π), while the thigh was still swinging back in stance.
  - That lifted the backward-swinging foot and loaded the forward-swinging one, so the robot walked backward (−0.67 m/s).
  - The torso then pitched back to about −0.47 rad and fell.

**Round 2 changes**
- **Balance:** back to round 0's sign, with stronger gains: −1.5·obs[1] − 0.3·obs[10] − 0.15·obs[8].
  - A thigh bias of +0.15 sets a slight forward lean of about +0.1 rad.
  - The obs[8] term tilts the torso back when the robot goes fast.
- **Knee:** keeps round 1's phasing, 0.5·cos φ − 0.25·sin φ.
  - It is extended in stance and flexed in swing, with peak flexion at φ ≈ 2.7.
  - I added a +0.1 bias so the stance knee holds the body weight.
- **Thigh rhythm:** reduced to −0.5·cos φ, which leaves more torque headroom for balance.
- **Frequency:** back to 1.0 Hz.
- **Unchanged:** the feet and the antiphase coupling.

```json
{"target": "cpg", "obs_dim": 17, "act_dim": 6, "hidden": 16,
 "oscillators": [
   {"name": "R", "freq_hz": 1.0, "phase0": 0.0},
   {"name": "L", "freq_hz": 1.0, "phase0": 3.14159}
 ],
 "couplings": [
   {"from": "R", "to": "L", "weight": 2.0, "phase_lag": 3.14159},
   {"from": "L", "to": "R", "weight": 2.0, "phase_lag": 3.14159}
 ],
 "bias": {"a0": 0.15, "a3": 0.15, "a1": 0.1, "a4": 0.1},
 "units": [
   {"type": "linear", "name": "R_thigh_rhythm", "inputs": {"cos(R)": 1.0},
    "range": 1.0, "tol": 0.02, "to": {"a0": -0.5}},
   {"type": "linear", "name": "R_knee_rhythm", "inputs": {"cos(R)": 0.5, "sin(R)": -0.25},
    "range": 0.6, "tol": 0.02, "to": {"a1": 1.0}},
   {"type": "linear", "name": "L_thigh_rhythm", "inputs": {"cos(L)": 1.0},
    "range": 1.0, "tol": 0.02, "to": {"a3": -0.5}},
   {"type": "linear", "name": "L_knee_rhythm", "inputs": {"cos(L)": 0.5, "sin(L)": -0.25},
    "range": 0.6, "tol": 0.02, "to": {"a4": 1.0}},
   {"type": "linear", "name": "torso_balance_speed", "inputs": {"obs[1]": 1.5, "obs[10]": 0.3, "obs[8]": 0.15},
    "range": 3.0, "tol": 0.05, "to": {"a0": -1.0, "a3": -1.0}},
   {"type": "linear", "name": "R_foot_hold", "inputs": {"obs[4]": 1.0},
    "range": 1.0, "tol": 0.05, "to": {"a2": -1.0}},
   {"type": "linear", "name": "L_foot_hold", "inputs": {"obs[7]": 1.0},
    "range": 1.0, "tol": 0.05, "to": {"a5": -1.0}}
 ]}
```