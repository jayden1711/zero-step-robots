def act(obs):
    x, theta, xdot, thetadot = obs
    u = 0.2 * x + 0.5 * xdot + 12.0 * theta + 1.5 * thetadot
    if u > 3.0:
        u = 3.0
    elif u < -3.0:
        u = -3.0
    return [float(u)]
