I couldn't simulate this controller, so it is untested. It is designed by hand from the Walker2d model, and the joint sign conventions below come from my reading of the model file. It is a single central pattern generator: one oscillator drives smooth joint targets, and saturating PD controllers (tanh units) track them, with posture and speed feedback added on top.

**How it works**

- **Rhythm and leg pattern.** One oscillator at 1 Hz drives the right leg with phase φ and the left leg with φ+π.
  - Right thigh target: −0.25 + 0.25·sin φ. This sweeps from −0.5 to 0, staying inside the hip's [−150°, 0] range.
  - Knee target: −0.4 − 0.4·cos(φ+π/4). The knee is nearly straight in stance, bends to about −0.8 in early swing for foot clearance, and starts bending in late stance for toe-off.
  - Ankle target: a +0.1 forward-lean bias, about 0.2 rad toe-up in swing and a little push-off in late stance.
- **Torso balance.** Both hips get a torso-pitch term, 2·(θ − 0.2). Because the hips can only extend, the gait needs a slight backward torso lean, so 0.2 is the reference. Together with the stance-leg joint stiffness this holds the torso upright.
- **Speed regulation.** Both hips also get a Raibert-style term, 0.15·(vx − 0.6). When the robot moves fast, the swing foot lands further forward; when it is slow, the foot lands closer.
- **Damping kept stable for 8 ms control steps.**
  - Hip damping uses the thigh's world-frame angular velocity (joint velocity + torso angular velocity). This damps a swinging leg without making the light torso chatter when both feet are planted.
  - Ankle damping is kept very small because the foot's inertia is small, and larger damping would go unstable at this step size.
- **Start-up.** The initial phase π/2 makes the right leg's starting target match the standing pose (stance start). The left leg goes straight to its toe-off pose.

```json
{"target": "cpg", "obs_dim": 17, "act_dim": 6, "hidden": 16,
 "oscillators": [{"name": "osc", "freq_hz": 1.0, "phase0": 1.5708}],
 "couplings": [],
 "bias": {},
 "units": [
   {"type": "reflex", "name": "right_hip", "inputs": {"obs[2]": -6.0, "sin(osc)": 1.5, "obs[11]": -0.5, "obs[1]": 2.0, "obs[10]": -0.4, "obs[8]": 0.15},
    "threshold": 1.99, "sharpness": 1.0, "to": {"a0": 1.0}},
   {"type": "reflex", "name": "left_hip", "inputs": {"obs[5]": -6.0, "sin(osc)": -1.5, "obs[14]": -0.5, "obs[1]": 2.0, "obs[10]": -0.4, "obs[8]": 0.15},
    "threshold": 1.99, "sharpness": 1.0, "to": {"a3": 1.0}},
   {"type": "reflex", "name": "right_knee", "inputs": {"obs[3]": -4.0, "cos(osc)": -1.131, "sin(osc)": 1.131, "obs[12]": -0.2},
    "threshold": 1.6, "sharpness": 1.0, "to": {"a1": 1.0}},
   {"type": "reflex", "name": "left_knee", "inputs": {"obs[6]": -4.0, "cos(osc)": 1.131, "sin(osc)": -1.131, "obs[15]": -0.2},
    "threshold": 1.6, "sharpness": 1.0, "to": {"a4": 1.0}},
   {"type": "reflex", "name": "right_ankle", "inputs": {"obs[4]": -3.0, "cos(osc)": 0.573, "sin(osc)": 0.177, "obs[13]": -0.03},
    "threshold": -0.3, "sharpness": 1.0, "to": {"a2": 1.0}},
   {"type": "reflex", "name": "left_ankle", "inputs": {"obs[7]": -3.0, "cos(osc)": -0.573, "sin(osc)": -0.177, "obs[16]": -0.03},
    "threshold": -0.3, "sharpness": 1.0, "to": {"a5": 1.0}}
 ]}
```