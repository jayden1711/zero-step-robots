Rounds 1 and 2 both drifted backward while standing on both feet, so I'm changing the balance strategy for round 3. The thigh joint can't flex past 0, so the positive thigh torque from the balance term is blocked at the limit and can't pitch the torso forward.

Instead, the feet now do the balancing. With the foot flat on the ground, a positive ankle torque tips the body forward, so I feed the torso angle and angular velocity to both ankles with a negative gain. A small positive foot bias makes the robot lean slightly forward. I reduced the thigh balance gain from 3 to 2 and removed the old ankle-hold units. This is untested.

```json
{"target": "cpg", "obs_dim": 17, "act_dim": 6, "hidden": 16,
 "oscillators": [
  {"name": "R", "freq_hz": 1.0, "phase0": 0.0},
  {"name": "L", "freq_hz": 1.0, "phase0": 3.14159}
 ],
 "couplings": [
  {"from": "R", "to": "L", "weight": 3.0, "phase_lag": 3.14159},
  {"from": "L", "to": "R", "weight": 3.0, "phase_lag": 3.14159}
 ],
 "bias": {"a0": 0.25, "a3": 0.25, "a1": 0.2, "a4": 0.2, "a2": 0.15, "a5": 0.15},
 "units": [
  {"type": "linear", "name": "right_leg_rhythm", "inputs": {"sin(R)": 1.0},
   "range": 1.0, "tol": 0.02, "to": {"a0": -0.25, "a1": 0.5}},
  {"type": "linear", "name": "left_leg_rhythm", "inputs": {"sin(L)": 1.0},
   "range": 1.0, "tol": 0.02, "to": {"a3": -0.25, "a4": 0.5}},
  {"type": "linear", "name": "torso_balance", "inputs": {"obs[1]": 1.0, "obs[10]": 0.2},
   "range": 2.0, "tol": 0.05, "to": {"a0": -2.0, "a3": -2.0}},
  {"type": "linear", "name": "ankle_balance", "inputs": {"obs[1]": 1.0, "obs[10]": 0.3},
   "range": 2.0, "tol": 0.05, "to": {"a2": -3.0, "a5": -3.0}}
 ]}
```