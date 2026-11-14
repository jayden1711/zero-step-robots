This is a single-shot design. I could not run anything, so all numbers come from hand analysis of the dynamics.

**Assumptions.** I am taking the joint conventions from my memory of `walker2d.xml`, not from a source I checked here. The one that matters most is the torso hinge (`rooty`) axis. I assumed it turns the opposite way to the leg joints, so `obs[1] > 0` means the torso leans forward. If that is wrong, the torso feedback pushes the torso the wrong way and the robot falls almost at once. The full set:

- `rooty` turns about +y; the leg joints turn about −y.
- Thigh angle below 0 means the thigh swings backward relative to the torso. It can only move between −150° and 0°.
- Knee angle below 0 means the knee bends.
- Foot angle above 0 means the toe points up.
- A positive hip torque tips the torso forward.

**Gait.**
- **Oscillators:** Two oscillators, one per leg, held half a cycle apart. The base rate is 0.75 Hz and rises with forward speed, to about 0.9 Hz at 0.9 m/s. The legs start at touchdown (right) and lift-off (left), so the left leg's first push gives the robot some starting speed.
- **Hips:** Each hip steers its leg to a target angle measured from vertical, which runs from −0.35 to +0.25 rad. The hips also keep the torso near a target lean that is set by speed: about −0.12 rad (back) when stopped, −0.25 at 0.9 m/s, and further back when faster.
  - The torso gain (5) is higher than the leg gain (3), so the leg standing on the ground mostly holds the torso steady.
  - The hip cannot swing the thigh ahead of the torso, so leaning back is the only way to place a foot in front of the body. A slow walker leans less, takes shorter steps and keeps moving. A fast walker leans more, steps further ahead and slows down.
- **Knees:** The knee target is pushed against the straight-leg limit while the leg carries weight. It bends to about −0.8 rad in mid-swing, with the timing shifted earlier so the knee is straight again before the foot lands.
- **Ankles:** Each foot is kept level with the ground, computed from the torso and leg angles. On top of that, an ankle torque based on speed pushes the toes down when the robot goes too fast and acts the other way when it is slow.
- **Damping:** The damping gains are sized so the light torso stays stable with the 8 ms control step.

```json
{"target": "cpg", "obs_dim": 17, "act_dim": 6, "hidden": 16,
 "oscillators": [
   {"name": "R", "freq_hz": 0.75, "phase0": 0.0, "feedback": {"obs[8]": 1.0}},
   {"name": "L", "freq_hz": 0.75, "phase0": 3.14159, "feedback": {"obs[8]": 1.0}}
 ],
 "couplings": [
   {"from": "R", "to": "L", "weight": 3.0, "phase_lag": 3.14159},
   {"from": "L", "to": "R", "weight": 3.0, "phase_lag": 3.14159}
 ],
 "bias": {"a0": -0.725, "a1": -0.3, "a2": 0.27, "a3": -0.725, "a4": -0.3, "a5": 0.27},
 "units": [
   {"type": "linear", "name": "hip_R",
    "inputs": {"cos(R)": 0.9, "obs[1]": -2.0, "obs[2]": -3.0, "obs[8]": -0.75, "obs[10]": 0.18, "obs[11]": -0.3},
    "range": 5.0, "tol": 0.05, "to": {"a0": 1.0}},
   {"type": "linear", "name": "hip_L",
    "inputs": {"cos(L)": 0.9, "obs[1]": -2.0, "obs[5]": -3.0, "obs[8]": -0.75, "obs[10]": 0.18, "obs[14]": -0.3},
    "range": 5.0, "tol": 0.05, "to": {"a3": 1.0}},
   {"type": "linear", "name": "knee_R",
    "inputs": {"sin(R)": 1.2415, "cos(R)": 0.384, "obs[3]": -2.0, "obs[12]": -0.1},
    "range": 4.0, "tol": 0.05, "to": {"a1": 1.0}},
   {"type": "linear", "name": "knee_L",
    "inputs": {"sin(L)": 1.2415, "cos(L)": 0.384, "obs[6]": -2.0, "obs[15]": -0.1},
    "range": 4.0, "tol": 0.05, "to": {"a4": 1.0}},
   {"type": "linear", "name": "ankle_R",
    "inputs": {"obs[1]": 1.5, "obs[2]": -1.5, "obs[3]": -1.5, "obs[4]": -1.5,
               "obs[10]": 0.05, "obs[11]": -0.05, "obs[12]": -0.05, "obs[13]": -0.05, "obs[8]": -0.3},
    "range": 3.0, "tol": 0.05, "to": {"a2": 1.0}},
   {"type": "linear", "name": "ankle_L",
    "inputs": {"obs[1]": 1.5, "obs[5]": -1.5, "obs[6]": -1.5, "obs[7]": -1.5,
               "obs[10]": 0.05, "obs[14]": -0.05, "obs[15]": -0.05, "obs[16]": -0.05, "obs[8]": -0.3},
    "range": 3.0, "tol": 0.05, "to": {"a5": 1.0}}
 ]}
```