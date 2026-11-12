This uses one oscillator. The legs are kept in antiphase by construction: the left leg's commands use the negated cos/sin of the same phase, which is a phase shift of exactly π. So no coupling term is needed.

**Kinematic consequence of the stated sign conventions.** A thigh's world angle is (torso angle − thigh joint angle), and thigh angles must stay ≤ 0. So a foot can only be placed ahead of the hip if the torso leans slightly back. The balance loop therefore holds the torso at about −0.25 rad. That leaves room for the front foot to reach about 0.22 rad ahead of the hip without hitting the hip joint limit.

**Thigh control is split into two decoupled parts:**
- **Differential (scissor) unit.** A PD loop tracks the inter-thigh angle q_R − q_L = 0.45·sin φ, with partial velocity feedforward. It applies equal and opposite torques to the two thighs, so the torso feels no net reaction from the stride. The stance thigh's share of the torque pushes the hip forward over the foot.
- **Common-mode balance unit.** A PD loop on torso angle (target −0.25) and torso angular velocity applies the same torque to both thighs. On the grounded leg this pitches the light torso back to the target. The sign is negative feedback on obs[1] and obs[10], as required.

**Knees.** A PD loop tracks −0.35 − 0.55·cos(φ + 0.4). This gives about −0.9 rad of flexion early in swing, for roughly 9 cm of foot clearance. In mid-stance the target is +0.2, so the knee presses against its 0 limit and the stance leg locks straight.

**Feet.** A weak PD loop holds the toe about 0.2 rad up in late swing, so the heel lands first, and near 0 in stance. When the trailing foot is flat on the ground late in stance, its angle exceeds the target, so the spring presses the toe down and lifts the heel, giving a mild push-off.

**Cadence feedback.** The step rate rises with forward speed (0.75 Hz at rest, +1.2 rad/s per m/s). Faster stepping when the body speeds up helps catch forward falls. I deliberately left out the lean-based speed feedback. Here, leaning back is done through the stance hip, which actually propels the body forward, so that loop would destabilise the speed rather than regulate it.

**Gains.** They are chosen to stay well inside the stability limit of the 0.008 s update, given the estimated link inertias. Every unit is a sharpness-1 tanh, so it acts as a soft torque limit.

```json
{"target": "cpg", "obs_dim": 17, "act_dim": 6, "hidden": 16,
 "oscillators": [{"name": "p", "freq_hz": 0.75, "phase0": 0.0, "feedback": {"obs[8]": 1.2}}],
 "couplings": [],
 "units": [
   {"type": "reflex", "name": "thigh_scissor",
    "inputs": {"sin(p)": 1.35, "cos(p)": 0.5, "obs[2]": -3.0, "obs[5]": 3.0, "obs[11]": -0.35, "obs[14]": 0.35},
    "threshold": 0.0, "sharpness": 1.0, "to": {"a0": 1.0, "a3": -1.0}},
   {"type": "reflex", "name": "torso_balance",
    "inputs": {"obs[1]": -0.8, "obs[10]": -0.07},
    "threshold": 0.2, "sharpness": 1.0, "to": {"a0": 1.0, "a3": 1.0}},
   {"type": "reflex", "name": "knee_right",
    "inputs": {"cos(p)": -1.013, "sin(p)": 0.428, "obs[3]": -2.0, "obs[12]": -0.15},
    "threshold": 0.7, "sharpness": 1.0, "to": {"a1": 1.0}},
   {"type": "reflex", "name": "knee_left",
    "inputs": {"cos(p)": 1.013, "sin(p)": -0.428, "obs[6]": -2.0, "obs[15]": -0.15},
    "threshold": 0.7, "sharpness": 1.0, "to": {"a4": 1.0}},
   {"type": "reflex", "name": "foot_right",
    "inputs": {"cos(p)": 0.0478, "sin(p)": 0.0148, "obs[4]": -0.5, "obs[13]": -0.03},
    "threshold": -0.05, "sharpness": 1.0, "to": {"a2": 1.0}},
   {"type": "reflex", "name": "foot_left",
    "inputs": {"cos(p)": -0.0478, "sin(p)": -0.0148, "obs[7]": -0.5, "obs[16]": -0.03},
    "threshold": -0.05, "sharpness": 1.0, "to": {"a5": 1.0}}
 ]}
```