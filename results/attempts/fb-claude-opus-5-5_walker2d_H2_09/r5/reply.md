# Round 5 design (final)

## What rounds 0–4 show

All five designs fell the same way. The torso tipped back, the thigh angles stayed pinned near their 0 limit, and the robot drifted backward. The cause is the hip joint limit.

- **The hip can only extend.** The thigh range is [−2.62, 0], so a leg can never go in front of the torso line.
- **Positive hip torque was wasted.** Each of my torso controllers corrected a backward lean with positive hip torque. With the thigh at its limit, that torque does nothing: torso and legs lock into one rigid body, which keeps falling backward.
- **Swing reactions pushed the torso back.** Knee flexion and the swing-leg reactions pushed the thigh into its limit, so each one tipped the torso further back.

## The new gait: the leg in line with the torso is carried forward

The swing leg is held at its limit, in line with the torso. The stance hip then extends with negative torque. That one action does two useful things:

- It rotates the torso and the locked swing leg backward together, so the swing foot moves ahead of the body.
- It rotates the stance leg backward over its foot, which pushes the hip forward. This is the propulsion.

After landing, the back leg is brought forward again with positive torque. The front hip is at its limit, so it absorbs the reaction on the torso, which also pushes the body forward over the new stance foot.

## How the controller does this

- **Hips.** Each hip has a PD unit on its own joint angle, plus a phase reflex that switches its target.
  - Outside the window the target is +0.15. This holds the leg at its limit, or brings a back leg forward.
  - During that leg's late-stance window (cos φ > 0.5, a third of the cycle) the target is −0.5, which extends the hip.
  - The left hip uses the same window shifted by π.
  - Both hips also get mild torso feedback (−0.8θ − 0.1θ̇) and speed feedback (−0.1v). These only act on a hip that is not at its limit, so they limit how far the torso pitches back during extension.
- **Knees.**
  - In stance the knee is held straight.
  - In swing it is driven toward −0.6, from the start of swing until mid-swing. It then straightens to land.
  - The knee gain is softer than before (1.5) so the flexion kicks the torso less.
- **Feet.**
  - In stance the foot is a soft PD with a small forward-shin bias. The toes can resist a forward fall, but the heel cannot stop a backward one.
  - In swing the toe is raised for ground clearance.
- **Timing.** One oscillator at 0.9 Hz, starting at φ = 1.3. The right leg is already in swing, so the left hip's first extension begins about 0.14 s in.

The design uses 10 of the 16 units.

```json
{"target": "cpg", "obs_dim": 17, "act_dim": 6, "hidden": 16,
 "oscillators": [
   {"name": "P", "freq_hz": 0.9, "phase0": 1.3}
 ],
 "bias": {"a0": -0.175, "a3": -0.175, "a1": -0.425, "a4": -0.425, "a2": 0.13, "a5": 0.13},
 "units": [
   {"type": "linear", "name": "hip_R", "inputs": {"obs[2]": -1.0, "obs[11]": -0.15, "obs[1]": -0.8, "obs[10]": -0.1, "obs[8]": -0.1},
    "range": 2.5, "tol": 0.05, "to": {"a0": 1.0}},
   {"type": "linear", "name": "hip_L", "inputs": {"obs[5]": -1.0, "obs[14]": -0.15, "obs[1]": -0.8, "obs[10]": -0.1, "obs[8]": -0.1},
    "range": 2.5, "tol": 0.05, "to": {"a3": 1.0}},
   {"type": "reflex", "name": "ext_R", "inputs": {"cos(P)": 1.0},
    "threshold": 0.5, "sharpness": 8.0, "to": {"a0": -0.325}},
   {"type": "reflex", "name": "ext_L", "inputs": {"cos(P)": -1.0},
    "threshold": 0.5, "sharpness": 8.0, "to": {"a3": -0.325}},
   {"type": "linear", "name": "knee_R", "inputs": {"obs[3]": -1.5, "obs[12]": -0.12},
    "range": 3.0, "tol": 0.05, "to": {"a1": 1.0}},
   {"type": "linear", "name": "knee_L", "inputs": {"obs[6]": -1.5, "obs[15]": -0.12},
    "range": 3.0, "tol": 0.05, "to": {"a4": 1.0}},
   {"type": "reflex", "name": "flex_R", "inputs": {"cos(P)": -0.5, "sin(P)": 0.866},
    "threshold": 0.5, "sharpness": 8.0, "to": {"a1": -0.475, "a2": 0.08}},
   {"type": "reflex", "name": "flex_L", "inputs": {"cos(P)": 0.5, "sin(P)": -0.866},
    "threshold": 0.5, "sharpness": 8.0, "to": {"a4": -0.475, "a5": 0.08}},
   {"type": "linear", "name": "foot_R", "inputs": {"obs[4]": -0.5, "obs[13]": -0.03},
    "range": 1.5, "tol": 0.05, "to": {"a2": 1.0}},
   {"type": "linear", "name": "foot_L", "inputs": {"obs[7]": -0.5, "obs[16]": -0.03},
    "range": 1.5, "tol": 0.05, "to": {"a5": 1.0}}
 ]}
```