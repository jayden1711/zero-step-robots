import numpy as np

# Inner (angle) loop gains
K_TH = 3.5
K_THD = 0.5
# Outer (cart position) loop: reference lean angle
C_X = 0.1
C_XD = 0.14
TH_REF_MAX = 0.08


def reset():
    pass


def act(obs):
    x, th, xd, thd = (float(v) for v in obs)
    if not np.all(np.isfinite([x, th, xd, thd])):
        return [0.0]
    # To move the cart back toward 0, lean the pole toward 0 first.
    th_ref = -(C_X * x + C_XD * xd)
    th_ref = max(-TH_REF_MAX, min(TH_REF_MAX, th_ref))
    u = K_TH * (th - th_ref) + K_THD * thd
    u = max(-3.0, min(3.0, u))
    return [u]
