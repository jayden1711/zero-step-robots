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
            "f": sorted(x[k] for x in u if x["type"] == "reflex" for k in ("threshold", "sharpness"))}


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
