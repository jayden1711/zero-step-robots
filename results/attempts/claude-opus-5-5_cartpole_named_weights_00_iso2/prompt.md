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

## What you write: the weights of a neural network

The controller is a small neural network with one hidden layer of 16 tanh units. Observations go in raw.

    h = tanh(W1 @ obs + b1)
    action = clip(W2 @ h + b2, low, high)

Shapes (all weights and biases are real numbers; you choose every one of them):

- W1: [16, 4] (a list of 16 rows, each with 4 numbers)
- b1: [16]
- W2: [1, 16] (a list of 1 row(s), each with 16 numbers)
- b2: [1]

That is 97 numbers in total. There is no training: the numbers you write are the final weights.

Output format: reply with one JSON object in a single ```json code block, with exactly the keys `W1`, `b1`,
`W2`, `b2` and nothing else in the block. Numbers must be plain decimals (no expressions, no NaN or Infinity).
You may write any explanation outside the code block. If the reply has no valid block, or the shapes are wrong,
the controller scores as a failure.
