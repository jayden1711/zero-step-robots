This is a cart-pole balance task. I modelled the cart and pole with masses estimated from the MuJoCo XML: cart about 10.5 kg, pole about 5 kg with its centre of mass 0.3 m up, and an actuator gear of 100. The controller discretises that model with a zero-order hold over 0.04 s and computes a discrete LQR gain at import time.

The sign convention is that a positive pole angle tilts the pole toward +x, so pushing the cart toward +x recovers it. A cart displaced toward +x must first move further +x to tip the pole back. As a result, all four feedback gains come out positive.

If the LQR computation fails or gives an implausible gain, the module falls back to hand-tuned positive gains. I couldn't run this, so the mass and gear figures are estimates, but LQR's stability margins should tolerate moderate model error.

```python
import numpy as np

DT = 0.04
G = 9.81

# Approximate physical parameters of InvertedPendulum (MuJoCo, density 1000)
M_CART = 10.5      # cart capsule mass
M_POLE = 5.0       # pole capsule mass
L_COM = 0.3        # hinge to pole centre of mass
I_HINGE = 0.62     # pole inertia about hinge
GEAR = 100.0       # actuator gear

FALLBACK_K = np.array([0.3, 6.0, 0.6, 1.0])


def _expm(Mat):
    # scaling and squaring with Taylor series
    norm = np.max(np.sum(np.abs(Mat), axis=1))
    s = max(0, int(np.ceil(np.log2(norm + 1e-12))) + 1)
    A = Mat / (2.0 ** s)
    n = Mat.shape[0]
    E = np.eye(n)
    term = np.eye(n)
    for k in range(1, 25):
        term = term @ A / k
        E = E + term
    for _ in range(s):
        E = E @ E
    return E


def _compute_gain():
    m, Mc, l, I = M_POLE, M_CART, L_COM, I_HINGE
    Mt = Mc + m
    ml = m * l
    # Linearised: Mt*xdd + ml*thdd = F ; I*thdd + ml*xdd = m*g*l*th
    denom = I - ml * ml / Mt
    a_tt = m * G * l / denom
    b_t = -(ml / Mt) * GEAR / denom
    a_xt = -(ml / Mt) * a_tt
    b_x = GEAR / Mt - (ml / Mt) * b_t

    # state s = [x, th, v, w]
    A = np.zeros((4, 4))
    A[0, 2] = 1.0
    A[1, 3] = 1.0
    A[2, 1] = a_xt
    A[3, 1] = a_tt
    B = np.array([[0.0], [0.0], [b_x], [b_t]])

    aug = np.zeros((5, 5))
    aug[:4, :4] = A
    aug[:4, 4:] = B
    E = _expm(aug * DT)
    Ad = E[:4, :4]
    Bd = E[:4, 4:]

    Q = np.diag([1.0, 20.0, 0.5, 1.0])
    R = np.array([[0.5]])
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
    # u = -K s ; return gains so that u = gains . s
    gains = -K.flatten()
    # closed-loop stability check on the model
    eig = np.linalg.eigvals(Ad - Bd @ K)
    if not np.all(np.isfinite(gains)) or np.max(np.abs(eig)) >= 1.0:
        return FALLBACK_K.copy()
    # sanity: angle and angular-velocity gains must be positive
    if gains[1] <= 0 or gains[3] <= 0:
        return FALLBACK_K.copy()
    return gains


try:
    GAINS = _compute_gain()
except Exception:
    GAINS = FALLBACK_K.copy()


def reset():
    pass


def act(obs):
    try:
        s = np.asarray(obs, dtype=float).reshape(4)
        u = float(np.dot(GAINS, s))
        if not np.isfinite(u):
            u = 0.0
    except Exception:
        u = 0.0
    u = max(-3.0, min(3.0, u))
    return [u]
```