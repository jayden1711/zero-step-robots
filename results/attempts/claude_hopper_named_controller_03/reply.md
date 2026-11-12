I couldn't run or test this, so the controller is untested and the gains are my best estimates. It tries to stand upright and balance for the full 1000 steps, which earns about 1 reward per step, minus a small torque cost.

- **Foot:** the ankle torque balances the torso, driven by the torso angle and angular velocity. I assumed a forward lean (positive angle) calls for positive foot torque.
- **Thigh and leg:** these joints are held straight with a weak PD loop, so the leg acts as a rigid pole.
- **Not included:** I added no hopping or forward drive, because an untested gait is more likely to fall early than to add reward.

```python
def act(obs):
    ang = obs[1]
    q_thigh, q_leg = obs[2], obs[3]
    w_torso = obs[7]
    w_thigh, w_leg = obs[8], obs[9]
    vx = obs[5]

    foot = 3.0 * ang + 0.3 * w_torso + 0.1 * vx
    thigh = -1.0 * q_thigh - 0.1 * w_thigh
    leg = -1.0 * q_leg - 0.1 * w_leg

    def c(x):
        return max(-1.0, min(1.0, float(x)))

    return [c(thigh), c(leg), c(foot)]
```