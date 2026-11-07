"""Structural analysis of notable weight files. Local output only (RESULTS/notable/analysis_data.json).
For each attempt: per-hidden-unit saturation, input/output weight structure, the effective linear gain
(mean Jacobian of action w.r.t. observation along rollouts), how well a single linear policy imitates it
(least-squares fit on visited states), that fitted linear policy scored as its own policy, and a larger rerun.

usage: python scripts/analyze_weights.py RESULTS ATTEMPT_ID... (run through sim-run, from the repo root)
"""
import json
import sys
from pathlib import Path

import numpy as np

from zsr.harness import evaluate, run_episode
from zsr.policy import MLPPolicy, load_weights
from zsr.tasks import make_env

R = Path(sys.argv[1])
OBS = ["z", "angle", "thigh", "leg", "foot", "vx", "vz", "dangle", "dthigh", "dleg", "dfoot"]  # Gymnasium Hopper-v5 order


class Rec:
    def __init__(self, pol):
        self.pol, self.rows = pol, []

    def reset(self):
        self.pol.reset()

    def act(self, obs):
        p = self.pol.p
        pre = p["W1"] @ obs + p["b1"]
        h = np.tanh(pre)
        raw = p["W2"] @ h + p["b2"]
        J = p["W2"] @ ((1 - h ** 2)[:, None] * p["W1"])
        self.rows.append((obs.copy(), pre, h, raw, J))
        return self.pol.act(obs)


class Lin:
    def __init__(self, W, b, pol):
        self.W, self.b, self.pol = W, b, pol

    def reset(self):
        pass

    def act(self, obs):
        return np.clip(self.W @ obs + self.b, self.pol.low, self.pol.high)


out = {}
for aid in sys.argv[2:]:
    pol = load_weights("hopper", R / "notable" / aid / "parsed.weights.json")
    p = pol.p
    rec, env = Rec(pol), make_env("hopper")
    rets = [run_episode(env, rec, 10000 + i)["return"] for i in range(20)]
    O = np.array([r[0] for r in rec.rows]); PRE = np.array([r[1] for r in rec.rows])
    H = np.array([r[2] for r in rec.rows]); RAW = np.array([r[3] for r in rec.rows]); J = np.array([r[4] for r in rec.rows])
    A = np.clip(RAW, -1, 1)
    X = np.hstack([O, np.ones((len(O), 1))])
    coef, *_ = np.linalg.lstsq(X, RAW, rcond=None)
    pred = X @ coef
    r2 = 1 - ((RAW - pred) ** 2).sum(0) / ((RAW - RAW.mean(0)) ** 2).sum(0)
    lin = Lin(coef[:-1].T, coef[-1], pol)
    d = {
        "episodes_recorded": 20, "steps_recorded": int(len(O)), "mean_return_recorded": float(np.mean(rets)),
        "W1_abs_max": float(np.abs(p["W1"]).max()), "W2_abs_max": float(np.abs(p["W2"]).max()),
        "obs_mean": dict(zip(OBS, O.mean(0).round(4).tolist())), "obs_std": dict(zip(OBS, O.std(0).round(4).tolist())),
        "unit_saturation_frac(|tanh|>0.99)": (np.abs(H) > 0.99).mean(0).round(3).tolist(),
        "unit_mean_h": H.mean(0).round(3).tolist(), "unit_std_h": H.std(0).round(4).tolist(),
        "unit_pre_mean": PRE.mean(0).round(3).tolist(), "unit_pre_std": PRE.std(0).round(3).tolist(),
        "units_with_std_h_below_0.01": int((H.std(0) < 0.01).sum()),
        "action_raw_mean": RAW.mean(0).round(3).tolist(), "action_raw_std": RAW.std(0).round(3).tolist(),
        "action_clipped_frac": (np.abs(RAW) > 1).mean(0).round(3).tolist(),
        "mean_jacobian_action_wrt_obs": {f"a{k}": dict(zip(OBS, J.mean(0)[k].round(3).tolist())) for k in range(3)},
        "std_of_jacobian": J.std(0).round(3).tolist(),
        "linear_fit_R2_per_action": r2.round(4).tolist(),
        "linear_fit_W": {f"a{k}": dict(zip(OBS, coef[:-1, k].round(3).tolist())) for k in range(3)},
        "linear_fit_b": coef[-1].round(3).tolist(),
        "W1_rows": {f"u{u}": dict(zip(OBS, p["W1"][u].round(3).tolist())) | {"b": round(float(p["b1"][u]), 3)} for u in range(16)},
        "W2": p["W2"].round(3).tolist(), "b2": p["b2"].round(3).tolist(),
    }
    ev = evaluate("hopper", pol, 500, seed0=20000)
    d["rerun_500ep_seed20000"] = {k: ev[k] for k in ("mean_return", "sem_return", "median_return", "min_return", "frac_full_length",
                                                    "mean_distance", "mean_length")}
    ev = evaluate("hopper", lin, 100)
    d["fitted_linear_policy_stock_100ep"] = {k: ev[k] for k in ("mean_return", "median_return", "frac_full_length", "mean_distance")}
    out[aid] = d
    print(aid, "done", flush=True)
(R / "notable" / "analysis_data.json").write_text(json.dumps(out, indent=1))
