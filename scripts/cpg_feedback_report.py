"""Feedback-arm report (docs/prereg-2026-11-10-cpg-feedback.md s6, s7, s10). Usage: cpg_feedback_report.py RESULTS
Writes RESULTS/cpg_feedback_report.md. Primary = round-5 design on the held-out seeds; failures count as d = 0."""
import json
import sys
from pathlib import Path

import numpy as np

MODELS = ("claude-opus-5-5", "claude-sonnet-5-5")
TASKS = ("hopper", "walker2d")


def load(p):
    try:
        return json.loads(Path(p).read_text())
    except (OSError, ValueError):
        return None


def d_of(sc):
    if sc is None:
        return None
    return 0.0 if sc.get("failure") or "mean_distance_healthy" not in sc else sc["mean_distance_healthy"]


def stats(ds, passes, n_expected=10):
    ds = [x for x in ds if x is not None]
    if not ds:
        return "| 0 | | | | | |"
    return (f"| {len(ds)}{'' if len(ds) >= n_expected else ' (incomplete)'} | {passes} | {np.mean(ds):.2f} | "
            f"{np.median(ds):.2f} | {max(ds):.2f} | {sum(x >= 1.5 for x in ds)} |")


def main():
    res = Path(sys.argv[1])
    A = res / "attempts"
    out = ["# CPG feedback arm report (local; numbers stay in results/)", "",
           "Prereg: docs/prereg-2026-11-10-cpg-feedback.md. Level H2. 6 designs per attempt (round 0 + 5 revisions) from a "
           "fixed dev-seed summary (seeds 0..9); primary = round-5 design, scored on held-out seeds 10000..10099. Pass: mean "
           "d >= 3 m and >= 50 clean episodes; arm meets the target with >= 5 of 10 passing attempts. Simulation only.", ""]
    verdict, tokens = {}, {"calls": 0, "in": 0, "out": 0, "transport_failures": 0}
    for task in TASKS:
        out += [f"## {task}", "", "| arm | n | passes | mean d (m) | median d | best d | attempts >= 1.5 m |",
                "|---|---|---|---|---|---|---|"]
        for model in MODELS:
            dirs = sorted(A.glob(f"fb-{model}_{task}_H2_[0-9][0-9]"))
            fin = [load(d / "score.json") for d in dirs]
            npass = sum(1 for s in fin if s and s.get("passes_3m"))
            out.append(f"| feedback, {model}, round 5 (primary) " + stats([d_of(s) for s in fin], npass))
            r0 = [load(d / "r0" / "score.json") for d in dirs]
            out.append(f"| feedback, {model}, round 0 (its own no-feedback control) "
                       + stats([d_of(s) for s in r0], sum(1 for s in r0 if s and s.get("passes_3m"))))
            nf = [load(d / "score.json") for d in sorted(A.glob(f"cpg-{model}_{task}_H2_cpgspec_[0-9][0-9]"))]
            out.append(f"| no-feedback arm (track, H2), {model} "
                       + stats([d_of(s) for s in nf], sum(1 for s in nf if s and s.get("passes_3m"))))
            rs = [load(p) for p in sorted((res / "cpg_feedback" / "rs" / task / f"fromllm_{model}").glob("*.json"))]
            out.append(f"| RS-from-LLM (start = {model} round 0) "
                       + stats([d_of(r["score"]) for r in rs if r], sum(1 for r in rs if r and r["score"].get("passes_3m"))))
            if len(dirs) >= 10 and all(fin) and npass >= 5:
                verdict.setdefault(task, []).append(model)
            for d in dirs:
                tokens["transport_failures"] += len(list(d.glob("r*_try1")))
                for rj in d.glob("r[0-9]/run.json"):
                    u = (load(rj) or {}).get("usage") or {}
                    tokens["calls"] += 1
                    tokens["in"] += sum(u.get(k, 0) for k in ("input_tokens", "cache_read_input_tokens",
                                                              "cache_creation_input_tokens"))
                    tokens["out"] += u.get("output_tokens", 0)
        rr = [load(p) for p in sorted((res / "cpg_feedback" / "rs" / task / "random").glob("*.json"))]
        out.append("| RS-random (random CPG start) "
                   + stats([d_of(r["score"]) for r in rr if r], sum(1 for r in rr if r and r["score"].get("passes_3m"))))
        out += ["", f"Held-out mean d by round (median over attempts; never shown to the model):", "",
                "| model | r0 | r1 | r2 | r3 | r4 | r5 |", "|---|---|---|---|---|---|---|"]
        for model in MODELS:
            dirs = sorted(A.glob(f"fb-{model}_{task}_H2_[0-9][0-9]"))
            cells = []
            for k in range(6):
                ds = [d_of(load(d / f"r{k}" / "score.json")) for d in dirs]
                ds = [x for x in ds if x is not None]
                cells.append(f"{np.median(ds):.2f}" if ds else "")
            out.append(f"| {model} | " + " | ".join(cells) + " |")
        out += ["", "Per attempt (held-out mean d per round r0..r5; dev mean d per round in brackets):", ""]
        for model in MODELS:
            for d in sorted(A.glob(f"fb-{model}_{task}_H2_[0-9][0-9]")):
                cells = []
                for k in range(6):
                    h, fb = d_of(load(d / f"r{k}" / "score.json")), load(d / f"r{k}" / "feedback.json") or {}
                    dev = "err" if "error" in fb else (f"{fb['mean_d']:.2f}" if "mean_d" in fb else "")
                    cells.append(("" if h is None else f"{h:.2f}") + f" [{dev}]")
                s = load(d / "score.json") or {}
                out.append(f"- `{d.name}`: " + ", ".join(cells) + (" PASS" if s.get("passes_3m") else ""))
        out.append("")
    out += ["## Budget", "", f"Claude calls (rounds, incl. repeats kept as rK/): {tokens['calls']}; transport failures "
            f"repeated: {tokens['transport_failures']}; tokens in (incl. cache): {tokens['in']}; tokens out: {tokens['out']}.",
            "", "## Verdict (prereg s6)", ""]
    for task in TASKS:
        n_done = sum(len([d for d in A.glob(f"fb-{m}_{task}_H2_[0-9][0-9]") if (d / "score.json").exists()]) for m in MODELS)
        if verdict.get(task):
            out.append(f"- {task}: target met with feedback by {', '.join(verdict[task])} (H2).")
        else:
            out.append(f"- {task}: **did not work** with feedback either: no arm meets the target "
                       f"({n_done} of 20 attempts complete).")
    (res / "cpg_feedback_report.md").write_text("\n".join(out) + "\n")
    print(res / "cpg_feedback_report.md")


if __name__ == "__main__":
    main()
