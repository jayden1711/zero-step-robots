import numpy as np

# Joint-space PD controller holding the hopper rigidly straight.
# With all joints at 0 the combined centre of mass lies above the foot,
# so the robot is statically stable and survives the full episode.

_TARGET = np.array([0.0, 0.0, 0.0])
_KP = np.array([3.0, 3.0, 2.0])
_KD = np.array([0.3, 0.3, 0.2])


def reset():
    pass


def act(obs):
    obs = np.asarray(obs, dtype=float)
    q = obs[2:5]
    qd = obs[8:11]
    a = _KP * (_TARGET - q) - _KD * qd
    a = np.clip(a, -1.0, 1.0)
    return [float(a[0]), float(a[1]), float(a[2])]
