Round 0 fell over backward in about 0.27 s. The cause was posture geometry, not the feedback sign.

**What went wrong in round 0**
- The thigh joint sat pinned at its upper limit of 0 for the whole episode (min −0.005, max 0.004). The torso feedback was pushing positive torque into that limit, and a joint at its limit cannot move further that way, so the feedback had no effect.
- The leg bias of −0.4 bent the knee to about −0.35 rad. With the thigh pinned straight, the thigh and torso move as one rigid body. To keep the foot under the body, that body has to tilt back by roughly 0.53 × the knee bend. That predicts −0.19 rad, which is exactly the torso angle we saw.
- So this robot can only bend its knee if the thigh angle sits below 0. Otherwise the torso is forced backward.

**What changes in round 1**
- **Knee (a1):** a PD hold near straight (about −0.1 rad), with only a small rhythmic term (0.2 × cos). This keeps the forced backward tilt small.
- **Thigh (a0):** the same balance feedback on torso angle and angular velocity (−3 and −0.3). I dropped the positive bias that pushed the thigh into its limit, and added a small negative term on the thigh angle itself (−0.3 × obs[2]) so it hovers slightly below 0, where torque can act both ways. The forward swing is 0.2 × sin.
- **Foot (a2):** acts as an ankle balance controller. It has a soft PD on the foot angle, and its torque rises with forward speed (0.3 × obs[5]) with an offset that sets a target speed of about 0.5 m/s. When the robot is slower than that, the foot tips the leg forward; when faster, it pushes back. A small push-off term follows the hop rhythm.
- **Rhythm:** 2.5 Hz with smaller amplitudes than round 0. This round's main job is to survive and confirm the balance loop works.

```json
{"target": "cpg", "obs_dim": 11, "act_dim": 3, "hidden": 16,
 "oscillators": [{"name": "hop", "freq_hz": 2.5, "phase0": 0.0}],
 "couplings": [],
 "bias": {"a0": 0.0, "a1": -0.2, "a2": -0.15},
 "units": [
   {"type": "linear", "name": "thigh_balance_swing",
    "inputs": {"obs[1]": -3.0, "obs[7]": -0.3, "obs[2]": -0.3, "sin(hop)": 0.2},
    "range": 2.0, "tol": 0.05, "to": {"a0": 1.0}},
   {"type": "linear", "name": "knee_pd_push",
    "inputs": {"obs[3]": -2.0, "obs[9]": -0.1, "cos(hop)": 0.2},
    "range": 2.0, "tol": 0.05, "to": {"a1": 1.0}},
   {"type": "linear", "name": "ankle_balance_speed",
    "inputs": {"obs[4]": -1.0, "obs[10]": -0.05, "obs[5]": 0.3, "cos(hop)": 0.1},
    "range": 2.0, "tol": 0.05, "to": {"a2": 1.0}}
 ]}
```