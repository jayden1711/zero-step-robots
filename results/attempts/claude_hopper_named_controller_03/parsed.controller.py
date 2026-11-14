def act(obs):
    ang = obs[1]
    q_thigh, q_leg = obs[2], obs[3]
    w_torso = obs[7]
    w_thigh, w_leg = obs[8], obs[9]
    vx = obs[5]

    foot = 3.0 * ang + 0.3 * w_torso + 0.1 * vx
    thigh = -1.0 * q_thigh - 0.1 * w_thigh
    leg = -1.0 * q_leg - 0.1 * w_leg

    def c(x):
        return max(-1.0, min(1.0, float(x)))

    return [c(thigh), c(leg), c(foot)]
