This is a hand-designed CPG walker. It is untested, since I couldn't run the simulation. The design rests on a few physical assumptions.

**Key physical assumptions** (from the Walker2d XML: every hinge, including the torso's `rooty`, uses axis (0,−1,0)):
- A positive hip angle swings the leg forward relative to the torso. The hip range is [−150°, 0], so a leg can only reach in front of the hip in world terms if the torso leans back. The gait therefore holds the torso tilted back by about 0.3 rad. In this convention, positive torso angle means leaning back.
- A positive hip torque rotates the torso toward a negative angle. So the balance term is `+kt·(θ − θd)` on both hips.
- The knee is straight at its 0 limit and bends negative. The foot extends only forward of the ankle.
- The legs (about 20 kg) are far heavier than the torso (about 3.7 kg). Hip torques therefore mostly rotate the torso, so the torso mode is stiff and has little inertia. I chose the damping split to keep that mode stable at the 8 ms control step. The hips damp the leg's world angular velocity rather than the raw joint velocity.

**Structure** (6 units, each a saturating PD controller written as an exact `tanh` reflex):
- **Hips:** antisymmetric targets −0.32 ± 0.25·sin φ, plus feedback to hold the torso pitch near 0.3 rad leaning back.
- **Knees:** the swing knee bends to about −0.95 at the start of swing. In stance, the target is +0.14, which presses the knee against its straight limit, giving a stiff, compass-like stance leg. The bend timing makes the leg that moves forward also the leg that lifts, so the planted leg pushes the body forward.
- **Ankles:** the toe lifts in late swing, the foot pushes off in late stance, and a mild braking torque applies when the walker moves faster than 0.7 m/s.
- **Clock:** one oscillator at 0.75 Hz, sped up by forward velocity so the walker steps faster when it moves faster.

```json
{"target": "cpg", "obs_dim": 17, "act_dim": 6, "hidden": 16,
 "oscillators": [{"name": "osc", "freq_hz": 0.75, "phase0": 0.0, "feedback": {"obs[8]": 1.0}}],
 "couplings": [],
 "bias": {"a0": 0.0},
 "units": [
  {"type": "reflex", "name": "hip_R", "inputs": {"sin(osc)": 0.25, "obs[2]": -1.0, "obs[11]": -0.1375, "obs[1]": 0.5, "obs[10]": -0.1125},
   "threshold": 0.47, "sharpness": 4.0, "to": {"a0": 1.0}},
  {"type": "reflex", "name": "hip_L", "inputs": {"sin(osc)": -0.25, "obs[5]": -1.0, "obs[14]": -0.1375, "obs[1]": 0.5, "obs[10]": -0.1125},
   "threshold": 0.47, "sharpness": 4.0, "to": {"a3": 1.0}},
  {"type": "reflex", "name": "knee_R", "inputs": {"cos(osc)": -0.539, "sin(osc)": 0.109, "obs[3]": -1.0, "obs[12]": -0.1},
   "threshold": 0.4, "sharpness": 3.0, "to": {"a1": 1.0}},
  {"type": "reflex", "name": "knee_L", "inputs": {"cos(osc)": 0.539, "sin(osc)": -0.109, "obs[6]": -1.0, "obs[15]": -0.1},
   "threshold": 0.4, "sharpness": 3.0, "to": {"a4": 1.0}},
  {"type": "reflex", "name": "ankle_R", "inputs": {"sin(osc)": 0.186, "cos(osc)": 0.072, "obs[4]": -1.0, "obs[13]": -0.02, "obs[8]": -0.05},
   "threshold": -0.085, "sharpness": 1.5, "to": {"a2": 1.0}},
  {"type": "reflex", "name": "ankle_L", "inputs": {"sin(osc)": -0.186, "cos(osc)": -0.072, "obs[7]": -1.0, "obs[16]": -0.02, "obs[8]": -0.05},
   "threshold": -0.085, "sharpness": 1.5, "to": {"a5": 1.0}}
 ]}
```