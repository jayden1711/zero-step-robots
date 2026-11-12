import numpy as np


def reset():
    pass


def act(obs):
    angle = obs[1]
    angvel = obs[7]
    ankle = 4.0 * angle + 0.6 * angvel
    ankle = float(np.clip(ankle, -1.0, 1.0))
    return [0.5, 0.5, ankle]
