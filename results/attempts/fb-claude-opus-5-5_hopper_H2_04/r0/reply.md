This first design is a conservative hopping gait with strong posture control. The idea is to stay healthy first, then make progress forward.

**How the controller is built**
- **Oscillator:** one oscillator, "hop", runs at 2 Hz.
- **Torso balance (thigh, a0):** the thigh torque is −3·(torso angle + 0.15·torso angular velocity). This opposes both lean and pitch rate, as the hint says.
- **Lean and speed (thigh, a0):** a bias of +0.2 sets a slight forward lean. A small −0.2·x-velocity term leans the torso back when the robot goes too fast.
- **Leg and foot holding (a1, a2):** proportional-derivative (PD) control holds the leg joint at about −0.1 rad (slightly bent) and the foot at 0. This keeps the leg from collapsing.
- **Rhythm:**
  - The thigh swings with 0.3·cos.
  - The leg compresses and extends with 0.5·sin.
  - The foot pushes off with 0.3·sin, in phase with the leg.
  - The thigh swing leads the leg extension by a quarter cycle.
- **Rhythm size:** the rhythm amplitudes are kept moderate so the posture feedback stays in control. I'll scale them up once I see whether the robot stays upright.

```json
{"target": "cpg", "obs_dim": 11, "act_dim": 3, "hidden": 16,
 "oscillators": [{"name": "hop", "freq_hz": 2.0, "phase0": 0.0}],
 "bias": {"a0": 0.2, "a1": -0.2},
 "units": [
   {"type": "linear", "name": "torso_balance", "inputs": {"obs[1]": 1.0, "obs[7]": 0.15},
    "range": 0.6, "tol": 0.05, "to": {"a0": -3.0}},
   {"type": "linear", "name": "speed_reg", "inputs": {"obs[5]": 1.0},
    "range": 3.0, "tol": 0.05, "to": {"a0": -0.2}},
   {"type": "linear", "name": "leg_pd", "inputs": {"obs[3]": 1.0, "obs[9]": 0.05},
    "range": 1.5, "tol": 0.05, "to": {"a1": -2.0}},
   {"type": "linear", "name": "foot_pd", "inputs": {"obs[4]": 1.0, "obs[10]": 0.05},
    "range": 1.0, "tol": 0.05, "to": {"a2": -2.0}},
   {"type": "linear", "name": "thigh_rhythm", "inputs": {"cos(hop)": 1.0},
    "range": 1.0, "tol": 0.02, "to": {"a0": 0.3}},
   {"type": "linear", "name": "leg_rhythm", "inputs": {"sin(hop)": 1.0},
    "range": 1.0, "tol": 0.02, "to": {"a1": 0.5, "a2": 0.3}}
 ]}
```