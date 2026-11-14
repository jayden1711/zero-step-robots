This controller is untested, as the setup requires, so it may not reach the 3 m threshold. It is a hand-derived Raibert-style toe-hopper built on the Hopper's joint limits (thigh and knee can only go to ≤ 0) and its long, heavy foot.

**How it works:**

- **Clock:** a single 2 Hz oscillator `P` sets the hop rhythm. It starts at 3.3 rad so the robot settles for about 0.15 s before the first push.
- **Push-off (ankle):** while cos P > 0.5, a reflex applies up to −0.8 of plantar-flexion torque. This rolls the foot onto its toe, lifts the robot into a hop and adds a backward pitch impulse.
- **Ankle posture (always on):**
  - PD that keeps the foot level relative to the ground. It has no effect in stance, where the foot is already flat, and levels the foot in flight.
  - Mild stiffness on the shank lean.
  - A speed term 0.15·(0.8 − v) that leans the body forward when it is slow.
- **Hip, flight window (phase near 1.2 rad):** gated PD on the hip angle toward q1d = 0.2·v − 0.21. This places the foot forward when fast and back when slow, which is the Raibert foot-placement rule.
- **Hip, stance window (phase near 3.9 rad):** gated stiff torso servo toward θ = −0.04.
- **Gating:** each window is made from a pair of reflex units, G·[tanh(gate + ε·e) − tanh(gate)]. This gives a phase-windowed linear gain, and the two units cancel exactly outside the window.
- **Hip, always on:** a weak torso servo for safety.
- **Knee:** stiff PD near −0.15 rad for shock absorption.

```json
{"target": "cpg", "obs_dim": 11, "act_dim": 3, "hidden": 16,
 "oscillators": [{"name": "P", "freq_hz": 2.0, "phase0": 3.3}],
 "couplings": [],
 "bias": {"a0": -0.08, "a1": -0.3, "a2": -0.25},
 "units": [
   {"type": "linear", "name": "torso_base", "inputs": {"obs[1]": -2.0, "obs[7]": -0.15},
    "range": 2.0, "tol": 0.02, "to": {"a0": 1.0}},
   {"type": "reflex", "name": "hip_flight_gated", "inputs": {"obs[5]": 0.125, "obs[2]": -0.625, "obs[8]": -0.0375, "cos(P)": 0.543, "sin(P)": 1.398},
    "threshold": 1.63125, "sharpness": 1.0, "to": {"a0": 4.0}},
   {"type": "reflex", "name": "hip_flight_cancel", "inputs": {"cos(P)": 0.543, "sin(P)": 1.398},
    "threshold": 1.5, "sharpness": 1.0, "to": {"a0": -4.0}},
   {"type": "reflex", "name": "torso_stance_gated", "inputs": {"obs[1]": -1.25, "obs[7]": -0.0875, "cos(P)": -0.726, "sin(P)": -0.688},
    "threshold": 1.05, "sharpness": 1.0, "to": {"a0": 4.0}},
   {"type": "reflex", "name": "torso_stance_cancel", "inputs": {"cos(P)": -0.726, "sin(P)": -0.688},
    "threshold": 1.0, "sharpness": 1.0, "to": {"a0": -4.0}},
   {"type": "linear", "name": "knee_pd", "inputs": {"obs[3]": -2.0, "obs[9]": -0.15},
    "range": 3.0, "tol": 0.02, "to": {"a1": 1.0}},
   {"type": "linear", "name": "ankle_pd_speed", "inputs": {"obs[1]": 1.2, "obs[2]": -1.2, "obs[3]": -1.2, "obs[4]": -1.8, "obs[10]": -0.08, "obs[5]": -0.15},
    "range": 3.0, "tol": 0.02, "to": {"a2": 1.0}},
   {"type": "reflex", "name": "toe_pushoff", "inputs": {"cos(P)": 1.0},
    "threshold": 0.5, "sharpness": 4.0, "to": {"a2": -0.4}}
 ]}
```