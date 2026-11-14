import numpy as np

# Hip / knee posture targets (slightly inside the [−150°, 0] joint limits)
Q1_TARGET = -0.03
Q2_TARGET = -0.03

KP_JOINT = 3.0
KD_JOINT = 0.2

# Ankle balance gains (action units; gear ~200)
K_LEAN = 1.6
KD_LEAN = 0.35
LEAN_TARGET = 0.0
ANKLE_LIMIT = 0.14   # keep ankle torque small so the foot stays flat


def reset():
    pass


def act(obs):
    o = np.asarray(obs, dtype=float)
    theta = o[1]
    q1, q2, q3 = o[2], o[3], o[4]
    dtheta = o[7]
    dq1, dq2, dq3 = o[8], o[9], o[10]

    # Hip and knee: hold body rigid
    a1 = -KP_JOINT * (q1 - Q1_TARGET) - KD_JOINT * dq1
    a2 = -KP_JOINT * (q2 - Q2_TARGET) - KD_JOINT * dq2

    # Approximate whole-body lean about the ankle
    lean = theta + 0.5 * q1 + 0.2 * q2
    dlean = dtheta + 0.5 * dq1 + 0.2 * dq2

    # Ankle torque: reaction on shin rotates the body opposite to the lean
    a3 = K_LEAN * (lean - LEAN_TARGET) + KD_LEAN * dlean
    a3 = float(np.clip(a3, -ANKLE_LIMIT, ANKLE_LIMIT))

    a1 = float(np.clip(a1, -1.0, 1.0))
    a2 = float(np.clip(a2, -1.0, 1.0))
    return [a1, a2, a3]
