"""Task definitions. Environment ids and versions are fixed here and recorded with every score."""
from dataclasses import dataclass

import gymnasium as gym

HIDDEN = 16
EVAL_SEED0 = 10_000  # evaluation episode i uses reset seed EVAL_SEED0 + i; training seeds stay below this
DEFAULT_EPISODES = 100


@dataclass(frozen=True)
class Task:
    name: str
    env_id: str
    obs_dim: int
    act_dim: int
    act_low: tuple
    act_high: tuple
    max_steps: int = 1000


TASKS = {
    "cartpole": Task("cartpole", "InvertedPendulum-v5", 4, 1, (-3.0,), (3.0,)),
    "hopper": Task("hopper", "Hopper-v5", 11, 3, (-1.0,) * 3, (1.0,) * 3),
    "walker2d": Task("walker2d", "Walker2d-v5", 17, 6, (-1.0,) * 6, (1.0,) * 6),
}


def make_env(task: str, variant: str = None):
    t = TASKS[task]
    kw = {}
    if variant:
        from .variants import variant_xml_path
        kw["xml_file"] = variant_xml_path(task, variant)
    env = gym.make(t.env_id, max_episode_steps=t.max_steps, **kw)
    assert env.observation_space.shape == (t.obs_dim,)
    assert env.action_space.shape == (t.act_dim,)
    return env
