These are the weights for one tanh unit acting as a linear controller. I couldn't run or check anything here, so the gains come from a rough physics model and are not tested.

**What I assumed the system is.** The rules match MuJoCo's InvertedPendulum: 4 observations, actions limited to ±3, 0.04 s steps, failure past 0.2 on obs[1], and starting noise of 0.01. Under that assumption the observations are `obs = [cart position x, pole angle θ, cart velocity v, pole angular velocity ω]`. A positive action pushes the cart toward +x, and a positive θ means the pole tip leans toward +x.

**Model.** I estimated masses from MuJoCo's default density, which gives about 5 kg each for the cart and the pole. The motor gear is 100. Linearising gives:
- θ̈ ≈ 38θ − 37.6a
- ẍ ≈ 15a − 5.5θ

With the policy a = kx·x + kθ·θ + kv·v + kω·ω, the closed-loop characteristic polynomial is:

s⁴ + (37.6kω − 15kv)s³ + (37.6kθ − 38 − 15kx)s² + 363kv·s + 363kx

All four gains have to be positive. To return to the centre, the cart first has to tip the pole the other way, so the position and velocity terms push the "wrong" way at first.

**Gains.** I placed the poles at −2, −2, −6, −6. That gives a slow loop for cart position and a fast loop for balancing the pole. The resulting gains are:
- kx ≈ 0.40
- kθ ≈ 3.51
- kv ≈ 0.53
- kω ≈ 0.64

These leave a wide margin above the instability threshold kθ > ~1. The fastest pole times the step size is 6 × 0.04 = 0.24, which is safe for a 0.04 s step.

**Network.** I scale the gains down by 0.1 in the first hidden unit so tanh stays almost linear, then multiply back by 10 at the output. The other 15 units are left at zero.

```json
{"W1": [[0.0397, 0.351, 0.0529, 0.0636], [0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0]], "b1": [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0], "W2": [[10.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]], "b2": [0.0]}
```