This looks like MuJoCo's InvertedPendulum, with obs = [cart x, pole angle, cart velocity, angular velocity]. I couldn't run it, so I wrote a linear state-feedback controller from the standard LQR structure. All four gains are positive: push toward the lean, and give the cart position and velocity the same sign so it drifts back to center. The gains are my estimates, not tuned.

```python
def reset():
    pass


def act(obs):
    x, th, xd, thd = obs[0], obs[1], obs[2], obs[3]
    u = 0.3 * x + 8.0 * th + 0.5 * xd + 1.0 * thd
    return [max(-3.0, min(3.0, u))]
```