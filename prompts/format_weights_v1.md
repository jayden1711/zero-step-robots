## What you write: the weights of a neural network

The controller is a small neural network with one hidden layer of {{HIDDEN}} tanh units. Observations go in raw.

    h = tanh(W1 @ obs + b1)
    action = clip(W2 @ h + b2, low, high)

Shapes (all weights and biases are real numbers; you choose every one of them):

- W1: {{W1_SHAPE}} (a list of {{HIDDEN}} rows, each with {{OBS_DIM}} numbers)
- b1: {{B1_SHAPE}}
- W2: {{W2_SHAPE}} (a list of {{ACT_DIM}} row(s), each with {{HIDDEN}} numbers)
- b2: {{B2_SHAPE}}

That is {{N_PARAMS}} numbers in total. There is no training: the numbers you write are the final weights.

Output format: reply with one JSON object in a single ```json code block, with exactly the keys `W1`, `b1`,
`W2`, `b2` and nothing else in the block. Numbers must be plain decimals (no expressions, no NaN or Infinity).
You may write any explanation outside the code block. If the reply has no valid block, or the shapes are wrong,
the controller scores as a failure.
