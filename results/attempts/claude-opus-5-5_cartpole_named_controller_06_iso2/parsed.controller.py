import numpy as np

# Approximate physical parameters of InvertedPendulum (MuJoCo, density 1000)
_M_CART = 10.47   # capsule r=0.1, length 0.2
_M_POLE = 5.02    # capsule r=0.049, length 0.6
_L = 0.3          # pole COM distance from hinge
_I_POLE = _M_POLE * 0.6 ** 2 / 12.0
_G = 9.81
_GEAR = 100.0
_B_X = 1.0        # slider damping
_B_TH = 1.0       # hinge damping
_DT = 0.04

_FALLBACK_K = np.array([0.3, 6.0, 0.4, 0.8])


def _expm(A):
    n = np.linalg.norm(A, 1)
    s = max(0, int(np.ceil(np.log2(n + 1e-12))) + 1)
    As = A / (2.0 ** s)
    E = np.eye(A.shape[0])
    term = np.eye(A.shape[0])
    for k in range(1, 20):
        term = term @ As / k
        E = E + term
    for _ in range(s):
        E = E @ E
    return E


def _compute_gain():
    m, M, l = _M_POLE, _M_CART, _L
    J = _I_POLE + m * l * l
    Mass = np.array([[M + m, m * l], [m * l, J]])
    Minv = np.linalg.inv(Mass)
    # state z = [x, th, v, w]; generalized forces: [F - bx v, m g l th - bth w]
    A = np.zeros((4, 4))
    A[0, 2] = 1.0
    A[1, 3] = 1.0
    Fz = np.zeros((2, 4))
    Fz[0, 2] = -_B_X
    Fz[1, 1] = m * _G * l
    Fz[1, 3] = -_B_TH
    A[2:, :] = Minv @ Fz
    B = np.zeros((4, 1))
    B[2:, 0] = Minv @ np.array([_GEAR, 0.0])

    # ZOH discretization via augmented matrix exponential
    aug = np.zeros((5, 5))
    aug[:4, :4] = A * _DT
    aug[:4, 4:] = B * _DT
    E = _expm(aug)
    Ad = E[:4, :4]
    Bd = E[:4, 4:]

    Q = np.diag([1.0, 20.0, 0.1, 0.5])
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
    K = np.linalg.solve(R + BtP @ Bd, BtP @ Ad).ravel()
    # sanity: closed loop must be stable
    if not np.all(np.isfinite(K)):
        raise ValueError
    if np.max(np.abs(np.linalg.eigvals(Ad - Bd @ K.reshape(1, 4)))) >= 1.0:
        raise ValueError
    return -K


try:
    _K = _compute_gain()
except Exception:
    _K = _FALLBACK_K


def reset():
    pass


def act(obs):
    z = np.asarray(obs, dtype=float)
    if not np.all(np.isfinite(z)):
        return [0.0]
    u = float(_K @ z)
    u = max(-3.0, min(3.0, u))
    return [u]
