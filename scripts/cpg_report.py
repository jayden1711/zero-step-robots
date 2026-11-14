"""CPG-track report (docs/prereg-2026-11-09-cpg.md sections 3, 5, 8). Usage: cpg_report.py RESULTS
Writes RESULTS/cpg_report.md. Every attempt of every cell is listed; failures count as d = 0."""
import json
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np

LEVELS = ("H2", "H1", "H0")
# Post-hoc diagnostic (chosen after reading replies, not pre-registered): sign of the net gain (linear and reflex units) from torso pitch
# to the hip/thigh torque(s). Verified in the env: a forward lean is obs[1] > 0 and a negative thigh torque pitches the
# torso back, so a correcting gain is negative. Hopper: a0; walker2d: a0 and a3 (summed).
HIP = {"hopper": ("a0",), "walker2d": ("a0", "a3")}


def pitch_gain(spec, task):
    try:
        return sum(u.get("inputs", {}).get("obs[1]", 0) * sum(u.get("to", {}).get(a, 0) for a in HIP[task])
                   for u in spec.get("units", []))  # linear gain, or a reflex unit's slope sign
    except (AttributeError, TypeError):
        return None
BINS = [(-1e9, 0, "<0"), (0, 0.5, "0-0.5"), (0.5, 1.5, "0.5-1.5"), (1.5, 3, "1.5-3"), (3, 5, "3-5"), (5, 1e9, ">=5")]


def load(p):
    try:
        return json.loads(Path(p).read_text())
    except (OSError, ValueError):
        return None


def row(name, r, note=""):
    if r is None:
        return f"| {name} | not run | | | | | | | {note} |"
    return (f"| {name} | {r['mean_distance_healthy']:.2f} | {r['median_distance_healthy']:.2f} | "
            f"{r['min_distance_healthy']:.2f} | {r['n_clean_3m']} | {'yes' if r['passes_3m'] else 'no'} | "
            f"{r['mean_return']:.0f} | {r['frac_full_length']:.2f} | {note} |")


HEAD = ("| row | mean d (m) | median d | min d | clean eps (>=3 m) | passes | mean return | full-length frac | note |\n"
        "|---|---|---|---|---|---|---|---|---|")


def baselines(res: Path, task: str, out: list):
    b = res / "cpg" / "baselines" / task
    out += [f"### {task}: necessity table and CPG baselines", "", HEAD]
    out.append(row("zero weights", load(b / "zero.score.json")))
    rm = [load(b / f"random_mlp_{s}.score.json") for s in range(10)]
    rm = [r for r in rm if r]
    if rm:
        md = [r["mean_distance_healthy"] for r in rm]
        out.append(f"| random MLP (n={len(rm)}) | median {np.median(md):.2f}, max {max(md):.2f} | | | "
                   f"{sum(r['n_clean_3m'] for r in rm)} | {sum(r['passes_3m'] for r in rm)} pass | | | 10 seeds |")
    if task == "hopper":
        r = load(b / "standstill_best_return.score.json")
        out.append(row("stand-still (highest-return earlier attempt)", r, r and r.get("attempt", "")))
    r = load(b / "lunge.score.json")
    out.append(row("fall-forward lunge (best constant action, dev seeds)", r))
    r = load(b / "sinusoid.score.json")
    out.append(row("open-loop sinusoid (tuned on dev seeds)", r, r and f"{r.get('dev_episodes')} dev episodes"))
    rc = sorted((b / "random_cpg").glob("*.score.json"))
    rc = [load(p) for p in rc]
    if rc:
        md = [r["mean_distance_healthy"] for r in rc]
        out.append(f"| random CPG (n={len(rc)}) | median {np.median(md):.2f}, best {max(md):.2f} | | | "
                   f"{sum(r['n_clean_3m'] for r in rc)} | {sum(r['passes_3m'] for r in rc)} pass | | | "
                   f"necessity: median < 1.5 m: {'holds' if np.median(md) < 1.5 else 'FAILS'} |")
    r = load(b / "tuned_cpg.score.json")
    out.append(row("tuned CPG (headroom; search on dev seeds)", r, r and f"{r.get('dev_episodes')} dev episodes"))
    ppo = sorted((res / "cpg" / "ppo" / task).glob("*.score.json"))
    for p in ppo:
        r = load(p)
        if r and "mean_distance_healthy" in r:
            out.append(row(f"PPO {p.stem} (upper reference, env reward)", r))
        elif r:
            out.append(f"| PPO {p.stem} | rescore needed (old metric only: mean distance {r.get('mean_distance', 0):.2f}) |"
                       " | | | | | | |")
    out += ["", "Necessity rule (each simple baseline mean d < 1.5 m): "
            + ", ".join(f"{n}: {'holds' if r['mean_distance_healthy'] < 1.5 else 'FAILS'}"
                        for n, r in (("zero", load(b / "zero.score.json")), ("lunge", load(b / "lunge.score.json")),
                                     ("sinusoid", load(b / "sinusoid.score.json"))) if r), ""]


