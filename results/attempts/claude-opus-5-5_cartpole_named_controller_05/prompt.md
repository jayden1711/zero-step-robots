# Task: write a controller for a simulated robot

You will write a controller for a simulated robot. You cannot run code, test anything, or see any simulation
output: you get one reply, and the controller you write is scored exactly as written. Your score is the average
reward it earns in a physics simulation over many episodes.

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

## Scoring

Your controller is run in 100 episodes with fixed random seeds (the seeds differ only in the tiny random
perturbation of the initial state). The score is the mean total reward per episode. Higher is better.
The controller is deterministic: the same observation always produces the same action.

## What you write: a Python controller

Write a Python module that defines

    def act(obs):
        ...
        return [a_1, ..., a_1]

`obs` is a list of 4 floats (the observation above). `act` must return a sequence of 1 floats
(the action above; out-of-range values are clipped). You may use the Python standard library and numpy. You may
keep state between calls in module-level variables; if you do, also define `def reset():` which is called at the
start of every episode. The code gets no other information about the simulation, and no files or network.

Output format: reply with the complete module in a single ```python code block. You may write any explanation
outside the code block. If the reply has no valid block, or `act` raises an error or returns the wrong shape,
the controller scores as a failure.
