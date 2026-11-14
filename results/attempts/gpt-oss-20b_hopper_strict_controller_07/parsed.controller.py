import numpy as np

def reset() -> None:
    """
    Called at the start of each episode.
    No persistent state is needed for this simple controller.
    """
    pass

def act(obs: list) -> list:
    """
    Simple deterministic controller for the unknown system.

    Parameters
    ----------
    obs : list of 11 floats
        The current observation vector.

    Returns
    -------
    list of 3 floats
        Action values in the range [-1, 1] (will be clipped by the environment).
    """
    # Extract the most relevant observations
    o0 = obs[0]   # position‑like quantity (must stay > 0.7)
    o1 = obs[1]   # velocity‑like quantity (must stay within ±0.2)
    o5 = obs[5]   # related instantaneous rate of change (clipped to [-10, 10])

    # Action 0: keep velocity small while nudging forward
    a1 = 0.2 - 1.5 * o1

    # Action 1: keep position close to a nominal value (≈0.8)
    a2 = 0.8 - o0

    # Action 2: dampen the related rate of change
    a3 = -0.5 * o5

    # Clip actions to the allowed range
    a1 = max(-1.0, min(1.0, a1))
    a2 = max(-1.0, min(1.0, a2))
    a3 = max(-1.0, min(1.0, a3))

    return [float(a1), float(a2), float(a3)]
