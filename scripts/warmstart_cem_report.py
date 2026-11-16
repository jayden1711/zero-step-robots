"""Report for docs/addendum-2026-11-16-warmstart-robustness.md: the CEM replication (Q1) and the predictors (Q2).

    python scripts/warmstart_cem_report.py [results_dir]   # writes <results>/warmstart_cem_report.md and prints it
Reads results/warmstart_cem/ (new, confirmatory) and results/warmstart/ (hill climber; predictors exploratory there).
"""
import json
import sys
from math import comb
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from cpg_report import pitch_gain  # noqa: E402
import warmstart_report as wr  # noqa: E402

CHECKPOINTS = (20, 100, 200, 500)
FEATURES = [("F1", "pitch-to-hip gain sign correct (< 0)", False), ("F2", "start held-out mean d >= 0.5 m", False),
            ("F3", "hint level H2 (vs H0/H1)", True), ("F4", "model Opus (vs Sonnet)", True),
            ("F5", "two or more oscillators", False)]


def fisher_two_sided(a, b, c, d):
    """2x2 [[a, b], [c, d]]: sum of hypergeometric probabilities <= that of the observed table."""
    r1, c1, n = a + b, a + c, a + b + c + d

    def pr(x):
        return comb(c1, x) * comb(n - c1, r1 - x) / comb(n, r1)
    p0 = pr(a)
    return min(1.0, sum(pr(x) for x in range(max(0, r1 + c1 - n), min(r1, c1) + 1) if pr(x) <= p0 * (1 + 1e-9)))


def holm(ps):
    """Holm-Bonferroni: list of booleans 'rejected' at family-wise 0.05, in input order."""
    order = sorted(range(len(ps)), key=lambda i: ps[i])
    rej, m = [False] * len(ps), len(ps)
    for rank, i in enumerate(order):
        if ps[i] <= 0.05 / (m - rank):
            rej[i] = True
        else:
            break
    return rej


def start_d(results: Path, sid):
    p = results / "attempts" / sid / ("r0/score.json" if sid.startswith("fb-") else "score.json")
    return json.loads(p.read_text())["mean_distance_healthy"]


def features(results: Path, run, task="hopper"):
    sid, sp = run["start_id"], run["start_spec"]
    g = pitch_gain(sp, task)
    return {"F1": g is not None and g < 0, "F2": start_d(results, sid) >= 0.5, "F3": "_H2_" in sid,
            "F4": "opus" in sid, "F5": len(sp.get("oscillators", [])) >= 2}


def predictor_table(results: Path, runs, label):
    L = [f"| feature | seen before? | pass rate, yes | pass rate, no | odds ratio | two-sided Fisher p | survives Holm |",
         "|---|---|---|---|---|---|---|"]
    rows, ps = [], []
    feats = [features(results, r) for r in runs]
    for fid, name, seen in FEATURES:
        y = [r for r, f in zip(runs, feats) if f[fid]]
        n = [r for r, f in zip(runs, feats) if not f[fid]]
        a, b = sum(wr.passed_by(r, 500) for r in y), len(y) - sum(wr.passed_by(r, 500) for r in y)
        c, d = sum(wr.passed_by(r, 500) for r in n), len(n) - sum(wr.passed_by(r, 500) for r in n)
        p = fisher_two_sided(a, b, c, d)
        orr = (a * d / (b * c)) if b * c else float("inf")
        ps.append(p)
        rows.append((fid, name, seen, a, len(y), c, len(n), orr, p))
    rej = holm(ps)
    for (fid, name, seen, a, ny, c, nn, orr, p), r in zip(rows, rej):
        L.append(f"| {fid} {name} | {'yes' if seen else 'no'} | {a}/{ny} | {c}/{nn} | {orr:.2f} | {p:.4f} | "
                 f"{'**yes**' if r else 'no'} |")
    return [f"### Predictors, {label}", ""] + L + [""]


def main():
    results = Path(sys.argv[1] if len(sys.argv) > 1 else "results")
    task = "hopper"
    runs = {s: [json.loads(p.read_text()) for p in sorted((results / "warmstart_cem" / task / s).glob("*.json"))]
            for s in ("L", "P", "R", "H")}
    h_pass = sum(wr.passed_by(r, 500) for r in runs["H"])
    fallback = len(runs["H"]) == 10 and h_pass < 3
    L = ["# Warm-start robustness report (addendum docs/addendum-2026-11-16-warmstart-robustness.md)", "",
         "No LLM was called. Optimiser: CEM (population 20, 5 elites, 25 generations = 500 designs = 5,000 practice "
         "episodes), the same starts and budget as the hill climber in results/warmstart_report.md.", "",
         "## Q1: CEM replication, hopper", "",
         f"Calibration (H): {h_pass} of {len(runs['H'])} runs pass by 500"
         + (" -> fallback outcome in force." if fallback else "."), "",
         "| set | n | " + " | ".join(f"pass by {k}" for k in CHECKPOINTS) + " | median d @500 |",
         "|---|---|" + "---|" * (len(CHECKPOINTS) + 1)]
    import statistics
    for s in ("L", "P", "R", "H"):
        rs = runs[s]
        if not rs:
            L.append(f"| {s} | 0 |" + " |" * (len(CHECKPOINTS) + 1))
            continue
        L.append(f"| {s} | {len(rs)} | " + " | ".join(str(sum(wr.passed_by(r, k) for r in rs)) for k in CHECKPOINTS)
                 + f" | {statistics.median(wr.d_at(r, 500) for r in rs):.2f} |")
    L.append("")
    for lab, a, b, role in (("L vs R", "L", "R", "primary"), ("L vs P", "L", "P", "secondary")):
        c = wr.compare(runs[a], runs[b], fallback)
        if c is None:
            L.append(f"- {lab} ({role}): not computable yet.")
            continue
        ok = "**replicates**" if c["claim"] else "**does not replicate**"
        if lab == "L vs P":
            ok = "**L > P**" if c["claim"] else "**L not measurably above P**"
        inc = len(runs[a]) < 80 or len(runs[b]) < 80
        L.append(f"- {lab} ({role}), {c['outcome']}: {c['a']} vs {c['b']}, difference {c['diff']:+.2f}, one-sided "
                 f"p = {c['p']:.4f} -> {ok}" + (" (INCOMPLETE)" if inc else ""))
    L += ["", "## Q2: predictors of a good start (L runs, pass by 500)", ""]
    if runs["L"]:
        L += predictor_table(results, runs["L"], "CEM runs (confirmatory; Holm over 5 at 0.05)")
    hc = [json.loads(p.read_text()) for p in sorted((results / "warmstart" / task / "L").glob("*.json"))]
    if hc:
        L += predictor_table(results, hc, "hill-climber runs (EXPLORATORY: F3/F4 counts were seen before this addendum)")
    L += ["## Per run (CEM)", ""]
    for s in ("H", "L", "P", "R"):
        for r in runs[s]:
            L.append(f"- {s} `{r['start_id']}`: T={r['T']}, d@500 {wr.d_at(r, 500):.2f} m, {r['wall_s']} s")
    text = "\n".join(L) + "\n"
    (results / "warmstart_cem_report.md").write_text(text)
    print(text)


if __name__ == "__main__":
    main()
