"""Random-search proposer baselines with the feedback arm's budget (docs/prereg-2026-11-10-cpg-feedback.md s7).

    python scripts/rs_proposer.py random  <task>                 # RS-random: 10 runs, design 0 = random CPG (seeds 100..109)
    python scripts/rs_proposer.py fromllm <task> --model M       # RS-from-LLM: design 0 = each fb attempt's round-0 spec

6 designs per run; each later design perturbs every number of the best design so far (Gaussian, sd = 0.3*|v| + 0.1;
names, structure, dims and declared range/tol kept) and replaces it if its dev mean d (seeds 0..9, the same summary code
as the feedback arm) is higher. The final best design is scored once on the held-out scoring seeds.
Run through ~/projects/bin/sim-run. This is code search by construction: a baseline, never an LLM arm.
"""
import argparse
import copy
import hashlib
import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))
from circuitc import compile_cpg  # noqa: E402
from cpg_baselines import random_cpg_spec  # noqa: E402
from zsr.cpg import CPGPolicy  # noqa: E402
from zsr.feedback import summarize  # noqa: E402
from zsr.harness import evaluate  # noqa: E402

DESIGNS = 6
FIXED = {"obs_dim", "act_dim", "hidden", "range", "tol"}
RES = Path("/home/jayden/projects/zero-step-robots/results")


def perturb(x, rng, key=None):
    if isinstance(x, dict):
        return {k: (v if k in FIXED else perturb(v, rng, k)) for k, v in x.items()}
    if isinstance(x, list):
        return [perturb(v, rng, key) for v in x]
    if isinstance(x, (int, float)) and not isinstance(x, bool):
        return float(x + rng.normal(0, 0.3 * abs(x) + 0.1))
    return x


def dev_score(task, spec):
    _, data = summarize(task, spec)
    return -np.inf if "error" in data else data["mean_d"], data


def run(task, spec0, seed, out: Path):
    rng = np.random.default_rng(seed)
    best, (best_s, data) = spec0, dev_score(task, spec0)
    hist = [{"design": 0, "dev_mean_d": None if best_s == -np.inf else best_s, "accepted": True,
             "error": data.get("error")}]
    for k in range(1, DESIGNS):
        cand = perturb(copy.deepcopy(best), rng)
        s, data = dev_score(task, cand)
        acc = s > best_s
        if acc:
            best, best_s = cand, s
        hist.append({"design": k, "dev_mean_d": None if s == -np.inf else s, "accepted": bool(acc),
                     "error": data.get("error")})
    res = {"seed": seed, "history": hist, "final_spec": best}
    if best_s == -np.inf:
        res["score"] = {"failure": "no design compiled"}
    else:
        r = evaluate(task, CPGPolicy(task, compile_cpg(best)[0]))
        res["score"] = {k: v for k, v in r.items() if k != "episodes"}
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(res, indent=1))
    sc = res["score"]
    print(out.name, "final held-out mean d:", sc.get("mean_distance_healthy", sc.get("failure")), flush=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("mode", choices=("random", "fromllm"))
    ap.add_argument("task", choices=("hopper", "walker2d"))
    ap.add_argument("--model")
    ap.add_argument("--level", default="H2")
    a = ap.parse_args()
    base = RES / "cpg_feedback" / "rs" / a.task
    if a.mode == "random":
        for s in range(100, 110):
            out = base / "random" / f"{s}.json"
            if not out.exists():
                run(a.task, random_cpg_spec(a.task, s), s, out)
    else:
        for i in range(10):
            aid = f"fb-{a.model}_{a.task}_{a.level}_{i:02d}"
            f = RES / "attempts" / aid / "r0" / "parsed.spec.json"
            out = base / f"fromllm_{a.model}" / f"{aid}.json"
            if out.exists() or not f.exists():
                continue
            seed = int(hashlib.sha256(aid.encode()).hexdigest()[:8], 16)
            run(a.task, json.loads(f.read_text()), seed, out)


if __name__ == "__main__":
    main()
