"""Recompute every number quoted in docs/writeup.md from the files it links to, and check them.

Usage: python scripts/writeup_numbers.py [results_dir]   (default: results)
Reads only score.json / search.json / run.json files; runs no simulation and no model. Exits non-zero if any quoted
number differs from the recomputed value (at the precision quoted). Prints one line per check with its source path.
"""
import glob
import json
import os
import statistics
import sys

R = sys.argv[1] if len(sys.argv) > 1 else "results"
fails = []


def load(p):
    with open(os.path.join(R, p)) as f:
        return json.load(f)


def check(label, got, want, src, nd=2):
    ok = round(got, nd) == round(want, nd) if isinstance(want, float) else got == want
    print(f"{'ok  ' if ok else 'FAIL'} {label}: {got if not isinstance(got, float) else round(got, nd)} (quoted {want})  <- {src}")
    if not ok:
        fails.append(label)


def d(p):
    return load(p)["mean_distance_healthy"]


# --- no-feedback CPG track: 120 attempts, 0 pass ---
nf = sorted(glob.glob(os.path.join(R, "attempts/cpg-claude-*_cpgspec_[0-9][0-9]/score.json")))
check("no-feedback attempts", len(nf), 120, "attempts/cpg-claude-*_cpgspec_NN/score.json")
check("no-feedback passes", sum(json.load(open(p))["passes_3m"] for p in nf), 0, "same")
for task in ("hopper", "walker2d"):
    ps = [p for p in nf if f"_{task}_" in p]
    lens = {}
    for p in ps:
        cell = p.split("/")[-2].rsplit("_cpgspec", 1)[0]
        lens.setdefault(cell, []).extend(e["length"] for e in json.load(open(p))["episodes"])
    med = sorted(statistics.median(v) for v in lens.values())
    print(f"info {task}: median episode length per cell, min {med[0]} max {med[-1]} steps")
check("best hopper no-feedback", d("attempts/cpg-claude-opus-5-5_hopper_H0_cpgspec_06/score.json"), 1.08, "attempts/cpg-claude-opus-5-5_hopper_H0_cpgspec_06/score.json")
check("best walker2d no-feedback", d("attempts/cpg-claude-opus-5-5_walker2d_H1_cpgspec_01/score.json"), 1.30, "attempts/cpg-claude-opus-5-5_walker2d_H1_cpgspec_01/score.json")
best = {t: max(d(os.path.relpath(p, R)) for p in nf if f"_{t}_" in p) for t in ("hopper", "walker2d")}
check("max over hopper no-feedback", best["hopper"], 1.08, "attempts/cpg-claude-*_hopper_*")
check("max over walker2d no-feedback", best["walker2d"], 1.30, "attempts/cpg-claude-*_walker2d_*")

# --- baselines ---
B = "cpg/baselines"
for task, want in (("hopper", {"zero": -0.01, "lunge": 0.74, "sinusoid": 0.46, "tuned_cpg": 3.27}),
                   ("walker2d", {"zero": -0.17, "lunge": 0.96, "sinusoid": -0.05, "tuned_cpg": 1.29})):
    for k, v in want.items():
        check(f"{task} {k}", d(f"{B}/{task}/{k}.score.json"), v, f"{B}/{task}/{k}.score.json")
    rc = [json.load(open(p))["mean_distance_healthy"] for p in glob.glob(os.path.join(R, f"{B}/{task}/random_cpg/*.score.json"))]
    print(f"info {task} random CPG: n={len(rc)} median {statistics.median(rc):.2f} best {max(rc):.2f} pass {sum(x >= 3 for x in rc)}")
t = load(f"{B}/hopper/tuned_cpg.score.json")
check("hopper tuned CPG clean episodes", t["n_clean_3m"], 80, f"{B}/hopper/tuned_cpg.score.json")
check("hopper tuned CPG full-length fraction", t["frac_full_length"], 0.0, f"{B}/hopper/tuned_cpg.score.json")
check("walker2d tuned CPG clean", load(f"{B}/walker2d/tuned_cpg.score.json")["n_clean_3m"], 0, f"{B}/walker2d/tuned_cpg.score.json")
for task in ("hopper", "walker2d"):
    s = load(f"{B}/{task}/tuned_cpg.search.json")
    check(f"{task} tuned CPG dev episodes used", s["episodes_used"], 19650, f"{B}/{task}/tuned_cpg.search.json")
