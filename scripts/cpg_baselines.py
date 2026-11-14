"""CPG-track baselines (docs/prereg-2026-11-09-cpg.md section 5). Every row is scored by zsr.harness.evaluate on the
100 scoring episodes (seeds 10000..10099). Tuning sees dev seeds only: search fitness on seeds 0..9, the final pick
among the top candidates on seeds 10..19.

    python scripts/cpg_baselines.py necessity <task> --out DIR   # zero, random MLP x10, stand-still (hopper), lunge, sinusoid
    python scripts/cpg_baselines.py randcpg   <task> --out DIR   # 50 random CPG specs (distribution fixed below)
    python scripts/cpg_baselines.py tuned     <task> --out DIR   # hand-designed CPG structure, CEM on dev seeds

Run each through ~/projects/bin/sim-run (one process, one thread).
"""
import argparse
import json
import math
import sys
import time
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from circuitc import compile_cpg  # noqa: E402
from zsr.cpg import CPGPolicy  # noqa: E402
from zsr.harness import PythonController, evaluate, limit_resources, run_episode  # noqa: E402
from zsr.policy import load_weights, random_policy, zero_policy  # noqa: E402
from zsr.tasks import TASKS, make_env  # noqa: E402

SEARCH_SEEDS = range(0, 10)
PICK_SEEDS = range(10, 20)
BUDGET = 20_000  # dev episodes per task for the tuned CPG (prereg s5); the sinusoid uses half
MAIN_RESULTS = Path("/home/jayden/projects/zero-step-robots/results")

# joint layout per task: action index -> (angle obs index, velocity obs index); torso angle / rate obs indices
LAYOUT = {
    "hopper": {"joints": [(2, 8), (3, 9), (4, 10)], "pitch": 1, "pitch_rate": 7, "vx": 5, "legs": [[0, 1, 2]]},
    "walker2d": {"joints": [(2, 11), (3, 12), (4, 13), (5, 14), (6, 15), (7, 16)], "pitch": 1, "pitch_rate": 10,
                 "vx": 8, "legs": [[0, 1, 2], [3, 4, 5]]},
}


def base_spec(task):
    t = TASKS[task]
    return {"target": "cpg", "obs_dim": t.obs_dim, "act_dim": t.act_dim, "hidden": 16, "oscillators": [],
            "couplings": [], "bias": {}, "units": []}


def summary(r):
    keys = ("mean_distance_healthy", "median_distance_healthy", "min_distance_healthy", "n_clean_3m", "passes_3m",
            "mean_distance", "mean_return", "frac_full_length", "mean_length", "n_faults")
    return {k: r.get(k) for k in keys}


def save(out: Path, name: str, res: dict, extra: dict = None):
    out.mkdir(parents=True, exist_ok=True)
    res = {**res, **(extra or {})}
    (out / f"{name}.score.json").write_text(json.dumps(res, indent=1))
    print(name, json.dumps(summary(res)), flush=True)
    return res


def dev_score(env, pol, seeds):
    return float(np.mean([run_episode(env, pol, s)["distance_healthy"] for s in seeds]))


def cpg(task, spec):
    return CPGPolicy(task, compile_cpg(spec)[0])


# ---------------------------------------------------------------- search (CEM), shared by sinusoid and tuned CPG

def cem(task, build, x0, sigma0, budget, out: Path, name: str, pop=40, elite=10, seed=0):
    """Cross-entropy method on dev seeds. Returns the best spec picked on PICK_SEEDS among the elites of the last
    generations. Logs every generation; counts every dev episode against the budget."""
    rng = np.random.default_rng(seed)
    env = make_env(task)
    m, s = np.array(x0, float), np.array(sigma0, float)
    used, gen, hall, log = 0, 0, [], []
    while used + pop * len(SEARCH_SEEDS) <= budget - 5 * len(PICK_SEEDS):
        xs = m + s * rng.normal(size=(pop, len(m)))
        fit = np.array([dev_score(env, cpg(task, build(x)), SEARCH_SEEDS) for x in xs])
        used += pop * len(SEARCH_SEEDS)
        idx = np.argsort(-fit)[:elite]
        m = xs[idx].mean(axis=0)
        s = 0.8 * xs[idx].std(axis=0) + 0.2 * s
        hall += [(fit[i], xs[i]) for i in idx[:2]]
        log.append({"gen": gen, "episodes_used": used, "best": float(fit[idx[0]]), "elite_mean": float(fit[idx].mean())})
        print(name, log[-1], flush=True)
        gen += 1
    cands = sorted(hall, key=lambda h: -h[0])[:5]
    picks = [(dev_score(env, cpg(task, build(x)), PICK_SEEDS), x) for _, x in cands]
    used += len(cands) * len(PICK_SEEDS)
    best = max(picks, key=lambda p: p[0])
    out.mkdir(parents=True, exist_ok=True)
    (out / f"{name}.search.json").write_text(json.dumps(
        {"budget": budget, "episodes_used": used, "search_seeds": list(SEARCH_SEEDS), "pick_seeds": list(PICK_SEEDS),
         "log": log, "picks": [{"pick_score": p[0], "x": p[1].tolist()} for p in picks]}, indent=1))
    spec = build(best[1])
    (out / f"{name}.spec.json").write_text(json.dumps(spec, indent=1))
    return spec, used


