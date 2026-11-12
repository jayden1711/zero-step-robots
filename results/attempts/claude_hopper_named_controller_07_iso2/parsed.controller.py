def reset():
    pass


def act(obs):
    z, th, q1, q2, q3, vx, vz, w, w1, w2, w3 = obs

    a1 = -6.0 * q1 - 0.3 * w1
    a2 = -6.0 * q2 - 0.3 * w2
    a3 = 3.0 * th + 0.5 * w - 0.5 * q3 - 0.05 * w3

    def c(a):
        return max(-1.0, min(1.0, float(a)))

    return [c(a1), c(a2), c(a3)]
