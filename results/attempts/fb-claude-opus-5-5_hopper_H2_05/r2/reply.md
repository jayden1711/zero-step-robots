The key finding is a joint-limit asymmetry. The thigh joint is limited to [−2.62, 0], and in both rounds it sat at its upper limit: max thigh angle was 0.016 in round 0 and 0.017 in round 1. At that limit a positive thigh torque presses into the stop and does nothing.

**Why both rounds fell backward:**
- **Forward lean was corrected.** When the torso leaned forward, the balance term gave a negative thigh torque, which moves the thigh away from the limit, so it worked. The torso never exceeded +0.04.
- **Backward lean was not.** That needed a positive torque, which was absorbed by the limit. The bias, the swing rhythm and knee flexion all pushed the torso back, and nothing could stop it. Both rounds ended at a torso angle of about −0.19.
- **Round 1 failed faster.** Its hard knee flexion (−0.7, knee bent to −0.45) pitched the torso back within 0.08 s.
- **The knee had the same problem.** It sat at its 0 limit, so the positive half of the leg rhythm was wasted (leg max 0.003).

**Changes in round 2:**
- **Thigh off its stop:** a firmer posture spring now holds the thigh near −0.3 instead of 0, so the hip can push both ways. The balance gains are also raised (P 7, D 0.8).
- **Torso lean:** a small net forward-lean bias is kept, with the speed feedback.
- **Knee off its stop:** the leg posture target is −0.2 instead of 0, so both halves of the thrust rhythm act.
- **Softer thrust:** sharpness 2, amplitude 0.5 on the leg and 0.25 on the foot, at 2.2 Hz.
- **Thigh swing:** reduced to 0.25 so it doesn't overwhelm balance.

```json
{"target": "cpg", "obs_dim": 11, "act_dim": 3, "hidden": 16,
 "oscillators": [{"name": "hop", "freq_hz": 2.2, "phase0": 0.0}],
 "couplings": [],
 "bias": {"a0": -0.25, "a1": -0.3},
 "units": [
   {"type": "linear", "name": "torso_balance", "inputs": {"obs[1]": -7.0, "obs[7]": -0.8, "obs[5]": -0.1},
    "range": 4.0, "tol": 0.05, "to": {"a0": 1.0}},
   {"type": "linear", "name": "thigh_posture", "inputs": {"obs[2]": -1.5, "obs[8]": -0.1},
    "range": 3.0, "tol": 0.05, "to": {"a0": 1.0}},
   {"type": "linear", "name": "leg_posture", "inputs": {"obs[3]": -1.5, "obs[9]": -0.1},
    "range": 4.0, "tol": 0.05, "to": {"a1": 1.0}},
   {"type": "linear", "name": "foot_posture", "inputs": {"obs[4]": -2.0, "obs[10]": -0.1},
    "range": 3.0, "tol": 0.05, "to": {"a2": 1.0}},
   {"type": "reflex", "name": "push_thrust", "inputs": {"sin(hop)": 1.0}, "threshold": 0.0,
    "sharpness": 2.0, "to": {"a1": 0.5, "a2": 0.25}},
   {"type": "linear", "name": "swing_rhythm", "inputs": {"cos(hop)": 1.0},
    "range": 1.0, "tol": 0.01, "to": {"a0": 0.25}}
 ]}
```