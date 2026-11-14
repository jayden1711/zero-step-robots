def reset():
    pass


def act(obs):
    ang = obs[1]
    q_th, q_leg = obs[2], obs[3]
    w = obs[7]
    w_th, w_leg = obs[8], obs[9]

    a_th = -5.0 * q_th - 0.5 * w_th + 0.3
    a_leg = -5.0 * q_leg - 0.5 * w_leg + 0.3
    a_foot = 8.0 * ang + 1.0 * w

    return [max(-1.0, min(1.0, a)) for a in (a_th, a_leg, a_foot)]
