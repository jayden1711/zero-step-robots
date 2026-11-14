import numpy as np

DT = 0.04


def _model():
    # Approximate physical parameters of InvertedPendulum (MuJoCo, density 1000)
    M = 10.5          # cart mass
    m = 5.0           # pole mass
    l = 0.3           # pivot -> pole COM
    I = 0.6           # pole inertia about pivot
    g = 9.81
    gear = 100.0
    damp = 1.0        # hinge damping
    # (M+m) xdd + m l thdd = u
    # I thdd + m l xdd = m g l th - damp thd
    Mm = np.array([[M + m, m * l], [m * l, I]])
    Minv = np.linalg.inv(Mm)
    # generalized forces: [u, m g l th - damp thd]
    A = np.zeros((4, 4))
    A[0, 2] = 1.0
    A[1, 3] = 1.0
    # contribution of th
    A[2:, 1] = Minv @ np.array([0.0, m * g * l])
    # contribution of thd
    A[2:, 3] = Minv @ np.array([0.0, -damp])
    B = np.zeros((4, 1))
    B[2:, 0] = Minv @ np.array([gear, 0.0])
    return A, B


def _expm(Mat):
    # scaling and squaring with Taylor series
    norm = np.linalg.norm(Mat, 1)
    s = max(0, int(np.ceil(np.log2(norm + 1e-12))) + 1)
    X = Mat / (2.0 ** s)
    E = np.eye(Mat.shape[0])
    term = np.eye(Mat.shape[0])
    for k in range(1, 30):
        term = term @ X / k
        E = E + term
    for _ in range(s):
        E = E @ E
    return E


def _gain():
    A, B = _model()
    n = A.shape[0]
    aug = np.zeros((n + 1, n + 1))
    aug[:n, :n] = A * DT
    aug[:n, n:] = B * DT
    E = _expm(aug)
    Ad = E[:n, :n]
    Bd = E[:n, n:]
    Q = np.diag([1.0, 5.0, 0.1, 0.1])
    R = np.array([[0.5]])
    P = Q.copy()
    for _ in range(20000):
        BtP = Bd.T @ P
        K = np.linalg.solve(R + BtP @ Bd, BtP @ Ad)
        Pn = Q + Ad.T @ P @ (Ad - Bd @ K)
        Pn = 0.5 * (Pn + Pn.T)
        if np.max(np.abs(Pn - P)) < 1e-10 * (1.0 + np.max(np.abs(P))):
            P = Pn
            break
        P = Pn
    BtP = Bd.T @ P
    K = np.linalg.solve(R + BtP @ Bd, BtP @ Ad)
    # verify closed-loop stability
    eig = np.linalg.eigvals(Ad - Bd @ K)
    if not np.all(np.isfinite(K)) or np.max(np.abs(eig)) >= 1.0:
        raise ValueError("bad gain")
    return -K.reshape(-1)  # a = gain . state


try:
    _K = _gain()
except Exception:
    # fallback hand gains: [x, th, xd, thd]
    _K = np.array([0.3, 4.0, 0.5, 0.6])


def reset():
    pass


def act(obs):
    s = np.asarray(obs, dtype=float).reshape(-1)[:4]
    if not np.all(np.isfinite(s)):
        return [0.0]
    a = float(np.dot(_K, s))
    if not np.isfinite(a):
        a = 0.0
    a = max(-3.0, min(3.0, a))
    return [a]
