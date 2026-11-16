"""Tests for scripts/warmstart_signfix.py (addendum 2026-11-16 (b)). No LLM."""
import os
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))
import warmstart_signfix as sf  # noqa: E402
from cpg_report import pitch_gain  # noqa: E402

RESULTS = Path(os.environ.get("ZSR_RESULTS", ROOT / "results"))
SPEC = {"target": "cpg", "obs_dim": 11, "act_dim": 3, "hidden": 16, "oscillators": [], "couplings": [], "bias": {},
        "units": [{"type": "linear", "name": "hip", "inputs": {"obs[1]": 1.5, "obs[7]": 0.2}, "range": 2.0, "tol": 0.05,
                   "to": {"a0": 1.0}},
                  {"type": "linear", "name": "knee", "inputs": {"obs[1]": 0.7}, "range": 2.0, "tol": 0.05,
                   "to": {"a1": 1.0}}]}


def test_repair_flips_only_thigh_pitch_gains():
    s, ok = sf.repair(SPEC)
    assert ok and pitch_gain(s, "hopper") < 0
    assert s["units"][0]["inputs"] == {"obs[1]": -1.5, "obs[7]": 0.2}
    assert s["units"][1]["inputs"] == {"obs[1]": 0.7}  # unit not feeding a0 untouched
    assert SPEC["units"][0]["inputs"]["obs[1]"] == 1.5  # input not mutated


def test_unrepairable_when_no_pitch_input():
    sp = {**SPEC, "units": [{"type": "linear", "name": "hip", "inputs": {"obs[7]": 0.2}, "range": 2.0, "tol": 0.05,
                             "to": {"a0": 1.0}}]}
    assert sf.repair(sp)[1] is False


def test_mcnemar():
    assert sf.mcnemar_one_sided(0, 0) == 1.0
    assert abs(sf.mcnemar_one_sided(6, 0) - 1 / 64) < 1e-12
    assert abs(sf.mcnemar_one_sided(5, 1) - 7 / 64) < 1e-12


@pytest.mark.skipif(not (RESULTS / "attempts").exists(), reason="results not present")
def test_wrong_sign_set_is_30():
    assert len(sf.wrong_sign(RESULTS)) == 30
