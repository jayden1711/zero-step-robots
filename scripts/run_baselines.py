"""Score the non-learning arms (zero, random x10 seeds, reference Python controller) on both tasks.

Usage: sim-run python scripts/run_baselines.py [--out results/baselines]   (run from the repo root)
"""
import argparse
import json
from pathlib import Path

from zsr.harness import PythonController, evaluate, sha256
from zsr.policy import random_policy, zero_policy

RANDOM_SEEDS = range(10)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="results/baselines")
    ap.add_argument("--episodes", type=int, default=100)
    a = ap.parse_args()
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    for task in ("cartpole", "hopper"):
        arms = {"zero": [("zero", zero_policy(task), None)]}
        arms["random"] = [(f"random_seed{s}", random_policy(task, s), s) for s in RANDOM_SEEDS]
        ref = f"controllers/{task}_reference.py"
        arms["python_reference"] = [("python_reference", PythonController(task, ref), None)]
        lqr = out / "lqr" / "cartpole_lqr_stock.py"  # written by scripts/make_lqr.py
        if task == "cartpole" and lqr.exists():
            arms["lqr"] = [("lqr_stock", PythonController(task, lqr), None)]
        for arm, items in arms.items():
            for name, pol, seed in items:
                res = evaluate(task, pol, a.episodes)
                res.update({"arm": arm, "arm_seed": seed})
                if arm == "python_reference":
                    res["source_sha256"] = sha256(ref)
                if arm == "lqr":
                    res["source_sha256"] = sha256(lqr)
                (out / f"{task}_{name}.score.json").write_text(json.dumps(res, indent=1))
                print(f"{task:9s} {name:18s} mean_return={res['mean_return']:9.2f} frac_full={res['frac_full_length']:.2f}",
                      flush=True)


if __name__ == "__main__":
    main()