def attempts(res: Path, task: str, out: list):
    cells = defaultdict(list)
    transport = []
    for d in sorted((res / "attempts").glob(f"cpg-*_{task}_H?_cpgspec_*")):
        if not d.name[-2:].isdigit():  # renamed transport failures (_try1, _aborted1): kept, listed, not attempts
            transport.append(d.name)
            continue
        meta, sc = load(d / "meta.json"), load(d / "score.json")
        if meta is None:
            continue
        model = meta["model"]
        if sc is None:
            cells[(model, meta["arm"])].append((d.name, None, "not scored"))
        elif sc.get("failure"):
            cells[(model, meta["arm"])].append((d.name, 0.0, "FAIL: " + sc["failure"][:80]))
        else:
            sp = load(d / "parsed.spec.json")
            sc = {**sc, "pitch_gain": pitch_gain(sp, task) if isinstance(sp, dict) else None}
            cells[(model, meta["arm"])].append((d.name, sc["mean_distance_healthy"], sc))
    out += [f"### {task}: LLM attempts (mode cpgspec)", "",
            "| model | level | n | failures | passes (target: >= 5 of 10) | mean d | median d | best d | bins " +
            " / ".join(b[2] for b in BINS) + " | pitch->hip gain < 0 (post hoc) |", "|---|---|---|---|---|---|---|---|---|---|"]
    verdict = {}
    for (model, lv) in sorted(cells, key=lambda c: (c[0], LEVELS.index(c[1]))):
        xs = cells[(model, lv)]
        ds = [x[1] for x in xs if x[1] is not None]
        npass = sum(1 for x in xs if isinstance(x[2], dict) and x[2].get("passes_3m"))
        nfail = sum(1 for x in xs if isinstance(x[2], str) and x[2].startswith("FAIL"))
        bins = " / ".join(str(sum(lo <= v < hi for v in ds)) for lo, hi, _ in BINS)
        gains = [x[2].get("pitch_gain") for x in xs if isinstance(x[2], dict)]
        gsign = f"{sum(1 for g in gains if g is not None and g < 0)} of {len(gains)}"
        meets = npass >= 5 and len(xs) >= 10
        if meets:
            verdict.setdefault(model, []).append(lv)
        out.append(f"| {model} | {lv} | {len(xs)}{'' if len(xs) >= 10 else ' (incomplete)'} | {nfail} | {npass}"
                   f"{' MEETS' if meets else ''} | {np.mean(ds) if ds else float('nan'):.2f} | "
                   f"{np.median(ds) if ds else float('nan'):.2f} | {max(ds) if ds else float('nan'):.2f} | {bins} | {gsign} |")
    out += ["", "Per attempt (id: mean d to last healthy step, clean episodes, or failure):", ""]
    for key in sorted(cells):
        for name, dv, sc in cells[key]:
            extra = (f"{sc['n_clean_3m']} clean, return {sc['mean_return']:.0f}, full-length {sc['frac_full_length']:.2f}, "
                     f"pitch->hip gain {sc['pitch_gain'] if sc.get('pitch_gain') is None else round(sc['pitch_gain'], 2)}"
                     if isinstance(sc, dict) else sc)
            out.append(f"- `{name}`: {'' if dv is None else f'{dv:.2f} m, '}{extra}")
    if transport:
        out += ["", "Transport failures, repeated once with the same index (prereg s6; kept, see NOTE.md in each): "
                + ", ".join(f"`{t}`" for t in transport)]
    out.append("")
    return verdict


def complete_cells(res: Path, task: str) -> int:
    n = 0
    for model in ("claude-opus-5-5", "claude-sonnet-5-5"):
        for lv in LEVELS:
            ds = list((res / "attempts").glob(f"cpg-{model}_{task}_{lv}_cpgspec_[0-9][0-9]"))
            n += sum((d / "score.json").exists() for d in ds) >= 10
    return n


def main():
    res = Path(sys.argv[1])
    out = ["# CPG track report (local; numbers stay in results/)", "",
           "Prereg: docs/prereg-2026-11-09-cpg.md. d = forward displacement to the last healthy step, 100 scoring episodes "
           "(seeds 10000..10099). Attempt passes: mean d >= 3 m and >= 50 clean episodes. Arm meets the target: >= 5 of 10 "
           "attempts pass. Simulation only (MuJoCo through Gymnasium); one reply per attempt, no execution, no training.", ""]
    verdicts = {}
    for task in ("hopper", "walker2d"):
        baselines(res, task, out)
        verdicts[task] = attempts(res, task, out)
        verdicts[task + "_complete"] = complete_cells(res, task)
    out += ["## Verdict (prereg section 8)", ""]
    for task in ("hopper", "walker2d"):
        v, done = verdicts[task], verdicts[task + "_complete"]
        if v:
            out.append(f"- {task}: target met by " + "; ".join(
                f"{m} (lowest level {min(lvs, key=lambda lv: int(lv[1]))})" for m, lvs in v.items()))
        else:
            out.append(f"- {task}: **did not work**: no arm meets the target "
                       + ("(all 6 Claude cells complete, 10 attempts each)." if done == 6 else
                          f"({done} of 6 Claude cells complete so far)."))
    (res / "cpg_report.md").write_text("\n".join(out) + "\n")
    print(res / "cpg_report.md")


if __name__ == "__main__":
    main()
