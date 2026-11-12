import numpy as np

def reset():
    pass

def act(obs):
    o = np.asarray(obs, dtype=float)
    th = o[1]
    qt, ql, qf = o[2], o[3], o[4]
    vx = o[5]
    dth, dqt, dql, dqf = o[7], o[8], o[9], o[10]

    # hip / knee: keep the leg straight and aligned with the torso
    kp, kd = 1.0, 0.06
    a_thigh = -kp * qt - kd * dqt
    a_leg = -kp * ql - kd * dql

    # approximate tilt of the whole body's centre of mass about the foot
    phi = th - 0.6 * qt - 0.2 * ql
    dphi = dth - 0.6 * dqt - 0.2 * dql

    # ankle strategy: lean forward -> negative foot torque
    a_foot = -(0.75 * phi + 0.17 * dphi + 0.05 * vx) - 0.05 * qf - 0.005 * dqf
    a_foot = float(np.clip(a_foot, -0.25, 0.25))

    a = np.clip([a_thigh, a_leg, a_foot], -1.0, 1.0)
    return [float(a[0]), float(a[1]), float(a[2])]
