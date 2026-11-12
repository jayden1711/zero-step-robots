import numpy as np

# Joint PD gains (action units per rad, per rad/s); actuator gear ~200.
KP = np.array([3.0, 3.0, 3.0])
KD = np.array([0.3, 0.3, 0.3])

# Small extra correction on torso pitch (obs[1]) to keep posture upright.
K_TORSO_P = 1.0
K_TORSO_D = 0.1


def reset():
    pass


def act(obs):
    o = np.asarray(obs, dtype=float)
    q = o[2:5]          # thigh, leg, foot joint angles
    qd = o[8:11]        # their velocities
    pitch = o[1]
    pitch_rate = o[7]

    # Hold all joints rigid at their nominal (zero) angles.
    a = -KP * q - KD * qd

    # Keep the foot flat on the ground: the foot's absolute angle is the sum
    # of the root pitch and all joint angles. Correct the torso pitch through
    # the hip and the ankle, keeping the corrections small.
    a[0] += K_TORSO_P * pitch + K_TORSO_D * pitch_rate
    a[2] += -0.5 * (K_TORSO_P * pitch + K_TORSO_D * pitch_rate)

    a = np.clip(a, -1.0, 1.0)
    return [float(a[0]), float(a[1]), float(a[2])]
