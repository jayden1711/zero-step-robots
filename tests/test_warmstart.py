"""Tests for scripts/warmstart.py (docs/prereg-followup-draft.md section 10). No LLM, no network."""
import copy
import json
import os
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))
import warmstart as ws  # noqa: E402

RESULTS = Path(os.environ.get("ZSR_RESULTS", ROOT / "results"))

SPEC = {"target": "cpg", "obs_dim": 11, "act_dim": 3, "hidden": 16, "note": "test",
        "oscillators": [{"name": "a", "freq_hz": 2.0, "phase0": 0.5, "feedback": {"obs[1]": 0.7}},
                        {"name": "b", "freq_hz": 1.0, "phase0": 1.5}],
        "couplings": [{"from": "a", "to": "b", "weight": 2.0, "phase_lag": 3.0}],
        "bias": {"a0": 0.1, "a1": -0.2, "a2": 0.3},
        "units": [{"type": "linear", "name": "u", "inputs": {"cos(a)": 1.0, "obs[2]": -0.5}, "range": 2.0, "tol": 0.05,
                   "to": {"a0": 1.0, "a1": 0.5}},
                  {"type": "reflex", "name": "r", "inputs": {"sin(b)": 2.0}, "threshold": 0.4, "sharpness": 3.0,
                   "to": {"a2": -1.0}}]}


def skeleton(x):
    """Everything except the permuted numbers: keys, names, strings, and the fixed numeric fields."""
    if isinstance(x, dict):
        return {k: (v if k in ("obs_dim", "act_dim", "hidden", "range", "tol") else skeleton(v)) for k, v in x.items()}
    if isinstance(x, list):
        return [skeleton(v) for v in x]
    return x if isinstance(x, str) else "num"


def nums(sp):
    """Values per kind (a..f), as the prereg defines them; gains as absolute values."""
    o, c, u = sp["oscillators"], sp["couplings"], sp["units"]
    return {"a": sorted(x["freq_hz"] for x in o),
            "b": sorted([x["phase0"] for x in o] + [x["phase_lag"] for x in c]),
            "c": sorted(x["weight"] for x in c),
            "d": sorted([abs(v) for x in o for v in (x.get("feedback") or {}).values()]
                        + [abs(v) for x in u for v in x["inputs"].values()]
                        + [abs(v) for x in u for v in x["to"].values()]),
            "e": sorted(sp["bias"].values()),
            "f": sorted(x["threshold"] for x in u if x["type"] == "reflex"),
            "g": sorted(x["sharpness"] for x in u if x["type"] == "reflex")}


def test_permute_keeps_structure_and_fixed_fields():
    p = ws.permute(SPEC, 123)
    assert skeleton(p) == skeleton(SPEC)
    assert SPEC == json.loads(json.dumps(SPEC))  # input not mutated
    assert nums(p) == nums(SPEC)  # same multiset of values per kind (gains up to sign)


def test_permute_does_not_mutate_input_and_is_deterministic():
    before = copy.deepcopy(SPEC)
    assert ws.permute(SPEC, 7) == ws.permute(SPEC, 7)
    assert SPEC == before
    seen = {json.dumps(ws.permute(SPEC, s), sort_keys=True) for s in range(20)}
    assert len(seen) > 10


def test_permute_flips_signs_of_gains_only():
    flips = 0
    for s in range(50):
        p = ws.permute(SPEC, s)
        assert sorted(p["bias"].values()) == sorted(SPEC["bias"].values())  # biases permuted, never flipped
        flips += sum(v < 0 for v in p["units"][0]["to"].values())
    assert 20 < flips < 80  # 2 gains x 50 specs, each flipped with p 0.5 (and permuted among all gains)


def test_seed_sets_are_disjoint_from_earlier_random_cpgs():
    assert set(ws.R_SEEDS).isdisjoint(range(0, 50)) and set(ws.R_SEEDS).isdisjoint(range(100, 110))
    assert len(ws.R_SEEDS) == 80 and len(ws.H_SEEDS) == 10


def test_seed_rule_matches_rs_proposer():
    import hashlib
    aid = "fb-claude-opus-5-5_hopper_H2_00"
    assert ws.run_seed("L", aid) == int(hashlib.sha256(aid.encode()).hexdigest()[:8], 16)
    assert ws.run_seed("H", "hand_s3") == 3
    assert ws.run_seed("P", aid + "__perm") == ws.sha_seed(aid + "__perm") != ws.sha_seed(aid + "/perm")


