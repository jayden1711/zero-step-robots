def reset():
    pass


def act(obs):
    theta = obs[1]
    omega = obs[7]
    foot = 3.0 * theta + 0.3 * omega
    foot = max(-1.0, min(1.0, foot))
    return [0.0, 0.0, foot]