for task, want in (("hopper", [12.66, 17.48, 13.90]), ("walker2d", [16.57, 6.97, 3.75])):
    for i, v in enumerate(want):
        p = f"cpg/ppo/{task}/{task}_ppo_seed{i}.score.json"
        check(f"PPO {task} seed{i}", d(p), v, p)

# --- feedback arm ---
A = "attempts/fb-claude-opus-5-5_hopper_H2_"
for i, v in (("03", 6.42), ("08", 6.90)):
    check(f"Opus hopper fb {i} round 5", d(f"{A}{i}/score.json"), v, f"{A}{i}/score.json")
check("fb 03 round 0", d(f"{A}03/r0/score.json"), 6.12, f"{A}03/r0/score.json")
s8 = load(f"{A}08/score.json")
check("fb 08 clean", s8["n_clean_3m"], 100, f"{A}08/score.json")
check("fb 08 full-length fraction", s8["frac_full_length"], 1.0, f"{A}08/score.json")
check("fb 08 mean return", s8["mean_return"], 1862.0, f"{A}08/score.json", nd=0)
check("fb 08 wall seconds (100 full episodes)", s8["wall_s"], 6.0, f"{A}08/score.json", nd=0)
for r, v in ((0, -0.06), (1, 0.13), (2, 5.43)):
    check(f"fb 08 round {r}", d(f"{A}08/r{r}/score.json"), v, f"{A}08/r{r}/score.json")
check("fb 03 clean", load(f"{A}03/score.json")["n_clean_3m"], 100, f"{A}03/score.json")


def fb(model, task, r=None):
    out = []
    for p in sorted(glob.glob(os.path.join(R, f"attempts/fb-claude-{model}_{task}_H2_[0-9][0-9]"))):
        out.append(json.load(open(os.path.join(p, "score.json" if r is None else f"r{r}/score.json"))))
    return out


for model, task, npass, med, best_ in (("opus-5-5", "hopper", 2, 1.27, 6.90), ("sonnet-5-5", "hopper", 0, 0.94, 0.96),
                                       ("opus-5-5", "walker2d", 0, -1.10, 0.83), ("sonnet-5-5", "walker2d", 0, 0.68, 0.97)):
    sc = fb(model, task)
    ds = [s["mean_distance_healthy"] for s in sc]
    src = f"attempts/fb-claude-{model}_{task}_H2_NN/score.json"
    check(f"fb {model} {task} n", len(sc), 10, src)
    check(f"fb {model} {task} passes", sum(s["passes_3m"] for s in sc), npass, src)
    check(f"fb {model} {task} median d", statistics.median(ds), med, src)
    check(f"fb {model} {task} best d", max(ds), best_, src)
oh = [s["mean_distance_healthy"] for s in fb("opus-5-5", "hopper")]
check("fb opus hopper mean d", statistics.mean(oh), 1.92, "attempts/fb-claude-opus-5-5_hopper_H2_NN/score.json")
check("fb opus hopper attempts >= 1.5 m", sum(x >= 1.5 for x in oh), 4, "same")
check("fb opus walker2d round-0 median", statistics.median(s["mean_distance_healthy"] for s in fb("opus-5-5", "walker2d", 0)), -0.81,
      "attempts/fb-claude-opus-5-5_walker2d_H2_NN/r0/score.json")
check("fb opus hopper round-0 passes", sum(s["passes_3m"] for s in fb("opus-5-5", "hopper", 0)), 1,
      "attempts/fb-claude-opus-5-5_hopper_H2_NN/r0/score.json")

# calls and tokens
calls, tin, tout = 0, 0, 0
for p in glob.glob(os.path.join(R, "attempts/fb-claude-*/r*/run.json")):
    u = json.load(open(p)).get("usage") or {}
    calls += 1
    tin += u.get("input_tokens", 0) + u.get("cache_read_input_tokens", 0) + u.get("cache_creation_input_tokens", 0)
    tout += u.get("output_tokens", 0)
check("feedback calls (run.json files)", calls, 240, "attempts/fb-claude-*/r*/run.json")
print(f"info feedback tokens: in (incl. cache) {tin}, out {tout} (report: 2858684 / 1738817)")

