# Task: write a controller for a simulated system

You will write a controller for a simulated system. You cannot run code, test anything, or see any simulation
output: you get one reply, and the controller you write is scored exactly as written. Your score is the average
reward it earns in a physics simulation over many episodes.

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

## Scoring

Your controller is run in 100 episodes with fixed random seeds (the seeds differ only in the tiny random
perturbation of the initial state). The score is the mean total reward per episode. Higher is better.
The controller is deterministic: the same observation always produces the same action.

## What you write: a Python controller

Write a Python module that defines

    def act(obs):
        ...
        return [a_1, ..., a_3]

`obs` is a list of 11 floats (the observation above). `act` must return a sequence of 3 floats
(the action above; out-of-range values are clipped). You may use the Python standard library and numpy. You may
keep state between calls in module-level variables; if you do, also define `def reset():` which is called at the
start of every episode. The code gets no other information about the simulation, and no files or network.

Output format: reply with the complete module in a single ```python code block. You may write any explanation
outside the code block. If the reply has no valid block, or `act` raises an error or returns the wrong shape,
the controller scores as a failure.
