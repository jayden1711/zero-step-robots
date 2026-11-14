import numpy as np

# obs = [cart_pos, pole_angle, cart_vel, pole_ang_vel]
K_X = 0.1
K_TH = 5.0
K_XD = 0.3
K_THD = 0.5


def reset():
    pass


def act(obs):
    x, th, xd, thd = (float(v) for v in obs[:4])
    if not all(np.isfinite([x, th, xd, thd])):
        return [0.0]
    u = K_X * x + K_TH * th + K_XD * xd + K_THD * thd
    u = float(np.clip(u, -3.0, 3.0))
    return [u]
