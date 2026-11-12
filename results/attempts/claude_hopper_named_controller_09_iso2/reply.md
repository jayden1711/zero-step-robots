This is an untested balance controller. I couldn't run it, and the ankle torque sign comes from reading the Hopper model's axis conventions, so that is the main risk.

- **Straight stance:** the thigh and leg joints are held at their upper limit (0) with a small constant positive torque. In that position the leg is locked straight by the joint limits, so it can't buckle.
- **Ankle balance:** the foot torque is a PD term on torso angle and angular velocity. A positive torso angle means leaning backward, and a positive foot torque pushes the torso forward, so the correction has the right direction.

```python
def reset():
    pass


def act(obs):
    ang = obs[1]
    angvel = obs[7]
    foot = 2.0 * ang + 0.3 * angvel
    foot = max(-1.0, min(1.0, foot))
    return [0.3, 0.3, foot]
```