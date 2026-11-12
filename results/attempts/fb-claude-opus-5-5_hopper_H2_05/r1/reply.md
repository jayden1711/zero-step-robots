Round 0 never really hopped and fell backward. The foot was on the ground 88% of the time with only 4 touchdowns, and the leg bent by only about 0.19 rad. The thigh swing pushed the body forward and back about equally, then the whole body tipped backward.

**What the data shows:**
- **Balance sign is right.** The torso feedback did stabilise the torso for about 1.8 s. With 200× actuator gearing, a wrong sign would have tipped it over almost at once, so I keep the sign.
- **The rhythm is phased correctly.** x rose while the thigh swung back (phase about 1.3 to 3.8) and fell while it swung forward. The fix is to unload the leg during the forward swing.
- **The leg needs a real push-off.** The leg posture spring (gain 2) capped the leg rhythm at about ±0.2 rad. Thrust has to be much stronger.

**Changes in round 1:**
- **Leg thrust:** the leg rhythm becomes a near square-wave reflex, 0.7·tanh(3·sin), on the leg joint. It flexes hard and then extends hard. The leg spring is softer (1.5) and a −0.1 leg bias keeps the knee slightly bent.
- **Foot push:** the foot gets a smaller push (0.3) in the same phase as the leg.
- **Cycle frequency:** raised to 2.5 Hz for a brisker hop.
- **Thigh:** the swing rises to 0.35 on cos. The thigh posture spring is halved to 0.5 so it doesn't cancel the swing.
- **Torso balance:**
  - The P gain rises to 6 and the D gain to 0.8.
  - The forward-lean bias rises to 0.3, which targets about 0.05 rad of forward lean, to counter the backward drift.
  - The speed feedback rises to −0.15·obs[5].

```json
{"target": "cpg", "obs_dim": 11, "act_dim": 3, "hidden": 16,
 "oscillators": [{"name": "hop", "freq_hz": 2.5, "phase0": 0.0}],
 "couplings": [],
 "bias": {"a0": 0.3, "a1": -0.1},
 "units": [
   {"type": "linear", "name": "torso_balance", "inputs": {"obs[1]": -6.0, "obs[7]": -0.8, "obs[5]": -0.15},
    "range": 4.0, "tol": 0.05, "to": {"a0": 1.0}},
   {"type": "linear", "name": "thigh_posture", "inputs": {"obs[2]": -0.5, "obs[8]": -0.05},
    "range": 2.0, "tol": 0.05, "to": {"a0": 1.0}},
   {"type": "linear", "name": "leg_posture", "inputs": {"obs[3]": -1.5, "obs[9]": -0.1},
    "range": 4.0, "tol": 0.05, "to": {"a1": 1.0}},
   {"type": "linear", "name": "foot_posture", "inputs": {"obs[4]": -2.0, "obs[10]": -0.1},
    "range": 3.0, "tol": 0.05, "to": {"a2": 1.0}},
   {"type": "reflex", "name": "push_thrust", "inputs": {"sin(hop)": 1.0}, "threshold": 0.0,
    "sharpness": 3.0, "to": {"a1": 0.7, "a2": 0.3}},
   {"type": "linear", "name": "swing_rhythm", "inputs": {"cos(hop)": 1.0},
    "range": 1.0, "tol": 0.01, "to": {"a0": 0.35}}
 ]}
```