This controller is designed from first principles and has not been simulated, so how well it works is uncertain. It sets up a toe-hopping gait: the ankle pushes off to hop and also places the foot for balance, while the hip keeps the torso upright and the knee stays locked straight.

**Sign conventions used** (from the Hopper XML axes: `rooty` is about +y, the other joints are about −y):
- **Torso:** positive torso angle means leaning forward.
- **Hip (a0):** positive torque tips the torso forward.
- **Knee (a1):** positive torque straightens the knee into its limit.
- **Ankle (a2):** positive torque tips the shin forward and lifts the toes. Negative torque presses the toes down (plantarflex).

**Design**

- **Hip, torso posture (a0):** a PD controller holds the torso upright: a0 = −1.0·β − 0.15·β̇. The joint armature is about 1, giving a stiffness of about 200 Nm/rad, around 13 rad/s and near-critical damping.
- **Knee (a1):** a constant bias of 0.3 plus PD on the knee angle keeps the knee locked straight at its limit. This makes the leg a rigid strut.
- **Ankle, balance and foot placement (a2):** one linear PD law covers both phases.
  - Inputs are the foot joint angle, the global shin pitch (obs1 − obs2 − obs3), the shin pitch rate, and x-velocity against a target of 0.6 m/s.
  - The pitch reference is 0.09 rad, which puts the centre of mass over the middle of the foot.
  - **On the ground:** the law acts as ankle balance. The net pitch stiffness is about 123 Nm/rad above the gravity term, with a damping ratio of about 0.8.
  - **In the air:** the same law sets the foot angle. Moving too fast points the toes down, so the robot lands on its toe ahead of the centre of mass and slows. Moving too slowly lifts the toes, so it lands on its heel behind the centre of mass and speeds up. This is Raibert-style foot placement using the 0.39 m foot.
- **Hop drive (a2):** a 2.5 Hz oscillator adds a one-sided plantarflex pulse of about 64 Nm peak during roughly 40% of each cycle. This pushes the robot off its toes to hop. The reaction torque also pitches the leg backward, which brings the foot forward under the body during flight.
  - The pulse is built from a reflex unit plus a bias.
  - The starting phase is set so the first push comes roughly when the robot lands after its initial 4 cm drop.

```json
{"target": "cpg", "obs_dim": 11, "act_dim": 3, "hidden": 16,
 "oscillators": [{"name": "hop", "freq_hz": 2.5, "phase0": -1.0}],
 "couplings": [],
 "bias": {"a1": 0.3, "a2": 0.08},
 "units": [
   {"type": "linear", "name": "hip_torso_pd",
    "inputs": {"obs[1]": -1.0, "obs[7]": -0.15},
    "range": 1.0, "tol": 0.02, "to": {"a0": 1.0}},
   {"type": "linear", "name": "knee_lock",
    "inputs": {"obs[3]": -3.0, "obs[9]": -0.1},
    "range": 1.0, "tol": 0.02, "to": {"a1": 1.0}},
   {"type": "linear", "name": "ankle_balance_placement",
    "inputs": {"obs[4]": -0.5, "obs[10]": -0.1,
               "obs[1]": -0.5, "obs[2]": 0.5, "obs[3]": 0.5,
               "obs[7]": -0.15, "obs[8]": 0.15, "obs[9]": 0.15,
               "obs[5]": -0.25},
    "range": 1.5, "tol": 0.05, "to": {"a2": 1.0}},
   {"type": "reflex", "name": "hop_pushoff_pulse",
    "inputs": {"sin(hop)": 1.0}, "threshold": 0.3, "sharpness": 5.0,
    "to": {"a2": -0.16}}
 ]}
```