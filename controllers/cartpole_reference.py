"""Reference Python controller for cartpole: linear state feedback. Used to test the harness."""
K = (0.5, 12.0, 1.0, 1.5)


def act(obs):
    return [sum(k * o for k, o in zip(K, obs))]
