# Task: design the controller network of a simulated walking robot

You will design the controller of a simulated robot. You cannot run code, test anything, or see any simulation
output: you get one reply, and the controller you write is scored exactly as written. There is no training: the
numbers you write become the final weights of the controller network.

{{TASK_SPEC}}

## Scoring

Your controller is run in 100 episodes of 1000 steps (8 seconds of simulated time) with fixed random seeds (the
seeds differ only in the tiny random perturbation of the initial state). For each episode we measure d, the forward
displacement of the torso along +x from the start to the last step at which the robot was still healthy (so the
fall that ends an episode earns nothing).

- Your score is the mean of d over the 100 episodes, in metres. Higher is better.
- The controller passes if the mean of d is at least 3 m and at least 50 of the 100 episodes reach d >= 3 m.

The environment's own reward is given above for completeness; it is not the score.
The controller is deterministic: it has no randomness.
{{HINT}}
{{OUTPUT_FORMAT}}
