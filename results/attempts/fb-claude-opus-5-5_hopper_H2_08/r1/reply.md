## Round 0 diagnosis

- **The thigh was pinned at its joint limit.** The thigh angle stayed in [-0.005, 0.003] even though mean |a0| was 0.46. The thigh's upper limit is 0, so the positive a0 that should have corrected the backward lean only pressed the joint against its stop. The thigh balance loop had no effect.
- **The robot tipped over its foot as one rigid stick.** The torso angle reached -0.19 while the thigh angle stayed at 0, and x moved backward. That points to ankle torque. In the late part of the cycle, cos(hop) was about -1, so the rhythm sent a2 ≈ -0.3. The foot PD added more negative torque as the foot angle rose to +0.1. With the foot planted, negative a2 tips the leg, and everything above it, backward. The negative leg torque (bending to -0.3) also pushed the same way.

## Changes for round 1

- **Thigh off its limit:** the posture target is now -0.1, so the torso PD can act in both directions. The torso PD is stiffer: -3·obs[1] - 0.4·obs[7].
- **Ankle-strategy balance (new unit):** `a2 += -2·obs[1] - 0.3·obs[7] - 0.3·(obs[5] - 0.4)`.
  - Leaning backward or moving backward gives positive foot torque, which tips the body forward.
  - The obs[5] term regulates forward speed towards 0.4 m/s.
- **Foot rhythm removed.** The foot PD is weaker, so it doesn't fight the balance unit.
- **Leg and thigh rhythm reduced** to 0.25 and 0.15 until survival is established.

```json
{"target": "cpg", "obs_dim": 11, "act_dim": 3, "hidden": 16,
 "oscillators": [{"name": "hop", "freq_hz": 2.0, "phase0": 0.0}],
 "couplings": [],
 "bias": {"a0": 0.0, "a1": -0.2, "a2": 0.12},
 "units": [
   {"type": "linear", "name": "torso_pd", "inputs": {"obs[1]": -3.0, "obs[7]": -0.4},
    "range": 2.5, "tol": 0.05, "to": {"a0": 1.0}},
   {"type": "linear", "name": "thigh_posture", "inputs": {"obs[2]": -1.0, "obs[8]": -0.05},
    "range": 2.0, "tol": 0.05, "to": {"a0": 1.0}},
   {"type": "linear", "name": "leg_pd", "inputs": {"obs[3]": -2.0, "obs[9]": -0.1},
    "range": 2.5, "tol": 0.05, "to": {"a1": 1.0}},
   {"type": "linear", "name": "foot_pd", "inputs": {"obs[4]": -1.0, "obs[10]": -0.05},
    "range": 1.5, "tol": 0.05, "to": {"a2": 1.0}},
   {"type": "linear", "name": "ankle_balance", "inputs": {"obs[1]": -2.0, "obs[7]": -0.3, "obs[5]": -0.3},
    "range": 2.5, "tol": 0.05, "to": {"a2": 1.0}},
   {"type": "linear", "name": "rhythm_cos", "inputs": {"cos(hop)": 1.0},
    "range": 1.0, "tol": 0.02, "to": {"a1": 0.25}},
   {"type": "linear", "name": "rhythm_sin", "inputs": {"sin(hop)": 1.0},
    "range": 1.0, "tol": 0.02, "to": {"a0": 0.15}}
 ]}
```