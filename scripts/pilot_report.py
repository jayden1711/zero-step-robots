"""Aggregate every scored attempt (all of them, failures included) into RESULTS/pilot_report.md. Local only.
Tables: per model x mode x task x arm on the stock environment, and on each modified-physics variant, with the
baselines (including the do-nothing zero policy for hopper) in every table. Reads attempts/*/score.json,
baselines/*.score.json and variants/*.score.json. usage: python scripts/pilot_report.py RESULTS_DIR"""
import collections
import glob
import json
import statistics as st
import sys
from pathlib import Path

R = Path(sys.argv[1])
FULL = 900.0  # an episode-mean return at or above this is "survives (nearly) the whole 1000 steps"


def load(pattern):
    return [json.load(open(f)) for f in sorted(glob.glob(str(R / pattern)))]


def f1(x):
    return "-" if x is None else f"{x:.1f}"


def stats(vals):
    ok = [v for v in vals if v is not None]
    if not ok:
        return "-", "-", "-", "-", "-"
    q = st.quantiles(ok, n=4) if len(ok) > 1 else [ok[0]] * 3
    return f1(st.mean(ok)), f1(st.median(ok)), f"{f1(q[0])}-{f1(q[2])}", f1(min(ok)), f1(max(ok))


meta = {}
for f in sorted(glob.glob(str(R / "attempts/*/meta.json"))):
    m = json.load(open(f))
    meta[m["id"]] = m
stock = {}
for f in sorted(glob.glob(str(R / "attempts/*/score.json"))):
    s = json.load(open(f))
    stock[s["id"]] = s
var = collections.defaultdict(dict)  # source -> variant -> score
for s in load("variants/*.score.json"):
    var[s["source"]][s["variant"]] = s
base = {}
for f in sorted(glob.glob(str(R / "baselines/*.score.json")) + glob.glob(str(R / "baselines/ppo/*.score.json"))):
    base[Path(f).name.replace(".score.json", "")] = json.load(open(f))

HOPPER_DT = 0.008  # Hopper-v5 env.dt (frame_skip 4 x 0.002 s)
MOVES_M = 1.0      # "travels forward" = mean forward distance >= this many metres per episode (fixed before looking)


def hop_note(s):
    d, n = s.get("mean_distance"), s.get("mean_length")
    return None if d is None or not n else (d, d / (n * HOPPER_DT))


cells = collections.defaultdict(list)
for i, m in meta.items():
    if i in stock:
        cells[(m["task"], m["model"], m["mode"], m["arm"])].append(i)

L = ["# Report (local, not for git)", "",
     "Simulation only (MuJoCo via Gymnasium). Score = mean return over 100 episodes, reset seeds 10000..10099.",
     "Every attempt is listed, failures (unparsable/invalid replies) included and counted as failures, not dropped.",
     f"`full` = attempts whose mean return is >= {FULL:.0f}. On hopper a return near 1000 can mean standing without "
     "falling for 1000 steps (reward is 1/step alive + forward speed): see the distance columns. For hopper, the "
     f"per-attempt cells read `return/forward-distance`; `n moving` counts attempts with mean forward distance >= {MOVES_M:.0f} m "
     "per episode (threshold fixed in the script, not tuned). Forward speed = distance / (mean steps x 0.008 s).", ""]


def table(task, variant):
    rows = []
    for (t, model, mode, arm), ids in sorted(cells.items()):
        if t != task:
            continue
        sc, dist, spd, pa = [], [], [], []
        for i in ids:
            s = stock[i] if variant is None else var.get(i, {}).get(variant)
            if s is None:
                sc.append(None)
                dist.append(None)
                pa.append("F")
                continue
            ok = not s.get("failure") and not s.get("load_error")
            sc.append(s.get("mean_return") if ok else None)
            dist.append(s.get("mean_distance"))
            h = hop_note(s) if ok else None
            if h:
                spd.append(h[1])
            pa.append(f"{s['mean_return']:.0f}/{h[0]:.1f}m" if h and ok else "F")
        nfail = sum(1 for i in ids if stock[i].get("failure"))
        mean, med, iqr, lo, hi = stats(sc)
        full = sum(1 for x in sc if x is not None and x >= FULL)
        d = [x for x in dist if x is not None]
        if task == "hopper":
            mv = sum(1 for x in d if x >= MOVES_M)
            rows.append(f"| {model} | {mode} | {arm} | {len(ids)} | {nfail} | {full} | {mean} | {med} | {iqr} | {lo} | {hi} | "
                        f"{f1(st.median(d)) if d else '-'} | {f1(st.median(spd)) if spd else '-'} | {mv} | {', '.join(pa)} |")
        else:
            rows.append(f"| {model} | {mode} | {arm} | {len(ids)} | {nfail} | {full} | {mean} | {med} | {iqr} | {lo} | {hi} | "
                        f"{', '.join('F' if x is None else f'{x:.0f}' for x in sc)} |")
    return rows


