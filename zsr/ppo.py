"""PPO baseline (Stable-Baselines3, CPU). The actor is a one-hidden-layer tanh MLP so its weights export to the
harness weight format and are scored by the same code as every other arm."""
import argparse
import json
import time
from pathlib import Path

import numpy as np
import torch

from .harness import evaluate
from .policy import MLPPolicy, save_weights
from .tasks import HIDDEN, make_env

TIMESTEPS = {"cartpole": 100_000, "hopper": 1_000_000}


def export_actor(model, task: str) -> MLPPolicy:
    pn = model.policy.mlp_extractor.policy_net
    W1, b1 = pn[0].weight, pn[0].bias
    W2, b2 = model.policy.action_net.weight, model.policy.action_net.bias
    t = lambda x: x.detach().cpu().numpy().astype(np.float64)
    return MLPPolicy(task, {"W1": t(W1), "b1": t(b1), "W2": t(W2), "b2": t(b2)})


def train(task: str, seed: int, timesteps: int, outdir: Path, n_eval: int = 100):
    from stable_baselines3 import PPO

    torch.set_num_threads(1)
    env = make_env(task)
    model = PPO("MlpPolicy", env, seed=seed, device="cpu", verbose=0,
                policy_kwargs=dict(net_arch=dict(pi=[HIDDEN], vf=[64, 64]), activation_fn=torch.nn.Tanh))
    t0 = time.time()
    model.learn(total_timesteps=timesteps)
    pol = export_actor(model, task)
    outdir.mkdir(parents=True, exist_ok=True)
    save_weights(pol, outdir / f"{task}_ppo_seed{seed}.weights.json")
    res = evaluate(task, pol, n_eval)
    res.update({"arm": "ppo", "train_seed": seed, "train_timesteps": timesteps, "train_wall_s": time.time() - t0,
                "sb3_algo": "PPO default hyperparameters, net_arch pi=[16] vf=[64,64], tanh"})
    (outdir / f"{task}_ppo_seed{seed}.score.json").write_text(json.dumps(res, indent=1))
    print(task, seed, "mean_return", res["mean_return"], "frac_full", res["frac_full_length"], flush=True)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("task")
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--timesteps", type=int)
    ap.add_argument("--outdir", default="results/baselines/ppo")
    a = ap.parse_args()
    train(a.task, a.seed, a.timesteps or TIMESTEPS[a.task], Path(a.outdir))
