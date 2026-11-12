# Round 5 (final): stop pushing the torso backwards

## What all five rounds have in common

Every design that survived more than a moment (rounds 0, 1, 2 and 4) had a **negative constant hip bias**, between −0.19 and −0.51 per hip. Every one of those settled with the torso at about −0.3 to −0.5 and drifted backwards. Round 3, with bias −0.55 and the opposite feedback sign, pitched to −0.85 within 0.06 s.

The data agree on two things:
- **A negative hip torque drives obs[1] negative.**
- **Negative feedback on obs[1] and obs[10] is the stabilising sign.** It survived for seconds; the positive sign failed almost immediately.

The real problem was therefore the bias, not the feedback sign. In round 4 the hips settled at roughly b − q − obs[1] − 0.2·v ≈ +0.3 per hip. With bias −0.22, that balance was only reached once the torso had leaned back to about −0.3, and that backward lean carried the robot backwards.

## Changes

1. **Hip bias −0.22 → +0.30.** This moves the equilibrium lean to about 0 to +0.05 at a forward speed near 0.5 m/s, instead of −0.3.
2. **Stiffer torso feedback: obs[1] gain −2.0, obs[10] gain −0.25.** This halves the effect of any error in that equilibrium estimate. The obs[8] speed term stays at −0.2, so the robot leans back when it goes fast and forward when it goes slow.

Everything else is unchanged from round 4: the oscillators, the couplings, the knee rhythm (straight in stance, flexed in early swing), and the soft ankles.

Because the score counts only forward displacement, erring towards a forward lean costs little compared with the steady backward drift seen in every round so far.

```json
{"target": "cpg", "obs_dim": 17, "act_dim": 6, "hidden": 16,
 "oscillators": [
   {"name": "R", "freq_hz": 0.9, "phase0": 1.5708},
   {"name": "L", "freq_hz": 0.9, "phase0": 4.7124}
 ],
 "couplings": [
   {"from": "R", "to": "L", "weight": 2.0, "phase_lag": 3.14159},
   {"from": "L", "to": "R", "weight": 2.0, "phase_lag": 3.14159}
 ],
 "bias": {"a0": 0.3, "a1": -0.3, "a3": 0.3, "a4": -0.3},
 "units": [
   {"type": "linear", "name": "hip_R",
    "inputs": {"cos(R)": 0.16, "obs[2]": -1.0, "obs[1]": -2.0, "obs[11]": -0.1, "obs[10]": -0.25, "obs[8]": -0.2},
    "range": 3.5, "tol": 0.05, "to": {"a0": 1.0}},
   {"type": "linear", "name": "knee_R",
    "inputs": {"sin(R)": 0.79, "cos(R)": 0.24, "obs[3]": -1.5, "obs[12]": -0.1},
    "range": 3.0, "tol": 0.03, "to": {"a1": 1.0}},
   {"type": "linear", "name": "ankle_R",
    "inputs": {"obs[4]": -0.5, "obs[13]": -0.03},
    "range": 1.0, "tol": 0.03, "to": {"a2": 1.0}},
   {"type": "linear", "name": "hip_L",
    "inputs": {"cos(L)": 0.16, "obs[5]": -1.0, "obs[1]": -2.0, "obs[14]": -0.1, "obs[10]": -0.25, "obs[8]": -0.2},
    "range": 3.5, "tol": 0.05, "to": {"a3": 1.0}},
   {"type": "linear", "name": "knee_L",
    "inputs": {"sin(L)": 0.79, "cos(L)": 0.24, "obs[6]": -1.5, "obs[15]": -0.1},
    "range": 3.0, "tol": 0.03, "to": {"a4": 1.0}},
   {"type": "linear", "name": "ankle_L",
    "inputs": {"obs[7]": -0.5, "obs[16]": -0.03},
    "range": 1.0, "tol": 0.03, "to": {"a5": 1.0}}
 ]}
```