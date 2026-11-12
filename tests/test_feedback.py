import hashlib
import json
import sys
from pathlib import Path

import pytest

from zsr import attempt
from zsr.feedback import summarize

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
import run_feedback as rf  # noqa: E402


@pytest.mark.parametrize("task", ["hopper", "walker2d"])
def test_round0_differs_from_no_feedback_prompt_only_in_the_opening(task):
    fb, nf = rf.round0_prompt(task, "H2"), attempt.build_prompt(task, "cpgspec", "H2")
    a, b = fb.split("\n\n", 2), nf.split("\n\n", 2)
    assert a[0] == b[0] and a[2] == b[2] and a[1] != b[1]
    assert "round-5 design is final" in a[1]


def test_rounds_carry_history_verbatim_and_final_sentence_only_last():
    hist = [("reply zero ```json\n{}\n```", "summary zero"), ("reply one", "summary one")]
    p2 = rf.round_prompt("hopper", "H2", hist, 2)
    assert p2.startswith(rf.round0_prompt("hopper", "H2"))
    assert p2.index("reply zero") < p2.index("summary zero") < p2.index("reply one") < p2.index("summary one")
    assert "round 2 of 5" in p2 and "last round" not in p2
    p5 = rf.round_prompt("hopper", "H2", hist * 2 + hist[:1], 5)
    assert "round 5 of 5" in p5 and "last round: this design is final" in p5
    assert "{{" not in p5


def test_parse_reply():
    assert rf.parse_reply("x")["error"].startswith("no ```json")
    assert "not valid JSON" in rf.parse_reply("```json\n{bad\n```")["error"]
    assert rf.parse_reply("```json\n{}\n```\n```json\n{\"a\": 1}\n```") == {"a": 1}


def test_frozen_feedback_prompts():
    for line in (attempt.PROMPTS / "SHA256SUMS-cpg-feedback.txt").read_text().splitlines():
        h, name = line.split()
        assert hashlib.sha256((attempt.PROMPTS / name).read_bytes()).hexdigest() == h, name


def test_summary_layout_and_errors():
    spec = {"target": "cpg", "obs_dim": 11, "act_dim": 3, "hidden": 16,
            "oscillators": [{"name": "o", "freq_hz": 2.0, "phase0": 0.0}],
            "units": [{"type": "linear", "name": "u", "inputs": {"sin(o)": 0.2, "obs[1]": -1.0}, "range": 1.0,
                       "tol": 0.05, "to": {"a0": 1.0}}]}
    text, data = summarize("hopper", spec)
    assert len(data["episodes"]) == 10 and "seed | d (m)" in text and "touchdowns" in text
    assert "u: " in text.split("saturated):")[1]
    trace = text.split("every 0.1 s:")[1].strip().splitlines()[1:]
    assert 1 <= len(trace) <= 15 and trace[0].startswith("0.00 |")
    assert summarize("hopper", {"error": "no reply was received"})[1]["error"] == "no reply was received"
    assert "do not match" in summarize("walker2d", spec)[1]["error"]
    assert json.dumps(data)


def test_rs_perturb_keeps_structure():
    import numpy as np
    import rs_proposer as rs
    spec = {"target": "cpg", "obs_dim": 11, "act_dim": 3, "hidden": 16,
            "oscillators": [{"name": "o", "freq_hz": 2.0, "phase0": 0.0}],
            "units": [{"type": "linear", "name": "u", "inputs": {"sin(o)": 0.5}, "range": 1.0, "tol": 0.05,
                       "to": {"a0": 1.0}}]}
    p = rs.perturb(spec, np.random.default_rng(0))
    assert p["obs_dim"] == 11 and p["units"][0]["range"] == 1.0 and p["units"][0]["tol"] == 0.05
    assert p["oscillators"][0]["name"] == "o" and p["units"][0]["type"] == "linear"
    assert p["oscillators"][0]["freq_hz"] != 2.0 and p["units"][0]["inputs"]["sin(o)"] != 0.5
