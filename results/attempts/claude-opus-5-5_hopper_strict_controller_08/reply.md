This controller only tries to balance in place. It does not attempt forward motion. The reasoning is that a hopping gait written without any testing is likely to fall early, and a fall loses more reward than forward speed could add. Standing healthy for all 1000 steps should score about 1000. I have not been able to run this.

How it works:

- **System guess:** The observation and health rules match a planar one-legged hopper:
  - obs[0] is height and obs[1] is torso pitch.
  - obs[2..4] are the hip, knee and ankle angles.
  - obs[5..10] are the matching velocities.
  - The 3 actions are torques on those three joints.
- **Hip and knee:** Each is held rigidly at its starting angle of about 0 with a stiff PD controller. Because each actuator pushes directly along its own joint coordinate, `a = -kp*q - kd*qdot` is stabilizing whatever the axis sign.
- **Ankle:** With hip and knee rigid, the body above the foot acts as one inverted pendulum about the ankle. While the foot is flat, the ankle angle equals the lean of that pendulum.
  - A PD controller on the ankle, with stiffness well above the gravity term (roughly m·g·h ≈ 100 N·m/rad), keeps it upright.
  - The ankle gain is kept moderate so the torque stays small and the foot does not tip.
- **Torso pitch:** A small extra term on torso pitch, applied at the hip, keeps |obs[1]| well below 0.2.

```python
import numpy as np

# Joint PD gains (action units per rad, per rad/s)
KP_HIP, KD_HIP = 3.0, 0.3
KP_KNEE, KD_KNEE = 3.0, 0.3
KP_ANKLE, KD_ANKLE = 2.0, 0.4
# Extra torso-pitch correction through the hip
KP_TORSO, KD_TORSO = 1.0, 0.1


def reset():
    pass


def act(obs):
    o = np.asarray(obs, dtype=float)
    pitch = o[1]
    q_hip, q_knee, q_ankle = o[2], o[3], o[4]
    pitch_d = o[7]
    qd_hip, qd_knee, qd_ankle = o[8], o[9], o[10]

    a_hip = -KP_HIP * q_hip - KD_HIP * qd_hip
    # hip torque reaction leans torso forward for positive action -> push back on forward pitch
    a_hip += -KP_TORSO * pitch - KD_TORSO * pitch_d

    a_knee = -KP_KNEE * q_knee - KD_KNEE * qd_knee

    a_ankle = -KP_ANKLE * q_ankle - KD_ANKLE * qd_ankle

    a = np.clip([a_hip, a_knee, a_ankle], -1.0, 1.0)
    return [float(a[0]), float(a[1]), float(a[2])]
```