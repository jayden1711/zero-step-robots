def reset():
    pass


def act(obs):
    th = obs[1]
    q1, q2, q3 = obs[2], obs[3], obs[4]
    w = obs[7]
    dq1, dq2, dq3 = obs[8], obs[9], obs[10]

    a3 = 6.0 * th + 0.8 * w - 0.5 * q3 * 0.0
    a2 = -4.0 * q2 - 0.15 * dq2
    a1 = -4.0 * q1 - 0.15 * dq1 + 2.0 * th + 0.3 * w

    def c(x):
        return max(-1.0, min(1.0, x))

    return [c(a1), c(a2), c(a3)]
