import numpy as np


def reset():
    pass


def act(obs):
    o = np.asarray(obs, dtype=float)
    ang = o[1]
    thigh, leg, foot = o[2], o[3], o[4]
    angv = o[7]
    thigh_v, leg_v, foot_v = o[8], o[9], o[10]

    # stiff PD holding thigh and leg straight (0 is also their joint limit)
    kp, kd = 1.5, 0.15
    a_thigh = -kp * (thigh - 0.0) - kd * thigh_v
    a_leg = -kp * (leg - 0.0) - kd * leg_v

    # ankle strategy: body (rigid above ankle) is an inverted pendulum on the flat foot.
    # positive foot torque rotates the body toward negative torso angle.
    a_foot = 1.5 * ang + 0.3 * angv
    # keep the ankle torque modest so the foot does not tip off its edges
    a_foot = float(np.clip(a_foot, -0.15, 0.15))

    return [float(np.clip(a_thigh, -1, 1)),
            float(np.clip(a_leg, -1, 1)),
            a_foot]
