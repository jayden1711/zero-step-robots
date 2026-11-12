The controller only balances in place. It does not hop. I couldn't test anything, and a hand-tuned hopping gait I can't tune is likely to fall early. Standing upright for the full 1000 steps reliably earns about 1000 reward, which is the most dependable result here.

**How it works:**
- **Joint signs.** All joints rotate about the −y axis. A positive torso angle means the torso leans back. Negative thigh and leg angles mean the hip and knee are bending.
- **Hip and knee.** Both are held stiff at 0, so the leg stays straight and the torso stays in line with the thigh. Both joints sit at their joint limit there, which acts like a locked knee and adds stability.
- **Ankle.** The ankle balances the whole body like an inverted pendulum. With the foot flat, the foot angle equals minus the leg's tilt, so pushing the foot angle back to 0 keeps the body upright. The stiffness (about 2 × 200 Nm/rad) is well above the gravity effect (about 80 Nm/rad).
- **Extra torso feedback.** A small term based on the torso's own angle and angular velocity is added to both the hip and the ankle, so that the 0.2 rad tilt limit is never approached.
- **Gain sizes.** The joints have armature 1, which adds inertia. With that, these PD gains are well damped at 0.008 s steps.

```python
import numpy as np

# PD gains (normalised action units; actuator gear is 200)
KP = np.array([3.0, 3.0, 2.0])
KD = np.array([0.3, 0.3, 0.25])
TARGET = np.array([0.0, 0.0, 0.0])

# extra global torso attitude feedback
K_TORSO_HIP = 1.0
D_TORSO_HIP = 0.1
K_TORSO_FOOT = 0.5
D_TORSO_FOOT = 0.05


def reset():
    pass


def act(obs):
    obs = np.asarray(obs, dtype=float)
    q = obs[2:5]
    qd = obs[8:11]
    th = obs[1]
    thd = obs[7]

    u = KP * (TARGET - q) - KD * qd

    # torso leaning back (th > 0): positive hip torque pitches torso forward
    u[0] += K_TORSO_HIP * th + D_TORSO_HIP * thd
    # positive ankle torque pitches the whole body forward
    u[2] += K_TORSO_FOOT * th + D_TORSO_FOOT * thd

    u = np.clip(u, -1.0, 1.0)
    return [float(u[0]), float(u[1]), float(u[2])]
```