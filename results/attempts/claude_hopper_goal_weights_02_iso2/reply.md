This is a hand-designed controller, since I can't train or test anything. I read the setup as a Hopper-like system: obs[0] is torso height, obs[1] is torso pitch, and obs[7] is pitch rate. The strategy is to survive 1000 steps for about 1000 reward, rather than to run fast.

- **Thigh and leg (actions 0 and 1):** a constant +1 torque, which presses the joints against their straight-leg limit.
- **Foot (action 2):** a PD controller on torso pitch, `2.8*tanh(angle) + 2.0*tanh(0.2*pitch_rate)`, that acts like an ankle balancing an inverted pendulum.
- **Assumptions:** the positive-pitch-means-forward-lean sign and the gains are guesses I could not check. If the sign is wrong, the hopper will fall.

```json
{
  "W1": [
    [0,1.0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0.2,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0]
  ],
  "b1": [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
  "W2": [
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [2.8,2.0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
  ],
  "b2": [1.0,1.0,0.0]
}
```