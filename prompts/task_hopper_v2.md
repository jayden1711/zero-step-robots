## The environment

The controller receives raw numbers and returns raw numbers. Nothing else is known about the system.

- Observation: a vector `obs` of 11 numbers (indices 0 to 10), raw, not normalised. Indices 5 to 10 are clipped
  to [-10, 10].
- Action: a vector of 3 numbers. Values outside [-1, 1] are clipped to that range.
- One step is 0.008 seconds of simulated time. The action is applied for the whole step.
- Initial state: every position and velocity is perturbed by a small uniform random amount (at most 0.005).

Reward and episode rules:

- Reward per step = 1 (while the system is healthy) + v - 0.001 * (sum of the squared action values, after
  clipping), where v is the change in an unobserved x coordinate over the step divided by the step time.
  obs[5] is a related instantaneous rate of change, not identical to v.
- The system is healthy while all of these hold: obs[0] > 0.7; |obs[1]| < 0.2; and every value in obs[2:] is
  strictly inside (-100, 100), checked before the clipping of indices 5 to 10.
- The episode terminates as soon as the system is not healthy. Otherwise it is cut off after 1000 steps.
