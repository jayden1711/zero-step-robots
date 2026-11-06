import json
from pathlib import Path

import numpy as np
import pytest

from circuitc import CompileError, compile_spec, evaluate_spec, forward

EX = Path(__file__).resolve().parent.parent / "circuitc" / "examples"
RNG = np.random.default_rng(0)


def base(units, **kw):
    return {"obs_dim": 3, "act_dim": 2, "hidden": 4, "units": units, **kw}


def test_reflex_is_exact():
    spec = base([{"type": "reflex", "inputs": {"obs[0]": 2.0, "obs[2]": -1.0}, "threshold": 0.3, "sharpness": 7.0,
                  "to": {"a1": -2.5}}], bias={"a0": 0.1})
    p, _ = compile_spec(spec)
    for obs in RNG.normal(size=(200, 3)):
        assert np.allclose(forward(p, obs), evaluate_spec(spec, obs), atol=1e-12)


def test_linear_within_declared_tolerance_and_saturates_outside():
    spec = base([{"type": "linear", "inputs": {"obs[1]": 4.0, "obs[2]": -1.0}, "range": 2.0, "tol": 0.02,
                  "to": {"a0": 1.5, "a1": -0.5}}])
    p, rep = compile_spec(spec)
    assert rep[0]["rel_error_bound"] == 0.02
    for _ in range(500):
        obs = RNG.normal(size=3)
        z = 4.0 * obs[1] - obs[2]
        if abs(z) <= 2.0:
            ideal, got = evaluate_spec(spec, obs), forward(p, obs)
            assert np.all(np.abs(got - ideal) <= 0.02 * np.abs(ideal) + 1e-12)
    far = np.array([0.0, 50.0, 0.0])  # outside range: saturates, is not linear any more
    assert abs(forward(p, far)[0]) < abs(evaluate_spec(spec, far)[0]) / 5


def test_additive_units_and_bias():
    spec = base([{"type": "linear", "inputs": {"obs[0]": 1.0}, "range": 1.0, "to": {"a0": 1.0}},
                 {"type": "reflex", "inputs": {"obs[0]": 1.0}, "threshold": 0.0, "sharpness": 3.0, "to": {"a0": 1.0}}],
                bias={"a0": -0.2, "a1": 0.4})
    p, _ = compile_spec(spec)
    obs = np.array([0.05, 0, 0])
    ideal = evaluate_spec(spec, obs)
    assert ideal[1] == 0.4 and abs(ideal[0] - (-0.2 + 0.05 + np.tanh(0.15))) < 1e-12
    assert np.allclose(forward(p, obs), ideal, atol=0.01 * 0.05 + 1e-9)


@pytest.mark.parametrize("bad", [
    base([{"type": "oscillator", "frequency": 2.0}]),  # no time/phase input or recurrence in this architecture
    base([{"type": "linear", "inputs": {"obs[3]": 1.0}, "range": 1, "to": {"a0": 1}}]),  # obs out of range
    base([{"type": "linear", "inputs": {"obs[0]": 1.0}, "range": 1, "to": {"a2": 1}}]),  # action out of range
    base([{"type": "linear", "inputs": {"obs[0]": 1.0}, "range": 1, "to": {"a0": 1}}] * 5),  # more units than hidden
    base([{"type": "linear", "inputs": {"obs[0]": 1.0}, "range": 0, "to": {"a0": 1}}]),
    base([{"type": "linear", "inputs": {"obs[0]": 1.0}, "range": 1, "to": {"a0": 1}, "extra": 1}]),
    base([{"type": "reflex", "inputs": {"obs[0]": 1.0}, "threshold": 0, "sharpness": -1, "to": {"a0": 1}}]),
    base([{"type": "linear", "inputs": {"obs[0]": float("nan")}, "range": 1, "to": {"a0": 1}}]),
    base([{"type": "linear", "inputs": {"obs[0]": 1.0}, "range": 1e-9, "tol": 1e-9, "to": {"a0": 1}}]),  # weights too big
])
def test_unsupported_is_an_error_not_an_approximation(bad):
    with pytest.raises(CompileError):
        compile_spec(bad)


@pytest.mark.parametrize("name,task", [("cartpole_pd", "cartpole"), ("hopper_pd_hold", "hopper")])
def test_examples_compile_and_load_in_the_harness(name, task, tmp_path):
    from zsr.policy import MLPPolicy
    spec = json.loads((EX / f"{name}.json").read_text())
    p, _ = compile_spec(spec)
    pol = MLPPolicy(task, p)  # shapes and finiteness validated by the same loader every arm uses
    obs = RNG.normal(scale=0.05, size=spec["obs_dim"])
    assert np.allclose(pol.act(obs), evaluate_spec(spec, obs), atol=0.01 * np.abs(evaluate_spec(spec, obs)).max() + 1e-9)
