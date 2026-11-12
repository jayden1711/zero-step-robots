"""Target `cpg`: spec -> `cpg-v1` weights (docs/prereg-2026-11-09-cpg.md section 2). Deterministic, no learning.

Spec (JSON object):
  {"target": "cpg", "obs_dim": 11, "act_dim": 3, "hidden": 16,
   "oscillators": [                                       # at most 4
     {"name": "hop", "freq_hz": 2.0, "phase0": 0.0,       # natural frequency (Hz), initial phase (rad)
      "feedback": {"obs[1]": 0.5}}                         # optional: adds sum_i gain_i * obs[i] to d(phase)/dt (rad/s)
   ],
   "couplings": [                                         # optional
     {"from": "a", "to": "b", "weight": 2.0, "phase_lag": 3.1416}
        # adds  weight * sin(phase_from - phase_to - phase_lag)  to d(phase_to)/dt: pulls `to` towards lagging
        # `from` by phase_lag radians
   ],
   "bias": {"a0": 0.0},
   "units": [ ... ]                                       # the `linear` / `reflex` units of circuitc/compiler.py;
  }                                                       # inputs may also name "cos(hop)" and "sin(hop)"

The network computes, per step:  y = [cos ph_1, sin ph_1, ...];  h = tanh(W1 [obs; y] + b1);  a = clip(W2 h + b2);
then  ph <- ph + dt * (2 pi f + sum_j C_ij sin(ph_j - ph_i - Phi_ij) + S obs).
Oscillator inputs are mapped to input columns obs_dim + 2k (cos) and obs_dim + 2k + 1 (sin), and the units are
compiled by `compile_spec` unchanged, so their exactness guarantees are the same.
"""
import math
import re

import numpy as np

from .compiler import CompileError, _check_keys, _num, compile_spec, evaluate_spec

MAX_OSC = 4
_OSC_IN = re.compile(r"^(cos|sin)\((\w+)\)$")
_OBS = re.compile(r"^obs\[(\d+)\]$")
_NAME = re.compile(r"^\w+$")


def _obs_gains(d, obs_dim, where):
    g = np.zeros(obs_dim)
    if d is None:
        return g
    if not isinstance(d, dict):
        raise CompileError(f"{where}: must be an object like {{\"obs[1]\": 0.5}}")
    for k, v in d.items():
        m = _OBS.match(k)
        if not m or int(m.group(1)) >= obs_dim:
            raise CompileError(f"{where}: bad input name {k!r} (obs_dim={obs_dim}; oscillator feedback takes obs only)")
        g[int(m.group(1))] = _num(v, f"{where}.{k}")
    return g


def _oscillators(spec, obs_dim):
    oscs = spec.get("oscillators", [])
    if not isinstance(oscs, list):
        raise CompileError("'oscillators' must be a list")
    if len(oscs) > MAX_OSC:
        raise CompileError(f"{len(oscs)} oscillators; the architecture has at most {MAX_OSC}")
    names, f, th0, S = {}, [], [], []
    for k, o in enumerate(oscs):
        where = f"oscillators[{k}]"
        if not isinstance(o, dict):
            raise CompileError(f"{where}: must be an object")
        _check_keys(o, ("name", "freq_hz", "phase0", "feedback"), where)
        n = o.get("name")
        if not isinstance(n, str) or not _NAME.match(n) or n in names:
            raise CompileError(f"{where}: 'name' must be a unique identifier (letters, digits, _)")
        names[n] = k
        f.append(_num(o.get("freq_hz"), f"{where}.freq_hz"))
        th0.append(_num(o.get("phase0", 0.0), f"{where}.phase0"))
        S.append(_obs_gains(o.get("feedback"), obs_dim, f"{where}.feedback"))
    m = len(oscs)
    C, Phi = np.zeros((m, m)), np.zeros((m, m))
    cps = spec.get("couplings", [])
    if not isinstance(cps, list):
        raise CompileError("'couplings' must be a list")
    for k, c in enumerate(cps):
        where = f"couplings[{k}]"
        if not isinstance(c, dict):
            raise CompileError(f"{where}: must be an object")
        _check_keys(c, ("from", "to", "weight", "phase_lag"), where)
        if c.get("from") not in names or c.get("to") not in names or c["from"] == c["to"]:
            raise CompileError(f"{where}: 'from' and 'to' must name two different oscillators")
        i, j = names[c["to"]], names[c["from"]]
        if C[i, j] != 0.0:
            raise CompileError(f"{where}: duplicate coupling {c['from']} -> {c['to']}")
        C[i, j] = _num(c.get("weight"), f"{where}.weight")
        Phi[i, j] = _num(c.get("phase_lag", 0.0), f"{where}.phase_lag")
    S = np.array(S).reshape(m, obs_dim)
    return names, np.array(f), np.array(th0), C, Phi, S


