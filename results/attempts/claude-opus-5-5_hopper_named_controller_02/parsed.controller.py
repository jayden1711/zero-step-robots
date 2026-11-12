import numpy as np

# Joint PD gains (action units; actuator gear is 200 Nm per unit)
KP = np.array([3.0, 3.0, 2.5])
KD = np.array([0.30, 0.25, 0.20])

# Whole-body balance feedback applied at the ankle (foot joint)
K_TILT = 2.0      # per radian of torso tilt
K_TILT_RATE = 0.3 # per rad/s of torso angular velocity
K_VX = 0.15       # per m/s of forward drift

TARGET = np.array([0.0, 0.0, 0.0])


def reset():
    pass


def act(obs):
    o = np.asarray(obs, dtype=float)
    tilt = o[1]
    q = o[2:5]
    vx = o[5]
    tilt_rate = o[7]
    qd = o[8:11]

    a = -KP * (q - TARGET) - KD * qd

    # Ankle strategy: forward lean (tilt > 0) -> negative foot torque pushes body back.
    a[2] += -K_TILT * tilt - K_TILT_RATE * tilt_rate - K_VX * vx

    # Keep the upper body from folding at the hip while balancing.
    a[0] += -0.5 * tilt - 0.05 * tilt_rate

    a = np.clip(a, -1.0, 1.0)
    return [float(a[0]), float(a[1]), float(a[2])]
