I couldn't run anything, so this is a reasoned design, not a tested one. There's a real chance it misses the 3 m bar. The riskiest choice is the sign of the torso feedback, explained below.

## Correction to the brief: torso feedback sign

In `hopper.xml`, the torso pitch joint and the thigh, leg and foot joints all use the same axis, (0, −1, 0). That has two consequences:

- **The thigh torque reacts on the torso with the opposite sign.** With the foot planted, a thigh torque +τ pushes the torso pitch by −τ. So a negative thigh torque *raises* `obs[1]`. The brief agrees: it says a negative thigh torque pitches the torso backward.
- **So a positive `obs[1]` is a backward lean, not a forward one.** That matches the right-hand rule about −y.
- **Upright feedback must have the same sign as `obs[1]` and `obs[7]`.** The control law is a0 = +2.0·obs[1] + 0.2·obs[7]. Using the opposite sign, as the brief suggests, would push the torso further over.

If my reading of the model is wrong, this controller fails, because this one sign holds everything up.

## Gait concept

The thigh and knee can only bend backward. With an upright torso, the foot therefore stays behind the hip, and bending the knee barely changes the leg's length. The big ankle-to-toe lever (0.32 m) is the effective way to push off. Each joint gets one job:

- **Hip (a0):** keeps the torso upright with PD control on `obs[1]` and `obs[7]`. In flight the torso is light compared with the heavy leg, so the hip can only correct the torso, not swing the leg forward.
- **Knee (a1):** holds the knee slightly bent (target −0.1 rad) with PD control. A small extension pulse comes from the oscillator.
- **Ankle (a2):** does three things:
  - **Balance:** PD control on the shin's world angle (sum of `obs[1..3]`), aiming for a forward lean of 0.2 rad.
  - **Speed:** when the robot is slower than 0.6 m/s it leans further forward; when faster, it presses the toe down to brake.
  - **Landing:** in flight it keeps the foot level (sum of `obs[1..4]`). This term is near zero while the foot is flat on the ground. If the body leans too far forward, the foot lands toe-first, which brakes it.
- **Rhythm:** one 1.8 Hz oscillator gives a push-off window during about 35% of each cycle. In that window the toe presses down (−0.4) and the knee extends (+0.2). Pressing at the toe, which sits ahead of the centre of mass, lifts the body and adds backward pitch momentum. In flight the hip feedback turns that momentum into the leg swinging forward under the body. The starting phase delays the first push until after the initial drop to the ground.

The biases make each pulse contribute zero outside its window. They also set the knee target, the lean target, the speed target and a small allowance for gravity at the ankle.

```json
{"target": "cpg", "obs_dim": 11, "act_dim": 3, "hidden": 16,
 "oscillators": [{"name": "hop", "freq_hz": 1.8, "phase0": -2.0}],
 "couplings": [],
 "bias": {"a0": 0.0, "a1": -0.05, "a2": 0.07},
 "units": [
   {"type": "linear", "name": "hip_torso_pd",
    "inputs": {"obs[1]": 2.0, "obs[7]": 0.2},
    "range": 1.5, "tol": 0.02, "to": {"a0": 1.0}},
   {"type": "linear", "name": "knee_pd",
    "inputs": {"obs[3]": -1.5, "obs[9]": -0.1},
    "range": 1.5, "tol": 0.02, "to": {"a1": 1.0}},
   {"type": "reflex", "name": "knee_push",
    "inputs": {"sin(hop)": 1.0}, "threshold": 0.45, "sharpness": 5.0,
    "to": {"a1": 0.1}},
   {"type": "linear", "name": "ankle_lean_speed",
    "inputs": {"obs[1]": 1.2, "obs[2]": 1.2, "obs[3]": 1.2,
               "obs[7]": 0.2, "obs[8]": 0.2, "obs[9]": 0.2,
               "obs[5]": -0.15},
    "range": 2.0, "tol": 0.02, "to": {"a2": 1.0}},
   {"type": "linear", "name": "foot_level",
    "inputs": {"obs[1]": -1.2, "obs[2]": -1.2, "obs[3]": -1.2, "obs[4]": -1.2,
               "obs[7]": -0.1, "obs[8]": -0.1, "obs[9]": -0.1, "obs[10]": -0.1},
    "range": 1.5, "tol": 0.02, "to": {"a2": 1.0}},
   {"type": "reflex", "name": "ankle_push",
    "inputs": {"sin(hop)": 1.0}, "threshold": 0.45, "sharpness": 5.0,
    "to": {"a2": -0.2}}
 ]}
```