def lower(spec):
    """Rewrite a cpg spec as a plain feedforward spec over the extended input [obs; y]. Returns (plain, osc)."""
    if not isinstance(spec, dict):
        raise CompileError("spec must be a JSON object")
    if spec.get("target") != "cpg":
        raise CompileError("spec: 'target' must be \"cpg\"")
    _check_keys(spec, ("target", "obs_dim", "act_dim", "hidden", "oscillators", "couplings", "bias", "units", "note"),
                "spec")
    obs_dim = spec.get("obs_dim")
    if not isinstance(obs_dim, int) or isinstance(obs_dim, bool) or obs_dim <= 0:
        raise CompileError("obs_dim must be a positive integer")
    names, f, th0, C, Phi, S = _oscillators(spec, obs_dim)
    units = spec.get("units")
    if not isinstance(units, list):
        raise CompileError("'units' must be a list")
    plain_units = []
    for i, u in enumerate(units):
        if not isinstance(u, dict) or not isinstance(u.get("inputs"), dict):
            plain_units.append(u)  # compile_spec reports the error
            continue
        ins = {}
        for k, v in u["inputs"].items():
            m = _OSC_IN.match(k)
            if m:
                if m.group(2) not in names:
                    raise CompileError(f"units[{i}]: input {k!r} names an unknown oscillator")
                k = f"obs[{obs_dim + 2 * names[m.group(2)] + (m.group(1) == 'sin')}]"
            elif not _OBS.match(k):
                raise CompileError(f"units[{i}]: bad input name {k!r} (use obs[i], cos(<osc>), sin(<osc>))")
            if k in ins:
                raise CompileError(f"units[{i}]: input {k!r} given twice")
            ins[k] = v
        plain_units.append({**u, "inputs": ins})
    plain = {k: spec[k] for k in ("act_dim", "hidden", "bias") if k in spec}
    plain.update({"obs_dim": obs_dim + 2 * len(names), "units": plain_units})
    return plain, {"names": names, "f": f, "theta0": th0, "C": C, "Phi": Phi, "S": S, "obs_dim": obs_dim}


def compile_cpg(spec):
    """Return (params, report): params is a `cpg-v1` dict of lists, ready for json.dump."""
    plain, osc = lower(spec)
    w, report = compile_spec(plain)
    for name, k in osc["names"].items():
        report.append({"oscillator": name, "index": k, "freq_hz": float(osc["f"][k]),
                       "input_columns": [osc["obs_dim"] + 2 * k, osc["obs_dim"] + 2 * k + 1]})
    params = {"format": "cpg-v1", "f": osc["f"], "C": osc["C"], "Phi": osc["Phi"], "S": osc["S"],
              "theta0": osc["theta0"], **w}
    return {k: (v.tolist() if isinstance(v, np.ndarray) else v) for k, v in params.items()}, report


def simulate_spec(spec, obs_seq, dt=0.008):
    """The spec's own meaning, computed directly from the spec (ideal units, phases integrated here), no weights.
    Returns the action sequence for a given observation sequence."""
    plain, osc = lower(spec)
    names = osc["names"]
    ph = osc["theta0"].copy()
    out = []
    for obs in obs_seq:
        obs = np.asarray(obs, float)
        y = np.empty(2 * len(names))
        y[0::2], y[1::2] = np.cos(ph), np.sin(ph)
        out.append(evaluate_spec(plain, np.concatenate([obs, y])))
        dph = 2 * math.pi * osc["f"].copy()
        for i in range(len(ph)):
            for j in range(len(ph)):
                dph[i] += osc["C"][i, j] * math.sin(ph[j] - ph[i] - osc["Phi"][i, j])
        ph = ph + dt * (dph + osc["S"] @ obs)
    return np.array(out)
