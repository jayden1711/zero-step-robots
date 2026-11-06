"""Spec -> weights. Deterministic, no learning. Anything the architecture cannot express is a CompileError.

Spec (JSON object):
  {"obs_dim": 4, "act_dim": 1, "hidden": 16,
   "bias": {"a0": 0.0},                                  # optional constant action offsets
   "units": [
     {"type": "linear", "name": "...", "inputs": {"obs[1]": 12.0, "obs[3]": 1.5}, "range": 0.5, "tol": 0.01,
      "to": {"a0": 1.0}},
        # contributes   to[a] * sum_i inputs[i]*obs[i]   to action a, as an ideal linear term. It is realised by one
        # tanh unit used inside its linear range, so it is exact only up to a bound the compiler computes and checks:
        # for |sum| <= range the relative error is <= tol. Outside `range` the unit saturates (reported, not hidden).
     {"type": "reflex", "name": "...", "inputs": {"obs[0]": 1.0}, "threshold": 0.7, "sharpness": 20.0,
      "to": {"a0": 1.0}}
        # contributes   to[a] * tanh(sharpness * (sum_i inputs[i]*obs[i] - threshold))   to action a. Exact.
   ]}
Unsupported types (e.g. "oscillator": this architecture has no time/phase input or recurrence) are errors.
"""
import math
import re

import numpy as np

_IN = re.compile(r"^obs\[(\d+)\]$")
_ACT = re.compile(r"^a(\d+)$")
SUPPORTED = ("linear", "reflex")
MAX_ABS_WEIGHT = 1e4


class CompileError(ValueError):
    pass


def _check_keys(d, allowed, where):
    extra = set(d) - set(allowed)
    if extra:
        raise CompileError(f"{where}: unexpected keys {sorted(extra)}")


def _num(x, where):
    if isinstance(x, bool) or not isinstance(x, (int, float)) or not math.isfinite(x):
        raise CompileError(f"{where}: expected a finite number, got {x!r}")
    return float(x)


def _inputs(u, obs_dim, where):
    if not isinstance(u.get("inputs"), dict) or not u["inputs"]:
        raise CompileError(f"{where}: 'inputs' must be a non-empty object like {{\"obs[2]\": -3.0}}")
    w = np.zeros(obs_dim)
    for k, v in u["inputs"].items():
        m = _IN.match(k)
        if not m or int(m.group(1)) >= obs_dim:
            raise CompileError(f"{where}: bad input name {k!r} (obs_dim={obs_dim})")
        w[int(m.group(1))] = _num(v, f"{where}.inputs.{k}")
    return w


def _targets(u, act_dim, where):
    if not isinstance(u.get("to"), dict) or not u["to"]:
        raise CompileError(f"{where}: 'to' must be a non-empty object like {{\"a0\": 1.0}}")
    c = np.zeros(act_dim)
    for k, v in u["to"].items():
        m = _ACT.match(k)
        if not m or int(m.group(1)) >= act_dim:
            raise CompileError(f"{where}: bad action name {k!r} (act_dim={act_dim})")
        c[int(m.group(1))] = _num(v, f"{where}.to.{k}")
    return c


