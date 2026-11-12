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
