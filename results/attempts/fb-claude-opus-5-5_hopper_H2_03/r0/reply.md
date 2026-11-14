Round 0 is a conservative baseline: a mild knee-driven hop on a stiff, balanced posture. Since I can't run anything, the main aim is to learn whether the balance loops keep the robot upright, and only then push for speed.

**Rhythm.** One 2 Hz oscillator `P` drives the knee's target angle: `q3_ref = -0.25 - 0.25·cos(P)`.
- It starts at `phase0 = π`, where the target is a straight leg, matching the initial pose.
- The knee then compresses to -0.5 rad and extends again once per cycle.
- The knee uses PD tracking: `a1 = 2·(q3_ref − q3) − 0.1·q̇3`.

**Torso balance (hip, a0).** `a0 = −2.0·θ − 0.15·θ̇`.
- This should give a natural frequency of about 18 rad/s and damping ratio ≈ 0.7, using effective inertia ≈ joint armature 1 + torso.
- A weak spring holds the thigh near −0.1 rad, so in flight the leg returns toward vertical.

**Whole-body balance and speed (ankle, a2).**
- Because thigh and leg angles are both ≤ 0, crouching forces the shin to lean forward. The ankle therefore regulates the thigh's absolute angle `α_t = q2 − θ` toward a slightly forward-leaning reference, rather than regulating the centre of mass directly.
- Gains are stiffness 1.5 and damping 0.26 on `q̇2 − θ̇`. The robot leans further forward when it is below a target speed of 0.5 m/s (gain 0.15).
- A second term `0.5·(θ − q2 − q3 − q4)` keeps the foot level with the ground in flight. In stance, with the foot flat, this term is zero.

```json
{"target": "cpg", "obs_dim": 11, "act_dim": 3, "hidden": 16,
 "oscillators": [{"name": "P", "freq_hz": 2.0, "phase0": 3.14159}],
 "couplings": [],
 "bias": {"a0": -0.03, "a1": -0.5, "a2": 0.15},
 "units": [
   {"type": "linear", "name": "torso_pd", "inputs": {"obs[1]": -2.0, "obs[7]": -0.15},
    "range": 1.5, "tol": 0.05, "to": {"a0": 1.0}},
   {"type": "linear", "name": "thigh_spring", "inputs": {"obs[2]": -0.3, "obs[8]": -0.03},
    "range": 1.0, "tol": 0.05, "to": {"a0": 1.0}},
   {"type": "linear", "name": "knee_pd_rhythm", "inputs": {"obs[3]": -2.0, "obs[9]": -0.1, "cos(P)": -0.5},
    "range": 2.5, "tol": 0.05, "to": {"a1": 1.0}},
   {"type": "linear", "name": "ankle_balance_speed", "inputs": {"obs[2]": 1.5, "obs[1]": -1.5, "obs[8]": 0.26, "obs[7]": -0.26, "obs[5]": -0.15},
    "range": 1.5, "tol": 0.05, "to": {"a2": 1.0}},
   {"type": "linear", "name": "foot_flat", "inputs": {"obs[1]": 0.5, "obs[2]": -0.5, "obs[3]": -0.5, "obs[4]": -0.5, "obs[10]": -0.05},
    "range": 1.5, "tol": 0.05, "to": {"a2": 1.0}}
 ]}
```

What I'll read from the results:
- **Very short episodes (< 100 steps):** probably a sign error or an unstable gain in the torso or ankle loop.
- **Long episodes with little displacement:** balance works, so the next step is a stronger push-off (larger knee amplitude, ankle push in phase, higher speed target).
- **Falls after some forward travel:** speed regulation needs tightening.