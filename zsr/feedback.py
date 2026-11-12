"""Feedback summary for the CPG feedback arm (docs/prereg-2026-11-10-cpg-feedback.md section 3). Dev seeds only.

    python -m zsr.feedback <task> SPEC.json OUT.txt [--json OUT.json]

SPEC.json is a cpg spec (compiled here) or {"error": "..."} for a reply that did not parse; a compile error becomes the
summary. The text layout is fixed; OUT.json holds the same numbers for the report and the random-search baselines.
"""
import argparse
import json
import math
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from circuitc import CompileError, compile_cpg  # noqa: E402
from circuitc.cpg import lower  # noqa: E402

from .cpg import CPGPolicy  # noqa: E402
from .tasks import TASKS, make_env  # noqa: E402

DEV_SEEDS = tuple(range(10))
CLEAN_M = 3.0
FEET = {"hopper": ("foot_geom",), "walker2d": ("foot_geom", "foot_left_geom")}
FOOT_LABEL = {"hopper": ("foot",), "walker2d": ("right foot", "left foot")}
JOINTS = {"hopper": ("thigh", "leg", "foot"),
          "walker2d": ("right thigh", "right leg", "right foot", "left thigh", "left leg", "left foot")}


def end_reason(task, env, steps, max_steps):
    if steps >= max_steps:
        return "cut off at 1000 steps"
    u = env.unwrapped
    z, ang = float(u.data.qpos[1]), float(u.data.qpos[2])
    if task == "hopper":
        if not z > 0.7:
            return "height too low"
        if not abs(ang) < 0.2:
            return "torso angle out of range"
        return "state out of range"
    if not z > 0.8:
        return "height too low"
    if not z < 2.0:
        return "height too high"
    if not -1.0 < ang < 1.0:
        return "torso angle out of range"
    return "state out of range"


def contacts(task, env):
    m, d = env.unwrapped.model, env.unwrapped.data
    feet = [m.geom(n).id for n in FEET[task]]
    floor = m.geom("floor").id
    on = [False] * len(feet)
    for i in range(d.ncon):
        g1, g2 = d.contact[i].geom1, d.contact[i].geom2
        for k, f in enumerate(feet):
            if {g1, g2} == {f, floor}:
                on[k] = True
    return on


def episode(task, env, pol, seed, detail=False, lin=None):
    obs, _ = env.reset(seed=seed)
    pol.reset()
    u = env.unwrapped
    x0 = float(u.data.qpos[0])
    x_h, steps, t = x0, 0, TASKS[task]
    rec = {"q": [], "a": [], "pitch": [], "z": [], "contact": [], "trace": [], "lin_out": None}
    lin_out = np.zeros(len(lin)) if lin else None
    while True:
        if detail:
            on = contacts(task, env)
            if lin:
                xin = np.concatenate([np.asarray(obs, float), pol.osc_out()])
                for k, (w, r) in enumerate(lin):
                    lin_out[k] += abs(float(w @ xin)) > r
            if len(rec["trace"]) < 15 and steps * u.dt >= 0.1 * len(rec["trace"]) - 1e-9:  # first step at/after each 0.1 s
                rec["trace"].append((steps * u.dt, float(u.data.qpos[0]) - x0, float(u.data.qpos[1]),
                                     float(u.data.qpos[2]), on, [float(p) % (2 * math.pi) for p in pol.theta]))
        a = pol.act(obs)
        if detail:
            rec["q"].append(np.asarray(u.data.qpos[3:3 + t.act_dim], float).copy())
            rec["a"].append(np.asarray(a, float))
            rec["pitch"].append(float(u.data.qpos[2]))
            rec["z"].append(float(u.data.qpos[1]))
            rec["contact"].append(on)
        obs, _, term, trunc, _ = env.step(np.asarray(a, np.float32))
        steps += 1
        if not term:
            x_h = float(u.data.qpos[0])
        if term or trunc:
            break
    out = {"seed": seed, "d": x_h - x0, "time": steps * u.dt, "steps": steps,
           "end": end_reason(task, env, steps, t.max_steps)}
    if detail:
        if lin:
            rec["lin_out"] = (lin_out / max(steps, 1)).tolist()
        out["detail"] = rec
    return out


def linear_units(spec):
    plain, _ = lower(spec)
    res = []
    for u in plain["units"]:
        if u.get("type") != "linear":
            continue
        w = np.zeros(plain["obs_dim"])
        for k, v in u["inputs"].items():
            w[int(k[4:-1])] = float(v)
        res.append((u.get("name", ""), w, float(u["range"])))
    return res


