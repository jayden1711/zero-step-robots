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

The goal is to move forward as far as possible (forward distance).

## Scoring

Your controller is run in 100 episodes with fixed random seeds (the seeds differ only in the tiny random
perturbation of the initial state). The score is the mean total reward per episode. Higher is better.
The controller is deterministic: the same observation always produces the same action.

## What you write: the weights of a neural network

The controller is a small neural network with one hidden layer of 16 tanh units. Observations go in raw.

    h = tanh(W1 @ obs + b1)
    action = clip(W2 @ h + b2, low, high)

Shapes (all weights and biases are real numbers; you choose every one of them):

- W1: [16, 11] (a list of 16 rows, each with 11 numbers)
- b1: [16]
- W2: [3, 16] (a list of 3 row(s), each with 16 numbers)
- b2: [3]

That is 243 numbers in total. There is no training: the numbers you write are the final weights.

Output format: reply with one JSON object in a single ```json code block, with exactly the keys `W1`, `b1`,
`W2`, `b2` and nothing else in the block. Numbers must be plain decimals (no expressions, no NaN or Infinity).
You may write any explanation outside the code block. If the reply has no valid block, or the shapes are wrong,
the controller scores as a failure.
