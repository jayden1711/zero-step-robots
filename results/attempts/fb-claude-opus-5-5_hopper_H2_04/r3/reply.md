Round 2 was the first design to move forward: about 1.5 m at 0.87 m/s, with real flight phases. Every episode then ended with the height too low at about 1.75 s. Episode seed 0 shows why:

- **The thigh angle ran away backward.** It reached −1.33 rad, so the leg ended up trailing far behind the torso.
- **The other joints stayed near straight.** The leg only bent to −0.18 rad, so the height loss came from the thigh, not the knee.
- **The torso stayed upright the whole time.** Its angle stayed between −0.06 and +0.08 rad.

So the body kept travelling forward but the foot was never brought back underneath it. The torso sank, from 1.31 m down to 0.71 m.

Nothing currently controls where the thigh is. The torso-balance and rhythm terms on a0 mostly cancel: the mean |a0| was only 0.10.

**Changes for round 3:**

- **New thigh placement unit.** It adds a0 = −1.0·(thigh angle + 0.1·thigh angular velocity). Combined with the bias, it pulls the thigh toward about −0.25 rad.
  - At the −1.33 rad seen in round 2, it gives about +1.1, which swings the leg forward hard. This mostly acts in flight, when the leg is light.
  - The damping term keeps the swing from overshooting.
- **a0 bias rebalanced.**
  - The forward-lean drive is lowered from 0.25 to 0.2.
  - The thigh unit's offset (−1.0 × 0.25) is folded in, so the net a0 bias is −0.05.
  - When the thigh sits at −0.25 rad, the lean drive is the same 0.2 as intended.
- **Stronger speed regulation:** −0.25 goes to −0.35 per m/s of x-velocity. This limits the acceleration that left the leg behind, and the robot leans less once it reaches about 0.6 m/s.
- **Foot push-off reduced:** the foot rhythm goes from 0.4 to 0.3·sin. The foot reached 0.70 rad, close to its 0.79 limit.
- **Unchanged:** torso balance, the leg and foot PD, the 2 Hz oscillator and the thigh and leg rhythm amplitudes.

```json
{"target": "cpg", "obs_dim": 11, "act_dim": 3, "hidden": 16,
 "oscillators": [{"name": "hop", "freq_hz": 2.0, "phase0": 0.0}],
 "bias": {"a0": -0.05, "a1": 0.1, "a2": 0.1},
 "units": [
   {"type": "linear", "name": "torso_balance", "inputs": {"obs[1]": 1.0, "obs[7]": 0.25},
    "range": 1.0, "tol": 0.05, "to": {"a0": -3.0, "a2": -1.5}},
   {"type": "linear", "name": "speed_reg", "inputs": {"obs[5]": 1.0},
    "range": 3.0, "tol": 0.05, "to": {"a0": -0.35}},
   {"type": "linear", "name": "thigh_place", "inputs": {"obs[2]": 1.0, "obs[8]": 0.1},
    "range": 2.5, "tol": 0.05, "to": {"a0": -1.0}},
   {"type": "linear", "name": "leg_pd", "inputs": {"obs[3]": 1.0, "obs[9]": 0.05},
    "range": 1.5, "tol": 0.05, "to": {"a1": -2.0}},
   {"type": "linear", "name": "foot_pd", "inputs": {"obs[4]": 1.0, "obs[10]": 0.05},
    "range": 1.0, "tol": 0.05, "to": {"a2": -1.0}},
   {"type": "linear", "name": "thigh_rhythm", "inputs": {"cos(hop)": 1.0},
    "range": 1.0, "tol": 0.02, "to": {"a0": 0.45}},
   {"type": "linear", "name": "leg_rhythm", "inputs": {"sin(hop)": 1.0},
    "range": 1.0, "tol": 0.02, "to": {"a1": 0.6, "a2": 0.3}}
 ]}
```