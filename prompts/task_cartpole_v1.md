## The robot and environment

Environment: Gymnasium `InvertedPendulum-v5` (MuJoCo), a cart that slides on a rail with a pole hinged on top of it.

- Observation (4 numbers, raw, not normalised):
  1. cart position along the rail (metres)
  2. pole angle from vertical (radians)
  3. cart velocity
  4. pole angular velocity
- Action (1 number): the force applied to the cart. Values outside [-3, 3] are clipped to that range.
- One step is 0.04 seconds of simulated time. The action is applied for the whole step.
- Initial state: every position and velocity is perturbed by a small uniform random amount (at most 0.01).

Reward and episode rules:

- Reward is +1 for every step on which the pole is still upright, i.e. its angle satisfies |angle| <= 0.2 radians.
- The episode terminates as soon as |angle| > 0.2 radians (or any observation becomes non-finite).
- Otherwise the episode is cut off after 1000 steps, so the maximum score is 1000.
