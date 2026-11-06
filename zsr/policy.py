"""The weight-file format: a one-hidden-layer tanh MLP, raw observations in, clipped actions out.

    h = tanh(W1 @ obs + b1)            W1: (16, obs_dim), b1: (16,)
    a = clip(W2 @ h + b2, low, high)   W2: (act_dim, 16), b2: (act_dim,)

This is exactly the actor SB3 PPO learns with net_arch pi=[16] and tanh, so PPO weights export losslessly.
"""
import json

import numpy as np

from .tasks import HIDDEN, TASKS

KEYS = ("W1", "b1", "W2", "b2")


def shapes(task: str) -> dict:
    t = TASKS[task]
    return {"W1": (HIDDEN, t.obs_dim), "b1": (HIDDEN,), "W2": (t.act_dim, HIDDEN), "b2": (t.act_dim,)}


def n_params(task: str) -> int:
    return sum(int(np.prod(s)) for s in shapes(task).values())


class WeightError(ValueError):
    pass


class MLPPolicy:
    def __init__(self, task: str, params: dict):
        if not isinstance(params, dict):
            raise WeightError("weight file must be a JSON object")
        self.task = TASKS[task]
        self.p = {}
        for k, shp in shapes(task).items():
            if k not in params:
                raise WeightError(f"missing key {k}")
            try:
                a = np.array(params[k], dtype=np.float64)
            except (ValueError, TypeError) as e:
                raise WeightError(f"{k}: not a rectangular numeric array ({e})")
            if a.shape != shp:
                raise WeightError(f"{k}: shape {a.shape}, expected {shp}")
            if not np.isfinite(a).all():
                raise WeightError(f"{k}: contains non-finite values")
            self.p[k] = a
        extra = set(params) - set(KEYS)
        if extra:
            raise WeightError(f"unexpected keys {sorted(extra)}")
        self.low = np.array(self.task.act_low)
        self.high = np.array(self.task.act_high)

    def reset(self):
        pass

    def act(self, obs):
        h = np.tanh(self.p["W1"] @ np.asarray(obs, dtype=np.float64) + self.p["b1"])
        return np.clip(self.p["W2"] @ h + self.p["b2"], self.low, self.high)

    def to_json(self) -> dict:
        return {k: self.p[k].tolist() for k in KEYS}


def load_weights(task: str, path) -> MLPPolicy:
    with open(path) as f:
        return MLPPolicy(task, json.load(f))


def save_weights(policy: MLPPolicy, path):
    with open(path, "w") as f:
        json.dump(policy.to_json(), f, indent=1)


def zero_policy(task: str) -> MLPPolicy:
    return MLPPolicy(task, {k: np.zeros(s) for k, s in shapes(task).items()})


def random_policy(task: str, seed: int) -> MLPPolicy:
    """Gaussian weights with std 1/sqrt(fan_in), zero biases."""
    rng = np.random.default_rng(seed)
    params = {}
    for k, s in shapes(task).items():
        params[k] = rng.normal(0, 1 / np.sqrt(s[-1]), s) if k.startswith("W") else np.zeros(s)
    return MLPPolicy(task, params)
