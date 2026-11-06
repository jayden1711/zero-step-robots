"""Reference Python controller for hopper: linear feedback, K found by a 60-sample random search
(scripts/scan_hopper_ref.py, seed 0, 5 episodes each). It exists to test the harness; it is not a strong baseline."""
K = [[2.37, -1.4, -0.55, -0.46, 1.32, -0.82, 1.66, 1.6, 0.87, 0.44, -1.56],
     [0.18, -1.43, -0.36, 0.2, -0.31, 0.95, -0.13, -1.55, -1.06, -1.27, -0.32],
     [1.25, 0.51, 0.34, -1.29, 2.37, -0.03, 2.42, -0.87, -0.57, 2.6, -1.07]]


def act(obs):
    return [sum(k * o for k, o in zip(row, obs)) for row in K]
