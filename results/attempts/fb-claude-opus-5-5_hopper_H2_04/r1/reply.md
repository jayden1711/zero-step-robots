Round 0 fell backward after about 0.95 s in every episode. Two things in the data point to the cause:

- **The thigh was jammed against its upper limit.** It reached a maximum of +0.018 rad against a 0 limit, and a0 was saturated positive on 20% of steps. A positive thigh torque only pitches the torso forward if the thigh can still rotate. Pinned at the limit, torso and leg move as one rigid stick, so the hip loses its forward-correcting authority.
- **The leg rhythm itself caused the backward pitch.** The torso dipped at phase ≈ 5–0 (−0.137, then −0.128), right after sin(hop) is most negative. With the foot planted, a negative leg torque pitches the thigh backward, and through the locked hip the torso too. The −0.2 bias on a1 made this worse.

**Changes for round 1:**

- **Balance through the ankle too.** With the foot flat on the ground, a positive foot torque pitches the whole body forward, the same sign logic as the thigh. So the torso-balance unit now also drives a2 (gain −1.5). This works even when the thigh is at its limit, because the long, heavy foot can shift the centre of pressure.
- **Stronger damping.** The angular-velocity weight goes from 0.15 to 0.2.
- **Small forward-lean target.** Positive biases on a0 and a2 aim for a torso angle of about +0.05.
- **Straighter leg.** The a1 bias is now slightly positive. The leg PD is stiffer and targets about 0 (straight). The leg rhythm is cut to 0.3, so leg flexion no longer throws the torso back.
- **Rhythm and foot push-off.** The foot gets a small sin component for toe push-off. The thigh swing (0.3·cos) and speed regulation are kept.

```json
{"target": "cpg", "obs_dim": 11, "act_dim": 3, "hidden": 16,
 "oscillators": [{"name": "hop", "freq_hz": 2.0, "phase0": 0.0}],
 "bias": {"a0": 0.15, "a1": 0.1, "a2": 0.08},
 "units": [
   {"type": "linear", "name": "torso_balance", "inputs": {"obs[1]": 1.0, "obs[7]": 0.2},
    "range": 0.8, "tol": 0.05, "to": {"a0": -3.0, "a2": -1.5}},
   {"type": "linear", "name": "speed_reg", "inputs": {"obs[5]": 1.0},
    "range": 3.0, "tol": 0.05, "to": {"a0": -0.2}},
   {"type": "linear", "name": "leg_pd", "inputs": {"obs[3]": 1.0, "obs[9]": 0.05},
    "range": 1.5, "tol": 0.05, "to": {"a1": -3.0}},
   {"type": "linear", "name": "foot_pd", "inputs": {"obs[4]": 1.0, "obs[10]": 0.05},
    "range": 1.0, "tol": 0.05, "to": {"a2": -1.0}},
   {"type": "linear", "name": "thigh_rhythm", "inputs": {"cos(hop)": 1.0},
    "range": 1.0, "tol": 0.02, "to": {"a0": 0.3}},
   {"type": "linear", "name": "leg_rhythm", "inputs": {"sin(hop)": 1.0},
    "range": 1.0, "tol": 0.02, "to": {"a1": 0.3, "a2": 0.2}}
 ]}
```