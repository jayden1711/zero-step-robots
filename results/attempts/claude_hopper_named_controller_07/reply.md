This is a hand-designed balance controller. I could not run it, so it is untested and the gains are my estimates.

- **Straight leg:** the thigh and leg joints have range limits at 0 (fully extended). A small positive torque on both holds the hopper straight against those limits and acts as a rigid inverted pendulum.
- **Balance:** the foot torque is a PD law on torso angle and angular velocity. All joints share the same rotation axis, so a backward lean (positive angle) gets positive foot torque, which rotates the body forward.
- **Reward:** this aims at roughly 1 reward per step by staying upright for the full 1000 steps. It does not try to hop forward, since I couldn't tune that safely without testing.

```python
import numpy as np


def reset():
    pass


def act(obs):
    theta = obs[1]
    q1, q2, q3 = obs[2], obs[3], obs[4]
    w0 = obs[7]
    w1, w2, w3 = obs[8], obs[9], obs[10]

    # Ankle: PD on torso lean (positive lean = backward, positive torque corrects it)
    a3 = 3.0 * (theta + 0.3 * (q1 + q2 + q3)) + 0.5 * w0 - 0.02 * w3

    # Hold hip and knee extended against their joint limits at 0
    a1 = 0.25 - 0.03 * w1
    a2 = 0.35 - 0.03 * w2

    return [float(np.clip(a1, -1, 1)),
            float(np.clip(a2, -1, 1)),
            float(np.clip(a3, -1, 1))]
```