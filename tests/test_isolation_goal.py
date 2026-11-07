import importlib.util
import json
from pathlib import Path

import pytest

from zsr import attempt

ROOT = Path(__file__).resolve().parent.parent
spec = importlib.util.spec_from_file_location("run_pilot", ROOT / "scripts" / "run_pilot.py")
run_pilot = importlib.util.module_from_spec(spec)
spec.loader.exec_module(run_pilot)


@pytest.fixture
def home(tmp_path, monkeypatch):
    h = tmp_path / "home"
    h.mkdir()
    monkeypatch.setenv("HOME", str(h))
    return h


def test_preflight_passes_on_clean_tree(tmp_path, home):
    d = tmp_path / "a" / "b"
    d.mkdir(parents=True)
    run_pilot.preflight(d)


@pytest.mark.parametrize("name", ["CLAUDE.md", "CLAUDE.local.md", ".claude"])
def test_preflight_refuses_instruction_file_in_ancestor_or_cwd(tmp_path, home, name):
    d = tmp_path / "a" / "b"
    d.mkdir(parents=True)
    for where in (tmp_path, tmp_path / "a", d):
        p = where / name
        p.mkdir() if name == ".claude" else p.write_text("x")
        with pytest.raises(SystemExit, match="pre-flight FAILED"):
            run_pilot.preflight(d)
        p.rmdir() if name == ".claude" else p.unlink()
    run_pilot.preflight(d)


def test_preflight_refuses_user_claude_md(tmp_path, home):
    (home / ".claude").mkdir()
    (home / ".claude" / "CLAUDE.md").write_text("x")
    with pytest.raises(SystemExit, match="pre-flight FAILED"):
        run_pilot.preflight(tmp_path)


def test_goal_arm_is_strict_plus_one_sentence_hopper_only():
    strict = attempt.build_prompt("hopper", "weights", "strict")
    goal = attempt.build_prompt("hopper", "weights", "goal")
    sentence = (ROOT / "prompts" / "goal_hopper_v2.md").read_text().strip()
    assert sentence.count("\n") == 0 and sentence.count(".") == 1  # one sentence
    assert goal.replace("\n\n" + sentence, "", 1) == strict  # nothing else changed
    assert "forward" in sentence and "{{" not in goal
    for mode in attempt.MODES:
        assert attempt.prompt_hash("hopper", mode, "goal") != attempt.prompt_hash("hopper", mode, "strict")
    with pytest.raises(ValueError):
        attempt.build_prompt("cartpole", "weights", "goal")


def test_goal_attempt_meta_and_extra(tmp_path):
    d = attempt.new_attempt("g1", "hopper", "controller", "m", "test", tmp_path, "goal", {"isolation": "x"})
    m = json.loads((d / "meta.json").read_text())
    assert m["arm"] == "goal" and m["prompt_version"] == "v2" and m["isolation"] == "x"
    assert "goal_hopper_v2.md" in m["template_sha256"]
