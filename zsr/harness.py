"""Scoring harness. One code path scores every arm: random, zero, Python controller, PPO, LLM weights."""
import argparse
import hashlib
import importlib.util
import json
import resource
import sys
import time
from pathlib import Path

import gymnasium
import numpy as np

from .policy import load_weights
from .tasks import DEFAULT_EPISODES, EVAL_SEED0, TASKS, make_env


class ControllerError(RuntimeError):
    pass


class PythonController:
    """Wraps a file defining `act(obs) -> sequence of floats` and optionally `reset()`."""

    def __init__(self, task: str, path):
        spec = importlib.util.spec_from_file_location("zsr_controller", path)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        if not callable(getattr(mod, "act", None)):
            raise ControllerError("controller file must define act(obs)")
        self.mod = mod
        self.task = TASKS[task]
        self.low = np.array(self.task.act_low)
        self.high = np.array(self.task.act_high)

    def reset(self):
        if callable(getattr(self.mod, "reset", None)):
            self.mod.reset()

    def act(self, obs):
        a = np.asarray(self.mod.act([float(x) for x in obs]), dtype=np.float64).reshape(-1)
        if a.shape != (self.task.act_dim,):
            raise ControllerError(f"act() returned shape {a.shape}, expected ({self.task.act_dim},)")
        if not np.isfinite(a).all():
            raise ControllerError("act() returned non-finite values")
        return np.clip(a, self.low, self.high)


def run_episode(env, policy, seed: int) -> dict:
    obs, _ = env.reset(seed=seed)
    policy.reset()
    x0 = float(env.unwrapped.data.qpos[0])
    ret, steps, fault = 0.0, 0, None
    while True:
        try:
            action = policy.act(obs)
        except Exception as e:  # a crashing controller keeps what it earned so far; the fault is recorded
            fault = f"{type(e).__name__}: {e}"
            break
        obs, r, term, trunc, _ = env.step(action.astype(np.float32))
        ret += float(r)
        steps += 1
        if term or trunc:
            break
    return {"seed": seed, "return": ret, "length": steps, "terminated_early": bool(steps < env.spec.max_episode_steps),
            "distance": float(env.unwrapped.data.qpos[0]) - x0, "fault": fault}


def evaluate(task: str, policy, n_episodes: int = DEFAULT_EPISODES, seed0: int = EVAL_SEED0) -> dict:
    env = make_env(task)
    eps = [run_episode(env, policy, seed0 + i) for i in range(n_episodes)]
    env.close()
    rets = np.array([e["return"] for e in eps])
    lens = np.array([e["length"] for e in eps])
    t = TASKS[task]
    return {
        "task": task,
        "env_id": t.env_id,
        "gymnasium": gymnasium.__version__,
        "n_episodes": n_episodes,
        "seed0": seed0,
        "mean_return": float(rets.mean()),
        "sem_return": float(rets.std(ddof=1) / np.sqrt(n_episodes)) if n_episodes > 1 else 0.0,
        "std_return": float(rets.std()),
        "median_return": float(np.median(rets)),
        "min_return": float(rets.min()),
        "max_return": float(rets.max()),
        "mean_length": float(lens.mean()),
        "frac_full_length": float((lens >= t.max_steps).mean()),
        "mean_distance": float(np.mean([e["distance"] for e in eps])),
        "n_faults": sum(e["fault"] is not None for e in eps),
        "first_fault": next((e["fault"] for e in eps if e["fault"]), None),
        "episodes": eps,
    }


def limit_resources(cpu_s=3600, mem_gb=4):
    resource.setrlimit(resource.RLIMIT_CPU, (cpu_s, cpu_s))
    resource.setrlimit(resource.RLIMIT_AS, (mem_gb << 30, mem_gb << 30))


def sha256(path) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main(argv=None):
    ap = argparse.ArgumentParser(description="Score a weight file or Python controller.")
    ap.add_argument("task", choices=TASKS)
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--weights", help="JSON weight file")
    g.add_argument("--controller", help="Python file defining act(obs)")
    ap.add_argument("--episodes", type=int, default=DEFAULT_EPISODES)
    ap.add_argument("--out", help="write the full result JSON here")
    a = ap.parse_args(argv)
    t0 = time.time()
    src = a.weights or a.controller
    if a.controller:
        limit_resources()
    try:
        pol = load_weights(a.task, a.weights) if a.weights else PythonController(a.task, a.controller)
    except Exception as e:
        res = {"task": a.task, "load_error": f"{type(e).__name__}: {e}"}
    else:
        res = evaluate(a.task, pol, a.episodes)
    res.update({"source": str(src), "source_sha256": sha256(src), "wall_s": time.time() - t0})
    if a.out:
        Path(a.out).parent.mkdir(parents=True, exist_ok=True)
        Path(a.out).write_text(json.dumps(res, indent=1))
    print(json.dumps({k: v for k, v in res.items() if k != "episodes"}, indent=1))
    return 0 if "load_error" not in res else 2


if __name__ == "__main__":
    sys.exit(main())
