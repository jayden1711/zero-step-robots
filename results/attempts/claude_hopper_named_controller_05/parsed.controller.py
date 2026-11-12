import numpy as np


def reset():
    pass


def act(obs):
    z, th, q_thigh, q_leg, q_foot, vx, vz, w, wt, wl, wf = [float(x) for x in obs]

    # lean slightly back when moving forward, forward when moving backward
    th_des = float(np.clip(-0.05 * vx, -0.05, 0.05))
    err = th - th_des

    a_foot = 5.0 * err + 0.5 * w
    a_thigh = 3.0 * err + 0.3 * w
    a_leg = -3.0 * q_leg - 0.1 * wl

    # also damp the foot joint's own motion
    a_foot -= 0.05 * wf

    a = [a_thigh, a_leg, a_foot]
    return [float(np.clip(x, -1.0, 1.0)) for x in a]
