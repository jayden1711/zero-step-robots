Round 1 fell backward in under 1 s, worse than round 0. Here is what I think happened and what this round changes.

**What went wrong in round 1**

- The thigh stayed pinned at its upper joint limit (0 rad, max seen 0.011).
- Adding obs[1] into the leg-vertical hold made the total balance demand on the thigh strongly positive whenever the torso tipped back. A positive thigh torque only pushes the thigh further against that limit.
- With the thigh against its stop, the thigh motor can't move anything, so it has no effect on the torso. That is why a0 saturated 18% of the time while the torso slowly fell back.
- So the balance loop needs the thigh to sit away from its 0 limit. Round 0's problem was the opposite one: the thigh drifted all the way to −1.18.

**Round-2 changes**

- **Thigh hold.** The hold acts on the thigh joint alone (obs[2] + 0.1·obs[8], no torso term), with gain 1.0. That is 3× round 0, which stops the −1.18 drift. With a0 bias −0.05 the thigh's resting point is about −0.05 rad, just off the limit.
- **Torso balance.** Same as round 0, which kept the torso within [−0.03, 0.10].
- **Speed control at the ankle.** Forward drive and speed limiting now go through the foot instead of the thigh bias: a2 += −0.2·(obs[5] − 0.5), split into a bias of +0.1 and a −0.2·obs[5] term.
  - When foot torque is positive with the foot planted, it tips the leg and body forward. Below 0.5 m/s it adds forward lean; above 0.5 m/s it brakes.
  - This leaves the thigh free to do balance.
- **Unchanged from round 1.** Rhythm (2 Hz), leg hold, and foot hold.

```json
{"target": "cpg", "obs_dim": 11, "act_dim": 3, "hidden": 16,
 "oscillators": [{"name": "hop", "freq_hz": 2.0, "phase0": 0.0}],
 "couplings": [],
 "bias": {"a0": -0.05, "a2": 0.1},
 "units": [
   {"type": "linear", "name": "torso_balance", "inputs": {"obs[1]": 1.0, "obs[7]": 0.15, "obs[5]": 0.03},
    "range": 1.5, "tol": 0.02, "to": {"a0": -3.0}},
   {"type": "linear", "name": "hop_rhythm", "inputs": {"sin(hop)": 1.0},
    "range": 1.2, "tol": 0.01, "to": {"a0": -0.25, "a1": 0.4, "a2": 0.2}},
   {"type": "linear", "name": "leg_pd", "inputs": {"obs[3]": 1.0, "obs[9]": 0.1},
    "range": 3.0, "tol": 0.02, "to": {"a1": -0.8}},
   {"type": "linear", "name": "foot_pd", "inputs": {"obs[4]": 1.0, "obs[10]": 0.1},
    "range": 2.0, "tol": 0.02, "to": {"a2": -1.0}},
   {"type": "linear", "name": "thigh_hold", "inputs": {"obs[2]": 1.0, "obs[8]": 0.1},
    "range": 3.0, "tol": 0.02, "to": {"a0": -1.0}},
   {"type": "linear", "name": "ankle_speed", "inputs": {"obs[5]": 1.0},
    "range": 4.0, "tol": 0.02, "to": {"a2": -0.2}}
 ]}
```