"""Small random search over a linear hopper controller, to pick a reference that runs a while. Not a baseline arm."""
import numpy as np

from zsr.harness import evaluate
from zsr.policy import MLPPolicy, shapes


class Lin:
    def __init__(self, K):
        self.K = K
        self.p = None

    def reset(self):
        pass

    def act(self, obs):
        return np.clip(self.K @ np.asarray(obs), -1, 1)


rng = np.random.default_rng(0)
best = (-1, None)
for i in range(60):
    K = rng.normal(0, 1.0, (3, 11))
    r = evaluate("hopper", Lin(K), 5, seed0=500)["mean_return"]
    if r > best[0]:
        best = (r, K)
print("best", best[0])
np.save("results/hopper_ref_K.npy", best[1])
print(repr(np.round(best[1], 2).tolist()))
