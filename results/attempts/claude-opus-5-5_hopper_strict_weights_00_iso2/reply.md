This looks like the Hopper task. My reading of the observation vector:

| Index | Meaning |
|---|---|
| 0 | height |
| 1 | torso angle |
| 2–4 | thigh, leg and foot joint angles |
| 5–7 | x, z and angle velocities |
| 8–10 | joint velocities |

**Approach.** The flat foot gives the hopper a support base under its centre of mass. So I hold all three joints stiffly at zero (straight leg, flat foot), and the hopper stays upright and healthy for all 1000 steps. That earns about 1 per step, with negligible control cost.

**Controller.** Hidden units 0–2 each implement a saturated PD law for one joint: `action_j = -tanh(Kp·q_j + Kd·q̇_j)`. The other hidden units are unused.

| Joint | Kp | Kd |
|---|---|---|
| Thigh | 5 | 0.5 |
| Leg | 5 | 0.4 |
| Foot | 4 | 0.2 |

**Caveats.** I couldn't run or test this. The design relies on two assumptions I haven't checked: that I've mapped the observation indices correctly, and that a positive action produces a positive joint torque. I deliberately didn't try to hop forward. That could score above 1000, but without testing it is far more likely to fall early.

```json
{
"W1": [
[0,0,5,0,0,0,0,0,0.5,0,0],
[0,0,0,5,0,0,0,0,0,0.4,0],
[0,0,0,0,4,0,0,0,0,0,0.2],
[0,0,0,0,0,0,0,0,0,0,0],
[0,0,0,0,0,0,0,0,0,0,0],
[0,0,0,0,0,0,0,0,0,0,0],
[0,0,0,0,0,0,0,0,0,0,0],
[0,0,0,0,0,0,0,0,0,0,0],
[0,0,0,0,0,0,0,0,0,0,0],
[0,0,0,0,0,0,0,0,0,0,0],
[0,0,0,0,0,0,0,0,0,0,0],
[0,0,0,0,0,0,0,0,0,0,0],
[0,0,0,0,0,0,0,0,0,0,0],
[0,0,0,0,0,0,0,0,0,0,0],
[0,0,0,0,0,0,0,0,0,0,0],
[0,0,0,0,0,0,0,0,0,0,0]
],
"b1": [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
"W2": [
[-1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
[0,-1,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
[0,0,-1,0,0,0,0,0,0,0,0,0,0,0,0,0]
],
"b2": [0,0,0]
}
```