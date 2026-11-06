## The environment

The controller receives raw numbers and returns raw numbers. Nothing else is known about the system.

- Observation: a vector `obs` of 4 numbers (indices 0 to 3), raw, not normalised.
- Action: a vector of 1 number. Values outside [-3, 3] are clipped to that range.
- One step is 0.04 seconds of simulated time. The action is applied for the whole step.
- Initial state: every position and velocity is perturbed by a small uniform random amount (at most 0.01).

Reward and episode rules:

- Reward is +1 for every step on which |obs[1]| <= 0.2.
- The episode terminates as soon as |obs[1]| > 0.2 (or any observation becomes non-finite).
- Otherwise the episode is cut off after 1000 steps, so the maximum score is 1000.
