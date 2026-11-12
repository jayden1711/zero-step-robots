Round 3 was stable. Holding the hip off its stop gave it control in both directions, and all 10 episodes survived the full 8 s. But the robot is still rocking in place: the foot was on the ground 99% of the time and it averaged 0.02 m/s. Round 2 is the only design that got real flight (foot off the ground 26% of the time), from its 0.75 knee push. It failed only because the hip was stuck at its stop.

**Changes for round 4.** Keep round 3's hip structure and bring back a strong hop, with more forward lean so the hops travel.

- **Stronger knee push.** `leg_push` goes up to 0.7 and the knee PD drops to −1.5, close to round 2, which produced flight.
- **Stronger hip balance, so it can absorb the backward pitch from deeper compression.** The torso angle gain goes from −4 to −5 and the angular velocity gain from −0.5 to −0.6. Round 3 used only 0.09 mean |a0|, so there is plenty of headroom.
- **More margin from the stop and more forward lean.** The thigh target moves from −0.15 to −0.2 rad and the torso lean reference rises to +0.05 rad. Hip bias = 5·0.05 + 1.5·(−0.2) = −0.05.
- **Hip and ankle rhythm.** Thigh swing rises to 0.2, still swinging the leg forward after push-off. The ankle push rises to −0.25 to match the knee. Ankle balance is unchanged.

```json
{"target": "cpg", "obs_dim": 11, "act_dim": 3, "hidden": 16,
 "oscillators": [{"name": "hop", "freq_hz": 2.0, "phase0": 0.0}],
 "bias": {"a0": -0.05, "a1": 0.0, "a2": 0.075},
 "units": [
   {"type": "linear", "name": "torso_balance_hip", "inputs": {"obs[1]": -5.0, "obs[7]": -0.6},
    "range": 6.0, "tol": 0.05, "to": {"a0": 1.0}},
   {"type": "linear", "name": "thigh_pd", "inputs": {"obs[2]": -1.5, "obs[8]": -0.1},
    "range": 3.0, "tol": 0.05, "to": {"a0": 1.0}},
   {"type": "linear", "name": "thigh_swing", "inputs": {"sin(hop)": 0.2},
    "range": 0.25, "tol": 0.02, "to": {"a0": 1.0}},
   {"type": "linear", "name": "torso_balance_ankle", "inputs": {"obs[1]": -1.5, "obs[7]": -0.2},
    "range": 2.0, "tol": 0.05, "to": {"a2": 1.0}},
   {"type": "linear", "name": "leg_pd", "inputs": {"obs[3]": -1.5, "obs[9]": -0.1},
    "range": 3.0, "tol": 0.05, "to": {"a1": 1.0}},
   {"type": "linear", "name": "leg_push", "inputs": {"cos(hop)": 0.7},
    "range": 0.75, "tol": 0.02, "to": {"a1": 1.0}},
   {"type": "linear", "name": "foot_pd", "inputs": {"obs[4]": -1.0, "obs[10]": -0.05},
    "range": 2.0, "tol": 0.05, "to": {"a2": 1.0}},
   {"type": "linear", "name": "foot_push", "inputs": {"cos(hop)": -0.25},
    "range": 0.3, "tol": 0.02, "to": {"a2": 1.0}}
 ]}
```