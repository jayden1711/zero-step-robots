I designed this controller by linearizing the cart-pole and computing an LQR (linear-quadratic regulator) gain. I couldn't run any of it, so the score is untested.

**Model.** The parameters are estimated from the standard `inverted_pendulum.xml`:

- Pole: capsule 0.6 m long, radius 0.049, density 1000, so about 5 kg.
- Cart: about 10.5 kg.
- Motor gear: 100, so the force is 100·u.

Linearizing gives approximately:

- θ'' ≈ 32.3·θ − 21.3·u
- x'' ≈ 8.5·u − 3.13·θ

**Sign convention.** Pushing the cart in +x tips the pole toward −θ. So a pole leaning in +θ is caught with positive force. Following the usual LQR result, all four gains on (x, θ, v, ω) come out positive.

**Gain computation.** At import time, the module discretizes the model at dt = 0.04 using a series expansion of the matrix exponential. It then solves the discrete Riccati equation by iteration. If anything goes wrong numerically, it falls back to hand-tuned gains. The output is clipped to [-3, 3].

```python
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
```

**Caveats:**

- The model parameters are estimates from the XML, not measured, so the gains may not be optimal.
- The module contains a leftover first gain computation (`_compute_gain`) whose result isn't used. Only `_final_gain` sets the active gains. It's harmless but redundant.