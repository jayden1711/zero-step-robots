This controller uses a discrete-time LQR built from a linearised model of the MuJoCo cart-pole. I haven't run it, so the gains are unverified.

**Model.** The parameters come from the model file (`inverted_pendulum.xml`):
- Cart: a capsule of radius 0.1 and length 0.2, giving about 10.5 kg.
- Pole: a capsule of radius 0.049 and length 0.6, giving about 5.0 kg, with its centre of mass about 0.3 m above the hinge.
- Motor gear is 100, so an action of ±3 is ±300 N.
- Joint damping is 1.

A positive pole angle means the pole tips toward +x, so pushing the cart toward +x corrects it.

**Controller.** At import, the module:
1. builds the linearised equations of motion,
2. converts them to discrete time for the 0.04 s step,
3. solves the Riccati equation by iteration to get the feedback gains.

The cost weights penalise the pole angle most heavily, while still keeping the cart near the centre of the rail. If the numeric solve fails or gives an implausible result, it falls back to hand-chosen gains.

```python
import numpy as np

DT = 0.04


def _expm(M):
    # scaling-and-squaring Taylor matrix exponential
    n = np.linalg.norm(M, 1)
    s = max(0, int(np.ceil(np.log2(n + 1e-12))) + 1) if n > 0.5 else 0
    A = M / (2.0 ** s)
    E = np.eye(M.shape[0])
    term = np.eye(M.shape[0])
    for k in range(1, 30):
        term = term @ A / k
        E = E + term
    for _ in range(s):
        E = E @ E
    return E


def _compute_gain():
    m_cart = 10.47
    m_pole = 5.02
    l = 0.30            # pole COM distance from hinge
    I = 0.62            # pole inertia about hinge
    g = 9.81
    gear = 100.0
    damp = 1.0

    Mm = np.array([[m_cart + m_pole, m_pole * l],
                   [m_pole * l, I]])
    G = np.array([[0.0, 0.0],
                  [0.0, m_pole * g * l]])
    D = np.array([[damp, 0.0],
                  [0.0, damp]])
    Bf = np.array([[gear], [0.0]])

    Minv = np.linalg.inv(Mm)
    # state: [x, th, xd, thd]
    A = np.zeros((4, 4))
    A[0, 2] = 1.0
    A[1, 3] = 1.0
    A[2:, :2] = Minv @ G
    A[2:, 2:] = -Minv @ D
    B = np.zeros((4, 1))
    B[2:, :] = Minv @ Bf

    aug = np.zeros((5, 5))
    aug[:4, :4] = A
    aug[:4, 4:] = B
    E = _expm(aug * DT)
    Ad = E[:4, :4]
    Bd = E[:4, 4:]

    Q = np.diag([1.0, 10.0, 0.2, 0.2])
    R = np.array([[1.0]])

    P = Q.copy()
    for _ in range(5000):
        S = R + Bd.T @ P @ Bd
        K = np.linalg.solve(S, Bd.T @ P @ Ad)
        Pn = Q + Ad.T @ P @ (Ad - Bd @ K)
        if np.max(np.abs(Pn - P)) < 1e-10 * (1 + np.max(np.abs(P))):
            P = Pn
            break
        P = Pn
    S = R + Bd.T @ P @ Bd
    K = np.linalg.solve(S, Bd.T @ P @ Ad)
    return K.reshape(-1)


try:
    _K = _compute_gain()
    if not np.all(np.isfinite(_K)) or _K[1] >= 0:
        raise ValueError
except Exception:
    # fallback: u = -K s with K = [-x, -th, -xd, -thd] gains
    _K = np.array([-0.5, -8.0, -0.8, -1.0])


def reset():
    pass


def act(obs):
    s = np.asarray(obs, dtype=float)
    if not np.all(np.isfinite(s)):
        return [0.0]
    u = float(-_K @ s)
    u = max(-3.0, min(3.0, u))
    return [u]
```