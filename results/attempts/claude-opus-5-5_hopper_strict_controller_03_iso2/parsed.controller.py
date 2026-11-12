import numpy as np

_t = 0

KP = np.array([4.0, 4.0, 4.0])
KD = np.array([0.2, 0.2, 0.2])
LEAN = 0.1          # final forward lean of the straight leg (rad)
RAMP = 300          # steps to reach full lean


def reset():
    global _t
    _t = 0


def act(obs):
    global _t
    o = np.asarray(obs, dtype=float)
    q = o[2:5]          # thigh, leg, foot joint angles
    qd = o[8:11]        # joint velocities
    vx = o[5]
    phi = o[1]
    phid = o[7]

    lean = LEAN * min(1.0, _t / RAMP)
    # straight leg tilted forward, torso upright, foot flat (targets sum to 0)
    target = np.array([-lean, 0.0, lean])

    a = -KP * (q - target) - KD * qd
    # keep torso upright via hip (hip torque reaction acts on torso)
    a[0] += 1.0 * phi + 0.05 * phid
    # damp horizontal rocking with the ankle
    a[2] -= 0.3 * vx

    _t += 1
    return [float(x) for x in np.clip(a, -1.0, 1.0)]
