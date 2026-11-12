import numpy as np

# Linear state feedback from pole placement (all closed-loop poles at s = -4)
# on the linearized cart-pole model of InvertedPendulum-v5.
K_X = 1.229      # cart position
K_V = 1.229      # cart velocity
K_TH = 6.515     # pole angle
K_OM = 1.242     # pole angular velocity


def reset():
    pass


def act(obs):
    x, th, v, om = (float(o) for o in obs)
    a = K_X * x + K_V * v + K_TH * th + K_OM * om
    if not np.isfinite(a):
        a = 0.0
    a = float(np.clip(a, -3.0, 3.0))
    return [a]
