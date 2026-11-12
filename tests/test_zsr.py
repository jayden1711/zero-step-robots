import json
from pathlib import Path

import numpy as np
import pytest

from zsr import attempt
from zsr.harness import PythonController, evaluate
from zsr.policy import MLPPolicy, WeightError, n_params, random_policy, save_weights, load_weights, shapes, zero_policy
from zsr.tasks import TASKS

ROOT = Path(__file__).resolve().parent.parent


@pytest.mark.parametrize("task", TASKS)
def test_param_counts_and_roundtrip(task, tmp_path):
    pol = random_policy(task, 3)
    assert n_params(task) == sum(v.size for v in pol.p.values())
    save_weights(pol, tmp_path / "w.json")
    pol2 = load_weights(task, tmp_path / "w.json")
    obs = np.linspace(-1, 1, TASKS[task].obs_dim)
    assert np.allclose(pol.act(obs), pol2.act(obs))


def test_weight_validation():
    good = {k: np.zeros(s).tolist() for k, s in shapes("cartpole").items()}
    MLPPolicy("cartpole", good)
    bad_shape = dict(good, W1=[[0.0] * 3] * 16)
    with pytest.raises(WeightError):
        MLPPolicy("cartpole", bad_shape)
    with pytest.raises(WeightError):
        MLPPolicy("cartpole", {k: v for k, v in good.items() if k != "b2"})
    with pytest.raises(WeightError):
        MLPPolicy("cartpole", dict(good, extra=[1]))
    with pytest.raises(WeightError):
        MLPPolicy("cartpole", dict(good, b2=[float("nan")]))


def test_action_clipped():
    p = {k: np.zeros(s) for k, s in shapes("cartpole").items()}
    p["b2"] = np.array([100.0])
    assert MLPPolicy("cartpole", p).act(np.zeros(4))[0] == 3.0


def test_evaluation_is_deterministic():
    a = evaluate("hopper", random_policy("hopper", 1), 3)
    b = evaluate("hopper", random_policy("hopper", 1), 3)
    assert a["episodes"] == b["episodes"]


def test_reference_controller_solves_cartpole():
    r = evaluate("cartpole", PythonController("cartpole", ROOT / "controllers/cartpole_reference.py"), 5)
    assert r["frac_full_length"] == 1.0 and r["mean_return"] == 1000


def test_hopper_reference_runs():
    r = evaluate("hopper", PythonController("hopper", ROOT / "controllers/hopper_reference.py"), 3)
    assert r["n_faults"] == 0 and r["mean_return"] > 0


def test_crashing_controller_is_scored_and_logged(tmp_path):
    f = tmp_path / "c.py"
    f.write_text("def act(obs):\n    raise RuntimeError('boom')\n")
    r = evaluate("cartpole", PythonController("cartpole", f), 2)
    assert r["n_faults"] == 2 and "boom" in r["first_fault"] and r["mean_return"] == 0


def test_prompts_filled_and_stable():
    for task in attempt.PROMPT_TASKS:
        for mode in attempt.MODES:
            p = attempt.build_prompt(task, mode)
            assert "{{" not in p
            assert p == attempt.build_prompt(task, mode)
    assert f"{n_params('hopper')} numbers in total" in attempt.build_prompt("hopper", "weights")


def test_strict_arm_has_no_sensor_names_and_named_arm_does():
    banned = ("angle", "height", "torso", "cart", "pole", "thigh", "foot", "Gymnasium", "MuJoCo")
    for task in attempt.PROMPT_TASKS:
        for mode in attempt.MODES:
            strict = attempt.build_prompt(task, mode, "strict")
            assert "{{" not in strict
            low = strict.lower()
            assert not [w for w in banned if w.lower() in low], (task, mode)
            assert attempt.prompt_hash(task, mode, "strict") != attempt.prompt_hash(task, mode, "named")
    assert "cart position" in attempt.build_prompt("cartpole", "weights", "named")


def test_prompt_has_no_numbers_from_solutions():
    # Fairness guard: the prompt must not contain any constant from the reference controllers.
    p = "".join(attempt.build_prompt(t, "weights", a) for t in TASKS for a in attempt.ARMS
            if attempt.arm_valid(t, a) and a not in attempt.LEVELS)
    for token in ("12.0", "2.37", "1.4", "K ="):
        assert token not in p


def test_attempt_lifecycle_weights_and_failures(tmp_path):
    d = attempt.new_attempt("t1", "cartpole", "weights", "none", "test", tmp_path)
    meta = json.loads((d / "meta.json").read_text())
    assert meta["prompt_sha256"] == attempt.prompt_hash("cartpole", "weights")
    assert meta["arm"] == "strict" and meta["prompt_version"] == "v2"
    dn = attempt.new_attempt("t1n", "cartpole", "weights", "none", "test", tmp_path, "named")
    mn = json.loads((dn / "meta.json").read_text())
    assert mn["arm"] == "named" and mn["prompt_version"] == "v1"
    with pytest.raises(FileExistsError):
        attempt.new_attempt("t1", "cartpole", "weights", "none", "test", tmp_path)
    w = json.dumps(zero_policy("cartpole").to_json())
    (d / "reply.md").write_text(f"draft\n```json\n{{}}\n```\nfinal\n```json\n{w}\n```\n")
    r = attempt.score_attempt(d, 3)
    assert r["failure"] is None and r["n_episodes"] == 3  # the last block wins

    d2 = attempt.new_attempt("t2", "cartpole", "weights", "none", "test", tmp_path)
    (d2 / "reply.md").write_text("I refuse to write numbers")
    r2 = attempt.score_attempt(d2, 3)
    assert r2["failure"] and (d2 / "score.json").exists()

    d3 = attempt.new_attempt("t3", "cartpole", "controller", "none", "test", tmp_path)
    (d3 / "reply.md").write_text("```python\ndef act(obs):\n    return [obs[1] * 10]\n```")
    assert attempt.score_attempt(d3, 3)["failure"] is None
