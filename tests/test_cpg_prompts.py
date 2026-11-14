import json

import pytest

from zsr import attempt


@pytest.mark.parametrize("task", attempt.CPG_TASKS)
def test_levels_render_nest_and_differ(task):
    p = {lv: attempt.build_prompt(task, "cpgspec", lv) for lv in attempt.LEVELS}
    for lv, text in p.items():
        assert "{{" not in text and text == attempt.build_prompt(task, "cpgspec", lv)
        assert "mean of d is at least 3 m" in text  # the score is distance, not the env reward
    assert "Design hint" not in p["H0"] and "Design hint" in p["H1"] and "Facts and ranges" not in p["H1"]
    h1 = open(attempt.PROMPTS / f"hint_{task}_H1_v3.md").read().strip()
    assert h1 in p["H1"] and h1 in p["H2"] and "Facts and ranges" in p["H2"]
    assert len({attempt.prompt_hash(task, "cpgspec", lv) for lv in attempt.LEVELS}) == 3


def test_modes_and_levels_go_together():
    with pytest.raises(ValueError):
        attempt.build_prompt("hopper", "weights", "H1")
    with pytest.raises(ValueError):
        attempt.build_prompt("hopper", "cpgspec", "strict")
    with pytest.raises(ValueError):
        attempt.build_prompt("cartpole", "cpgspec", "H0")


def test_frozen_hashes_match():
    """prompts/SHA256SUMS-cpg.txt freezes the v3 files (prereg section 4); a released file is never edited."""
    import hashlib
    for line in (attempt.PROMPTS / "SHA256SUMS-cpg.txt").read_text().splitlines():
        h, name = line.split()
        assert hashlib.sha256((attempt.PROMPTS / name).read_bytes()).hexdigest() == h, name


def test_cpgspec_reply_is_compiled_and_scored(tmp_path):
    d = attempt.new_attempt("t1", "hopper", "cpgspec", "fake", "test", tmp_path, arm="H0")
    meta = json.loads((d / "meta.json").read_text())
    assert meta["prompt_version"] == "v3" and meta["arm"] == "H0"
    spec = {"target": "cpg", "obs_dim": 11, "act_dim": 3, "hidden": 16,
            "oscillators": [{"name": "o", "freq_hz": 2.0, "phase0": 0.0}],
            "units": [{"type": "reflex", "inputs": {"sin(o)": 1.0}, "threshold": 0.0, "sharpness": 1.0,
                       "to": {"a1": 0.1}}]}
    (d / "reply.md").write_text("draft\n```json\n{}\n```\nfinal\n```json\n" + json.dumps(spec) + "\n```\n")
    r = attempt.score_attempt(d, episodes=2)
    assert r["failure"] is None and "mean_distance_healthy" in r and (d / "parsed.cpg.json").exists()


def test_bad_spec_is_a_logged_failure(tmp_path):
    d = attempt.new_attempt("t2", "walker2d", "cpgspec", "fake", "test", tmp_path, arm="H2")
    (d / "reply.md").write_text('```json\n{"target": "cpg", "obs_dim": 11, "act_dim": 3, "hidden": 16, "units": []}\n```')
    r = attempt.score_attempt(d, episodes=2)
    assert "do not match" in r["failure"] and json.loads((d / "score.json").read_text())["failure"]