def summarize(task, spec, cpg_out=None):
    """Return (text, data). data['error'] is set when there is no controller. cpg_out: also write the compiled weights."""
    if not isinstance(spec, dict) or "error" in spec and "target" not in spec:
        msg = spec.get("error") if isinstance(spec, dict) else "reply has no valid spec"
        return f"Your design could not be tested: {msg}\n", {"error": msg}
    try:
        t = TASKS[task]
        if (spec.get("obs_dim"), spec.get("act_dim"), spec.get("hidden")) != (t.obs_dim, t.act_dim, 16):
            raise CompileError(f"spec dims {spec.get('obs_dim')}/{spec.get('act_dim')}/{spec.get('hidden')} do not "
                               f"match the task ({t.obs_dim}/{t.act_dim}/16)")
        params, _ = compile_cpg(spec)
        pol = CPGPolicy(task, params)
        if cpg_out:
            Path(cpg_out).write_text(json.dumps(params, indent=1))
        lin = linear_units(spec)
    except Exception as e:  # compile or load error is the feedback
        msg = f"{type(e).__name__}: {e}"
        return f"Your design could not be tested: {msg}\n", {"error": msg}
    env = make_env(task)
    eps = [episode(task, env, pol, s, detail=(s == 0), lin=[(w, r) for _, w, r in lin]) for s in DEV_SEEDS]
    env.close()
    ds = np.array([e["d"] for e in eps])
    ts = np.array([e["time"] for e in eps])
    L = ["Test results on 10 practice episodes (seeds 0 to 9; the scored episodes are different).", "",
         "Per episode:", "seed | d (m) | time survived (s) | how it ended"]
    L += [f"{e['seed']} | {e['d']:.2f} | {e['time']:.2f} | {e['end']}" for e in eps]
    speed = float(np.mean(ds / np.maximum(ts, 1e-9)))
    L += ["", f"Over the 10 episodes: mean d {ds.mean():.2f} m, min {ds.min():.2f}, max {ds.max():.2f}; mean time survived "
          f"{ts.mean():.2f} s; mean forward speed {speed:.2f} m/s; episodes with d >= 3 m: {int((ds >= CLEAN_M).sum())}"]
    det = eps[0]["detail"]
    q, a = np.array(det["q"]), np.array(det["a"])
    L += ["", "Episode seed 0 in detail:", "joint | min angle (rad) | max angle (rad) | mean |action| | fraction of steps "
          "with |action| >= 0.99"]
    for j, name in enumerate(JOINTS[task]):
        L.append(f"{name} | {q[:, j].min():.3f} | {q[:, j].max():.3f} | {np.abs(a[:, j]).mean():.2f} | "
                 f"{(np.abs(a[:, j]) >= 0.99).mean():.2f}")
    L.append(f"torso angle min {min(det['pitch']):.3f}, max {max(det['pitch']):.3f} rad; torso height min "
             f"{min(det['z']):.2f}, max {max(det['z']):.2f} m")
    c = np.array(det["contact"], bool).reshape(len(det["contact"]), -1)
    for k, lab in enumerate(FOOT_LABEL[task]):
        col = c[:, k]
        onsets = int(col[0]) + int(np.sum(col[1:] & ~col[:-1]))
        L.append(f"{lab}: on the ground {col.mean():.2f} of the steps, {onsets} touchdowns")
    L += ["", "First 1.5 s of episode seed 0, every 0.1 s:",
          "time (s) | x (m) | torso height (m) | torso angle (rad) | " + " | ".join(f"{lab} contact" for lab in FOOT_LABEL[task])
          + " | oscillator phase(s) mod 2 pi"]
    for (tm, x, z, ang, on, ph) in det["trace"]:
        L.append(f"{tm:.2f} | {x:.2f} | {z:.2f} | {ang:.3f} | " + " | ".join("yes" if o else "no" for o in on)
                 + " | " + (", ".join(f"{p:.2f}" for p in ph) if ph else "none"))
    if lin:
        L += ["", "Linear units, fraction of steps of episode seed 0 with |input sum| > declared range (saturated):"]
        L += [f"{n or f'unit {i}'}: {f:.2f}" for i, ((n, _, _), f) in enumerate(zip(lin, det["lin_out"]))]
    data = {"episodes": [{k: v for k, v in e.items() if k != "detail"} for e in eps], "mean_d": float(ds.mean()),
            "mean_time": float(ts.mean()), "n_clean": int((ds >= CLEAN_M).sum())}
    return "\n".join(L) + "\n", data


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("task", choices=("hopper", "walker2d"))
    ap.add_argument("spec")
    ap.add_argument("out")
    ap.add_argument("--json")
    ap.add_argument("--cpg-out", help="write the compiled cpg-v1 weights here (for held-out scoring)")
    a = ap.parse_args()
    try:
        spec = json.loads(Path(a.spec).read_text())
    except (OSError, ValueError) as e:
        spec = {"error": f"could not read the spec ({type(e).__name__})"}
    text, data = summarize(a.task, spec, a.cpg_out)
    Path(a.out).write_text(text)
    if a.json:
        Path(a.json).write_text(json.dumps(data, indent=1))
    print(text)


if __name__ == "__main__":
    main()
