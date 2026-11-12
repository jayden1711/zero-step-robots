This is a conservative standing controller. I haven't run it, and I haven't verified that the sign convention below is correct. It uses the ankle torque as a PD controller on torso angle to keep the hopper upright for all 1000 steps, which should earn about 1000 reward from the alive bonus. It doesn't try to hop forward, because I can't test a hopping gait and a fall would terminate the episode.

The thigh and leg joints start at their straight-leg limits, so they are left at zero torque. The sign of the ankle gain comes from my reading of the joint axes, which is the main risk.

```python
def reset():
    pass


def act(obs):
    theta = obs[1]
    omega = obs[7]
    foot = 3.0 * theta + 0.3 * omega
    foot = max(-1.0, min(1.0, foot))
    return [0.0, 0.0, foot]
```