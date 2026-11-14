Round 1 fixed balance: all 10 episodes survived the full 8 s with the torso within ±0.09 rad. But it barely moved (0.01 m/s). The foot stayed on the ground 99% of the time, and the knee bent only to −0.195. So the rhythm is rocking a planted robot rather than hopping it. This round keeps the balance loops and strengthens the gait.

- **Stronger knee push.** The `leg_push` amplitude goes up from 0.4 to 0.75. The knee PD drops from −3 to −1.5, so it stops cancelling the compression. The knee should bend deeply when cos(hop) < 0 and extend hard enough at cos(hop) > 0 to leave the ground.
- **Larger hip stroke.** `thigh_swing` goes up from 0.15 to 0.3. With +sin(hop), the thigh is driven backward during compression and push-off (sin < 0), which moves the body forward over the planted foot. It swings forward again in flight (sin > 0), ready to land.
- **More forward lean.** The hip lean reference rises from about 0.03 to 0.05 rad (hip bias 0.15), so the body tends to travel forward. The ankle reference is already 0.05.
- **Ankle push.** The foot rhythm rises slightly, from −0.15 to −0.2, in step with the stronger knee.

```json
{"target": "cpg", "obs_dim": 11, "act_dim": 3, "hidden": 16,
 "oscillators": [{"name": "hop", "freq_hz": 2.0, "phase0": 0.0}],
 "bias": {"a0": 0.15, "a1": 0.0, "a2": 0.075},
 "units": [
   {"type": "linear", "name": "torso_balance_hip", "inputs": {"obs[1]": -3.0, "obs[7]": -0.4},
    "range": 4.0, "tol": 0.05, "to": {"a0": 1.0}},
   {"type": "linear", "name": "thigh_pd", "inputs": {"obs[2]": -0.5, "obs[8]": -0.05},
    "range": 2.0, "tol": 0.05, "to": {"a0": 1.0}},
   {"type": "linear", "name": "thigh_swing", "inputs": {"sin(hop)": 0.3},
    "range": 0.35, "tol": 0.02, "to": {"a0": 1.0}},
   {"type": "linear", "name": "torso_balance_ankle", "inputs": {"obs[1]": -1.5, "obs[7]": -0.2},
    "range": 2.0, "tol": 0.05, "to": {"a2": 1.0}},
   {"type": "linear", "name": "leg_pd", "inputs": {"obs[3]": -1.5, "obs[9]": -0.1},
    "range": 3.0, "tol": 0.05, "to": {"a1": 1.0}},
   {"type": "linear", "name": "leg_push", "inputs": {"cos(hop)": 0.75},
    "range": 0.8, "tol": 0.02, "to": {"a1": 1.0}},
   {"type": "linear", "name": "foot_pd", "inputs": {"obs[4]": -1.0, "obs[10]": -0.05},
    "range": 2.0, "tol": 0.05, "to": {"a2": 1.0}},
   {"type": "linear", "name": "foot_push", "inputs": {"cos(hop)": -0.2},
    "range": 0.25, "tol": 0.02, "to": {"a2": 1.0}}
 ]}
```