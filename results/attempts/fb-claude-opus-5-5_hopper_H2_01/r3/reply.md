Round 2 survived all 8 s but moved 0 m. The robot stood with the foot down 99% of the time and rocked in place, with the torso averaging a slight backward lean. Nothing was driving it forward.

- **Weak leg rhythm.** The leg-hold target was straight (0 rad), which is also the leg's upper joint limit. So the extension half of the rhythm pushed into the stop and did no work, and the leg only bent to −0.3 rad.
- **No forward lean.** The thigh hold (gain 1.0) and the −0.05 a0 bias cancelled any forward lean. The ankle term alone could not produce forward motion.

**Round-3 changes**

- **Real push-off.**
  - The leg-hold target moves to a slightly bent knee: a1 bias −0.1 gives about −0.13 rad.
  - The leg rhythm amplitude rises from 0.4 to 0.6, so extension now has room to push.
  - The foot rhythm rises from 0.2 to 0.35.
- **Forward lean.**
  - The a0 bias goes from −0.05 to +0.06.
  - The thigh-hold gain drops from 1.0 to 0.7. That sits between round 0 (0.3, which drifted) and round 2 (1.0, which stood still).
- **Stronger speed regulation.** The obs[5] weight in torso balance rises from 0.03 to 0.08. At about 0.6 m/s the robot leans back by roughly 0.05 rad, which stops the runaway seen in round 0.
- **Thigh swing.** The thigh rhythm rises from −0.25 to −0.3: it sweeps back in stance and swings forward in flight.
- **Unchanged.** Torso-angle and angular-velocity gains, frequency (2 Hz), foot hold, and the ankle speed term.

```json
{"target": "cpg", "obs_dim": 11, "act_dim": 3, "hidden": 16,
 "oscillators": [{"name": "hop", "freq_hz": 2.0, "phase0": 0.0}],
 "couplings": [],
 "bias": {"a0": 0.06, "a1": -0.1, "a2": 0.1},
 "units": [
   {"type": "linear", "name": "torso_balance", "inputs": {"obs[1]": 1.0, "obs[7]": 0.15, "obs[5]": 0.08},
    "range": 1.5, "tol": 0.02, "to": {"a0": -3.0}},
   {"type": "linear", "name": "hop_rhythm", "inputs": {"sin(hop)": 1.0},
    "range": 1.2, "tol": 0.01, "to": {"a0": -0.3, "a1": 0.6, "a2": 0.35}},
   {"type": "linear", "name": "leg_pd", "inputs": {"obs[3]": 1.0, "obs[9]": 0.1},
    "range": 3.0, "tol": 0.02, "to": {"a1": -0.8}},
   {"type": "linear", "name": "foot_pd", "inputs": {"obs[4]": 1.0, "obs[10]": 0.1},
    "range": 2.0, "tol": 0.02, "to": {"a2": -1.0}},
   {"type": "linear", "name": "thigh_hold", "inputs": {"obs[2]": 1.0, "obs[8]": 0.1},
    "range": 3.0, "tol": 0.02, "to": {"a0": -0.7}},
   {"type": "linear", "name": "ankle_speed", "inputs": {"obs[5]": 1.0},
    "range": 4.0, "tol": 0.02, "to": {"a2": -0.2}}
 ]}
```