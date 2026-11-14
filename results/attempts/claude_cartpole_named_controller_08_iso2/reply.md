This is an untested linear state-feedback controller. A positive pole angle means the pole leans toward +x, so the controller pushes the cart the same way. The cart position and velocity terms have the same sign, which is what a non-minimum-phase LQR design gives. The gains are kept small because the motor gear is strong and the 0.04 s step could otherwise make the loop unstable.

```python
def reset():
    pass


def act(obs):
    x, th, xd, thd = obs
    u = 0.02 * x + 0.6 * th + 0.04 * xd + 0.08 * thd
    return [max(-3.0, min(3.0, u))]
```

I chose the gains from a rough dynamics estimate and could not check them in simulation, so they are the main risk to the score.