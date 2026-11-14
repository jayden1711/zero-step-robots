```python
import numpy as np

# Proportional controller gain
Kp = 5.0

def act(obs):
    """
    Control the system to keep the second observation (obs[1]) close to zero.
    The action is a single scalar clipped to the range [-3, 3] (the environment
    will clip automatically, but we clip here for safety).
    """
    # Compute proportional term
    a = -Kp * obs[1]
    # Clip to action bounds
    a = max(min(a, 3.0), -3.0)
    return [a]

def reset():
    """
    Reset any internal state at the beginning of an episode.
    This controller has no persistent state, so this function is a no-op.
    """
    pass
```