HDR = ["| model | mode | arm | n | unparsable | full | mean | median | IQR | min | max | per-attempt |",
       "|---|---|---|---|---|---|---|---|---|---|---|---|"]
HDR_H = ["| model | mode | arm | n | unparsable | full | mean return | median return | IQR | min | max | median fwd distance (m) | "
         f"median fwd speed (m/s) | n moving (dist >= {MOVES_M:.0f} m) | per-attempt return/distance |",
         "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|"]


def brow(task, label, vals, ss):
    """Baseline row; ss = list of score dicts (same order as vals)."""
    mean, med, iqr, lo, hi = stats(vals)
    full = sum(1 for x in vals if x >= FULL)
    if task == "hopper":
        hn = [hop_note(x) for x in ss]
        d = [h[0] for h in hn if h]
        sp = [h[1] for h in hn if h]
        return (f"| baseline: {label} | - | - | {len(vals)} | 0 | {full} | {mean} | {med} | {iqr} | {lo} | {hi} | "
                f"{f1(st.median(d)) if d else '-'} | {f1(st.median(sp)) if sp else '-'} | {sum(1 for x in d if x >= MOVES_M)} | "
                f"{', '.join(f'{v:.0f}/{h[0]:.1f}m' for v, h in zip(vals, hn) if h)} |")
    return (f"| baseline: {label} | - | - | {len(vals)} | 0 | {full} | {mean} | {med} | {iqr} | {lo} | {hi} | "
            f"{', '.join(f'{x:.0f}' for x in vals)} |")


def baseline_rows(task, variant):
    rows = []
    groups = collections.defaultdict(list)
    for name, s in base.items():
        if not name.startswith(task + "_"):
            continue
        g = name[len(task) + 1:]
        g = "random (10 seeds)" if g.startswith("random") else "PPO (3 seeds)" if g.startswith("ppo") else g
        if g == "zero":
            g = "zero weights (do nothing)"
        groups[g].append(name)
    for g, names in sorted(groups.items()):
        vals, ss = [], []
        for n in names:
            src = n if n.startswith(task + "_ppo") else n.replace(task + "_", "", 1)
            s = base[n] if variant is None else var.get(src, {}).get(variant)
            if s is not None:
                vals.append(s.get("mean_return"))
                ss.append(s)
        if vals:
            rows.append(brow(task, g, vals, ss))
    if variant is not None and task == "cartpole":
        s = var.get("lqr_" + variant, {}).get(variant)
        if s:
            rows.append(brow(task, "LQR matched to this variant", [s["mean_return"]], [s]))
    c = R / "circuit" / f"{task}_{'pd' if task == 'cartpole' else 'pd_hold'}" / "score.json"
    s = json.load(open(c)) if variant is None and c.exists() else var.get(f"circuit_{c.parent.name}", {}).get(variant)
    if s:
        rows.append(brow(task, "compiler fixture (author-written spec, NOT an LLM)", [s["mean_return"]], [s]))
    return rows


from zsr.variants import variant_names  # noqa: E402

for task in ("cartpole", "hopper"):
    for variant in [None] + variant_names(task):
        L += [f"## {task}: {'stock environment' if variant is None else 'variant ' + variant}", ""] + (HDR_H if task == "hopper" else HDR)
        L += table(task, variant) + baseline_rows(task, variant) + [""]

L += ["## Failures (unparsable or invalid replies)", ""]
for i, s in sorted(stock.items()):
    if s.get("failure"):
        L.append(f"- {i}: {s['failure']}")
L += ["", "## Faults inside episodes (controller crashed mid-episode; reward earned before the crash is kept)", ""]
for i, s in sorted(stock.items()):
    if s.get("n_faults"):
        L.append(f"- {i}: {s['n_faults']} of {s['n_episodes']} episodes, first: {s['first_fault']}")
(R / "pilot_report.md").write_text("\n".join(L) + "\n")
print(R / "pilot_report.md")
