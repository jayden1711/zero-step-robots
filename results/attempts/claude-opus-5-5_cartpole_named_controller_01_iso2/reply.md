This uses a discrete LQR controller. The gains are computed once at import from a linearized model of the MuJoCo cart-pole: cart about 10.5 kg, pole about 5 kg, pole length 0.6 m, actuator gear 100. The model is discretized at the 0.04 s control step. I couldn't run it, so it's untested.

Sign convention: positive pole angle means the pole leans toward +x, so pushing the cart toward +x catches it. The cart-position term pulls the cart back toward the centre of the rail. If the computation ever fails, the controller falls back to fixed gains.

```python
import numpy as np

DT = 0.04
GEAR = 100.0


def _expm(M, terms=30):
    # Matrix exponential via scaling-and-squaring + Taylor series
    n = M.shape[0]
    norm = np.linalg.norm(M, ord=np.inf)
    s = max(0, int(np.ceil(np.log2(norm))) + 1) if norm > 0 else 0
    A = M / (2.0 ** s)
    E = np.eye(n)
    term = np.eye(n)
    for k in range(1, terms):
        term = term @ A / k
        E = E + term
    for _ in range(s):
        E = E @ E
    return E


def _compute_gain():
    M = 10.5      # cart mass
    m = 5.0       # pole mass
    l = 0.3       # hinge -> pole COM
    I = m * 0.6 ** 2 / 3.0 + m * 0.049 ** 2 / 4.0  # inertia about hinge
    g = 9.81

    # [[M+m, m l],[m l, I]] [xdd, thdd] = [F, m g l th]
    Mm = np.array([[M + m, m * l], [m * l, I]])
    Minv = np.linalg.inv(Mm)
    # state s = [x, th, v, w]
    A = np.zeros((4, 4))
    A[0, 2] = 1.0
    A[1, 3] = 1.0
    # accelerations from theta term
    acc_th = Minv @ np.array([0.0, m * g * l])
    A[2, 1] = acc_th[0]
    A[3, 1] = acc_th[1]
    # small hinge damping
    acc_w = Minv @ np.array([0.0, -1.0])
    A[2, 3] = acc_w[0]
    A[3, 3] = acc_w[1]
    acc_u = Minv @ np.array([GEAR, 0.0])
    B = np.zeros((4, 1))
    B[2, 0] = acc_u[0]
    B[3, 0] = acc_u[1]

    # Zero-order-hold discretization via augmented exponential
    aug = np.zeros((5, 5))
    aug[:4, :4] = A * DT
    aug[:4, 4:] = B * DT
    E = _expm(aug)
    Ad = E[:4, :4]
    Bd = E[:4, 4:]

    Q = np.diag([1.0, 10.0, 0.2, 0.2])
    R = np.array([[1.0]])
    P = Q.copy()
    for _ in range(5000):
        BtP = Bd.T @ P
        K = np.linalg.solve(R + BtP @ Bd, BtP @ Ad)
        Pn = Q + Ad.T @ P @ (Ad - Bd @ K)
        if np.max(np.abs(Pn - P)) < 1e-10:
            P = Pn
            break
        P = Pn
    BtP = Bd.T @ P
    K = np.linalg.solve(R + BtP @ Bd, BtP @ Ad)
    K = K.reshape(-1)
    if not np.all(np.isfinite(K)):
        raise ValueError
    # sanity: closed loop stable
    eig = np.linalg.eigvals(Ad - Bd @ K.reshape(1, 4))
    if np.max(np.abs(eig)) >= 1.0:
        raise ValueError
    return K


try:
    _K = _compute_gain()
except Exception:
    # fallback: u = -K s with K negative => positive feedback gains
    _K = -np.array([0.5, 6.0, 0.8, 1.2])


def reset():
    pass


def act(obs):
    s = np.asarray(obs, dtype=float).reshape(-1)[:4]
    if not np.all(np.isfinite(s)):
        return [0.0]
    u = float(-_K @ s)
    u = max(-3.0, min(3.0, u))
    return [u]
```