# ---------------------------------------------------------------- necessity rows

def sinusoid_builder(task):
    n = TASKS[task].act_dim

    def build(x):  # x = [f, (c, s, b) per joint]; open loop: no obs input anywhere
        sp = base_spec(task)
        sp["oscillators"] = [{"name": "o", "freq_hz": float(abs(x[0]) + 0.1), "phase0": 0.0}]
        for j in range(n):
            c, s_, b = x[1 + 3 * j: 4 + 3 * j]
            sp["units"].append({"type": "reflex", "name": f"j{j}", "inputs": {"cos(o)": float(c), "sin(o)": float(s_)},
                                "threshold": 0.0, "sharpness": 1.0, "to": {f"a{j}": 1.0}})
            sp["bias"][f"a{j}"] = float(b)
        return sp
    return build, [2.0] + [0.0] * (3 * n), [1.0] + [0.7] * (3 * n)


def standstill_attempt():
    """Highest-return clean hopper attempt of the earlier arms (the healthy-reward exploit)."""
    best = None
    for d in (MAIN_RESULTS / "attempts").iterdir():
        try:
            meta = json.loads((d / "meta.json").read_text())
            sc = json.loads((d / "score.json").read_text())
        except (OSError, ValueError):
            continue
        if meta.get("task") != "hopper" or meta.get("contaminated") or sc.get("failure") or "mean_return" not in sc:
            continue
        if best is None or sc["mean_return"] > best[0]:
            best = (sc["mean_return"], d, meta["mode"])
    return best


