Round 0 failed at the hip. The thigh stayed at 0 ± 0.005 rad, which is its upper joint limit, and its torque was mostly positive. A positive thigh torque at that limit only pushes against the stop, so the torso-balance loop could not move anything. Once the hop rhythm hit cos ≈ −1 (around 0.3 s), it bent the knee and pointed the foot down while sin(hop) pulled the hip negative. All three pitch the body backward. With no working correction the robot tipped back about the heel.

Changes for round 1:

- **Ankle balance (new).** A positive foot torque, with the foot planted, pitches the body forward. The ankle now gets feedback from torso angle (−1.5) and torso angular velocity (−0.2), with a small forward-lean reference. This catches backward lean, which the hip cannot correct while it sits at its limit. The hip loop stays in place to correct forward lean.
- **Coherent push-off.** The foot rhythm sign is flipped. The foot now points down while the knee extends, and turns up while the knee compresses. In the compression half it pitches the body forward, which counters the backward pitch, instead of adding to it.
- **Knee.** The PD toward straight is stiffer (−3), and the push amplitude is slightly larger (0.4).
- **Smaller destabilising terms.** The thigh swing is reduced from 0.25 to 0.15, and the foot PD is softened so the balance term isn't overridden.

```json
{"target": "cpg", "obs_dim": 11, "act_dim": 3, "hidden": 16,
 "oscillators": [{"name": "hop", "freq_hz": 2.0, "phase0": 0.0}],
 "bias": {"a0": 0.09, "a1": 0.0, "a2": 0.075},
 "units": [
   {"type": "linear", "name": "torso_balance_hip", "inputs": {"obs[1]": -3.0, "obs[7]": -0.4},
    "range": 4.0, "tol": 0.05, "to": {"a0": 1.0}},
   {"type": "linear", "name": "thigh_pd", "inputs": {"obs[2]": -0.5, "obs[8]": -0.05},
    "range": 2.0, "tol": 0.05, "to": {"a0": 1.0}},
   {"type": "linear", "name": "thigh_swing", "inputs": {"sin(hop)": 0.15},
    "range": 0.2, "tol": 0.02, "to": {"a0": 1.0}},
   {"type": "linear", "name": "torso_balance_ankle", "inputs": {"obs[1]": -1.5, "obs[7]": -0.2},
    "range": 2.0, "tol": 0.05, "to": {"a2": 1.0}},
   {"type": "linear", "name": "leg_pd", "inputs": {"obs[3]": -3.0, "obs[9]": -0.1},
    "range": 3.0, "tol": 0.05, "to": {"a1": 1.0}},
   {"type": "linear", "name": "leg_push", "inputs": {"cos(hop)": 0.4},
    "range": 0.45, "tol": 0.02, "to": {"a1": 1.0}},
   {"type": "linear", "name": "foot_pd", "inputs": {"obs[4]": -1.0, "obs[10]": -0.05},
    "range": 2.0, "tol": 0.05, "to": {"a2": 1.0}},
   {"type": "linear", "name": "foot_push", "inputs": {"cos(hop)": -0.15},
    "range": 0.2, "tol": 0.02, "to": {"a2": 1.0}}
 ]}
```