# --- random-search proposer ---
for task, sub, npass, best_ in (("hopper", "random", 0, 0.48), ("hopper", "fromllm_claude-opus-5-5", 1, 6.12),
                                ("walker2d", "random", 0, -0.06)):
    runs = [json.load(open(p))["score"] for p in glob.glob(os.path.join(R, f"cpg_feedback/rs/{task}/{sub}/*.json"))]
    src = f"cpg_feedback/rs/{task}/{sub}/"
    check(f"RS {task} {sub} n", len(runs), 10, src)
    check(f"RS {task} {sub} passes", sum(r["passes_3m"] for r in runs), npass, src)
    check(f"RS {task} {sub} best", max(r["mean_distance_healthy"] for r in runs), best_, src)

# --- derived statistics quoted in the write-up (computed, not read) ---
from math import comb

# one-sided Fisher exact: Opus hopper feedback round 5 (2/10) vs no-feedback H2 (0/10)
p = comb(10, 2) * comb(10, 0) / comb(20, 2)
check("Fisher one-sided p, 2/10 vs 0/10", p, 0.24, "computed from the two counts above")
# exact one-sided 95% upper bound on a per-attempt pass rate after 0 passes in n
for n, want in ((120, 0.025), (60, 0.049)):
    check(f"95% upper bound on pass rate, 0 of {n}", 1 - 0.05 ** (1 / n), want, "computed", nd=3)
# two-sided 95% Clopper-Pearson interval for 2 of 10 (by bisection on the binomial tail)


def binom_cdf(k, n, q):
    return sum(comb(n, i) * q ** i * (1 - q) ** (n - i) for i in range(k + 1))


def bisect(f, lo=0.0, hi=1.0):
    for _ in range(100):
        mid = (lo + hi) / 2
        lo, hi = (mid, hi) if f(mid) else (lo, mid)
    return lo


lo = bisect(lambda q: 1 - binom_cdf(1, 10, q) < 0.025)
hi = bisect(lambda q: binom_cdf(2, 10, q) > 0.025)
check("Clopper-Pearson 2/10 lower", lo, 0.025, "computed", nd=3)
check("Clopper-Pearson 2/10 upper", hi, 0.556, "computed", nd=3)

# --- warm-start study (docs/prereg-followup-draft.md; results/warmstart/) ---
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__))))
import warmstart_report as wr  # noqa: E402

W = os.path.join(R, "warmstart")


def ws_runs(task, s):
    return [json.load(open(p)) for p in sorted(glob.glob(os.path.join(W, task, s, "*.json")))]


want = {("hopper", "L"): 39, ("hopper", "P"): 27, ("hopper", "R"): 2, ("hopper", "H"): 5,
        ("walker2d", "L"): 2, ("walker2d", "P"): 1, ("walker2d", "R"): 0, ("walker2d", "H"): 0}
runs = {k: ws_runs(*k) for k in want}
for k, v in want.items():
    src = f"warmstart/{k[0]}/{k[1]}/*.json"
    check(f"warm-start {k[0]} {k[1]} n", len(runs[k]), 10 if k[1] == "H" else 80, src)
    check(f"warm-start {k[0]} {k[1]} pass by 500", sum(r["T"] is not None for r in runs[k]), v, src)
hl = [r for r in runs[("hopper", "L")] if not r["start_id"].startswith("fb-")]
check("warm-start hopper L, no-feedback starts only, pass", sum(r["T"] is not None for r in hl), 23, "warmstart/hopper/L/cpg-claude-*.json")
check("warm-start hopper L pass by 6", sum(r["T"] == 6 for r in runs[("hopper", "L")]), 1, "warmstart/hopper/L/*.json")
check("warm-start hopper L vs R Fisher p < 0.001", wr.fisher_one_sided(39, 80, 2, 80) < 0.001, True, "computed")
check("warm-start hopper L vs P Fisher p", wr.fisher_one_sided(39, 80, 27, 80), 0.038, "computed", nd=3)
dl = [wr.d_at(r, 500) for r in runs[("walker2d", "L")]]
dr = [wr.d_at(r, 500) for r in runs[("walker2d", "R")]]
dp = [wr.d_at(r, 500) for r in runs[("walker2d", "P")]]
check("warm-start walker2d L median d@500", statistics.median(dl), 0.92, "warmstart/walker2d/L/*.json")
check("warm-start walker2d R median d@500", statistics.median(dr), 0.76, "warmstart/walker2d/R/*.json")
check("warm-start walker2d P median d@500", statistics.median(dp), -0.05, "warmstart/walker2d/P/*.json")
check("warm-start walker2d L vs R Mann-Whitney p", wr.mann_whitney_greater(dl, dr), 0.267, "computed", nd=3)
check("warm-start walker2d L vs P Mann-Whitney p < 0.001", wr.mann_whitney_greater(dl, dp) < 0.001, True, "computed")
for s, v, c in ((0, 1.29, 0), (1, 1.09, 0), (2, 5.06, 96)):
    p = f"warmstart/walker2d/headroom/tuned_cpg_50k_seed{s}.score.json"
    check(f"headroom seed {s} d", d(p), v, p)
    check(f"headroom seed {s} clean", load(p)["n_clean_3m"], c, p)
