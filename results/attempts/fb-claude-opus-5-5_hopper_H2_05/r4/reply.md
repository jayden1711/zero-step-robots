# Round 4: let the shin lean forward so the knee can bend

**Diagnosis.** I checked the recorded joint ranges against the stated sign conventions. In every round, the torso angle at the fall (about −0.19) roughly equals the knee bend (−0.19 to −0.43), with the thigh pinned at 0 and the foot near flat.

That means the robot is not tipping over as a rigid stick. The knee buckles, and the torso and thigh rotate backward together about the knee:

- **The knee was driven into flexion.** Each design applied knee-flexing torque: the −0.225 and −0.3 biases and the flex half of the thrust. Round 3 flexed first and fell fastest. Round 0 extended first and lasted longest.
- **The hip cannot compensate.** Keeping the torso upright over a bent knee needs the torso to rotate forward relative to the thigh. That needs a thigh angle above 0, which the joint stop forbids. All the positive hip torque just pressed into the stop, which is why a0 was saturated 16–32% of the time.
- **The foot posture spring made it worse.** It held the shin vertical. The only way left for the knee to bend was for the thigh and torso to tip back.

**Changes for round 4:**
- **Ankle balance on the centre of mass:**
  - The ankle now acts as a balance controller on the hip's horizontal offset from the ankle, B ≈ 1.1·obs[1] − obs[2] − 0.5·obs[3].
  - It is no longer a spring to a fixed foot angle, so the shin can lean forward when the knee bends, the way a ski crouch works.
  - It is bounded to ±0.12 so the foot does not roll onto its heel.
  - It targets the centre of mass 3 cm ahead of the ankle, minus a little per m/s of speed. This is the forward drive.
- **Foot-level term:** kept. It is zero while the foot is flat on the ground and keeps the foot flat in flight.
- **Knee:** a moderate spring to −0.12, so there is room to extend. The thrust rhythm starts in its extension half (phase0 = 0, as in round 0).
- **Hip:**
  - A small positive lock bias plus torso PD, P 3 and D 0.1. The damping is chosen to stay stable at the 0.008 s step.
  - A light thigh spring toward 0.
  - A small backward hip drive during push-off.

```json
{"target": "cpg", "obs_dim": 11, "act_dim": 3, "hidden": 16,
 "oscillators": [{"name": "hop", "freq_hz": 2.2, "phase0": 0.0}],
 "couplings": [],
 "bias": {"a0": 0.1, "a1": -0.24},
 "units": [
   {"type": "linear", "name": "torso_balance", "inputs": {"obs[1]": -3.0, "obs[7]": -0.1},
    "range": 1.5, "tol": 0.05, "to": {"a0": 1.0}},
   {"type": "linear", "name": "thigh_posture", "inputs": {"obs[2]": -1.0, "obs[8]": -0.03},
    "range": 1.0, "tol": 0.05, "to": {"a0": 1.0}},
   {"type": "linear", "name": "knee_posture", "inputs": {"obs[3]": -2.0, "obs[9]": -0.05},
    "range": 2.0, "tol": 0.05, "to": {"a1": 1.0}},
   {"type": "reflex", "name": "ankle_com_balance",
    "inputs": {"obs[1]": -1.1, "obs[2]": 1.0, "obs[3]": 0.5, "obs[7]": -0.08, "obs[8]": 0.08, "obs[9]": 0.04, "obs[5]": -0.03},
    "threshold": -0.03, "sharpness": 20.0, "to": {"a2": 0.12}},
   {"type": "linear", "name": "foot_level", "inputs": {"obs[1]": 0.4, "obs[2]": -0.4, "obs[3]": -0.4, "obs[4]": -0.4, "obs[10]": -0.03},
    "range": 1.0, "tol": 0.05, "to": {"a2": 1.0}},
   {"type": "reflex", "name": "thrust", "inputs": {"sin(hop)": 1.0}, "threshold": 0.0,
    "sharpness": 2.0, "to": {"a0": -0.08, "a1": 0.4, "a2": -0.08}}
 ]}
```