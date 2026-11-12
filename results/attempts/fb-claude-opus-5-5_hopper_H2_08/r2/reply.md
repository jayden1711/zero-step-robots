## Round 1 diagnosis

- **Balance works.** The robot survived all 10 episodes for the full 8 s. Torso angle stayed within ±0.065 rad, and no unit saturated.
- **It never moved forward.**
  - The foot was on the ground 99% of the time, with one touchdown, so the robot never left the ground.
  - x swayed back and forth by about ±0.03 m in step with the 2 Hz rhythm: forward while the torso pitched back, back while it pitched forward. The net result was d ≈ 0.13 m.
  - A one-legged robot cannot make net progress while its foot stays planted, so the gait needs real flight phases.

## Changes for round 2

1. **Stronger leg rhythm (a1: 0.25 → 0.6).** With the joint bent near -0.28 rad at most, the leg could not push hard enough to leave the ground. Positive cos(hop) now extends the leg sharply (push-off), and negative cos(hop) compresses it.
2. **Foot push-off in phase with leg extension (a2 += 0.3·cos).** Positive foot torque in stance tips the body forward, which adds forward impulse during push-off.
3. **Thigh drives propulsion (new).** The thigh now gets `-0.3·cos(hop)`, in phase with leg extension. In stance this sweeps the leg backward and pushes the body forward. When cos(hop) < 0 (flight and compression), the thigh torque turns positive and returns the leg towards 0, the forward position, ready for landing. A small `sin` term (0.1) is kept for swing timing.
4. **Thigh posture and leg damping unchanged.** The thigh posture target stays at -0.1. Leg PD damping is slightly higher, so landings don't buckle the leg.
5. **Balance loops unchanged, with a stronger push towards speed.** The ankle speed term rises to -0.4·(obs[5] - 0.5), written as bias +0.2 on a2 together with the existing offset. This pushes harder for forward motion.

This round is deliberately more aggressive. Surviving in place scores about 0, so I would rather learn how a real hop fails and tune it back.

```json
{"target": "cpg", "obs_dim": 11, "act_dim": 3, "hidden": 16,
 "oscillators": [{"name": "hop", "freq_hz": 2.0, "phase0": 0.0}],
 "couplings": [],
 "bias": {"a0": 0.0, "a1": -0.2, "a2": 0.2},
 "units": [
   {"type": "linear", "name": "torso_pd", "inputs": {"obs[1]": -3.0, "obs[7]": -0.4},
    "range": 2.5, "tol": 0.05, "to": {"a0": 1.0}},
   {"type": "linear", "name": "thigh_posture", "inputs": {"obs[2]": -1.0, "obs[8]": -0.05},
    "range": 2.5, "tol": 0.05, "to": {"a0": 1.0}},
   {"type": "linear", "name": "leg_pd", "inputs": {"obs[3]": -2.0, "obs[9]": -0.15},
    "range": 3.0, "tol": 0.05, "to": {"a1": 1.0}},
   {"type": "linear", "name": "foot_pd", "inputs": {"obs[4]": -1.0, "obs[10]": -0.05},
    "range": 1.5, "tol": 0.05, "to": {"a2": 1.0}},
   {"type": "linear", "name": "ankle_balance", "inputs": {"obs[1]": -2.0, "obs[7]": -0.3, "obs[5]": -0.4},
    "range": 3.0, "tol": 0.05, "to": {"a2": 1.0}},
   {"type": "linear", "name": "rhythm_cos", "inputs": {"cos(hop)": 1.0},
    "range": 1.0, "tol": 0.02, "to": {"a0": -0.3, "a1": 0.6, "a2": 0.3}},
   {"type": "linear", "name": "rhythm_sin", "inputs": {"sin(hop)": 1.0},
    "range": 1.0, "tol": 0.02, "to": {"a0": 0.1}}
 ]}
```