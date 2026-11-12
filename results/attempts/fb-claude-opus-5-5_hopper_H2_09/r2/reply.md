## Round 2: revert to the stated sign, keep the thigh off its joint stop, and add ankle balance

**What round 1 shows.** Flipping the thigh balance sign was wrong. The torso fell backward in about 0.1 s, ten times faster than in round 0. The thigh torque sat at the action limit on 29% of steps, which means the loop was driving the torso further over. The stated convention holds: negative thigh torque pitches the torso backward. The −0.11 bias made this worse by pushing the torso back from the first step.

**Rereading round 0 with the correct sign.** The backward drift in round 0 was not a sign problem.

- In seed 0, the thigh angle peaked at +0.010 rad. That is at its upper joint limit of 0.
- The balance loop was pushing positive thigh torque into that joint stop. The torque could not rotate the torso relative to the leg, so the whole robot slowly tipped backward as one rigid body. This is why x went negative.

Hip torque alone cannot stop the whole body from tipping while it pivots on the foot. That needs an ankle torque.

**Changes:**

1. **Balance sign reverted.** Thigh torque is now −3·(obs[1] + 0.25·obs[7]). This has more damping than round 0 and a lower gain, so it should saturate less.
2. **Thigh held off its stop.** A thigh hold toward −0.2 rad (gain −1.0, plus a −0.2 bias on a0) leaves room for the balance torque to act in both directions. The +0.12 forward-lean bias is removed. Forward lean waits until standing is confirmed.
3. **New ankle balance.** a2 gets −1.0·(obs[1] + 0.2·obs[7]). By the same reaction rule, positive foot torque pitches the leg forward. So when the robot tips back, the ankle pushes it forward again.
4. **Rhythm kept small.** Thigh swing is 0.1; push-off is 0.3 at the leg and 0.1 at the foot.

**How to read the round-2 results:**

- If the robot now survives several seconds near upright, I'll add forward lean and scale up the hop.
- If it still tips back with the thigh at 0, I'll move the thigh target further negative and raise the ankle gain.
- If it now tips forward, I'll reduce the ankle gain and the thigh offset.

```json
{"target": "cpg", "obs_dim": 11, "act_dim": 3, "hidden": 16,
 "oscillators": [{"name": "hop", "freq_hz": 2.5, "phase0": 0.0}],
 "bias": {"a0": -0.2, "a1": -0.1},
 "units": [
   {"type": "linear", "name": "torso_pd", "inputs": {"obs[1]": 1.0, "obs[7]": 0.25},
    "range": 3.0, "tol": 0.02, "to": {"a0": -3.0}},
   {"type": "linear", "name": "thigh_hold", "inputs": {"obs[2]": 1.0, "obs[8]": 0.1},
    "range": 3.0, "tol": 0.02, "to": {"a0": -1.0}},
   {"type": "linear", "name": "thigh_swing", "inputs": {"cos(hop)": 1.0},
    "range": 1.2, "tol": 0.01, "to": {"a0": 0.1}},
   {"type": "linear", "name": "leg_hold", "inputs": {"obs[3]": 1.0, "obs[9]": 0.1},
    "range": 3.0, "tol": 0.02, "to": {"a1": -2.0}},
   {"type": "linear", "name": "foot_hold", "inputs": {"obs[4]": 1.0, "obs[10]": 0.1},
    "range": 2.0, "tol": 0.02, "to": {"a2": -2.0}},
   {"type": "linear", "name": "ankle_balance", "inputs": {"obs[1]": 1.0, "obs[7]": 0.2},
    "range": 3.0, "tol": 0.02, "to": {"a2": -1.0}},
   {"type": "linear", "name": "pushoff", "inputs": {"sin(hop)": 1.0},
    "range": 1.2, "tol": 0.01, "to": {"a1": 0.3, "a2": 0.1}}
 ]}
```