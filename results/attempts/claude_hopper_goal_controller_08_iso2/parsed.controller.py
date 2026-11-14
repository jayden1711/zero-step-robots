import numpy as np


def reset():
    pass


def act(obs):
    angle = obs[1]
    vx = obs[5]
    angvel = obs[7]
    foot = 10.0 * angle + 1.0 * angvel + 0.3 * vx
    foot = float(np.clip(foot, -1.0, 1.0))
    return [1.0, 1.0, foot]
