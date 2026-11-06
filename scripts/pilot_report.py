"""Aggregate every scored attempt (all of them, failures included) into results/pilot_report.md. Local only.
usage: python scripts/pilot_report.py RESULTS_DIR"""
import glob, json, statistics as st, sys, collections
from pathlib import Path

R = Path(sys.argv[1])
cells = collections.defaultdict(list)
for f in sorted(glob.glob(str(R / "attempts/*/score.json"))):
    s = json.load(open(f)); m = json.load(open(f.replace("score", "meta")))
    cells[(m["model"], m["task"], m["arm"])].append((m["id"], s))
base = {}
for f in sorted(glob.glob(str(R / "baselines/*.score.json"))):
    s = json.load(open(f)); base[Path(f).name.replace(".score.json", "")] = s.get("mean_return")
L = ["# Pilot report (local, not for git)", "", "Weights mode, 10 attempts per model x task x arm. Score = mean return over 100 episodes.",
     "Every attempt is listed, failures included.", "",
     "| model | task | arm | n | parse/shape failures | mean | median | best | worst | per-attempt scores |", "|---|---|---|---|---|---|---|---|---|---|"]
for (model, task, arm), v in sorted(cells.items()):
    sc = [s["mean_return"] if s.get("mean_return") is not None else None for _, s in v]
    fails = sum(1 for _, s in v if s.get("failure"))
    ok = [x for x in sc if x is not None]
    f = lambda x: f"{x:.1f}"
    L.append(f"| {model} | {task} | {arm} | {len(v)} | {fails} | {f(st.mean(ok)) if ok else '-'} | {f(st.median(ok)) if ok else '-'} | "
             f"{f(max(ok)) if ok else '-'} | {f(min(ok)) if ok else '-'} | {', '.join('FAIL' if x is None else f(x) for x in sc)} |")
L += ["", "## Baselines (same harness)", ""] + [f"- {k}: {v:.1f}" for k, v in base.items() if v is not None]
L += ["", "## Failures", ""]
for (model, task, arm), v in sorted(cells.items()):
    for i, s in v:
        if s.get("failure"):
            L.append(f"- {i}: {s['failure']}")
(R / "pilot_report.md").write_text("\n".join(L) + "\n")
print(R / "pilot_report.md")
