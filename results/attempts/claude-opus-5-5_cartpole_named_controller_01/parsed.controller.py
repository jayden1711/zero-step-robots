import numpy as np

# Linear state feedback: u = c*x + d*v + a*theta + b*omega
# Gains from pole placement on a linearised cart-pole model
# (fast pair: wn=7, zeta=0.8; slow pair: wn=1.5, zeta=0.9).
K_X = 0.53
K_V = 0.756
K_TH = 5.55
K_OM = 0.955


def reset():
    pass


def act(obs):
    x, th, v, om = (float(o) for o in obs[:4])
    u = K_X * x + K_V * v + K_TH * th + K_OM * om
    if not np.isfinite(u):
        u = 0.0
    u = max(-3.0, min(3.0, u))
    return [u]
