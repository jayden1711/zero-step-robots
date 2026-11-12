## Round 1: flip the thigh balance sign and stand slightly crouched

**What round 0 shows.** In every episode the torso fell backward. The fall was slow and smooth, and it lined up with the thigh rhythm:

- At oscillator phase 0, cos(hop) = 1 and the thigh swing adds +0.3 to a0. At those moments the torso pitched further back: −0.043 at 0.4 s and −0.114 at 0.8 s.
- At phase ≈ 1.6, cos(hop) ≈ 0 and the swing adds nothing. There the torso recovered toward upright: −0.004 and −0.077.
- The +0.12 bias kept pushing the torso backward from the start.

So in this simulation, **positive thigh torque pitches the torso backward**. That fits the joint mechanics: the hip torque acts as +τ on the thigh and −τ on the torso, and the planted leg barely moves. It contradicts the stated sign fact. As a result, the round-0 balance loop was positive feedback. It saturated (14% of steps at |a0| ≥ 0.99), driving the torso further back.

A second problem: the thigh and leg holds targeted angle 0, which is the joints' upper limit. A positive torque there is partly absorbed by the joint stop.

**Changes:**

1. **Balance sign flipped.** The thigh torque is now a0 = +3·(obs[1] + 0.15·obs[7]). When the torso leans back, this gives a negative thigh torque, which pitches the torso forward.
2. **Forward lean set by a negative bias.** The lean is now produced by a negative bias on a0 instead of a positive one.
3. **Posture moved off the joint limits.** The thigh is held near −0.1 rad and the leg near −0.1 rad, set through the biases. That way torques act in both directions.
4. **Rhythm kept small this round.** The thigh swing is 0.15, the leg push 0.4 and the foot push 0.2. I'll only scale the hop up once standing balance is confirmed.

```json
{"target": "cpg", "obs_dim": 11, "act_dim": 3, "hidden": 16,
 "oscillators": [{"name": "hop", "freq_hz": 2.5, "phase0": 0.0}],
 "bias": {"a0": -0.11, "a1": -0.2},
 "units": [
   {"type": "linear", "name": "torso_pd", "inputs": {"obs[1]": 1.0, "obs[7]": 0.15},
    "range": 2.0, "tol": 0.02, "to": {"a0": 3.0}},
   {"type": "linear", "name": "thigh_hold", "inputs": {"obs[2]": 1.0, "obs[8]": 0.1},
    "range": 3.0, "tol": 0.02, "to": {"a0": -0.5}},
   {"type": "linear", "name": "thigh_swing", "inputs": {"cos(hop)": 1.0},
    "range": 1.2, "tol": 0.01, "to": {"a0": 0.15}},
   {"type": "linear", "name": "leg_hold", "inputs": {"obs[3]": 1.0, "obs[9]": 0.1},
    "range": 3.0, "tol": 0.02, "to": {"a1": -2.0}},
   {"type": "linear", "name": "foot_hold", "inputs": {"obs[4]": 1.0, "obs[10]": 0.1},
    "range": 2.0, "tol": 0.02, "to": {"a2": -2.0}},
   {"type": "linear", "name": "pushoff", "inputs": {"sin(hop)": 1.0},
    "range": 1.2, "tol": 0.01, "to": {"a1": 0.4, "a2": 0.2}}
 ]}
```

**How to read the round-1 results:**

- If the torso now stays within ±0.1 rad for much longer, the sign flip is confirmed, and next round I'll scale up the hop and the lean for speed.
- If it now falls forward quickly, the flip was wrong. I'll revert to the stated sign and keep the off-limit posture.