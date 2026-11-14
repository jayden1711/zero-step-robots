import numpy as np

# Joint PD gains (action units; actuator gear = 200)
KP_JOINT = 5.0
KD_JOINT = 0.25

# Ankle balance gains on whole-body lean (positive lean = leaning back)
KP_LEAN = 2.0
KD_LEAN = 0.5
FOOT_LIMIT = 0.15

THIGH_TARGET = 0.0
LEG_TARGET = 0.0


def reset():
    pass


def act(obs):
    o = np.asarray(obs, dtype=float)
    torso, thigh, leg = o[1], o[2], o[3]
    torso_w, thigh_w, leg_w = o[7], o[8], o[9]

    # Keep hip and knee rigid and straight
    a_thigh = -KP_JOINT * (thigh - THIGH_TARGET) - KD_JOINT * thigh_w
    a_leg = -KP_JOINT * (leg - LEG_TARGET) - KD_JOINT * leg_w

    # Ankle strategy: balance the rigid body over the flat foot
    lean = torso + thigh + leg
    lean_w = torso_w + thigh_w + leg_w
    a_foot = KP_LEAN * lean + KD_LEAN * lean_w
    a_foot = float(np.clip(a_foot, -FOOT_LIMIT, FOOT_LIMIT))

    a = np.clip([a_thigh, a_leg, a_foot], -1.0, 1.0)
    return [float(a[0]), float(a[1]), float(a[2])]
