Round 2 failed for the same reason as round 0, and the gait push made it worse.

**What went wrong.** The thigh sat at its upper joint limit of 0 rad the whole time. Its torque was saturated on 32% of steps, mostly positive, and positive torque into the stop does nothing. So the hip could only ever pitch the torso backward, never forward. The larger thigh swing, with negative torque during compression, pitched the torso back. The stronger knee compression (down to −0.45 rad) did the same. The torso passed −0.2 rad at 0.3 s.

Round 1 survived largely because its thigh happened to leave the stop (down to −0.149 rad).

**Changes for round 3:**

- **Hip held off its limit.** The thigh PD now holds the thigh near −0.15 rad, with gain −1.5 and a damping term. That gives the hip torque room to act in both directions, so it can correct backward lean as well as forward lean. The hip bias of −0.135 combines this −0.15 rad thigh target with the previous ~+0.03 rad torso lean reference.
- **Stronger hip balance.** Torso gains go from −3 to −4 on the angle and from −0.4 to −0.5 on the angular velocity, now that the hip has authority.
- **Gait between rounds 1 and 2.** Knee push is 0.55 (round 1 was 0.4, round 2 was 0.75), with knee PD −2.0. Thigh swing goes back to the safe 0.15. Foot rhythm stays at −0.2. Ankle balance is unchanged.

```json
{"target": "cpg", "obs_dim": 11, "act_dim": 3, "hidden": 16,
 "oscillators": [{"name": "hop", "freq_hz": 2.0, "phase0": 0.0}],
 "bias": {"a0": -0.135, "a1": 0.0, "a2": 0.075},
 "units": [
   {"type": "linear", "name": "torso_balance_hip", "inputs": {"obs[1]": -4.0, "obs[7]": -0.5},
    "range": 5.0, "tol": 0.05, "to": {"a0": 1.0}},
   {"type": "linear", "name": "thigh_pd", "inputs": {"obs[2]": -1.5, "obs[8]": -0.1},
    "range": 3.0, "tol": 0.05, "to": {"a0": 1.0}},
   {"type": "linear", "name": "thigh_swing", "inputs": {"sin(hop)": 0.15},
    "range": 0.2, "tol": 0.02, "to": {"a0": 1.0}},
   {"type": "linear", "name": "torso_balance_ankle", "inputs": {"obs[1]": -1.5, "obs[7]": -0.2},
    "range": 2.0, "tol": 0.05, "to": {"a2": 1.0}},
   {"type": "linear", "name": "leg_pd", "inputs": {"obs[3]": -2.0, "obs[9]": -0.1},
    "range": 3.0, "tol": 0.05, "to": {"a1": 1.0}},
   {"type": "linear", "name": "leg_push", "inputs": {"cos(hop)": 0.55},
    "range": 0.6, "tol": 0.02, "to": {"a1": 1.0}},
   {"type": "linear", "name": "foot_pd", "inputs": {"obs[4]": -1.0, "obs[10]": -0.05},
    "range": 2.0, "tol": 0.05, "to": {"a2": 1.0}},
   {"type": "linear", "name": "foot_push", "inputs": {"cos(hop)": -0.2},
    "range": 0.25, "tol": 0.02, "to": {"a2": 1.0}}
 ]}
```