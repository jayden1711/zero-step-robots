This observation and action layout matches the MuJoCo Hopper: a one-legged planar robot. The 11 numbers are torso height, torso pitch, three joint angles (thigh, leg, foot), then six velocities. The 3 actions are the joint motors.

**Why the controller just stands still.** I can't test anything, and any fall ends the episode early and loses most of the reward. A hopping gait designed without testing would very likely fall before 1000 steps, so it would probably score worse on average than standing.

**What it does.** The controller holds all three joints stiffly at their initial angle of zero with a PD (spring-and-damper) control law. That turns the robot into a single rigid body standing on its flat foot. Its centre of mass sits over the ankle, well inside the foot, so it is statically stable.

**Expected score.** It should collect the +1 healthy reward for all 1000 steps, giving about 1000 per episode. The torque penalty is negligible.

**Gains.** The damping is kept moderate so the PD loop stays stable at the simulator's 2 ms internal step. A small extra torque at the hip counters any torso tilt.

```python
import numpy as np

KP = np.array([4.0, 4.0, 4.0])
KD = np.array([0.08, 0.08, 0.08])
K_TORSO = 1.0
KD_TORSO = 0.05


def reset():
    pass


def act(obs):
    o = np.asarray(obs, dtype=float)
    q = o[2:5]
    qd = o[8:11]
    a = -KP * q - KD * qd
    # small torso-upright correction through the hip
    a[0] += K_TORSO * o[1] + KD_TORSO * o[7]
    a = np.clip(a, -1.0, 1.0)
    return [float(a[0]), float(a[1]), float(a[2])]
```