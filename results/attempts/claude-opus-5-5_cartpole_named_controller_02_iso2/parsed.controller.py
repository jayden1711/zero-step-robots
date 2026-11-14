import numpy as np

_DT = 0.04


def _compute_gain():
    # Linearized cart-pole (estimated from InvertedPendulum-v5 model), u = action
    A = np.array([
        [0.0, 0.0, 1.0, 0.0],
        [0.0, 0.0, 0.0, 1.0],
        [0.0, -3.13, 0.0, 0.0],
        [0.0, 32.3, 0.0, 0.0],
    ])
    B = np.array([[0.0], [0.0], [8.5], [-21.3]])
    # Discretize via series expansion of the block matrix exponential
    n = 4
    Mbig = np.zeros((5, 5))
    Mbig[:4, :4] = A * _DT
    Mbig[:4, 4:] = B * _DT
    E = np.eye(5)
    term = np.eye(5)
    for k in range(1, 30):
        term = term @ Mbig / k
        E = E + term
    Ad = E[:4, :4]
    Bd = E[:4, 4:]
    Q = np.diag([1.0, 5.0, 0.1, 0.1])
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
    # u = -K s; sign so that positive theta -> positive force
    return -K.flatten()


try:
    _GAIN = _compute_gain()
    if (not np.all(np.isfinite(_GAIN))) or _GAIN[1] >= 0:
        raise ValueError
    _GAIN = -_GAIN  # convert to u = G . s with G mostly positive
except Exception:
    _GAIN = None

if _GAIN is None or not np.all(np.isfinite(_GAIN)) or _GAIN[1] <= 0:
    _GAIN = np.array([0.3, 3.0, 0.4, 0.4])

# Final controller: u = -K s computed above corresponds to u = _GAIN_SIGNED . s
_K = None


def _final_gain():
    # u = -K s from LQR; recompute directly to avoid sign confusion
    try:
        A = np.array([
            [0.0, 0.0, 1.0, 0.0],
            [0.0, 0.0, 0.0, 1.0],
            [0.0, -3.13, 0.0, 0.0],
            [0.0, 32.3, 0.0, 0.0],
        ])
        B = np.array([[0.0], [0.0], [8.5], [-21.3]])
        Mbig = np.zeros((5, 5))
        Mbig[:4, :4] = A * _DT
        Mbig[:4, 4:] = B * _DT
        E = np.eye(5)
        term = np.eye(5)
        for k in range(1, 30):
            term = term @ Mbig / k
            E = E + term
        Ad = E[:4, :4]
        Bd = E[:4, 4:]
        Q = np.diag([1.0, 5.0, 0.1, 0.1])
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
        K = np.linalg.solve(R + BtP @ Bd, BtP @ Ad).flatten()
        G = -K  # u = G . s
        # closed-loop check
        cl = Ad - Bd @ K.reshape(1, 4)
        if (np.all(np.isfinite(G)) and G[1] > 0
                and np.max(np.abs(np.linalg.eigvals(cl))) < 1.0):
            return G
    except Exception:
        pass
    return np.array([0.3, 3.0, 0.4, 0.4])


_K = _final_gain()


def reset():
    pass


def act(obs):
    s = np.asarray(obs, dtype=float)
    if not np.all(np.isfinite(s)):
        return [0.0]
    u = float(np.dot(_K, s))
    if not np.isfinite(u):
        u = 0.0
    u = max(-3.0, min(3.0, u))
    return [u]