@pytest.mark.skipif(not (RESULTS / "attempts").exists(), reason="results/attempts not present")
@pytest.mark.parametrize("task", ["hopper", "walker2d"])
def test_l_set_is_80_per_task_and_all_compile(task):
    from circuitc import compile_cpg
    L = ws.l_starts(task, RESULTS)
    assert len(L) == 80
    assert sum(sid.startswith("fb-") for sid, _ in L) == 20
    for sid, sp in L:
        compile_cpg(sp)
        compile_cpg(ws.permute(sp, ws.sha_seed(sid + "/perm")))  # P designs keep declared ranges, so they compile


@pytest.mark.skipif(not (RESULTS / "cpg_feedback/rs/hopper/fromllm_claude-opus-5-5").exists(),
                    reason="RS-from-LLM results not present")
def test_checkpoint_6_reproduces_rs_from_llm(tmp_path):
    """The first 6 designs of an L run from a feedback round-0 start replay the existing RS-from-LLM run exactly."""
    aid = "fb-claude-opus-5-5_hopper_H2_00"
    ref = json.loads((RESULTS / f"cpg_feedback/rs/hopper/fromllm_claude-opus-5-5/{aid}.json").read_text())
    spec0 = dict(ws.l_starts("hopper", RESULTS))[aid]
    res = ws.run("hopper", "L", aid, spec0, ws.run_seed("L", aid), tmp_path / "r.json", designs=6, checkpoints=(6,))
    want = [h["dev_mean_d"] for h in ref["history"]]
    got = res["dev_history"]
    assert len(got) == 6
    assert all((w is None and g is None) or abs(w - g) < 1e-3 for w, g in zip(want, got))
    assert res["checkpoints"][0]["spec"] == ref["final_spec"]


# ---------------------------------------------------------------- report statistics
import warmstart_report as wr  # noqa: E402


def test_fisher_matches_writeup_value():
    assert abs(wr.fisher_one_sided(2, 10, 0, 10) - 45 / 190) < 1e-12
    assert wr.fisher_one_sided(0, 80, 0, 80) == 1.0


def test_mann_whitney_direction_and_ties():
    x, y = [float(i) for i in range(40)], [float(i) - 30 for i in range(40)]
    assert wr.mann_whitney_greater(x, y) < 1e-6
    assert wr.mann_whitney_greater(y, x) > 0.999
    same = [0.0] * 30 + [1.0] * 10
    assert 0.4 < wr.mann_whitney_greater(same, list(same)) <= 0.6


def _fake(task, s, i, T, d):
    cps = [{"designs": k, "dev_mean_d": d, "spec": {},
            "heldout": {"mean_distance_healthy": d if (T and k >= T) or k == 500 else 0.1,
                        "passes_3m": bool(T and k >= T)}} for k in wr.CHECKPOINTS]
    return {"task": task, "set": s, "start_id": f"{s}{i}", "T": T, "checkpoints": cps, "wall_s": 1.0}


def test_report_end_to_end_primary_and_fallback(tmp_path):
    def write(task, s, runs):
        d = tmp_path / "warmstart" / task / s
        d.mkdir(parents=True, exist_ok=True)
        for r in runs:
            (d / f"{r['start_id']}.json").write_text(json.dumps(r))
    # hopper: H passes 5/10 (no fallback); L 30/80 pass, R 5/80 -> claim; P 28/80 -> L not above P
    write("hopper", "H", [_fake("hopper", "H", i, 100 if i < 5 else None, 3.5 if i < 5 else 1.0) for i in range(10)])
    write("hopper", "L", [_fake("hopper", "L", i, 200 if i < 30 else None, 4.0 if i < 30 else 0.5) for i in range(80)])
    write("hopper", "P", [_fake("hopper", "P", i, 200 if i < 28 else None, 4.0 if i < 28 else 0.5) for i in range(80)])
    write("hopper", "R", [_fake("hopper", "R", i, 500 if i < 5 else None, 3.2 if i < 5 else 0.2) for i in range(80)])
    # walker2d: H 1/10 -> fallback in force
    write("walker2d", "H", [_fake("walker2d", "H", i, 500 if i < 1 else None, 3.1 if i < 1 else 0.3) for i in range(10)])
    sys.argv = ["warmstart_report.py", str(tmp_path)]
    wr.main()
    text = (tmp_path / "warmstart_report.md").read_text()
    hop = text.split("## walker2d")[0]
    assert "L vs R (primary), pass by checkpoint 500: 30/80 vs 5/80" in hop
    assert "**measurable warm-start value**" in hop
    assert "**L not measurably above P**" in hop
    wal = text.split("## walker2d")[1]
    assert "fallback primary outcome in force" in wal
    assert "Stage B headroom: not run yet" in wal
