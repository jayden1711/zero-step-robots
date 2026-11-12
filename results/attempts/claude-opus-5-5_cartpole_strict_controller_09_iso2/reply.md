This appears to be the MuJoCo InvertedPendulum: obs = [cart position, pole angle, cart velocity, pole angular velocity], with the action driving the cart through a gear of about 100. I estimated the cart and pole masses from the standard model geometry and built a linearized model from them. At import, the module discretizes that model at the 0.04 s step and solves a discrete-time LQR problem with numpy. The controller is linear state feedback with clipping. A positive pole angle tilts the tip toward +x, so the cart is pushed toward +x to catch it. The cart position is also regulated so the cart stays inside its ±1 rail.

None of this has been run. The masses, gear and joint damping are recalled from the standard model and could be off. If the model is wrong, the controller could fail.

```python
import numpy as np

# Linearized cart-pole model (MuJoCo InvertedPendulum-like parameters)
_M_CART = 10.5      # kg (capsule r=0.1, half-length 0.1, density 1000)
_M_POLE = 5.0       # kg (capsule r=0.049, length 0.6)
_L_COM = 0.3        # pivot -> pole COM
_I_PIV = _M_POLE * 0.6 ** 2 / 3.0
_G = 9.81
_GEAR = 100.0
_D_SLIDE = 1.0
_D_HINGE = 1.0
_DT = 0.04


def _expm(A):
    n = A.shape[0]
    norm = np.max(np.sum(np.abs(A), axis=1))
    s = max(0, int(np.ceil(np.log2(max(norm, 1e-12)))) + 1)
    As = A / (2 ** s)
    E = np.eye(n)
    term = np.eye(n)
    for k in range(1, 30):
        term = term @ As / k
        E = E + term
    for _ in range(s):
        E = E @ E
    return E


def _compute_gain():
    ml = _M_POLE * _L_COM
    Mm = np.array([[_M_CART + _M_POLE, ml], [ml, _I_PIV]])
    Minv = np.linalg.inv(Mm)
    # state s = [x, th, xd, thd]; generalized forces:
    # cart: 100u - d*xd ; pole: m g l th - d*thd
    A = np.zeros((4, 4))
    A[0, 2] = 1.0
    A[1, 3] = 1.0
    Fs = np.zeros((2, 4))
    Fs[0, 2] = -_D_SLIDE
    Fs[1, 1] = _M_POLE * _G * _L_COM
    Fs[1, 3] = -_D_HINGE
    A[2:, :] = Minv @ Fs
    Bc = np.zeros((4, 1))
    Bc[2:, 0] = Minv @ np.array([_GEAR, 0.0])

    # ZOH discretization via augmented matrix exponential
    aug = np.zeros((5, 5))
    aug[:4, :4] = A
    aug[:4, 4:] = Bc
    E = _expm(aug * _DT)
    Ad = E[:4, :4]
    Bd = E[:4, 4:]

    Q = np.diag([2.0, 20.0, 0.2, 0.2])
    R = np.array([[2.0]])
    P = Q.copy()
    for _ in range(5000):
        S = R + Bd.T @ P @ Bd
        K = np.linalg.solve(S, Bd.T @ P @ Ad)
        Pn = Q + Ad.T @ P @ (Ad - Bd @ K)
        if np.max(np.abs(Pn - P)) < 1e-10 * max(1.0, np.max(np.abs(P))):
            P = Pn
            break
        P = Pn
    S = R + Bd.T @ P @ Bd
    K = np.linalg.solve(S, Bd.T @ P @ Ad)
    K = K.reshape(-1)
    if not np.all(np.isfinite(K)):
        raise ValueError
    # closed loop sanity check
    eig = np.abs(np.linalg.eigvals(Ad - Bd @ K.reshape(1, -1)))
    if np.max(eig) >= 1.0:
        raise ValueError
    return K


try:
    _K = _compute_gain()
except Exception:
    # fallback: u = -K s  (positive push when pole tilts toward +x)
    _K = np.array([-0.3, -6.0, -0.5, -1.0])


def reset():
    pass


def act(obs):
    s = np.asarray(obs, dtype=float).reshape(-1)[:4]
    if not np.all(np.isfinite(s)):
        return [0.0]
    u = -float(_K @ s)
    u = max(-3.0, min(3.0, u))
    return [u]
```