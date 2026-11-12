def reset():
    pass


def act(obs):
    ang = obs[1]
    angvel = obs[7]
    foot = 2.0 * ang + 0.3 * angvel
    foot = max(-1.0, min(1.0, foot))
    return [0.3, 0.3, foot]
