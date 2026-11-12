import numpy as np

# Joint-space PD that holds the initial upright posture (all joint angles = 0).
# With joints stiff, the hopper is a statically stable rigid body standing on its
# foot, so it stays healthy for the full episode and collects the +1/step bonus.

KP = np.array([1.0, 1.0, 2.0])     # thigh, leg, foot
KD = np.array([0.06, 0.08, 0.15])
TARGET = np.array([0.0, 0.0, 0.0])


def reset():
    pass


def act(obs):
    obs = np.asarray(obs, dtype=float)
    q = obs[2:5]
    qd = obs[8:11]
    a = KP * (TARGET - q) - KD * qd
    a = np.clip(a, -1.0, 1.0)
    return [float(a[0]), float(a[1]), float(a[2])]
