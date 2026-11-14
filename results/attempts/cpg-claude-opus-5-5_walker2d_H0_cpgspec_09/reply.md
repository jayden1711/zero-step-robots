This is a hand-designed gait that I haven't simulated or tested. The physics reasoning is below; the exact numbers are estimates.

**Sign conventions.** All of Walker2d's hinge joints, including the torso's `rooty`, rotate about the axis (0, −1, 0). A negative angle therefore swings a limb's lower end toward −x (backward), and a positive torso angle means leaning back. The thigh range is [−150°, 0°], so a thigh can't swing ahead of the torso axis. To place a foot forward, the torso has to lean back a little.

**Control structure.** Each part of the controller has its own job:

1. **Torso balance (equal torque on both hips).** A hip torque pushes the torso the opposite way, so applying `Kt·(θ − θ*) + Dt·ω` to both hips holds the torso angle at θ* = 0.35 rad (leaning back). This sign is correct no matter how the legs are posed.
2. **Leg swing as a scissor (opposite torques on the two hips).** A spring-damper acts on the angle between the legs, ψ = q_R − q_L, pulling it toward a sine-wave target. Because the two hip torques are equal and opposite, the swing produces **no net torque on the torso**. Stepping and torso balance therefore don't interfere. The target is phase-advanced by 1 rad to make up for the lag of the swing response.
3. **Knees.** Each knee has a spring-damper pulling it toward +0.15 rad. The joint stops at 0, so the stance leg locks straight against that limit. A sharp switch, driven by the oscillator phase, bends the swing knee toward about −1 rad early in its swing so the foot clears the ground.
4. **Ankles.** Each ankle has a weak spring holding the foot level. It adds a small toe-up torque during swing and a small toe-down push-off late in stance.
5. **Step timing.** Forward speed feeds into the oscillator: the phase advances 2.5 rad/s faster per m/s of x-velocity. When the robot slows down, steps come later, which avoids taking an over-long step and falling backward. At about 0.6 m/s the gait runs at roughly 0.85 Hz with steps of about 0.4 m.

```json
{"target": "cpg", "obs_dim": 17, "act_dim": 6, "hidden": 16,
 "oscillators": [{"name": "p", "freq_hz": 0.6, "phase0": -1.0, "feedback": {"obs[8]": 2.5}}],
 "couplings": [],
 "bias": {"a0": -0.28, "a3": -0.28, "a1": -0.425, "a4": -0.425, "a2": 0.0, "a5": 0.0},
 "units": [
   {"type": "linear", "name": "torso_pd", "inputs": {"obs[1]": 1.0, "obs[10]": 0.07},
    "range": 2.0, "tol": 0.05, "to": {"a0": 0.8, "a3": 0.8}},
   {"type": "linear", "name": "scissor_pd", "inputs": {"obs[2]": 1.0, "obs[5]": -1.0, "obs[11]": 0.15, "obs[14]": -0.15},
    "range": 3.0, "tol": 0.05, "to": {"a0": -2.0, "a3": 2.0}},
   {"type": "linear", "name": "scissor_ff", "inputs": {"sin(p)": 0.5403, "cos(p)": 0.8415},
    "range": 1.0, "tol": 0.02, "to": {"a0": 0.8, "a3": -0.8}},
   {"type": "linear", "name": "knee_r_pd", "inputs": {"obs[3]": 1.0, "obs[12]": 0.15},
    "range": 3.0, "tol": 0.05, "to": {"a1": -1.0}},
   {"type": "linear", "name": "knee_l_pd", "inputs": {"obs[6]": 1.0, "obs[15]": 0.15},
    "range": 3.0, "tol": 0.05, "to": {"a4": -1.0}},
   {"type": "reflex", "name": "knee_r_flex", "inputs": {"cos(p)": 0.955, "sin(p)": -0.296},
    "threshold": 0.2, "sharpness": 4.0, "to": {"a1": -0.575, "a2": 0.08}},
   {"type": "reflex", "name": "knee_l_flex", "inputs": {"cos(p)": -0.955, "sin(p)": 0.296},
    "threshold": 0.2, "sharpness": 4.0, "to": {"a4": -0.575, "a5": 0.08}},
   {"type": "linear", "name": "foot_r_pd", "inputs": {"obs[4]": 1.0, "obs[13]": 0.1},
    "range": 2.0, "tol": 0.05, "to": {"a2": -0.4}},
   {"type": "linear", "name": "foot_l_pd", "inputs": {"obs[7]": 1.0, "obs[16]": 0.1},
    "range": 2.0, "tol": 0.05, "to": {"a5": -0.4}},
   {"type": "reflex", "name": "pushoff_r", "inputs": {"sin(p)": -0.955, "cos(p)": -0.296},
    "threshold": 0.7, "sharpness": 5.0, "to": {"a2": -0.08}},
   {"type": "reflex", "name": "pushoff_l", "inputs": {"sin(p)": 0.955, "cos(p)": 0.296},
    "threshold": 0.7, "sharpness": 5.0, "to": {"a5": -0.08}}
 ]}
```

The ankle biases cancel to 0: the +0.08 offset for the toe-up switch and the −0.08 offset for the push-off switch sum to zero. Each ankle therefore gets +0.16 (toe up) in mid-swing, −0.16 (toe down) at push-off, and about 0 otherwise.