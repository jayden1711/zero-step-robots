Round 2 was the first design to stay up for all 8 s, in every episode, so the balance signs are now settled. But it barely moved: d was only 0.15 m. The foot was on the ground 99% of the time and never hopped. The 0.25 leg rhythm was too weak to lift off, and x only rocked back and forth about once a second, with almost no net drift. Three rounds remain, so this one has to start a real gait while keeping the balance loops that worked.

**Changes for round 3**

1. **Stronger hop rhythm**:
   - Leg rhythm amplitude goes from 0.25 to 0.6.
   - The leg PD setpoint moves to −0.3 rad, so the leg has room to compress and then push off.
   - The foot gets a 0.25 rhythm in phase with the leg, to add ankle push-off.
   - Thigh swing amplitude goes from 0.15 to 0.3.
2. **Stronger balance**, to absorb the larger disturbances from hopping:
   - Thigh: `−4·obs[1] − 0.5·obs[7]`.
   - Ankle: `−2.5·obs[1] − 0.4·obs[7]`.
   - I widened the linear ranges so these terms don't saturate.
3. **Forward drive**: the lean target rises to 0.06 rad and falls by 0.05 rad per m/s of forward speed.
   - On the thigh this gives a `−0.2·obs[5]` term; on the ankle, a `−0.125·obs[5]` term.
   - If the robot drifts backward, the target lean grows and pushes it forward again.

**Biases**

| Action | Bias | Where it comes from |
|---|---|---|
| a0 | +0.09 | thigh PD toward −0.15 (−0.15) plus lean term (4 × 0.06 = +0.24) |
| a1 | −0.6 | leg PD gain 2 × setpoint −0.3 |
| a2 | +0.15 | ankle lean term, 2.5 × 0.06 |

**What to look for in the results**

- If the robot now falls, the leg-to-thigh phase (cos vs. sin) is the next thing to test.
- If x goes negative, the lean target needs to be larger.

```json
{"target": "cpg", "obs_dim": 11, "act_dim": 3, "hidden": 16,
 "oscillators": [{"name": "hop", "freq_hz": 2.0, "phase0": 0.0}],
 "bias": {"a0": 0.09, "a1": -0.6, "a2": 0.15},
 "units": [
   {"type": "linear", "name": "torso_balance", "inputs": {"obs[1]": -4.0, "obs[7]": -0.5, "obs[5]": -0.2},
    "range": 3.5, "tol": 0.05, "to": {"a0": 1.0}},
   {"type": "linear", "name": "thigh_pd", "inputs": {"obs[2]": -1.0, "obs[8]": -0.1},
    "range": 2.5, "tol": 0.05, "to": {"a0": 1.0}},
   {"type": "linear", "name": "thigh_rhythm", "inputs": {"sin(hop)": 0.3},
    "range": 0.5, "tol": 0.02, "to": {"a0": 1.0}},
   {"type": "linear", "name": "leg_pd", "inputs": {"obs[3]": -2.0, "obs[9]": -0.2},
    "range": 4.0, "tol": 0.05, "to": {"a1": 1.0}},
   {"type": "linear", "name": "leg_rhythm", "inputs": {"cos(hop)": 0.6},
    "range": 0.9, "tol": 0.02, "to": {"a1": 1.0}},
   {"type": "linear", "name": "ankle_balance", "inputs": {"obs[1]": -2.5, "obs[7]": -0.4, "obs[5]": -0.125},
    "range": 3.0, "tol": 0.05, "to": {"a2": 1.0}},
   {"type": "linear", "name": "foot_pd", "inputs": {"obs[4]": -0.5, "obs[10]": -0.05},
    "range": 2.0, "tol": 0.05, "to": {"a2": 1.0}},
   {"type": "linear", "name": "foot_rhythm", "inputs": {"cos(hop)": 0.25},
    "range": 0.4, "tol": 0.02, "to": {"a2": 1.0}}
 ]}
```