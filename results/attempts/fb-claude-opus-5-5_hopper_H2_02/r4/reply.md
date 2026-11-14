Round 3 is the first design that moved: 1.48 m at about 1 m/s. It fell in every episode at about 1.53 s, from height too low.

**What round 3 showed**

- The robot shuffled forward with the foot on the ground 95% of the time. It never really hopped.
- The torso kept accelerating forward, but the leg was not carried along with it:
  - The thigh angle reached −1.04 rad, meaning the leg trailed far behind the hip.
  - The foot hit its −0.79 limit.
  - The height fell steadily, from 1.27 m at 0.9 s to 0.72 m by 1.53 s.
- So the body fell forward over a leg left behind. The forward drive was too strong and the leg had nothing pulling it back under the body.
- Passing only needs about 0.4 m/s (3 m in 8 s). Holding round 2's stability at a modest speed is worth more than going fast.

**Changes for round 4**

1. **Weaker forward drive**:
   - The lean target drops from 0.06 to 0.02 rad.
   - Speed feedback doubles: −0.4·obs[5] on the thigh and −0.25·obs[5] on the ankle. At about 0.5 m/s this cancels the lean drive.
2. **Stronger thigh PD**: gain 2 (was 1) toward −0.1 rad, with more damping. When the leg trails, as at −1.0 rad, this gives a strong forward swing that brings the leg back under the hip.
3. **Stiffer foot PD**: 1.5 (was 0.5), so the ankle stays off its limit.
4. **More hop**: the leg rhythm rises from 0.6 to 0.7, to get some flight so the foot can be repositioned.
5. **Kept from round 3**: thigh rhythm 0.3 and foot rhythm 0.25.

**Biases**

| Action | Bias | Where it comes from |
|---|---|---|
| a0 | −0.12 | thigh PD (2 × −0.1 = −0.2) plus lean term (4 × 0.02 = +0.08) |
| a1 | −0.6 | leg PD gain 2 × setpoint −0.3 (unchanged) |
| a2 | +0.05 | ankle lean term, 2.5 × 0.02 |

```json
{"target": "cpg", "obs_dim": 11, "act_dim": 3, "hidden": 16,
 "oscillators": [{"name": "hop", "freq_hz": 2.0, "phase0": 0.0}],
 "bias": {"a0": -0.12, "a1": -0.6, "a2": 0.05},
 "units": [
   {"type": "linear", "name": "torso_balance", "inputs": {"obs[1]": -4.0, "obs[7]": -0.5, "obs[5]": -0.4},
    "range": 4.0, "tol": 0.05, "to": {"a0": 1.0}},
   {"type": "linear", "name": "thigh_pd", "inputs": {"obs[2]": -2.0, "obs[8]": -0.2},
    "range": 4.0, "tol": 0.05, "to": {"a0": 1.0}},
   {"type": "linear", "name": "thigh_rhythm", "inputs": {"sin(hop)": 0.3},
    "range": 0.5, "tol": 0.02, "to": {"a0": 1.0}},
   {"type": "linear", "name": "leg_pd", "inputs": {"obs[3]": -2.0, "obs[9]": -0.2},
    "range": 4.0, "tol": 0.05, "to": {"a1": 1.0}},
   {"type": "linear", "name": "leg_rhythm", "inputs": {"cos(hop)": 0.7},
    "range": 1.0, "tol": 0.02, "to": {"a1": 1.0}},
   {"type": "linear", "name": "ankle_balance", "inputs": {"obs[1]": -2.5, "obs[7]": -0.4, "obs[5]": -0.25},
    "range": 3.5, "tol": 0.05, "to": {"a2": 1.0}},
   {"type": "linear", "name": "foot_pd", "inputs": {"obs[4]": -1.5, "obs[10]": -0.1},
    "range": 3.0, "tol": 0.05, "to": {"a2": 1.0}},
   {"type": "linear", "name": "foot_rhythm", "inputs": {"cos(hop)": 0.25},
    "range": 0.4, "tol": 0.02, "to": {"a2": 1.0}}
 ]}
```