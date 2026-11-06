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

cells = collections.defaultdict(list)
for i, m in meta.items():
    if i in stock:
        cells[(m["task"], m["model"], m["mode"], m["arm"])].append(i)

L = ["# Report (local, not for git)", "",
     "Simulation only (MuJoCo via Gymnasium). Score = mean return over 100 episodes, reset seeds 10000..10099.",
     "Every attempt is listed, failures (unparsable/invalid replies) included and counted as failures, not dropped.",
     f"`full` = attempts whose mean return is >= {FULL:.0f}. On hopper a return near 1000 can mean standing without "
     "falling for 1000 steps (reward is 1/step alive + forward speed): see the distance column.", ""]


def table(task, variant):
    rows = []
    for (t, model, mode, arm), ids in sorted(cells.items()):
        if t != task:
            continue
        sc, dist = [], []
        for i in ids:
            s = stock[i] if variant is None else var.get(i, {}).get(variant)
            if s is None:
                sc.append(None)
                dist.append(None)
                continue
            sc.append(s.get("mean_return") if not s.get("failure") and not s.get("load_error") else None)
            dist.append(s.get("mean_distance"))
        nfail = sum(1 for i in ids if stock[i].get("failure"))
        mean, med, iqr, lo, hi = stats(sc)
        full = sum(1 for x in sc if x is not None and x >= FULL)
        d = [x for x in dist if x is not None]
        rows.append(f"| {model} | {mode} | {arm} | {len(ids)} | {nfail} | {full} | {mean} | {med} | {iqr} | {lo} | {hi} | "
                    f"{f1(st.median(d)) if d else '-'} | {', '.join('F' if x is None else f'{x:.0f}' for x in sc)} |")
    return rows


HDR = ["| model | mode | arm | n | unparsable | full | mean | median | IQR | min | max | median distance | per-attempt |",
       "|---|---|---|---|---|---|---|---|---|---|---|---|---|"]


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
        vals, dist = [], []
        for n in names:
            src = n if n.startswith(task + "_ppo") else n.replace(task + "_", "", 1)
            s = base[n] if variant is None else var.get(src, {}).get(variant)
            if s is not None:
                vals.append(s.get("mean_return"))
                dist.append(s.get("mean_distance"))
        if not vals:
            continue
        mean, med, iqr, lo, hi = stats(vals)
        rows.append(f"| baseline: {g} | - | - | {len(vals)} | 0 | {sum(1 for x in vals if x >= FULL)} | {mean} | {med} | {iqr} | "
                    f"{lo} | {hi} | {f1(st.median(dist)) if dist else '-'} | {', '.join(f'{x:.0f}' for x in vals)} |")
    if variant is not None and task == "cartpole":
        s = var.get("lqr_" + variant, {}).get(variant)
        if s:
            rows.append(f"| baseline: LQR matched to this variant | - | - | 1 | 0 | {int(s['mean_return'] >= FULL)} | "
                        f"{f1(s['mean_return'])} | - | - | - | - | {f1(s['mean_distance'])} | {s['mean_return']:.0f} |")
    c = R / "circuit" / f"{task}_{'pd' if task == 'cartpole' else 'pd_hold'}" / "score.json"
    s = json.load(open(c)) if variant is None and c.exists() else var.get(f"circuit_{c.parent.name}", {}).get(variant)
    if s:
        rows.append(f"| compiler fixture (author-written spec, NOT an LLM) | - | - | 1 | 0 | {int(s['mean_return'] >= FULL)} | "
                    f"{f1(s['mean_return'])} | - | - | - | - | {f1(s['mean_distance'])} | {s['mean_return']:.0f} |")
    return rows


from zsr.variants import variant_names  # noqa: E402

for task in ("cartpole", "hopper"):
    for variant in [None] + variant_names(task):
        L += [f"## {task}: {'stock environment' if variant is None else 'variant ' + variant}", ""] + HDR
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
