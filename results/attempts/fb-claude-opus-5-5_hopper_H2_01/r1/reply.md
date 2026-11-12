The robot falls at about 1.8 s with "height too low". The thigh drifted back to −1.18 rad while the torso stayed upright (torso angle never left [−0.03, 0.10]). The torso-balance loop keeps the torso level by rotating the thigh backward. The thigh posture hold (gain 0.3) was too weak to stop this. So the leg ends up trailing behind the hip, the hip sinks, and the robot settles below 0.7 m. The sinking is visible from 1.2 s, when height drops from 1.14 to 1.03.

Round-1 changes, still conservative:
- **Stronger leg-angle hold.** The thigh posture now holds the leg's absolute angle (torso + thigh, obs[1]+obs[2]) near vertical, with damping. The gain rises from 0.3 to 1.0. This keeps the foot under the hip instead of letting balance trade torso angle for thigh drift.
- **Smaller forward-lean bias.** The a0 bias drops from 0.09 to 0.05. Mean speed was already 0.61 m/s, more than the 0.375 m/s needed for 3 m in 8 s. Staying up matters more than speed now.
- **Foot.** The foot reached +0.62 rad. Its hold gain goes from 0.5 to 1.0 and its rhythmic push from 0.3 to 0.2.
- **Unchanged.** Leg hold, rhythm frequency and torso balance stay the same, so this round mainly tests the drift fix.

(Last round I sent two code blocks by mistake; this reply has one.)

```json
{"target": "cpg", "obs_dim": 11, "act_dim": 3, "hidden": 16,
 "oscillators": [{"name": "hop", "freq_hz": 2.0, "phase0": 0.0}],
 "couplings": [],
 "bias": {"a0": 0.05},
 "units": [
   {"type": "linear", "name": "torso_balance", "inputs": {"obs[1]": 1.0, "obs[7]": 0.15, "obs[5]": 0.03},
    "range": 1.5, "tol": 0.02, "to": {"a0": -3.0}},
   {"type": "linear", "name": "hop_rhythm", "inputs": {"sin(hop)": 1.0},
    "range": 1.2, "tol": 0.01, "to": {"a0": -0.25, "a1": 0.4, "a2": 0.2}},
   {"type": "linear", "name": "leg_pd", "inputs": {"obs[3]": 1.0, "obs[9]": 0.1},
    "range": 3.0, "tol": 0.02, "to": {"a1": -0.8}},
   {"type": "linear", "name": "foot_pd", "inputs": {"obs[4]": 1.0, "obs[10]": 0.1},
    "range": 2.0, "tol": 0.02, "to": {"a2": -1.0}},
   {"type": "linear", "name": "leg_vertical_hold", "inputs": {"obs[1]": 1.0, "obs[2]": 1.0, "obs[8]": 0.1},
    "range": 3.0, "tol": 0.02, "to": {"a0": -1.0}}
 ]}
```