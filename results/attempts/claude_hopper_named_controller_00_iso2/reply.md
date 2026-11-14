I wrote a standing-balance controller, which I could not run or test. Staying upright for all 1000 steps is worth about 1000 reward, so I aimed for that rather than speed. I assumed joint sign conventions from the Hopper model files (all joint axes are `0 -1 0`, so positive torso angle means leaning backward), and the gains are untuned guesses.

- **Foot:** positive torque tips the body forward, so the foot torque follows the torso angle and angular velocity to correct a lean.
- **Thigh and leg:** PD terms hold both joints near straight (angle 0), with a small torso-angle term on the thigh.

```python
def reset():
    pass


def act(obs):
    th = obs[1]
    q1, q2, q3 = obs[2], obs[3], obs[4]
    w = obs[7]
    dq1, dq2, dq3 = obs[8], obs[9], obs[10]

    a3 = 6.0 * th + 0.8 * w - 0.5 * q3 * 0.0
    a2 = -4.0 * q2 - 0.15 * dq2
    a1 = -4.0 * q1 - 0.15 * dq1 + 2.0 * th + 0.3 * w

    def c(x):
        return max(-1.0, min(1.0, x))

    return [c(a1), c(a2), c(a3)]
```