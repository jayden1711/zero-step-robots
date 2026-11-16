"""Warm-start value of zero-step designs (docs/prereg-followup-draft.md). No LLM is called anywhere in this file.

    python scripts/warmstart.py list  <task>                          # start-set sizes and ids, runs nothing
    python scripts/warmstart.py run   <task> H                        # Stage 0: 10 hand-start calibration runs
    python scripts/warmstart.py run   <task> LPR [--shard k/n]        # Stage 1/3: L_i, P_i, R_i interleaved by index i
    python scripts/warmstart.py run   <task> L|P|R [--only ID]        # one set, or one start
    python scripts/warmstart.py headroom walker2d --seed S            # Stage B: tuned-CPG CEM, 50,000 dev episodes

Start sets (prereg section 3): L = the 60 no-feedback CPG-track specs + the 20 feedback round-0 specs per task;
P = each L spec with its numbers permuted within kind and gains sign-flipped; R = random_cpg_spec seeds 1000..1079;
H = the unsearched hand start of tuned_builder, optimiser seeds 0..9.
Search (prereg section 4): rs_proposer's (1+1) hill climber, unchanged logic, 500 designs; the best-so-far design at
checkpoints 6, 25, 50, 100, 200, 500 is scored once on the held-out seeds. Held-out scores never feed the search.
One JSON per run in <results>/warmstart/<task>/<set>/<id>.json, written when the run completes (resumable: existing
files are skipped). Run through ~/projects/bin/sim-run (one process, one thread).
"""
import argparse
import copy
import hashlib
import json
import sys
import time
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))

DESIGNS = 500
CHECKPOINTS = (6, 25, 50, 100, 200, 500)
R_SEEDS = range(1000, 1080)
H_SEEDS = range(0, 10)
MAIN_RESULTS = Path("/home/jayden/projects/zero-step-robots/results")
SETS = ("L", "P", "R", "H")


def sha_seed(s: str) -> int:
    """First 8 hex digits of SHA-256, as rs_proposer.py seeds its RS-from-LLM runs."""
    return int(hashlib.sha256(s.encode()).hexdigest()[:8], 16)


# ---------------------------------------------------------------- start sets

def l_starts(task, results: Path):
    """[(start_id, spec)]: no-feedback track specs, then feedback round-0 specs, each sorted by id."""
    att = results / "attempts"
    nf = sorted(att.glob(f"cpg-claude-*_{task}_H?_cpgspec_[0-9][0-9]/parsed.spec.json"))
    r0 = sorted(att.glob(f"fb-claude-*_{task}_H2_[0-9][0-9]/r0/parsed.spec.json"))
    out = [(p.parent.name, json.loads(p.read_text())) for p in nf]
    out += [(p.parent.parent.name, json.loads(p.read_text())) for p in r0]
    return out


def permute(spec, seed):
    """The P control (prereg section 3): keep structure; permute numbers among slots of the same kind within this spec;
    then flip the sign of every gain with probability 0.5. Fixed fields (dims, names, range, tol, targets) untouched."""
    sp = copy.deepcopy(spec)
    rng = np.random.default_rng(seed)
    kinds = {k: [] for k in "abcdefg"}  # each slot = (container, key)
    for o in sp.get("oscillators", []):
        kinds["a"].append((o, "freq_hz"))
        if "phase0" in o:
            kinds["b"].append((o, "phase0"))
        for k in sorted(o.get("feedback") or {}):
            kinds["d"].append((o["feedback"], k))
    for c in sp.get("couplings", []):
        if "phase_lag" in c:
            kinds["b"].append((c, "phase_lag"))
        if "weight" in c:
            kinds["c"].append((c, "weight"))
    for u in sp.get("units", []):
        for k in sorted(u.get("inputs") or {}):
            kinds["d"].append((u["inputs"], k))
        for k in sorted(u.get("to") or {}):
            kinds["d"].append((u["to"], k))
        if u.get("type") == "reflex":
            if "threshold" in u:
                kinds["f"].append((u, "threshold"))
            if "sharpness" in u:  # its own kind: the compiler requires sharpness > 0
                kinds["g"].append((u, "sharpness"))
    for k in sorted(sp.get("bias") or {}):
        kinds["e"].append((sp["bias"], k))
    for kind in "abcdefg":
        slots = kinds[kind]
        vals = [float(c[k]) for c, k in slots]
        for (c, k), i in zip(slots, rng.permutation(len(slots))):
            c[k] = vals[i]
    for c, k in kinds["d"]:
        if rng.random() < 0.5:
            c[k] = -c[k]
    return sp


def p_starts(task, results: Path):
    return [(f"{aid}__perm", permute(sp, sha_seed(f"{aid}/perm"))) for aid, sp in l_starts(task, results)]


def r_starts(task):
    from cpg_baselines import random_cpg_spec
    return [(f"rand{s}", random_cpg_spec(task, s)) for s in R_SEEDS]


def h_starts(task):
    from cpg_baselines import tuned_builder
    build, x0, _ = tuned_builder(task)
    return [(f"hand_s{k}", build(x0)) for k in H_SEEDS]


def starts(task, which, results: Path):
    return {"L": lambda: l_starts(task, results), "P": lambda: p_starts(task, results),
            "R": lambda: r_starts(task), "H": lambda: h_starts(task)}[which]()


