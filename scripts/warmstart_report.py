"""Report for the warm-start study (docs/prereg-followup-draft.md sections 5-6). Reads results/warmstart/ only.

    python scripts/warmstart_report.py [results_dir]     # writes <results>/warmstart_report.md and prints it

Primary (hopper): L vs R pass-by-500 rate, claim iff rate difference >= 0.10 AND one-sided Fisher exact p < 0.05.
Fallback (decided in the prereg): if fewer than 3 of 10 H runs pass by 500 on that task, the primary outcome is the
held-out mean d at checkpoint 500, L vs R, one-sided Mann-Whitney U p < 0.05 AND median difference >= 0.5 m.
Secondary: the same rule for L vs P. Walker2d: same rules, interpreted only if Stage B shows headroom.
"""
import json
import statistics
import sys
from math import comb, erf, sqrt
from pathlib import Path

CHECKPOINTS = (6, 25, 50, 100, 200, 500)
N_PLANNED = {"L": 80, "P": 80, "R": 80, "H": 10}


def fisher_one_sided(a, n1, b, n2):
    """P(X >= a) for X = passes in group 1 under the hypergeometric null (margins fixed)."""
    k, tot = a + b, comb(n1 + n2, a + b)
    return sum(comb(n1, i) * comb(n2, k - i) for i in range(a, min(k, n1) + 1)) / tot


def mann_whitney_greater(x, y):
    """One-sided p for x stochastically greater than y: normal approximation with tie correction (n >= 20 per arm)."""
    allv = sorted((v, g) for g, vs in ((0, x), (1, y)) for v in vs)
    ranks, i = {}, 0
    rx = 0.0
    n = len(allv)
    tie_term = 0
    while i < n:
        j = i
        while j + 1 < n and allv[j + 1][0] == allv[i][0]:
            j += 1
        r = (i + j) / 2 + 1
        t = j - i + 1
        tie_term += t ** 3 - t
        rx += r * sum(1 for k in range(i, j + 1) if allv[k][1] == 0)
        i = j + 1
    n1, n2 = len(x), len(y)
    u = rx - n1 * (n1 + 1) / 2
    mu = n1 * n2 / 2
    sd = sqrt(n1 * n2 / 12 * ((n + 1) - tie_term / (n * (n - 1))))
    if sd == 0:
        return 1.0
    z = (u - mu - 0.5) / sd
    return 0.5 * (1 - erf(z / sqrt(2)))


def load(results: Path, task):
    out = {}
    for s in ("L", "P", "R", "H"):
        out[s] = [json.loads(p.read_text()) for p in sorted((results / "warmstart" / task / s).glob("*.json"))]
    return out


def d_at(run, k):
    c = next(c for c in run["checkpoints"] if c["designs"] == k)
    return c["heldout"].get("mean_distance_healthy", 0.0)  # a failure scores d = 0, as in the track


def passed_by(run, k):
    return run["T"] is not None and run["T"] <= k


def compare(a_runs, b_runs, fallback):
    na, nb = len(a_runs), len(b_runs)
    if not na or not nb:
        return None
    if not fallback:
        pa, pb = sum(passed_by(r, 500) for r in a_runs), sum(passed_by(r, 500) for r in b_runs)
        diff = pa / na - pb / nb
        p = fisher_one_sided(pa, na, pb, nb)
        return {"outcome": "pass by checkpoint 500", "a": f"{pa}/{na}", "b": f"{pb}/{nb}", "diff": diff, "p": p,
                "claim": diff >= 0.10 and p < 0.05}
    da, db = [d_at(r, 500) for r in a_runs], [d_at(r, 500) for r in b_runs]
    diff = statistics.median(da) - statistics.median(db)
    p = mann_whitney_greater(da, db)
    return {"outcome": "held-out mean d at checkpoint 500 (fallback)", "a": f"median {statistics.median(da):.2f} m",
            "b": f"median {statistics.median(db):.2f} m", "diff": diff, "p": p, "claim": diff >= 0.5 and p < 0.05}


