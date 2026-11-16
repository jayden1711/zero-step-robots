"""Numbers quoted in docs/prereg-followup-draft.md: start-set sizes, exact power of the primary test, compute estimate.

Usage: python scripts/followup_numbers.py [results_dir]   (reads files only; runs no simulation and no model)
"""
import glob
import json
import os
import sys
from math import comb

R = sys.argv[1] if len(sys.argv) > 1 else "results"

# start sets (zero-step designs: no-feedback track + feedback-arm round 0, which saw no feedback)
for task in ("hopper", "walker2d"):
    nf = glob.glob(os.path.join(R, f"attempts/cpg-claude-*_{task}_H?_cpgspec_[0-9][0-9]/parsed.spec.json"))
    r0 = glob.glob(os.path.join(R, f"attempts/fb-claude-*_{task}_H2_[0-9][0-9]/r0/parsed.spec.json"))
    print(f"{task}: no-feedback specs {len(nf)}, feedback round-0 specs {len(r0)}, L set {len(nf) + len(r0)}")


# exact power of a one-sided Fisher exact test (alpha 0.05), n per group, true rates p1 (L) > p0 (R)
def fisher_p(a, b, n):  # P(X >= a) under the hypergeometric, a = L passes, b = R passes, n per group
    k = a + b
    tot = comb(2 * n, k)
    return sum(comb(n, i) * comb(n, k - i) for i in range(a, min(k, n) + 1)) / tot


def power(n, p1, p0, alpha=0.05, min_diff=0.10):
    pw = 0.0
    pa = [comb(n, a) * p1 ** a * (1 - p1) ** (n - a) for a in range(n + 1)]
    pb = [comb(n, b) * p0 ** b * (1 - p0) ** (n - b) for b in range(n + 1)]
    for a in range(n + 1):
        if pa[a] < 1e-12:
            continue
        for b in range(n + 1):
            if pb[b] < 1e-12:
                continue
            if (a - b) / n >= min_diff and fisher_p(a, b, n) < alpha:
                pw += pa[a] * pb[b]
    return pw


for p1, p0 in ((0.25, 0.10), (0.20, 0.05), (0.30, 0.10), (0.15, 0.0), (0.20, 0.10)):
    print(f"power n=80/80, L {p1:.2f} vs R {p0:.2f} (Fisher one-sided 0.05 and diff >= 0.10): {power(80, p1, p0):.2f}")
print(f"false-positive rate at L = R = 0.10: {power(80, 0.10, 0.10):.3f}")

# compute: simulation speed from a 100-episode, 1000-step held-out scoring; episode lengths of the start designs
s = json.load(open(os.path.join(R, "attempts/fb-claude-opus-5-5_hopper_H2_08/score.json")))
sps = s["n_episodes"] * s["mean_length"] / s["wall_s"]
print(f"hopper steps/s (single thread, incl. policy): {sps:.0f}  <- attempts/fb-claude-opus-5-5_hopper_H2_08/score.json")
for budget in (500,):
    worst = budget * 10 * 1000 / sps
    print(f"worst case per run, {budget} designs x 10 dev episodes x 1000 steps: {worst / 60:.0f} min")
    runs = 2 * (80 * 3 + 10)
    print(f"worst case, {runs} runs: {runs * worst / 3600:.0f} CPU-h; with 2 sim-run slots {runs * worst / 7200:.0f} h wall")
cem = 3 * 50000 * 1000 / sps
print(f"Stage B worst case (3 CEM seeds x 50,000 walker2d dev episodes x 1000 steps, hopper speed): {cem / 3600:.1f} CPU-h")
