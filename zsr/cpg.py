"""The `cpg-v1` weight format (docs/prereg-2026-11-09-cpg.md section 2): M phase oscillators feeding the same
16-tanh-unit layer every other arm uses.

    y      = [cos th_1, sin th_1, ..., cos th_M, sin th_M]
    h      = tanh(W1 @ [obs; y] + b1)                       W1: (16, obs_dim + 2M)
    action = clip(W2 @ h + b2, low, high)                   W2: (act_dim, 16)
    th    <- th + dt * (2 pi f + sum_j C_ij sin(th_j - th_i - Phi_ij) + S @ obs)     (explicit Euler)

The action at step t uses th_t; th is then advanced with obs_t. th is reset to theta0 at every episode reset.
"""
import json

import numpy as np

from .tasks import HIDDEN, TASKS

FORMAT = "cpg-v1"
MAX_OSC = 4
DT = 0.008  # Hopper-v5 and Walker2d-v5: frame_skip 4 x timestep 0.002
KEYS = ("format", "f", "C", "Phi", "S", "theta0", "W1", "b1", "W2", "b2")


class CPGError(ValueError):
    pass


def shapes(task: str, m: int) -> dict:
    t = TASKS[task]
    return {"f": (m,), "C": (m, m), "Phi": (m, m), "S": (m, t.obs_dim), "theta0": (m,),
            "W1": (HIDDEN, t.obs_dim + 2 * m), "b1": (HIDDEN,), "W2": (t.act_dim, HIDDEN), "b2": (t.act_dim,)}


class CPGPolicy:
    def __init__(self, task: str, params: dict):
        if not isinstance(params, dict):
            raise CPGError("cpg file must be a JSON object")
        if params.get("format") != FORMAT:
            raise CPGError(f"format must be {FORMAT!r}")
        extra = set(params) - set(KEYS)
        if extra:
            raise CPGError(f"unexpected keys {sorted(extra)}")
        try:
            m = len(params["f"])
        except (KeyError, TypeError):
            raise CPGError("missing or invalid 'f'")
        if not 0 <= m <= MAX_OSC:
            raise CPGError(f"{m} oscillators; at most {MAX_OSC}")
        self.task, self.m, self.p = TASKS[task], m, {}
        for k, shp in shapes(task, m).items():
            if k not in params:
                raise CPGError(f"missing key {k}")
            try:
                a = np.array(params[k], dtype=np.float64)
            except (ValueError, TypeError) as e:
                raise CPGError(f"{k}: not a rectangular numeric array ({e})")
            if a.size == 0 and int(np.prod(shp)) == 0:
                a = a.reshape(shp)
            if a.shape != shp:
                raise CPGError(f"{k}: shape {a.shape}, expected {shp}")
            if not np.isfinite(a).all():
                raise CPGError(f"{k}: contains non-finite values")
            self.p[k] = a
        self.low, self.high = np.array(self.task.act_low), np.array(self.task.act_high)
        self.reset()

    def reset(self):
        self.theta = self.p["theta0"].copy()

    def osc_out(self):
        y = np.empty(2 * self.m)
        y[0::2], y[1::2] = np.cos(self.theta), np.sin(self.theta)
        return y

    def act(self, obs):
        obs = np.asarray(obs, dtype=np.float64)
        p = self.p
        h = np.tanh(p["W1"] @ np.concatenate([obs, self.osc_out()]) + p["b1"])
        a = np.clip(p["W2"] @ h + p["b2"], self.low, self.high)
        if self.m:
            th = self.theta
            diff = th[None, :] - th[:, None] - p["Phi"]  # [i, j] = th_j - th_i - Phi_ij
            dth = 2 * np.pi * p["f"] + (p["C"] * np.sin(diff)).sum(axis=1) + p["S"] @ obs
            self.theta = th + DT * dth
        return a

    def to_json(self) -> dict:
        return {"format": FORMAT, **{k: self.p[k].tolist() for k in KEYS[1:]}}


def load_cpg(task: str, path) -> CPGPolicy:
    with open(path) as f:
        return CPGPolicy(task, json.load(f))


def save_cpg(policy: CPGPolicy, path):
    with open(path, "w") as f:
        json.dump(policy.to_json(), f, indent=1)