def section(task, runs, results: Path):
    L = [f"## {task}", ""]
    h = runs["H"]
    h_pass = sum(passed_by(r, 500) for r in h)
    fallback = len(h) == N_PLANNED["H"] and h_pass < 3
    L.append(f"Stage 0 (H, hand start): {h_pass} of {len(h)} runs pass by checkpoint 500"
             + (" -> **fallback primary outcome in force** (prereg section 5)." if fallback else
                (" (incomplete)." if len(h) < N_PLANNED["H"] else ".")))
    L += ["", "| set | n (planned) | " + " | ".join(f"pass by {k}" for k in CHECKPOINTS)
          + " | median d @6 | median d @500 | >= 1.5 m @500 | >= 3 m @500 | >= 5 m @500 |",
          "|---|---|" + "---|" * (len(CHECKPOINTS) + 5)]
    for s in ("L", "P", "R", "H"):
        rs = runs[s]
        if not rs:
            L.append(f"| {s} | 0 ({N_PLANNED[s]}) |" + " |" * (len(CHECKPOINTS) + 5))
            continue
        d6, d500 = [d_at(r, 6) for r in rs], [d_at(r, 500) for r in rs]
        L.append(f"| {s} | {len(rs)} ({N_PLANNED[s]}) | " + " | ".join(str(sum(passed_by(r, k) for r in rs))
                                                                    for k in CHECKPOINTS)
                 + f" | {statistics.median(d6):.2f} | {statistics.median(d500):.2f} | "
                 + " | ".join(str(sum(x >= t for x in d500)) for t in (1.5, 3, 5)) + " |")
    L.append("")
    for lab, a, b, role in (("L vs R", "L", "R", "primary" if task == "hopper" else "Walker2d"),
                            ("L vs P", "L", "P", "secondary")):
        c = compare(runs[a], runs[b], fallback)
        if c is None:
            L.append(f"- {lab} ({role}): not computable yet.")
            continue
        verdict = "**measurable warm-start value**" if c["claim"] else "**no measurable warm-start value**"
        if lab == "L vs P":
            verdict = "**L > P (the specific numbers matter)**" if c["claim"] else "**L not measurably above P**"
        inc = any(len(runs[s]) < N_PLANNED[s] for s in (a, b))
        L.append(f"- {lab} ({role}), {c['outcome']}: {c['a']} vs {c['b']}, difference {c['diff']:+.2f}, one-sided "
                 f"p = {c['p']:.3f} -> {verdict}" + (" (INCOMPLETE: sets below planned n)" if inc else ""))
    rev = compare(runs["R"], runs["L"], fallback)
    if rev:
        L.append(f"- R vs L (descriptive, the other direction): one-sided p = {rev['p']:.3f}")
    if task == "walker2d":
        hd = sorted((results / "warmstart" / task / "headroom").glob("*.score.json"))
        if hd:
            ok = [json.loads(p.read_text()) for p in hd]
            shown = any(o.get("passes_3m") for o in ok)
            L.append(f"- Stage B headroom: {len(ok)} of 3 CEM searches done; held-out mean d "
                     + ", ".join(f"{o['mean_distance_healthy']:.2f}" for o in ok)
                     + f" -> headroom {'**shown**' if shown else '**not shown**'}"
                     + ("" if shown else "; Walker2d comparisons say nothing about the model alone."))
        else:
            L.append("- Stage B headroom: not run yet; Walker2d comparisons are not interpreted.")
    L += ["", "Per run (start id: T, held-out d at 6 / 500, wall s):", ""]
    for s in ("H", "L", "P", "R"):
        for r in runs[s]:
            L.append(f"- {s} `{r['start_id']}`: T={r['T']}, d {d_at(r, 6):.2f} / {d_at(r, 500):.2f} m, {r['wall_s']} s")
    return L


def main():
    results = Path(sys.argv[1] if len(sys.argv) > 1 else "results")
    L = ["# Warm-start study report (prereg: docs/prereg-followup-draft.md)", "",
         "No LLM was called. Starts: L = zero-step LLM designs, P = permuted LLM designs, R = random CPGs, "
         "H = hand start (calibration). Search: rs_proposer (1+1) hill climber, 500 designs, practice seeds 0..9; "
         "checkpoints scored on held-out seeds 10000..10099. Pass = mean d >= 3 m and >= 50 clean episodes.", ""]
    for task in ("hopper", "walker2d"):
        L += section(task, load(results, task), results) + [""]
    text = "\n".join(L) + "\n"
    (results / "warmstart_report.md").write_text(text)
    print(text)


if __name__ == "__main__":
    main()
