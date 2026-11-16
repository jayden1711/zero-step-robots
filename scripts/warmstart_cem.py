"""CEM replication of the hopper warm-start result (docs/addendum-2026-11-16-warmstart-robustness.md). No LLM anywhere.

    python scripts/warmstart_cem.py run hopper H                  # calibration (10 hand-start runs)
    python scripts/warmstart_cem.py run hopper LPR [--shard k/n]  # L_i, P_i, R_i interleaved by index
Starts: exactly warmstart.py's sets. Search vector: every number rs_proposer.perturb changes, in its traversal order.
CEM: diagonal Gaussian, population 20, 5 elites, sd0 = 0.3|v| + 0.1, mean <- elite mean, sd <- 0.8 elite sd + 0.2 sd;
generation 1 = the start + 19 samples; 25 generations = 500 designs (5,000 practice episodes, as the hill climber).
Best-so-far (practice mean d) scored on the held-out seeds at checkpoints 20, 100, 200, 500. Run through sim-run.
One JSON per run in <results>/warmstart_cem/<task>/<set>/<id>.json (resumable).
"""
import argparse
import copy
import json
import sys
import time
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))
import warmstart as ws  # noqa: E402

POP, ELITE, GENS = 20, 5, 25
DESIGNS = POP * GENS
CHECKPOINTS = (20, 100, 200, 500)
FIXED = {"obs_dim", "act_dim", "hidden", "range", "tol"}  # = rs_proposer.FIXED


def slots(x, out=None, key=None):
    """(container, key) of every number rs_proposer.perturb changes, in its traversal order."""
    out = [] if out is None else out
    if isinstance(x, dict):
        for k, v in x.items():
            if k in FIXED:
                continue
            if isinstance(v, (int, float)) and not isinstance(v, bool):
                out.append((x, k))
            else:
                slots(v, out, k)
    elif isinstance(x, list):
        for i, v in enumerate(x):
            if isinstance(v, (int, float)) and not isinstance(v, bool):
                out.append((x, i))
            else:
                slots(v, out, key)
    return out


def vector(spec):
    return np.array([float(c[k]) for c, k in slots(spec)])


def with_vector(spec, v):
    sp = copy.deepcopy(spec)
    for (c, k), x in zip(slots(sp), v):
        c[k] = float(x)
    return sp


def run(task, which, start_id, spec0, seed, out: Path, gens=GENS, checkpoints=CHECKPOINTS):
    from rs_proposer import dev_score
    from circuitc import compile_cpg
    from zsr.cpg import CPGPolicy
    from zsr.harness import evaluate

    t0 = time.time()
    rng = np.random.default_rng(seed)
    x0 = vector(spec0)
    m, s = x0.copy(), 0.3 * np.abs(x0) + 0.1
    best, best_s, n, hist, cps, scored = spec0, -np.inf, 0, [], [], {}
    for g in range(gens):
        xs = m + s * rng.normal(size=(POP, len(m)))
        if g == 0:
            xs[0] = x0  # generation 1 = the start itself + 19 samples
        fit = []
        for x in xs:
            sp = with_vector(spec0, x)
            f, _ = dev_score(task, sp)
            n += 1
            fit.append(f)
            hist.append(None if f == -np.inf else round(f, 4))
            if f > best_s:
                best, best_s = sp, f
        fit = np.array(fit)
        idx = np.argsort(-fit, kind="stable")[:ELITE]
        m = xs[idx].mean(axis=0)
        s = 0.8 * xs[idx].std(axis=0) + 0.2 * s
        if n in checkpoints:
            key = json.dumps(best, sort_keys=True)
            if key not in scored:
                if best_s == -np.inf:
                    scored[key] = {"failure": "no design compiled"}
                else:
                    r = evaluate(task, CPGPolicy(task, compile_cpg(best)[0]))
                    scored[key] = {kk: v for kk, v in r.items() if kk != "episodes"}
            cps.append({"designs": n, "dev_mean_d": None if best_s == -np.inf else round(best_s, 4), "spec": best,
                        "heldout": scored[key]})
    first = next((c["designs"] for c in cps if c["heldout"].get("passes_3m")), None)
    res = {"task": task, "set": which, "start_id": start_id, "seed": seed, "optimiser": "cem", "designs": n,
           "checkpoints": cps, "T": first, "censored": first is None, "dev_history": hist,
           "wall_s": round(time.time() - t0, 1), "start_spec": spec0}
    out.parent.mkdir(parents=True, exist_ok=True)
    tmp = out.with_suffix(".tmp")
    tmp.write_text(json.dumps(res, indent=1))
    tmp.replace(out)
    print(f"cem {task} {which} {start_id}: T={first} final held-out d="
          f"{cps[-1]['heldout'].get('mean_distance_healthy') if cps else None} wall {res['wall_s']} s", flush=True)
    return res


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=("list", "run"))
    ap.add_argument("task", choices=("hopper",))
    ap.add_argument("sets", nargs="?", default="LPR", choices=("LPR", "L", "P", "R", "H"))
    ap.add_argument("--results", type=Path, default=ws.MAIN_RESULTS)
    ap.add_argument("--shard", default="0/1")
    a = ap.parse_args()
    items = ws.plan(a.task, a.sets, a.results)
    if a.cmd == "list":
        for w, sid, _ in items:
            print(w, sid)
        return
    k, nsh = (int(x) for x in a.shard.split("/"))
    base = a.results / "warmstart_cem" / a.task
    for i, (w, sid, spec) in enumerate(items):
        if i % nsh != k:
            continue
        out = base / w / f"{sid}.json"
        if not out.exists():
            run(a.task, w, sid, spec, ws.sha_seed(f"cem/{sid}"), out)


if __name__ == "__main__":
    main()