def run_seed(which, start_id):
    if which == "H":
        return int(start_id.rsplit("_s", 1)[1])
    return sha_seed(start_id)  # L, P, R: SHA-256 of the start id (the permutation itself uses "<aid>/perm")


# ---------------------------------------------------------------- the run

def run(task, which, start_id, spec0, seed, out: Path, designs=DESIGNS, checkpoints=CHECKPOINTS):
    from rs_proposer import dev_score, perturb
    from circuitc import compile_cpg
    from zsr.cpg import CPGPolicy
    from zsr.harness import evaluate

    t0 = time.time()
    rng = np.random.default_rng(seed)
    best, (best_s, data) = spec0, dev_score(task, spec0)
    hist = [None if best_s == -np.inf else round(best_s, 4)]
    acc = [True]
    cps, scored = [], {}
    for k in range(1, designs + 1):
        if k in checkpoints:  # best-so-far after k designs (indices 0..k-1); rs_proposer's final = checkpoint 6
            key = json.dumps(best, sort_keys=True)
            if key not in scored:
                if best_s == -np.inf:
                    scored[key] = {"failure": "no design compiled"}
                else:
                    r = evaluate(task, CPGPolicy(task, compile_cpg(best)[0]))
                    scored[key] = {kk: v for kk, v in r.items() if kk != "episodes"}
            cps.append({"designs": k, "dev_mean_d": None if best_s == -np.inf else round(best_s, 4), "spec": best,
                        "heldout": scored[key]})
        if k == designs:
            break
        cand = perturb(copy.deepcopy(best), rng)
        s, _ = dev_score(task, cand)
        a = bool(s > best_s)
        if a:
            best, best_s = cand, s
        hist.append(None if s == -np.inf else round(s, 4))
        acc.append(a)
    first_pass = next((c["designs"] for c in cps if c["heldout"].get("passes_3m")), None)
    res = {"task": task, "set": which, "start_id": start_id, "seed": seed, "designs": designs,
           "checkpoints": cps, "T": first_pass, "censored": first_pass is None,
           "dev_history": hist, "accepted": acc, "wall_s": round(time.time() - t0, 1), "start_spec": spec0}
    out.parent.mkdir(parents=True, exist_ok=True)
    tmp = out.with_suffix(".tmp")
    tmp.write_text(json.dumps(res, indent=1))
    tmp.replace(out)
    print(f"{task} {which} {start_id}: T={first_pass} final held-out d="
          f"{cps[-1]['heldout'].get('mean_distance_healthy')} wall {res['wall_s']} s", flush=True)
    return res


def plan(task, sets, results: Path):
    """Ordered [(set, start_id, spec)]. For 'LPR', interleave L_i, P_i, R_i by index (prereg section 6)."""
    if sets == "LPR":
        lists = [starts(task, w, results) for w in "LPR"]
        n = max(len(x) for x in lists)
        return [(w, *lst[i]) for i in range(n) for w, lst in zip("LPR", lists) if i < len(lst)]
    return [(sets, *x) for x in starts(task, sets, results)]


HEADROOM_BUDGET = 50_000
HEADROOM_SEEDS = (0, 1, 2)


def headroom(task, seed, results: Path):
    """Stage B (prereg section 6): the track's tuned-CPG search (same hand structure, search and pick seeds), budget
    raised from 20,000 to 50,000 dev episodes, CEM seed `seed`; the result is scored once on the held-out seeds."""
    from cpg_baselines import cem, cpg, save, tuned_builder
    from zsr.harness import evaluate
    assert seed in HEADROOM_SEEDS
    out = results / "warmstart" / task / "headroom"
    name = f"tuned_cpg_50k_seed{seed}"
    if (out / f"{name}.score.json").exists():
        return
    build, x0, s0 = tuned_builder(task)
    sp, used = cem(task, build, x0, s0, HEADROOM_BUDGET, out, name, seed=seed)
    save(out, name, evaluate(task, cpg(task, sp)), {"dev_episodes": used, "budget": HEADROOM_BUDGET, "cem_seed": seed})


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=("list", "run", "headroom"))
    ap.add_argument("task", choices=("hopper", "walker2d"))
    ap.add_argument("sets", nargs="?", default="LPR", choices=("LPR",) + SETS)
    ap.add_argument("--results", type=Path, default=MAIN_RESULTS)
    ap.add_argument("--shard", default="0/1", help="k/n: run every n-th planned start, offset k")
    ap.add_argument("--only")
    ap.add_argument("--seed", type=int, default=0)
    a = ap.parse_args()
    if a.cmd == "headroom":
        return headroom(a.task, a.seed, a.results)
    items = plan(a.task, a.sets, a.results)
    if a.cmd == "list":
        for w in SETS:
            print(w, sum(1 for x in items if x[0] == w))
        for w, sid, _ in items:
            print(w, sid)
        return
    k, n = (int(x) for x in a.shard.split("/"))
    base = a.results / "warmstart" / a.task
    for i, (w, sid, spec) in enumerate(items):
        if i % n != k or (a.only and sid != a.only):
            continue
        out = base / w / f"{sid}.json"
        if out.exists():
            continue
        run(a.task, w, sid, spec, run_seed(w, sid), out)


if __name__ == "__main__":
    main()
