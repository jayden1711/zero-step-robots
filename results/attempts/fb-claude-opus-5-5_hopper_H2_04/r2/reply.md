Round 1 fixed the falls: all 10 episodes lasted the full 8 s. But the robot barely moved. It covered about 0.08 m, with the foot on the ground 98% of the time and the leg almost locked (−0.04 to 0 rad). The posture control is now strong enough that the rhythm can't produce hops or any forward drift. Round 2 keeps the balance structure and adds drive:

- **Stronger rhythm:**
  - Thigh swing goes from 0.3 to 0.45·cos.
  - Leg extension goes from 0.3 to 0.6·sin.
  - Foot push-off goes from 0.2 to 0.4·sin.

  This should give real compression and push-off, and lift the foot off the ground.
- **Softer leg PD:** the gain drops from −3 to −2. The rhythm was being cancelled: the leg moved only 0.04 rad.
- **More forward lean:**
  - The a0 bias goes from 0.15 to 0.25 and the a2 bias from 0.08 to 0.1. This sets a lean target of about 0.07–0.08 rad, still well inside the 0.2 limit.
  - Speed regulation goes from −0.2 to −0.25·vx. At about 1 m/s this cancels the extra lean drive, so the robot leans forward only while it is slow.
- **Torso damping:** the angular-velocity weight goes from 0.2 to 0.25, for headroom against the bigger rhythm.

```json
{"target": "cpg", "obs_dim": 11, "act_dim": 3, "hidden": 16,
 "oscillators": [{"name": "hop", "freq_hz": 2.0, "phase0": 0.0}],
 "bias": {"a0": 0.25, "a1": 0.1, "a2": 0.1},
 "units": [
   {"type": "linear", "name": "torso_balance", "inputs": {"obs[1]": 1.0, "obs[7]": 0.25},
    "range": 1.0, "tol": 0.05, "to": {"a0": -3.0, "a2": -1.5}},
   {"type": "linear", "name": "speed_reg", "inputs": {"obs[5]": 1.0},
    "range": 3.0, "tol": 0.05, "to": {"a0": -0.25}},
   {"type": "linear", "name": "leg_pd", "inputs": {"obs[3]": 1.0, "obs[9]": 0.05},
    "range": 1.5, "tol": 0.05, "to": {"a1": -2.0}},
   {"type": "linear", "name": "foot_pd", "inputs": {"obs[4]": 1.0, "obs[10]": 0.05},
    "range": 1.0, "tol": 0.05, "to": {"a2": -1.0}},
   {"type": "linear", "name": "thigh_rhythm", "inputs": {"cos(hop)": 1.0},
    "range": 1.0, "tol": 0.02, "to": {"a0": 0.45}},
   {"type": "linear", "name": "leg_rhythm", "inputs": {"sin(hop)": 1.0},
    "range": 1.0, "tol": 0.02, "to": {"a1": 0.6, "a2": 0.4}}
 ]}
```