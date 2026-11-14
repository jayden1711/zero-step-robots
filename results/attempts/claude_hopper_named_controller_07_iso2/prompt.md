# Task: write a controller for a simulated robot

You will write a controller for a simulated robot. You cannot run code, test anything, or see any simulation
output: you get one reply, and the controller you write is scored exactly as written. Your score is the average
reward it earns in a physics simulation over many episodes.

## The robot and environment

Environment: Gymnasium `Hopper-v5` (MuJoCo), a planar one-legged robot (torso, thigh, leg, foot) that moves in
the x-z plane. Forward is +x.

- Observation (11 numbers, raw, not normalised):
  1. height (z) of the torso
  2. torso angle (radians)
  3. thigh joint angle
  4. leg joint angle
  5. foot joint angle
  6. torso x-velocity
  7. torso z-velocity
  8. torso angular velocity
  9. thigh joint angular velocity
  10. leg joint angular velocity
  11. foot joint angular velocity

  Velocities (6 to 11) are clipped to [-10, 10].
- Action (3 numbers): the torques at the thigh, leg and foot joints, in that order. Values outside [-1, 1] are
  clipped to that range.
- One step is 0.008 seconds of simulated time. The action is applied for the whole step.
- Initial state: every position and velocity is perturbed by a small uniform random amount (at most 0.005).

Reward and episode rules:

- Reward per step = 1 (while the hopper is healthy) + (torso x-velocity, measured over the step) - 0.001 * (sum of
  the squared action values, after clipping).
- The hopper is healthy while all of these hold: torso height z > 0.7; |torso angle| < 0.2 radians; and every
  joint angle and velocity is strictly inside (-100, 100).
- The episode terminates as soon as the hopper is not healthy. Otherwise it is cut off after 1000 steps.

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
