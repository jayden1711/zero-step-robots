This controller is a guess I couldn't simulate, so treat its chance of passing as low. It rests on two assumptions about the Hopper model, and if the first is wrong it will likely fail within the first second:

1. All four hinges (`rooty`, thigh, leg, foot) turn about the axis (0, −1, 0). That means:
   - obs[1] > 0 is the torso leaning **back**.
   - A positive joint angle swings the lower segment forward.
   - A positive foot angle lifts the toes.
2. The hip (range −150°..0) can only swing the thigh backward relative to the torso. So the robot can only travel with its leg leaning forward.

**How it works**

- **Hip (a0): keeps the torso upright.** It drives the torso toward a slight backward lean of 0.03 rad. Gains are about 400 Nm/rad and 24 Nm·s/rad: `a0 = 2(r − 0.03) + 0.12·ṙ`.
- **Knee (a1): stays locked straight.** It presses the knee against its 0° limit with a constant torque, plus extra torque if the knee starts to bend.
- **Ankle (a2): steers the foot's angle in the world.** Call that angle φ3 (the sum of torso, thigh, leg and foot angles). The ankle tracks a target φ3_des = 0.8·(−lean) − 0.3·(v − v_des), with stiffness 200 Nm/rad and damping.
  - **In the air**, this places the foot. If the robot leans forward or moves too fast, it points the toes down so it lands on the toes, ahead of the body, which brakes it. If it is too slow, it lifts the toes so it lands on the heel, behind the ankle.
  - **On the ground**, the foot is flat (φ3 = 0), so the same rule becomes a balance controller. It holds a forward lean and regulates speed by shifting the pressure point between heel and toe. Its stiffness is about 160 Nm/rad, against about 77 Nm/rad of gravity.
- **Hop pump.** A 2 Hz oscillator fires a toe push lasting about 40% of each cycle, peaking at about 100 Nm. This lifts the heel and launches a small hop.
  - The push starts earlier when the robot leans further forward or is already rising. It is weaker when the body is upright, so a push doesn't flip the robot backward.
  - The oscillator starts at phase π, so the first push comes after the initial drop has settled.

```json
{"target": "cpg", "obs_dim": 11, "act_dim": 3, "hidden": 16,
 "oscillators": [{"name": "hop", "freq_hz": 2.0, "phase0": 3.14159}],
 "couplings": [],
 "bias": {"a0": -0.06, "a1": 0.4, "a2": -0.15},
 "units": [
   {"type": "linear", "name": "hip_torso_pd",
    "inputs": {"obs[1]": 2.0, "obs[7]": 0.12},
    "range": 1.5, "tol": 0.03, "to": {"a0": 1.0}},
   {"type": "linear", "name": "knee_lock",
    "inputs": {"obs[3]": -2.0, "obs[9]": -0.1},
    "range": 1.5, "tol": 0.05, "to": {"a1": 1.0}},
   {"type": "linear", "name": "ankle_foot_placement_balance",
    "inputs": {"obs[1]": -0.2, "obs[2]": -0.2, "obs[3]": -0.2, "obs[4]": -1.0,
               "obs[5]": -0.3,
               "obs[7]": -0.1, "obs[8]": -0.1, "obs[9]": -0.1, "obs[10]": -0.1},
    "range": 2.0, "tol": 0.05, "to": {"a2": 1.0}},
   {"type": "reflex", "name": "toe_push_pump",
    "inputs": {"sin(hop)": 1.0, "obs[1]": -1.0, "obs[2]": -1.0, "obs[3]": -1.0, "obs[6]": 0.3},
    "threshold": 0.35, "sharpness": 6.0, "to": {"a2": -0.25}}
 ]}
```