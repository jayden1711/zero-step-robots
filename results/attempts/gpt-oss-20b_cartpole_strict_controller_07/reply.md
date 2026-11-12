```python
import math

def act(obs):
    """
    Simple proportional controller that keeps the second observation (index 1) close to zero.
    The action is a negative proportional feedback on obs[1], clipped to [-3, 3].
    """
    v = obs[1]
    # Proportional feedback
    action = -10.0 * v
    # Clip to action bounds
    if action > 3.0:
        action = 3.0
    elif action < -3.0:
        action = -3.0
    return [action]

def reset():
    """
    No internal state to reset for this controller.
    """
    pass
```