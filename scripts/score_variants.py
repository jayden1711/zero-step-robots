"""Score every arm on the modified-physics variants (zsr/variants.py) with the same harness and seeds as the stock
scores. Sources: baselines (zero, random x10, reference controller, cartpole LQR, PPO), every LLM attempt that has a
parsed weight/controller file, and compiled circuits. Writes RESULTS/variants/<source>__<task>__<variant>.score.json;
existing files are skipped (resumable). Run through sim-run, in chunks: --max-seconds N.

usage: python scripts/score_variants.py RESULTS [--max-seconds 500] [--episodes 100]
"""
import argparse
import glob
import json
import time
from pathlib import Path

from zsr.harness import PythonController, evaluate, limit_resources, sha256
from zsr.policy import load_weights, random_policy, zero_policy
from zsr.variants import variant_names


def sources(R: Path):
    """yield (source_name, task, kind, path_or_None, builder, matched_variant)"""
    for task in ("cartpole", "hopper"):
        yield f"zero", task, "weights", None, (lambda t=task: zero_policy(t)), None
        for s in range(10):
            yield f"random_seed{s}", task, "weights", None, (lambda t=task, s=s: random_policy(t, s)), None
        ref = Path(f"controllers/{task}_reference.py")
        yield "python_reference", task, "controller", ref, (lambda t=task, r=ref: PythonController(t, r)), None
        for w in sorted(glob.glob(str(R / f"baselines/ppo/{task}_ppo_seed*.weights.json"))):
            yield Path(w).name.replace(".weights.json", ""), task, "weights", Path(w), \
                (lambda t=task, w=w: load_weights(t, w)), None
    for p in sorted(glob.glob(str(R / "baselines/lqr/cartpole_lqr_*.py"))):
        v = Path(p).stem.replace("cartpole_lqr_", "")
        yield f"lqr_{v}", "cartpole", "controller", Path(p), (lambda p=p: PythonController("cartpole", p)), \
            (None if v == "stock" else v)
    for d in sorted(glob.glob(str(R / "attempts/*/"))):
        d = Path(d)
        if not (d / "score.json").exists():
            continue
        m = json.loads((d / "meta.json").read_text())
        if m["mode"] == "weights" and (d / "parsed.weights.json").exists():
            if json.loads((d / "score.json").read_text()).get("failure"):
                continue  # unparsable: nothing to score; the stock score.json already records the failure
            yield m["id"], m["task"], "weights", d / "parsed.weights.json", \
                (lambda t=m["task"], f=d / "parsed.weights.json": load_weights(t, f)), None
        elif m["mode"] == "controller" and (d / "parsed.controller.py").exists():
            yield m["id"], m["task"], "controller", d / "parsed.controller.py", \
                (lambda t=m["task"], f=d / "parsed.controller.py": PythonController(t, f)), None
    for w in sorted(glob.glob(str(R / "circuit/*/weights.json"))):
        task = Path(w).parent.name.split("_")[0]
        yield "circuit_" + Path(w).parent.name, task, "weights", Path(w), \
            (lambda t=task, w=w: load_weights(t, w)), None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("results")
    ap.add_argument("--max-seconds", type=float, default=0)
    ap.add_argument("--episodes", type=int, default=100)
    a = ap.parse_args()
    R = Path(a.results)
    out = R / "variants"
    out.mkdir(exist_ok=True)
    limit_resources(cpu_s=3600, mem_gb=4)
    t0, done, skipped = time.time(), 0, 0
    for name, task, kind, path, build, matched in sources(R):
        for v in variant_names(task):
            if matched is not None and matched != v:
                continue
            f = out / f"{name}__{task}__{v}.score.json"
            if f.exists():
                skipped += 1
                continue
            if a.max_seconds and time.time() - t0 > a.max_seconds:
                print(f"budget reached; done {done}, skipped {skipped}; rerun to resume")
                return
            try:
                res = evaluate(task, build(), a.episodes, variant=v)
            except Exception as e:  # a controller that fails to load is recorded, not dropped
                res = {"task": task, "variant": v, "load_error": f"{type(e).__name__}: {e}"}
            res.update({"source": name, "kind": kind, "source_path": str(path) if path else None,
                        "source_sha256": sha256(path) if path else None})
            f.write_text(json.dumps(res, indent=1))
            done += 1
    print(f"complete; done {done}, skipped {skipped}")


if __name__ == "__main__":
    main()
