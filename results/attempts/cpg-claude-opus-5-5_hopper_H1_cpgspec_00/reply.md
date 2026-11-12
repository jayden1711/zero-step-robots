This is an untested design: I couldn't simulate it, and the gains come from hand estimates. The biggest risk is the sign convention. I worked it out from the hinge axis (0, −1, 0). If that is wrong, the robot will move backward.

**How I read the mechanics (positive angle = lean back / lower end of the segment forward):**
- Thigh and knee are both limited to [−150°, 0]. So the shin's absolute angle ψ = obs[1]+obs[2]+obs[3] can never exceed the torso angle.
- Bending the knee, or letting the leg tilt back, therefore pushes the torso backward toward the 0.2 rad limit. The design keeps the knee straight (pressed against its stop) and keeps the body leaning slightly forward.
- Every joint has armature 1, so the hip barely swings the heavy leg in flight; hip torque mainly turns the torso. The hip is used only for torso balance: a0 = obs[1] + 0.15·obs[7] + 0.03, which holds the torso near −0.03 rad. All the joint feedback terms are PD laws, which stabilise regardless of the sign convention.
- With the knee near straight, bending it barely changes leg length, so the knee can't drive a hop. The ankle is the hop engine: pressing the toe down lifts the heel, and the 0.26 m toe lever gives plenty of push.

**How the gait works:**
- **Ankle lean and speed control:** a PD on the foot joint sets a forward lean of about 0.12 rad when standing still. Forward speed (obs[5]) reduces that lean target, so the lean, and with it the forward push, shrinks as speed rises.
- **Ankle rhythm:** a 1.75 Hz oscillator adds ±0.6 ankle torque. The body is forced above its pendulum resonance, so it rocks about 0.17 rad, in the range ψ ≈ −0.29 to +0.04, which stays clear of the backward limit.
  - The toe push happens when the body is furthest forward. It launches a small forward hop and pitches the body back during flight.
  - The heel press happens when the body is furthest back, and pitches it forward again.
- **Failure mode:** if speed runs away, the robot falls forward. A forward fall still counts as displacement until the height drops below 0.7 m. A backward fall ends the episode almost at once, so everything is biased forward.

```json
{"target": "cpg", "obs_dim": 11, "act_dim": 3, "hidden": 16,
 "oscillators": [{"name": "osc", "freq_hz": 1.75, "phase0": 0.0}],
 "bias": {"a0": 0.03, "a1": 0.05, "a2": 0.08},
 "units": [
   {"type": "linear", "name": "torso_balance", "inputs": {"obs[1]": 1.0, "obs[7]": 0.15},
    "range": 2.0, "tol": 0.02, "to": {"a0": 1.0}},
   {"type": "linear", "name": "knee_hold", "inputs": {"obs[3]": -0.5, "obs[9]": -0.05},
    "range": 1.5, "tol": 0.02, "to": {"a1": 1.0}},
   {"type": "linear", "name": "ankle_lean_speed", "inputs": {"obs[4]": -1.0, "obs[10]": -0.1, "obs[5]": -0.05},
    "range": 2.0, "tol": 0.02, "to": {"a2": 1.0}},
   {"type": "linear", "name": "ankle_rhythm", "inputs": {"sin(osc)": 1.0},
    "range": 1.0, "tol": 0.01, "to": {"a2": 0.6}}
 ]}
```