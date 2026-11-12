I can't simulate, so the design below rests on my reading of the `walker2d.xml` sign conventions. All hinges, including the torso, use axis `0 -1 0`. The hip and knee ranges are [-150°, 0], so a positive action pushes a joint toward straight. A negative thigh angle means the thigh is behind the torso, and the toes point toward +x. If those conventions are wrong, this controller will fail.

**Design (SIMBICON-style, with no stance/swing gating):**

- **Clock.** One phase oscillator runs at 0.55 Hz. Forward velocity speeds it up: dψ/dt = 2π·0.55 + 1.5·v. Cadence therefore rises with speed, so the swing leg keeps up with the body and doesn't fall behind it.
- **Hips, split into two independent modes:**
  - *Common mode* (a0+a3) keeps the torso at a slight backward lean: T = 1.0·(θ − (0.26 + 0.1·v)) + 0.1·θ̇. The torso feels −(a0+a3) exactly, so this works whichever leg is on the ground. The lean is needed because each hip can only swing the thigh back to vertical relative to the torso. The torso must lean back for a foot to land in front.
  - *Differential mode* (a0−a3) is a PD controller. It drives the angle between the legs, qR−qL, toward 2·0.22·sin ψ, which makes a compass gait. This mode puts no torque on the torso, so the two modes don't interfere.
- **Knees.** Each knee is a PD controller toward a target set by the phase. During that leg's swing window (ψ from about −1.3 to 0.6 for the right leg) the target is flexed, at −0.85 rad. Otherwise the target is +0.15, which presses the knee straight against its stop.
- **Ankles.** Each ankle is a PD controller that holds the foot at 0. During swing the target shifts to toes-up so the foot clears the ground. A push-off pulse (toes down, −0.4) fires just before that leg lifts off.
- **Start.** The phase starts at 0, with both legs together. The right leg lifts and swings forward first, which shifts the centre of mass forward over the left foot to start the first step.

```json
{"target": "cpg", "obs_dim": 17, "act_dim": 6, "hidden": 16,
 "oscillators": [{"name": "p", "freq_hz": 0.55, "phase0": 0.0, "feedback": {"obs[8]": 1.5}}],
 "couplings": [],
 "bias": {"a0": -0.13, "a1": -0.35, "a2": -0.1, "a3": -0.13, "a4": -0.35, "a5": -0.1},
 "units": [
   {"type": "linear", "name": "hip_R", "inputs": {"obs[1]": 0.5, "obs[10]": 0.05, "obs[8]": -0.05, "sin(p)": 0.66, "obs[2]": -1.5, "obs[5]": 1.5, "obs[11]": -0.1, "obs[14]": 0.1},
    "range": 3.0, "tol": 0.02, "to": {"a0": 1.0}},
   {"type": "linear", "name": "hip_L", "inputs": {"obs[1]": 0.5, "obs[10]": 0.05, "obs[8]": -0.05, "sin(p)": -0.66, "obs[2]": 1.5, "obs[5]": -1.5, "obs[11]": 0.1, "obs[14]": -0.1},
    "range": 3.0, "tol": 0.02, "to": {"a3": 1.0}},
   {"type": "linear", "name": "knee_R_pd", "inputs": {"obs[3]": -1.0, "obs[12]": -0.06},
    "range": 3.5, "tol": 0.02, "to": {"a1": 1.0}},
   {"type": "linear", "name": "knee_L_pd", "inputs": {"obs[6]": -1.0, "obs[15]": -0.06},
    "range": 3.5, "tol": 0.02, "to": {"a4": 1.0}},
   {"type": "reflex", "name": "swing_R", "inputs": {"cos(p)": 0.9394, "sin(p)": -0.3429},
    "threshold": 0.5817, "sharpness": 10.0, "to": {"a1": -0.5, "a2": 0.1}},
   {"type": "reflex", "name": "swing_L", "inputs": {"cos(p)": -0.9394, "sin(p)": 0.3429},
    "threshold": 0.5817, "sharpness": 10.0, "to": {"a4": -0.5, "a5": 0.1}},
   {"type": "linear", "name": "ankle_R_pd", "inputs": {"obs[4]": -0.5, "obs[13]": -0.03},
    "range": 0.8, "tol": 0.02, "to": {"a2": 1.0}},
   {"type": "linear", "name": "ankle_L_pd", "inputs": {"obs[7]": -0.5, "obs[16]": -0.03},
    "range": 0.8, "tol": 0.02, "to": {"a5": 1.0}},
   {"type": "reflex", "name": "push_R", "inputs": {"cos(p)": -0.0292, "sin(p)": -0.9996},
    "threshold": 0.92, "sharpness": 25.0, "to": {"a2": -0.2}},
   {"type": "reflex", "name": "push_L", "inputs": {"cos(p)": 0.0292, "sin(p)": 0.9996},
    "threshold": 0.92, "sharpness": 25.0, "to": {"a5": -0.2}}
 ]}
```