Round 3 lasted slightly longer than round 2 (1.88 s against 1.77 s) but failed the same way. The thigh again drifted backward, reaching −1.18 rad, and the robot sank until the height was too low. The thigh placement unit didn't stop the drift.

**Why the placement unit didn't work.** While the foot is on the ground, the thigh torque mainly pitches the torso. The torso-balance term cancels it there, and mean |a0| was only 0.08. The leg can only be swung forward while the foot is off the ground, in flight. The timing data show that the thigh rhythm was doing the opposite in flight:

- The foot leaves the ground at a phase of about 1.1–1.3. It lands again at about 3.6–3.8.
- Over that flight window, 0.45·cos(hop) runs from about +0.2 down to −0.8.
- So the rhythm drove the leg backward during most of every flight. This is why the leg ended up trailing further behind each hop.

**Changes for round 4:**

- **Thigh rhythm re-timed to swing forward in flight.** The thigh command is now 0.5·cos(hop − 2.0), which is −0.208·cos + 0.455·sin. It peaks in mid-flight (phase ≈ 2.0) and is negative during the middle of stance, around phase 5, where it pushes the leg back for propulsion.
- **Stronger thigh placement.** The gain goes from −1.0 to −1.2, still targeting −0.25 rad.
- **Slower target speed.** Only about 0.4 m/s is needed to cover 3 m in 8 s, and surviving matters more than speed.
  - The forward-lean drive drops from 0.2 to 0.18.
  - The speed feedback goes from −0.35 to −0.4.
  - The net a0 bias is 0.18 − 1.2 × 0.25 = −0.12.
- **Unchanged:** torso balance, the leg and foot PD, the leg and foot rhythm, and the 2 Hz oscillator.

```json
{"target": "cpg", "obs_dim": 11, "act_dim": 3, "hidden": 16,
 "oscillators": [{"name": "hop", "freq_hz": 2.0, "phase0": 0.0}],
 "bias": {"a0": -0.12, "a1": 0.1, "a2": 0.1},
 "units": [
   {"type": "linear", "name": "torso_balance", "inputs": {"obs[1]": 1.0, "obs[7]": 0.25},
    "range": 1.0, "tol": 0.05, "to": {"a0": -3.0, "a2": -1.5}},
   {"type": "linear", "name": "speed_reg", "inputs": {"obs[5]": 1.0},
    "range": 3.0, "tol": 0.05, "to": {"a0": -0.4}},
   {"type": "linear", "name": "thigh_place", "inputs": {"obs[2]": 1.0, "obs[8]": 0.1},
    "range": 2.5, "tol": 0.05, "to": {"a0": -1.2}},
   {"type": "linear", "name": "leg_pd", "inputs": {"obs[3]": 1.0, "obs[9]": 0.05},
    "range": 1.5, "tol": 0.05, "to": {"a1": -2.0}},
   {"type": "linear", "name": "foot_pd", "inputs": {"obs[4]": 1.0, "obs[10]": 0.05},
    "range": 1.0, "tol": 0.05, "to": {"a2": -1.0}},
   {"type": "linear", "name": "thigh_rhythm", "inputs": {"cos(hop)": -0.416, "sin(hop)": 0.909},
    "range": 1.0, "tol": 0.02, "to": {"a0": 0.5}},
   {"type": "linear", "name": "leg_rhythm", "inputs": {"sin(hop)": 1.0},
    "range": 1.0, "tol": 0.02, "to": {"a1": 0.6, "a2": 0.3}}
 ]}
```