def parse(spec):
    if not isinstance(spec, dict):
        raise CompileError("spec must be a JSON object")
    _check_keys(spec, ("obs_dim", "act_dim", "hidden", "bias", "units", "note"), "spec")
    for k in ("obs_dim", "act_dim", "hidden", "units"):
        if k not in spec:
            raise CompileError(f"spec: missing '{k}'")
    obs_dim, act_dim, hidden = spec["obs_dim"], spec["act_dim"], spec["hidden"]
    if not all(isinstance(x, int) and not isinstance(x, bool) and x > 0 for x in (obs_dim, act_dim, hidden)):
        raise CompileError("obs_dim, act_dim, hidden must be positive integers")
    bias = np.zeros(act_dim)
    for k, v in (spec.get("bias") or {}).items():
        m = _ACT.match(k)
        if not m or int(m.group(1)) >= act_dim:
            raise CompileError(f"bias: bad action name {k!r}")
        bias[int(m.group(1))] = _num(v, f"bias.{k}")
    if not isinstance(spec["units"], list):
        raise CompileError("'units' must be a list")
    if len(spec["units"]) > hidden:
        raise CompileError(f"{len(spec['units'])} units but the architecture has only {hidden} hidden units")
    units = []
    for i, u in enumerate(spec["units"]):
        where = f"units[{i}]"
        if not isinstance(u, dict):
            raise CompileError(f"{where}: must be an object")
        t = u.get("type")
        if t not in SUPPORTED:
            raise CompileError(f"{where}: type {t!r} is not expressible in this architecture (supported: {SUPPORTED})")
        w, c = _inputs(u, obs_dim, where), _targets(u, act_dim, where)
        if t == "linear":
            _check_keys(u, ("type", "name", "inputs", "range", "tol", "to"), where)
            r, tol = _num(u.get("range"), f"{where}.range"), _num(u.get("tol", 0.01), f"{where}.tol")
            if r <= 0 or not 0 < tol < 1:
                raise CompileError(f"{where}: need range > 0 and 0 < tol < 1")
            units.append({"type": t, "name": u.get("name", f"u{i}"), "w": w, "c": c, "range": r, "tol": tol})
        else:
            _check_keys(u, ("type", "name", "inputs", "threshold", "sharpness", "to"), where)
            k = _num(u.get("sharpness"), f"{where}.sharpness")
            if k <= 0:
                raise CompileError(f"{where}: sharpness must be > 0")
            units.append({"type": t, "name": u.get("name", f"u{i}"), "w": w, "c": c, "k": k,
                          "theta": _num(u.get("threshold"), f"{where}.threshold")})
    return obs_dim, act_dim, hidden, bias, units


def compile_spec(spec):
    """Return (params, report). params = {'W1','b1','W2','b2'} as float64 arrays."""
    obs_dim, act_dim, hidden, bias, units = parse(spec)
    W1, b1 = np.zeros((hidden, obs_dim)), np.zeros(hidden)
    W2, b2, report = np.zeros((act_dim, hidden)), bias.copy(), []
    for j, u in enumerate(units):
        if u["type"] == "linear":
            # tanh(s z)/s ~ z with relative error <= (s r)^2/3 on |z| <= r  (tanh x >= x - x^3/3)
            s = math.sqrt(3 * u["tol"]) / u["range"]
            W1[j], W2[:, j] = s * u["w"], u["c"] / s
            report.append({"unit": j, "name": u["name"], "type": "linear", "scale": s, "rel_error_bound": u["tol"],
                           "valid_for_abs_input_below": u["range"]})
        else:
            W1[j], b1[j], W2[:, j] = u["k"] * u["w"], -u["k"] * u["theta"], u["c"]
            report.append({"unit": j, "name": u["name"], "type": "reflex", "rel_error_bound": 0.0})
    for name, a in (("W1", W1), ("b1", b1), ("W2", W2), ("b2", b2)):
        if np.abs(a).max(initial=0.0) > MAX_ABS_WEIGHT:
            raise CompileError(f"{name} would need |weight| > {MAX_ABS_WEIGHT}: relax range/tol or sharpness")
    return {"W1": W1, "b1": b1, "W2": W2, "b2": b2}, report


def forward(params, obs):
    return params["W2"] @ np.tanh(params["W1"] @ np.asarray(obs, float) + params["b1"]) + params["b2"]


def evaluate_spec(spec, obs):
    """The spec's own meaning, computed directly (ideal linear terms, exact reflexes), without any weights."""
    obs_dim, act_dim, _, bias, units = parse(spec)
    obs = np.asarray(obs, float)
    a = bias.copy()
    for u in units:
        z = float(u["w"] @ obs)
        a += u["c"] * (z if u["type"] == "linear" else math.tanh(u["k"] * (z - u["theta"])))
    return a
