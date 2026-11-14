I couldn't test this, so it's a conservative balancing controller, not a hopping gait. It tries to keep the hopper standing for all 1000 steps, which should score roughly 1000.

- **Thigh and leg:** these hold their joint angle near 0, the straight-leg limit, with a small bias into the stop.
- **Foot:** ankle torque is a PD controller on torso angle, so it pushes the torso back upright.

The sign convention is my best guess: a positive torso angle means leaning backward, and a positive foot torque pushes the torso forward. If I have that backwards, the ankle torque will destabilise the hopper instead of balancing it.

```python
def reset():
    pass


def act(obs):
    ang = obs[1]
    q_th, q_leg = obs[2], obs[3]
    w = obs[7]
    w_th, w_leg = obs[8], obs[9]

    a_th = -5.0 * q_th - 0.5 * w_th + 0.3
    a_leg = -5.0 * q_leg - 0.5 * w_leg + 0.3
    a_foot = 8.0 * ang + 1.0 * w

    return [max(-1.0, min(1.0, a)) for a in (a_th, a_leg, a_foot)]
```