def necessity(task, out: Path):
    save(out, "zero", evaluate(task, zero_policy(task)))
    for s in range(10):
        save(out, f"random_mlp_{s}", evaluate(task, random_policy(task, s)), {"seed": s})
    # fall-forward lunge: the best constant action from {-1, 0, 1}^act_dim on dev seeds
    env, n = make_env(task), TASKS[task].act_dim
    grid = np.array(np.meshgrid(*[[-1.0, 0.0, 1.0]] * n)).reshape(n, -1).T
    lunge = []
    for a in grid:
        sp = base_spec(task)
        sp["bias"] = {f"a{j}": float(a[j]) for j in range(n)}
        lunge.append((dev_score(env, cpg(task, sp), PICK_SEEDS), sp))
    sc, sp = max(lunge, key=lambda t: t[0])
    (out / "lunge.spec.json").write_text(json.dumps(sp, indent=1))
    save(out, "lunge", evaluate(task, cpg(task, sp)), {"dev_score": sc, "dev_episodes": len(grid) * len(PICK_SEEDS)})
    build, x0, s0 = sinusoid_builder(task)
    sp, used = cem(task, build, x0, s0, BUDGET // 2, out, "sinusoid")
    save(out, "sinusoid", evaluate(task, cpg(task, sp)), {"dev_episodes": used})
    if task == "hopper":
        ret, d, mode = standstill_attempt()
        if mode == "controller":
            limit_resources()  # last row: the rlimits stay on for the rest of the process
            pol = PythonController(task, d / "parsed.controller.py")
        else:
            pol = load_weights(task, d / "parsed.weights.json")
        save(out, "standstill_best_return", evaluate(task, pol), {"attempt": d.name, "old_mean_return": ret})


# ---------------------------------------------------------------- random CPG (distribution fixed before scoring)

def random_cpg_spec(task, seed):
    rng = np.random.default_rng(seed)
    t, lay = TASKS[task], LAYOUT[task]
    sp = base_spec(task)
    m = int(rng.integers(1, 5))
    names = [f"o{k}" for k in range(m)]
    for nm in names:
        o = {"name": nm, "freq_hz": float(rng.uniform(0.5, 4.0)), "phase0": float(rng.uniform(0, 2 * math.pi))}
        if rng.random() < 0.5:
            o["feedback"] = {f"obs[{int(rng.integers(t.obs_dim))}]": float(rng.normal())}
        sp["oscillators"].append(o)
    for a in names:
        for b in names:
            if a != b and rng.random() < 0.5:
                sp["couplings"].append({"from": a, "to": b, "weight": float(rng.uniform(0, 5)),
                                        "phase_lag": float(rng.uniform(-math.pi, math.pi))})
    for j in range(t.act_dim):
        nm = names[int(rng.integers(m))]
        ins = {f"cos({nm})": float(rng.uniform(-1, 1)), f"sin({nm})": float(rng.uniform(-1, 1))}
        if rng.random() < 0.5:
            ins[f"obs[{int(rng.integers(t.obs_dim))}]"] = float(rng.normal())
        sp["units"].append({"type": "linear", "name": f"j{j}", "inputs": ins, "range": 3.0, "tol": 0.05,
                            "to": {f"a{j}": 1.0}})
        sp["bias"][f"a{j}"] = float(rng.uniform(-0.3, 0.3))
    return sp


def randcpg(task, out: Path, n=50):
    for s in range(n):
        sp = random_cpg_spec(task, s)
        (out / "random_cpg").mkdir(parents=True, exist_ok=True)
        (out / "random_cpg" / f"{s:02d}.spec.json").write_text(json.dumps(sp, indent=1))
        save(out / "random_cpg", f"{s:02d}", evaluate(task, cpg(task, sp)), {"seed": s})


# ---------------------------------------------------------------- tuned CPG (headroom)

def tuned_builder(task):
    """Hand-designed structure: one oscillator per leg (antiphase-coupled for walker2d, legs share coefficients by
    mirror symmetry); each joint torque = tanh(rhythm + torso pitch/rate feedback + own joint angle/rate damping
    + forward-speed term on the thigh) + bias."""
    lay = LAYOUT[task]
    legs = lay["legs"]

    def build(x):  # x = [f, w, then per joint-in-leg: c, s, kp, kd, kq, kqd, kv, b]
        sp = base_spec(task)
        names = [f"leg{i}" for i in range(len(legs))]
        for i, nm in enumerate(names):
            sp["oscillators"].append({"name": nm, "freq_hz": float(abs(x[0]) + 0.1), "phase0": math.pi * i})
        if len(names) == 2:
            w = float(abs(x[1]))
            sp["couplings"] = [{"from": names[0], "to": names[1], "weight": w, "phase_lag": math.pi},
                               {"from": names[1], "to": names[0], "weight": w, "phase_lag": math.pi}]
        for i, leg in enumerate(legs):
            for k, j in enumerate(leg):
                c, s_, kp, kd, kq, kqd, kv, b = x[2 + 8 * k: 10 + 8 * k]
                qa, qv = lay["joints"][j]
                ins = {f"cos({names[i]})": c, f"sin({names[i]})": s_, f"obs[{lay['pitch']}]": kp,
                       f"obs[{lay['pitch_rate']}]": kd, f"obs[{qa}]": kq, f"obs[{qv}]": kqd}
                if k == 0:
                    ins[f"obs[{lay['vx']}]"] = kv
                sp["units"].append({"type": "reflex", "name": f"j{j}",
                                    "inputs": {a: float(v) for a, v in ins.items()},
                                    "threshold": 0.0, "sharpness": 1.0, "to": {f"a{j}": 1.0}})
                sp["bias"][f"a{j}"] = float(b)
        return sp
    n = len(legs[0])
    # hand start: rhythm on every joint, torso feedback on the thigh with the sign that pitches the torso back on a
    # forward lean (negative thigh torque for positive pitch), mild joint damping
    x0 = [2.0 if task == "hopper" else 1.0, 3.0]
    s0 = [0.7, 2.0]
    for k in range(n):
        x0 += [0.5, 0.5, -2.0 if k == 0 else 0.0, -0.3 if k == 0 else 0.0, 0.0, -0.1, 0.0, 0.0]
        s0 += [0.5, 0.5, 1.5, 0.3, 1.0, 0.1, 0.3, 0.3]
    return build, x0, s0


def tuned(task, out: Path):
    build, x0, s0 = tuned_builder(task)
    sp, used = cem(task, build, x0, s0, BUDGET, out, "tuned_cpg")
    save(out, "tuned_cpg", evaluate(task, cpg(task, sp)), {"dev_episodes": used, "budget": BUDGET})


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=("necessity", "randcpg", "tuned"))
    ap.add_argument("task", choices=("hopper", "walker2d"))
    ap.add_argument("--out", default=str(MAIN_RESULTS / "cpg" / "baselines"))
    a = ap.parse_args()
    out = Path(a.out) / a.task
    t0 = time.time()
    {"necessity": necessity, "randcpg": randcpg, "tuned": tuned}[a.cmd](a.task, out)
    print(f"done {a.cmd} {a.task} in {time.time() - t0:.0f} s", flush=True)


if __name__ == "__main__":
    main()
