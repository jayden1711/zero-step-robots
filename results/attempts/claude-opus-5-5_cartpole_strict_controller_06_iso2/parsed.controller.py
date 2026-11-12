import numpy as np

# Inner (angle) loop gains
K_TH = 4.5
K_THD = 0.75
# Outer (cart position) loop: theta_ref = -(KP*x + KV*xdot)
KP = 0.05
KV = 0.15


def reset():
    pass


def act(obs):
    x, th, xd, thd = (float(v) for v in obs[:4])
    if not np.all(np.isfinite([x, th, xd, thd])):
        return [0.0]
    th_ref = -(KP * x + KV * xd)
    th_ref = max(-0.05, min(0.05, th_ref))
    a = K_TH * (th - th_ref) + K_THD * thd
    a = max(-3.0, min(3.0, a))
    return [a]
