This controller holds the hopper upright and still for the full 1000 steps. I haven't run it in the simulator, so the score and the gain margins below are estimates from the model's physics, not measurements.

**Why standing rather than hopping:** a stable stand earns about +1 per step, so roughly **1000** per episode. A hand-tuned forward hop could score more, but a gait I can't test is likely to fall early and score far less.

**How it works:**
- **Joint control:** each joint is pushed back to its upright angle of 0 with a spring-and-damper rule (PD control). The gear ratio is 200, so `Kp = 3` gives about 600 Nm/rad. Tipping the whole robot over takes only about 135 Nm/rad, so the joints should be stiff enough. The joints already include damping and extra inertia (armature), so moderate damping should not oscillate at the 8 ms control step.
- **Balance through the ankle:** if the body tilts by θ while the foot stays flat, the foot joint reads −θ. The joint controller then pushes back with +Kp·θ, which tilts the leg back toward upright. So holding the joints at 0 already balances the robot from the ankle.
- **Extra balance terms:** I added a small torso-angle term at the ankle and a torso-angle term at the hip to keep the torso well inside the ±0.2 rad limit.
- **Foot position:** the foot reaches from about −0.13 to +0.26 in x, and the centre of mass sits near x ≈ 0, so it stays over the foot.

```python
import numpy as np

KP = np.array([3.0, 3.0, 3.0])
KD = np.array([0.25, 0.25, 0.25])


def reset():
    pass


def act(obs):
    o = np.asarray(obs, dtype=float)
    torso_ang = o[1]
    q = o[2:5]
    torso_angvel = o[7]
    qd = o[8:11]

    a = -KP * q - KD * qd

    # Hip: keep the torso upright relative to the world.
    a[0] += -1.5 * torso_ang - 0.1 * torso_angvel
    # Ankle strategy: counter whole-body tilt via torque against the ground.
    a[2] += 1.0 * torso_ang + 0.1 * torso_angvel

    a = np.clip(a, -1.0, 1.0)
    return [float(a[0]), float(a[1]), float(a[2])]
```