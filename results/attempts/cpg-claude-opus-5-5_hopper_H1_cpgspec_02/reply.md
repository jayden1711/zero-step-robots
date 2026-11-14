This controller has not been run. It is a hand-reasoned design, so whether it reaches 3 m is uncertain.

**How I read the joint conventions** (all Hopper joints rotate about −y):
- A positive torso angle means the torso leans back.
- The thigh and knee can only fold backward from straight; 0 is their forward limit.
- A positive foot angle means toe up.

**The design:**
- **Oscillator:** one 2 Hz oscillator, `hop`, sets the gait rhythm.
- **Thigh:** the target is −0.1 − 0.15·cos(φ). The thigh swings forward to its stop for landing, then sweeps back during stance to push the body forward.
- **Knee:** the target is −0.15 − 0.2·sin(φ). The knee bends during flight for foot clearance and straightens and pushes during stance.
- **Foot:** the target is 0.1·sin(φ) − 0.1·cos(φ). The toe lifts before landing and pushes down in late stance.
- **Torso balance (through the hip):**
  - A PD loop on torso angle and angular rate holds a slight forward lean.
  - The lean target moves back as speed rises: θ* = −0.07 + 0.05·v.
- **Ankle balance:**
  - A PD loop on the foot joint keeps the leg upright over the flat foot.
  - The torso angle and rate are also fed to the ankle.
  - A small speed term makes the ankle brake when the robot moves too fast.
- **Gain limits:** I kept the gains below the limit for stability, given that each action is held for the whole 8 ms step and the foot and torso inertias are small.

```json
{"target": "cpg", "obs_dim": 11, "act_dim": 3, "hidden": 16,
 "oscillators": [{"name": "hop", "freq_hz": 2.0, "phase0": 3.14159}],
 "couplings": [],
 "bias": {"a0": 0.08, "a1": -0.15, "a2": 0.04},
 "units": [
   {"type": "linear", "name": "hip_torso_balance_and_thigh_pd", "inputs": {"obs[1]": 2.0, "obs[2]": -0.6, "obs[5]": -0.1}, "range": 1.5, "tol": 0.02, "to": {"a0": 1.0}},
   {"type": "linear", "name": "hip_damping", "inputs": {"obs[7]": 0.08, "obs[8]": -0.04}, "range": 1.0, "tol": 0.02, "to": {"a0": 1.0}},
   {"type": "linear", "name": "knee_pd", "inputs": {"obs[3]": -1.0}, "range": 1.5, "tol": 0.02, "to": {"a1": 1.0}},
   {"type": "linear", "name": "knee_damping", "inputs": {"obs[9]": -0.08}, "range": 1.0, "tol": 0.02, "to": {"a1": 1.0}},
   {"type": "linear", "name": "ankle_balance_pd", "inputs": {"obs[4]": -1.0, "obs[1]": 0.3, "obs[5]": -0.05}, "range": 1.5, "tol": 0.02, "to": {"a2": 1.0}},
   {"type": "linear", "name": "ankle_damping", "inputs": {"obs[10]": -0.05, "obs[7]": 0.15}, "range": 1.0, "tol": 0.02, "to": {"a2": 1.0}},
   {"type": "linear", "name": "rhythm_cos", "inputs": {"cos(hop)": 1.0}, "range": 1.0, "tol": 0.02, "to": {"a0": -0.09, "a2": -0.1}},
   {"type": "linear", "name": "rhythm_sin", "inputs": {"sin(hop)": 1.0}, "range": 1.0, "tol": 0.02, "to": {"a1": -0.2, "a2": 0.1}}
 ]}
```