import json

import numpy as np
import pytest

from circuitc import CompileError, compile_cpg, simulate_spec
from zsr.cpg import CPGError, CPGPolicy, DT
from zsr.harness import evaluate
from zsr.tasks import make_env

RNG = np.random.default_rng(1)


def spec(**kw):
    s = {"target": "cpg", "obs_dim": 11, "act_dim": 3, "hidden": 16,
         "oscillators": [{"name": "a", "freq_hz": 2.0, "phase0": 0.3, "feedback": {"obs[1]": 1.5}},
                         {"name": "b", "freq_hz": 1.7, "phase0": -1.0}],
         "couplings": [{"from": "a", "to": "b", "weight": 3.0, "phase_lag": 2.5},
                       {"from": "b", "to": "a", "weight": 1.0, "phase_lag": -2.5}],
         "bias": {"a2": 0.05},
         "units": [{"type": "reflex", "inputs": {"sin(a)": 2.0, "obs[3]": -1.0}, "threshold": 0.1, "sharpness": 3.0,
                    "to": {"a0": 0.4}},
                   {"type": "reflex", "inputs": {"cos(b)": 1.0}, "threshold": 0.0, "sharpness": 1.0,
                    "to": {"a1": -0.3, "a2": 0.2}}]}
    s.update(kw)
    return s


def test_env_dt_matches():
    for t in ("hopper", "walker2d"):
        env = make_env(t)
        assert env.unwrapped.dt == pytest.approx(DT)


def test_compiled_cpg_matches_spec_over_time():
    s = spec()
    params, rep = compile_cpg(json.loads(json.dumps(s)))
    pol = CPGPolicy("hopper", json.loads(json.dumps(params)))
    obs_seq = RNG.normal(scale=0.3, size=(300, 11))
    ideal = np.clip(simulate_spec(s, obs_seq), -1, 1)
    got = np.array([pol.act(o) for o in obs_seq])
    assert np.allclose(got, ideal, atol=1e-10)
    pol.reset()  # reset restores the initial phases
    assert np.allclose(pol.act(obs_seq[0]), ideal[0], atol=1e-10)


def test_uncoupled_oscillator_runs_at_its_frequency():
    s = spec(oscillators=[{"name": "a", "freq_hz": 2.5, "phase0": 0.0}], couplings=[],
             units=[{"type": "linear", "inputs": {"sin(a)": 1.0}, "range": 1.0, "tol": 0.001, "to": {"a0": 1.0}}])
    pol = CPGPolicy("hopper", compile_cpg(s)[0])
    n = int(round(1 / 2.5 / DT))  # 50 steps = one period
    for _ in range(n):
        pol.act(np.zeros(11))
    assert pol.theta[0] == pytest.approx(2 * np.pi)


@pytest.mark.parametrize("bad, msg", [
    ({"oscillators": [{"name": f"o{i}", "freq_hz": 1.0} for i in range(5)]}, "at most 4"),
    ({"couplings": [{"from": "a", "to": "a", "weight": 1.0}]}, "two different"),
    ({"couplings": [{"from": "a", "to": "zz", "weight": 1.0}]}, "two different"),
    ({"units": [{"type": "reflex", "inputs": {"cos(zz)": 1.0}, "threshold": 0, "sharpness": 1, "to": {"a0": 1}}]},
     "unknown oscillator"),
    ({"units": [{"type": "oscillator", "inputs": {"obs[0]": 1.0}, "to": {"a0": 1}}]}, "not expressible"),
    ({"oscillators": [{"name": "a", "freq_hz": 1.0, "feedback": {"sin(a)": 1.0}}], "couplings": []}, "obs only"),
    ({"target": "mlp"}, "target"),
])
def test_compile_errors(bad, msg):
    with pytest.raises(CompileError, match=msg):
        compile_cpg(spec(**bad))


def test_policy_rejects_bad_files():
    params = compile_cpg(spec())[0]
    with pytest.raises(CPGError):
        CPGPolicy("hopper", {**params, "format": "x"})
    with pytest.raises(CPGError):
        CPGPolicy("walker2d", params)  # wrong obs width for walker2d


def test_zero_oscillators_and_harness_metric():
    s = spec(oscillators=[], couplings=[], units=[])
    pol = CPGPolicy("hopper", compile_cpg(s)[0])
    r = evaluate("hopper", pol, n_episodes=2)
    for e in r["episodes"]:
        assert e["length"] < 1000 and abs(e["distance_healthy"]) <= abs(e["distance"]) + 0.5
    assert r["n_clean_3m"] == 0 and r["passes_3m"] is False
