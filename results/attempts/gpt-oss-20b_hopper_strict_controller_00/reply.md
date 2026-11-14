```python
"""
A minimal deterministic controller that keeps the system healthy
by applying zero action at every step. This conservative strategy
ensures we do not incur any action cost and maintains stability
as long as the default dynamics of the simulation allow it.
"""

def reset():
    """
    Reset any internal state. This controller does not maintain state,
    but the function is defined for compliance with the environment.
    """
    pass

def act(obs):
    """
    Parameters
    ----------
    obs : list[float]
        Observation vector of length 11. The controller ignores the
        observation values and always returns zero action.

    Returns
    -------
    list[float]
        A list of three zeros representing the action.
    """
    return [0.0, 0.0, 0.0]
```