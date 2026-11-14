This controller tries to keep the system standing still instead of hopping forward. Holding steady for all 1000 steps should score about 1000. A blind hopping gait could score more, but it would likely fall early and score far less. I could not run or test it, so the gains are estimates from the system's likely geometry and masses.

**What I assume the system is.** The specs match MuJoCo's Hopper: a one-legged body with a torso, thigh, leg and foot.
- `obs[0]` is height and `obs[1]` is torso angle.
- `obs[2:5]` are the thigh, knee and ankle joint angles.
- `obs[5:11]` are the velocities.
- All hinges rotate about −y, so a positive angle tilts a segment's top backward.
- The actions are the thigh, knee and ankle torques.

**How it balances.**
- **Hip:** a PD loop on the torso angle keeps the torso upright (sign: positive hip torque pitches the torso forward).
- **Knee:** a PD loop holds the knee straight.
- **Ankle:** the body is treated as an inverted pendulum around the ankle. A PD loop on the leg's absolute angle (`q1+q2+q3`) keeps it leaning very slightly forward, so the centre of mass sits over the middle of the foot rather than near the heel.
- **Gain size:** the gains are well above the gravity "stiffness" (about 60 Nm/rad against a 200× gear) and close to critically damped.

```python
import numpy as np

# Posture targets
LEG_LEAN_TARGET = -0.05   # absolute leg angle (slightly forward, CoM over mid-foot)
TORSO_TARGET = 0.0
KNEE_TARGET = 0.0

# Gains (action units; gear ~200)
KT, DT = 1.0, 0.1     # torso via hip
KK, DK = 2.0, 0.2     # knee
KA, DA = 1.5, 0.3     # ankle balance


def reset():
    pass


def act(obs):
    o = np.asarray(obs, dtype=float)
    q1, q2, q3, q4 = o[1], o[2], o[3], o[4]
    w1, w2, w3, w4 = o[7], o[8], o[9], o[10]

    # Hip: keep torso upright (positive hip torque pitches torso forward)
    u_hip = KT * (q1 - TORSO_TARGET) + DT * w1

    # Knee: hold straight
    u_knee = -KK * (q3 - KNEE_TARGET) - DK * w3

    # Ankle: inverted-pendulum balance on absolute leg angle
    phi = q1 + q2 + q3
    phid = w1 + w2 + w3
    u_ankle = KA * (phi - LEG_LEAN_TARGET) + DA * phid

    a = np.clip([u_hip, u_knee, u_ankle], -1.0, 1.0)
    return [float(a[0]), float(a[1]), float(a[2])]
```