wall = sum(r["wall_s"] for rs in runs.values() for r in rs)
print(f"info warm-start CPU time over all 500 runs: {wall / 3600:.1f} h")

# --- robustness addendum: CEM replication and predictors (results/warmstart_cem/) ---
import warmstart_cem_report as wcr  # noqa: E402


def cem_runs(s):
    return [json.load(open(p)) for p in sorted(glob.glob(os.path.join(R, "warmstart_cem", "hopper", s, "*.json")))]


cr = {s: cem_runs(s) for s in "LPRH"}
for s, v in (("L", 34), ("P", 8), ("R", 2), ("H", 7)):
    src = f"warmstart_cem/hopper/{s}/*.json"
    check(f"CEM hopper {s} n", len(cr[s]), 10 if s == "H" else 80, src)
    check(f"CEM hopper {s} pass by 500", sum(r["T"] is not None for r in cr[s]), v, src)
check("CEM L vs R Fisher p < 0.0001", wr.fisher_one_sided(34, 80, 2, 80) < 1e-4, True, "computed")
check("CEM L vs P Fisher p < 0.0001", wr.fisher_one_sided(34, 80, 8, 80) < 1e-4, True, "computed")
check("CEM L, one-reply starts only, pass", sum(r["T"] is not None for r in cr["L"] if not r["start_id"].startswith("fb-")),
      20, "warmstart_cem/hopper/L/cpg-claude-*.json")
from pathlib import Path as _P
feats = [wcr.features(_P(R), r) for r in cr["L"]]
for fid, ya, yn, na, nn in (("F1", 32, 50, 2, 30), ("F2", 11, 14, 23, 66), ("F3", 24, 40, 10, 40), ("F4", 20, 40, 14, 40),
                            ("F5", 1, 2, 33, 78)):
    y = [r for r, f in zip(cr["L"], feats) if f[fid]]
    n = [r for r, f in zip(cr["L"], feats) if not f[fid]]
    check(f"CEM predictor {fid} yes", (sum(r["T"] is not None for r in y), len(y)), (ya, yn), "warmstart_cem/hopper/L/")
    check(f"CEM predictor {fid} no", (sum(r["T"] is not None for r in n), len(n)), (na, nn), "warmstart_cem/hopper/L/")
ps = [wcr.fisher_two_sided(a, b - a, c, d - c) for a, b, c, d in ((32, 50, 2, 30), (11, 14, 23, 66), (24, 40, 10, 40),
                                                                   (20, 40, 14, 40), (1, 2, 33, 78))]
check("CEM predictors surviving Holm", wcr.holm(ps), [True, True, True, False, False], "computed")
check("CEM F1 p < 0.0001", ps[0] < 1e-4, True, "computed")
check("CEM F2 p", ps[1], 0.0057, "computed", nd=4)
check("CEM F3 p", ps[2], 0.0030, "computed", nd=4)
check("CEM F4 p", ps[3], 0.258, "computed", nd=3)
lo = [(r, f) for r, f in zip(cr["L"], feats) if "_H2_" not in r["start_id"]]
for sign, want in ((True, (9, 13)), (False, (1, 27))):
    rr = [r for r, f in lo if f["F1"] == sign]
    check(f"CEM H0/H1 sign {'correct' if sign else 'wrong'} (post hoc)", (sum(r["T"] is not None for r in rr), len(rr)), want,
          "warmstart_cem/hopper/L/")
cw = sum(r["wall_s"] for rs in cr.values() for r in rs)
check("CEM CPU hours", cw / 3600, 2.9, "warmstart_cem/hopper/*/*.json", nd=1)

print(f"\n{len(fails)} mismatches" + (": " + ", ".join(fails) if fails else ""))
sys.exit(1 if fails else 0)
