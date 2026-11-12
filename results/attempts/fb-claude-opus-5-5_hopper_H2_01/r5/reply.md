Round 4 survived longer than round 0 (3.1 s against 1.8 s), but it still failed the same way. The thigh drifted back to −1.17 rad and the torso tipped forward to 0.194 rad, so the robot either leaned past the limit or sank. This round fixes the cause I now think is behind that drift, and changes nothing else.

**Diagnosis: the thigh rhythm runs in the wrong phase.**

- **When the robot is in the air.** In round 4 the foot leaves the ground around phase 0.5–1.3 and lands around phase 2.5. So flight is roughly phase 0.5–2.4, with its middle near π/2. Stance is roughly phase 2.5–6.3.
- **What the old thigh command did.** It was −0.25·sin(phase).
  - In flight sin is positive, so the thigh was driven backward. The leg was never brought forward under the hip.
  - In stance sin is negative, so the thigh was driven forward. With the foot on the ground, that reaction pitches the torso forward.
- **The data agree.** In every cycle the torso angle climbs during phase 3.8–5.0, for example 0.008 → 0.046, 0.021 → 0.062 and 0.040 → 0.075. Over several hops the leg ends up trailing and the torso tips past 0.2 rad.

**Round-5 changes (from round 4):**

- **Thigh rhythm sign flipped: −0.25·sin becomes +0.3·sin.**
  - In flight the thigh now swings forward, back towards its 0 limit, so the foot lands under the hip. This also pitches the torso backward, which cancels the forward creep.
  - In stance the thigh now sweeps backward. That drives the hip forward over the foot, and the hip reaction pitches the torso back, as the design hint describes.
- **a0 bias 0.06 → 0.08.** Both halves of the new thigh rhythm pitch the torso backward. A little more forward bias guards against the backward falls of rounds 1–3 and keeps forward speed.
- **Unchanged:**
  - Torso balance −3·(obs[1] + 0.15·obs[7]).
  - Leg and foot rhythm, and the 2 Hz frequency.
  - Leg, foot and thigh holds.

I can't test this before it is scored, so I don't know it will pass. The phase flip is the one change the round-4 data clearly point to.

```json
{"target": "cpg", "obs_dim": 11, "act_dim": 3, "hidden": 16,
 "oscillators": [{"name": "hop", "freq_hz": 2.0, "phase0": 0.0}],
 "couplings": [],
 "bias": {"a0": 0.08},
 "units": [
   {"type": "linear", "name": "torso_balance", "inputs": {"obs[1]": 1.0, "obs[7]": 0.15},
    "range": 1.5, "tol": 0.02, "to": {"a0": -3.0}},
   {"type": "linear", "name": "hop_rhythm", "inputs": {"sin(hop)": 1.0},
    "range": 1.2, "tol": 0.01, "to": {"a0": 0.3, "a1": 0.4, "a2": 0.3}},
   {"type": "linear", "name": "leg_pd", "inputs": {"obs[3]": 1.0, "obs[9]": 0.1},
    "range": 3.0, "tol": 0.02, "to": {"a1": -0.8}},
   {"type": "linear", "name": "foot_pd", "inputs": {"obs[4]": 1.0, "obs[10]": 0.1},
    "range": 2.0, "tol": 0.02, "to": {"a2": -0.7}},
   {"type": "linear", "name": "thigh_posture", "inputs": {"obs[2]": 1.0, "obs[8]": 0.05},
    "range": 3.0, "tol": 0.02, "to": {"a0": -0.6}}
 ]}
```