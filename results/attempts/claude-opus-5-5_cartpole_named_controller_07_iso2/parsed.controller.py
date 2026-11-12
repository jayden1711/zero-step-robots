import numpy as np

DT = 0.04


def _expm(M, terms=30):
    out = np.eye(M.shape[0])
    term = np.eye(M.shape[0])
    for k in range(1, terms):
        term = term @ M / k
        out = out + term
    return out


def _compute_gain():
    # Physical estimates (MuJoCo InvertedPendulum, density 1000)
    Mc = 10.47      # cart mass
    m = 5.02        # pole mass
    l = 0.3         # pivot -> pole COM
    I_com = m * 0.6 ** 2 / 12.0
    Ip = I_com + m * l * l
    g = 9.81
    gear = 100.0
    d_slide = 1.0
    d_hinge = 1.0

    Mm = np.array([[Mc + m, m * l],
                   [m * l, Ip]])
    Minv = np.linalg.inv(Mm)
    # generalized forces: [F - d_slide*v, m g l th - d_hinge*w]
    # state s = [x, th, v, w]
    Kq = np.array([[0.0, 0.0],
                   [0.0, m * g * l]])
    Dq = np.array([[d_slide, 0.0],
                   [0.0, d_hinge]])
    A = np.zeros((4, 4))
    A[0, 2] = 1.0
    A[1, 3] = 1.0
    A[2:, :2] = Minv @ Kq
    A[2:, 2:] = -Minv @ Dq
    B = np.zeros((4, 1))
    B[2:, 0] = Minv @ np.array([gear, 0.0])

    # Discretize (ZOH) via augmented matrix exponential
    aug = np.zeros((5, 5))
    aug[:4, :4] = A * DT
    aug[:4, 4:] = B * DT
    E = _expm(aug, 40)
    Ad = E[:4, :4]
    Bd = E[:4, 4:]

    Q = np.diag([1.0, 20.0, 0.5, 0.5])
    R = np.array([[0.5]])

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
    K = K.reshape(-1)

    # Sanity check: closed loop must be stable
    eig = np.linalg.eigvals(Ad - Bd @ K.reshape(1, 4))
    if not np.all(np.isfinite(K)) or np.max(np.abs(eig)) >= 0.999:
        raise ValueError("bad gain")
    # sign sanity: angle gain must make u push in direction of lean
    if K[1] >= 0:
        raise ValueError("bad sign")
    return K


try:
    _K = _compute_gain()
except Exception:
    # fallback: u = -K s with hand-derived PD + gentle cart centering
    _K = -np.array([0.2, 4.5, 0.4, 0.75])


def reset():
    pass


def act(obs):
    s = np.asarray(obs, dtype=float).reshape(-1)[:4]
    if not np.all(np.isfinite(s)):
        return [0.0]
    u = float(-_K @ s)
    if not np.isfinite(u):
        u = 0.0
    u = max(-3.0, min(3.0, u))
    return [u]
