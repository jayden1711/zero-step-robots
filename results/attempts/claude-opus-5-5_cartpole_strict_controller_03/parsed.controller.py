import numpy as np

# State feedback: u = KX*x + KV*xdot + KT*theta + KW*thetadot
# obs = [cart position, pole angle, cart velocity, pole angular velocity]
KX = 0.23
KV = 0.53
KT = 5.4
KW = 1.1


def reset():
    pass


def act(obs):
    x, th, xd, thd = (float(v) for v in obs[:4])
    if not all(np.isfinite([x, th, xd, thd])):
        return [0.0]
    u = KX * x + KV * xd + KT * th + KW * thd
    u = max(-3.0, min(3.0, u))
    return [u]
