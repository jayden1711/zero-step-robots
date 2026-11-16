"""Sign-repair causal test (docs/addendum-2026-11-16-signfix.md). No LLM anywhere.

    python scripts/warmstart_signfix.py list                       # the wrong-sign hopper L designs, runs nothing
    python scripts/warmstart_signfix.py run cem|hc [--shard k/n]   # 500-design runs from the repaired designs
    python scripts/warmstart_signfix.py report [results]           # paired McNemar vs the original runs
Run through ~/projects/bin/sim-run.
"""
import argparse
import copy
import json
import sys
from math import comb
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))
import warmstart as ws  # noqa: E402
from cpg_report import pitch_gain  # noqa: E402

TASK = "hopper"


def repair(spec):
    """Flip the obs[1] input gain of every unit with a nonzero `to` weight on a0. Returns (spec, repaired_ok)."""
    sp = copy.deepcopy(spec)
    for u in sp.get("units", []):
        if (u.get("to") or {}).get("a0", 0) and "obs[1]" in (u.get("inputs") or {}):
            u["inputs"]["obs[1]"] = -u["inputs"]["obs[1]"]
    g = pitch_gain(sp, TASK)
    return sp, g is not None and g < 0


def wrong_sign(results: Path):
    out = []
    for sid, sp in ws.l_starts(TASK, results):
        g = pitch_gain(sp, TASK)
        if g is None or g >= 0:
            out.append((sid, sp))
    return out


def mcnemar_one_sided(b, c):
    """b = pairs where only S passes, c = pairs where only the original passes; P(X >= b), X ~ Bin(b + c, 1/2)."""
    n = b + c
    return 1.0 if n == 0 else sum(comb(n, i) for i in range(b, n + 1)) / 2 ** n


def run_all(opt, results: Path, shard):
    k, n = (int(x) for x in shard.split("/"))
    base = results / "warmstart_signfix" / TASK / opt
    for i, (sid, sp) in enumerate(wrong_sign(results)):
        if i % n != k:
            continue
        out = base / f"{sid}__signfix.json"
        if out.exists():
            continue
        s, ok = repair(sp)
        if opt == "hc":
            res = ws.run(TASK, "S", sid + "__signfix", s, ws.sha_seed("signfix/" + sid), out)
        else:
            import warmstart_cem as wc
            res = wc.run(TASK, "S", sid + "__signfix", s, ws.sha_seed("signfix-cem/" + sid), out)
        res["repairable"] = ok
        from circuitc import compile_cpg
        from zsr.cpg import CPGPolicy
        from zsr.harness import evaluate
        r0 = evaluate(TASK, CPGPolicy(TASK, compile_cpg(s)[0]))  # the repaired design itself, no search
        res["start_heldout"] = {kk: v for kk, v in r0.items() if kk != "episodes"}
        out.write_text(json.dumps(res, indent=1))


def report(results: Path):
    L = ["# Sign-repair report (addendum docs/addendum-2026-11-16-signfix.md)", "",
         "Designs: hopper L starts with pitch-to-hip net gain >= 0. S = obs[1] gain flipped on every unit feeding a0. "
         "Paired with the original run of the same design under the same optimiser. Pass = by checkpoint 500.", ""]
    ws_list = wrong_sign(results)
    for opt, orig_dir, role in (("cem", "warmstart_cem", "primary"), ("hc", "warmstart", "secondary")):
        rows, b, c, s_pass, o_pass, n, unrep = [], 0, 0, 0, 0, 0, 0
        for sid, _ in ws_list:
            f = results / "warmstart_signfix" / TASK / opt / f"{sid}__signfix.json"
            o = results / orig_dir / TASK / "L" / f"{sid}.json"
            if not f.exists():
                continue
            r, ro = json.loads(f.read_text()), json.loads(o.read_text())
            sp_ = r["T"] is not None and r.get("repairable", True)
            op_ = ro["T"] is not None
            unrep += not r.get("repairable", True)
            n += 1
            s_pass += sp_
            o_pass += op_
            b += sp_ and not op_
            c += op_ and not sp_
            d0 = r.get("start_heldout", {}).get("mean_distance_healthy")
            rows.append(f"- `{sid}`: S T={r['T']} (repairable {r.get('repairable')}), original T={ro['T']}, "
                        f"repaired design with no search d={d0 if d0 is None else round(d0, 2)} m")
        p = mcnemar_one_sided(b, c)
        claim = n > 0 and (s_pass - o_pass) >= 6 and p < 0.05
        L += [f"## {opt.upper()} ({role})", "",
              f"n = {n} of {len(ws_list)} (not repairable: {unrep}). S passes {s_pass}, original passes {o_pass}; "
              f"discordant: only S {b}, only original {c}; one-sided exact McNemar p = {p:.4f} -> "
              + ("**the sign is causal for search success**" if claim else "**not shown to be causal**"), ""] + rows + [""]
    text = "\n".join(L) + "\n"
    (results / "warmstart_signfix_report.md").write_text(text)
    print(text)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=("list", "run", "report"))
    ap.add_argument("opt", nargs="?", choices=("cem", "hc"))
    ap.add_argument("--results", type=Path, default=ws.MAIN_RESULTS)
    ap.add_argument("--shard", default="0/1")
    a = ap.parse_args()
    if a.cmd == "list":
        for sid, sp in wrong_sign(a.results):
            print(sid, "repairable" if repair(sp)[1] else "NOT repairable")
    elif a.cmd == "run":
        run_all(a.opt, a.results, a.shard)
    else:
        report(a.results)


if __name__ == "__main__":
    main()
