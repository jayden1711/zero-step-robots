"""Tests for scripts/warmstart_cem.py and warmstart_cem_report.py (addendum 2026-11-16). No LLM, no network."""
import copy
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))
import warmstart_cem as wc  # noqa: E402
from test_warmstart import SPEC  # noqa: E402


def test_slots_are_exactly_the_numbers_perturb_changes():
    from rs_proposer import perturb
    a = copy.deepcopy(SPEC)
    b = perturb(copy.deepcopy(SPEC), np.random.default_rng(0))
    va, vb = wc.vector(a), wc.vector(b)
    assert len(va) == len(vb) and np.all(va != vb)  # every slot changed by perturb
    # and nothing outside the slots changed
    assert wc.with_vector(b, va) == a


def test_vector_roundtrip_keeps_fixed_fields():
    v = wc.vector(SPEC)
    sp = wc.with_vector(SPEC, v + 1.0)
    assert wc.vector(sp).tolist() == (v + 1.0).tolist()
    for u0, u1 in zip(SPEC["units"], sp["units"]):
        assert u0.get("range") == u1.get("range") and u0.get("tol") == u1.get("tol")
    assert (sp["obs_dim"], sp["act_dim"], sp["hidden"]) == (11, 3, 16)
    assert SPEC == wc.with_vector(SPEC, v)


def test_cem_one_generation_runs(tmp_path):
    import warmstart as ws
    sid, spec = ws.r_starts("hopper")[0]
    res = wc.run("hopper", "R", sid, spec, 1, tmp_path / "r.json", gens=1, checkpoints=(20,))
    assert res["designs"] == 20 and len(res["dev_history"]) == 20 and len(res["checkpoints"]) == 1
    assert res["dev_history"][0] is not None  # design 0 is the start itself


def test_report_statistics():
    import warmstart_cem_report as r
    assert abs(r.fisher_two_sided(3, 1, 1, 3) - 0.4857) < 1e-3
    assert r.fisher_two_sided(10, 0, 0, 10) < 1e-4
    assert r.holm([0.001, 0.04, 0.5, 0.012, 0.3]) == [True, False, False, True, False]
