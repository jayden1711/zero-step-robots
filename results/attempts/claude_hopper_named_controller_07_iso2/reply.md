I can't run anything here, so this is a conservative balance controller aimed at surviving all 1000 steps (about 1000 reward) rather than at speed. I haven't tested it, and the sign of the foot feedback is derived from the MuJoCo joint-axis conventions, not checked in simulation.

- **Thigh and leg:** a stiff PD controller holds both joints at 0, a straight, extended leg.
- **Foot:** a torque on the foot reacts on the leg, so the foot action has the same sign as the torso angle and its angular velocity.

```python
def reset():
    pass


def act(obs):
    z, th, q1, q2, q3, vx, vz, w, w1, w2, w3 = obs

    a1 = -6.0 * q1 - 0.3 * w1
    a2 = -6.0 * q2 - 0.3 * w2
    a3 = 3.0 * th + 0.5 * w - 0.5 * q3 - 0.05 * w3

    def c(a):
        return max(-1.0, min(1.0, float(a)))

    return [c(a1), c(a2), c(a3)]
```