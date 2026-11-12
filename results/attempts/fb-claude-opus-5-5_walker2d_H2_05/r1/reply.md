The torso pitched backward within 0.2 s, settled around −0.35 to −0.45 rad, and the robot walked backward until it fell. This matches a net negative thigh torque, which pitches the torso back. At t = 0 the right thigh was saturated at −1, and the constant −0.5 bias was too strong for the weak torso feedback (gain 2). The thigh units also saturated 16% of the time at range 3.

**Changes for round 1**
- **Torso balance is stiffer:** angle gain goes from 2 to 5 and angular-velocity gain from 0.3 to 0.6. The forward-lean setpoint goes from 0.05 to 0.1 rad.
- **Thigh position PD is weaker:** Kp goes from 2 to 1, centred at −0.3. The net constant thigh bias is now +0.2 instead of −0.5.
- **Thigh rhythm is slightly smaller:** 0.5 instead of 0.6, so it saturates less.
- **Thigh unit range goes from 3 to 5.**
- Knees, feet and oscillators are unchanged.

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
 "bias": {"a0": 0.2, "a3": 0.2, "a1": 0.3, "a4": 0.3},
 "units": [
   {"type": "linear", "name": "R_thigh",
    "inputs": {"cos(R)": -0.5, "obs[2]": -1.0, "obs[11]": -0.1, "obs[1]": -5.0, "obs[10]": -0.6},
    "range": 5.0, "tol": 0.05, "to": {"a0": 1.0}},
   {"type": "linear", "name": "L_thigh",
    "inputs": {"cos(L)": -0.5, "obs[5]": -1.0, "obs[14]": -0.1, "obs[1]": -5.0, "obs[10]": -0.6},
    "range": 5.0, "tol": 0.05, "to": {"a3": 1.0}},
   {"type": "linear", "name": "R_knee",
    "inputs": {"sin(R)": -0.6, "cos(R)": -0.6, "obs[12]": -0.1},
    "range": 2.0, "tol": 0.05, "to": {"a1": 1.0}},
   {"type": "linear", "name": "L_knee",
    "inputs": {"sin(L)": -0.6, "cos(L)": -0.6, "obs[15]": -0.1},
    "range": 2.0, "tol": 0.05, "to": {"a4": 1.0}},
   {"type": "linear", "name": "R_foot",
    "inputs": {"obs[4]": -1.0, "obs[13]": -0.1},
    "range": 2.0, "tol": 0.05, "to": {"a2": 1.0}},
   {"type": "linear", "name": "L_foot",
    "inputs": {"obs[7]": -1.0, "obs[16]": -0.1},
    "range": 2.0, "tol": 0.05, "to": {"a5": 1.0}}
 ]}
```