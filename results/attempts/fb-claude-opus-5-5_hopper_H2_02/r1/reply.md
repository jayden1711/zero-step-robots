The round-0 controller fell backward in about 0.76 s, in every episode alike. These changes are partly a test of signs, so I've left the rhythm small for this round.

**What went wrong**

- The thigh angle stayed between -0.005 and +0.004 rad, right at its upper limit of 0.
- The thigh command was 0.61 on average and at the action limit 20% of the time. So it was pushing positive, into that limit.
- Because the joint was pinned, the hip did no work. The robot fell backward as one stiff piece, and x went negative.

**My reading of the balance sign**

The torso and all three joints rotate about the same axis. With the foot planted, a positive thigh torque increases the thigh angle, which means the torso rotates back relative to the leg. So positive torque should pitch the torso **backward**, the opposite of what the hint says. The data fits this: the positive balance command and the +0.15 bias only pressed the thigh into its stop. Round 1 tests this by reversing the balance sign. If the torso now falls forward instead, I'll reverse it back.

**Changes**

1. **Flipped balance on a0**: `+3·obs[1] + 0.3·obs[7]`. When the torso leans back, the thigh torque becomes negative, which by my reading pitches it forward.
   - The forward-lean target of about 0.05 rad now comes from a bias of -0.15.
   - Speed regulation is `+0.1·obs[5]`, so the robot leans less as it speeds up.
2. **A weak PD on the thigh toward -0.3 rad**. This keeps the hip away from its 0 limit so it can push in both directions.
3. **A slight crouch**: a PD on the leg toward -0.3 rad, so the leg joint is also off its stop.
4. **Gentler foot control**, so the foot can follow the ground.
5. **Smaller rhythm amplitudes**: 0.15 on the thigh, 0.2 on the leg and 0.1 on the foot. The goal this round is to survive and learn the signs, not to hop hard.

The bias on a0 combines the lean target (-0.15) and the thigh PD setpoint (-0.3), giving -0.45. The bias on a1 is -0.6, which is the leg PD gain of 2 times the -0.3 setpoint.

```json
{"target": "cpg", "obs_dim": 11, "act_dim": 3, "hidden": 16,
 "oscillators": [{"name": "hop", "freq_hz": 2.0, "phase0": 0.0}],
 "bias": {"a0": -0.45, "a1": -0.6},
 "units": [
   {"type": "linear", "name": "torso_balance", "inputs": {"obs[1]": 3.0, "obs[7]": 0.3, "obs[5]": 0.1},
    "range": 2.5, "tol": 0.05, "to": {"a0": 1.0}},
   {"type": "linear", "name": "thigh_pd", "inputs": {"obs[2]": -1.0, "obs[8]": -0.1},
    "range": 2.0, "tol": 0.05, "to": {"a0": 1.0}},
   {"type": "linear", "name": "thigh_rhythm", "inputs": {"sin(hop)": 0.15},
    "range": 0.3, "tol": 0.02, "to": {"a0": 1.0}},
   {"type": "linear", "name": "leg_pd", "inputs": {"obs[3]": -2.0, "obs[9]": -0.2},
    "range": 3.0, "tol": 0.05, "to": {"a1": 1.0}},
   {"type": "linear", "name": "leg_rhythm", "inputs": {"cos(hop)": 0.2},
    "range": 0.4, "tol": 0.02, "to": {"a1": 1.0}},
   {"type": "linear", "name": "foot_pd", "inputs": {"obs[4]": -1.0, "obs[10]": -0.1},
    "range": 2.0, "tol": 0.05, "to": {"a2": 1.0}},
   {"type": "linear", "name": "foot_rhythm", "inputs": {"cos(hop)": 0.1},
    "range": 0.2, "tol": 0.02, "to": {"a2": 1.0}}
 ]}
```