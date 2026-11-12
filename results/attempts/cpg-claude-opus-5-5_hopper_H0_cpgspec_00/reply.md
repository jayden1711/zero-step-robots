This controller uses pure feedback and no oscillators; hop timing comes from the vertical-velocity reflex. I haven't been able to simulate it, and the design depends on my recollection of the Hopper model geometry, so I have no way of knowing whether it walks or passes.

**Sign conventions.** These assume the root pitch joint turns about +y, and the thigh, leg and foot joints turn about −y.
- **θ (`obs[1]`):** positive means the torso leans forward.
- **Shin tilt:** φ_leg = θ − q_thigh − q_leg, positive when the top of the leg is forward.
- **Foot tilt:** φ_foot = φ_leg − q_foot, positive when the toe points down.
- **Foot shape:** the toe is about 0.26 m ahead of the ankle and the heel about 0.13 m behind.

If the root pitch axis is actually −y, the hip loop below has the wrong sign and the robot falls almost at once.

**Control loops:**
- **Hip (`a0`) keeps the torso upright.** It is a PD loop, `a0 = −2(θ + 0.02) − 0.15·θ̇`. The slight backward target leaves room before the thigh hits its 0 rad joint limit.
- **Knee (`a1`) holds the leg nearly straight.** It is a stiff PD loop aiming for q_leg = −0.1, so the leg acts like a firm strut.
- **Ankle (`a2`) does most of the work.** It is one linear unit made of three parts.
  - **Foot-flat PD on φ_foot.** When the foot is flat on the ground this term is zero. In flight it sets the angle the foot lands at.
  - **Balance PD on the virtual leg.** The virtual leg ψ ≈ θ − q_thigh − 0.53·q_leg is the line from foot to hip. The target is a forward lean of 0.15, with a small extra offset to carry the weight. On the ground this acts like a person balancing on their ankle.
  - **Speed term.** It adds `−0.15·(vx − 0.5)`.
  - **Effect in flight.** The same terms decide which part of the foot lands first. Leaning or moving too fast tilts the toe down, so the toe touches first, ahead of the centre of mass, and brakes. Moving too slowly tilts the toe up, so the heel touches first and the robot speeds up. The long foot does the job of foot placement, which the hip cannot do well: the light torso can only swing ±0.2 rad.
- **Hop thrust (reflex on `obs[6]`).** It adds `−0.2·tanh(3·vz)` to the ankle. When the body is rising, the ankle pushes the toe down. When it is falling, the ankle gives way. This puts energy into each bounce, which keeps a small self-timed hop going so the foot can move forward. The 4 cm drop at the start should set it off.

```json
{"target": "cpg", "obs_dim": 11, "act_dim": 3, "hidden": 16,
 "oscillators": [],
 "couplings": [],
 "bias": {"a0": -0.04, "a1": -0.15, "a2": 0.155},
 "units": [
   {"type": "linear", "name": "hip_torso_pd",
    "inputs": {"obs[1]": 1.0, "obs[7]": 0.075},
    "range": 1.0, "tol": 0.05, "to": {"a0": -2.0}},
   {"type": "linear", "name": "knee_pd",
    "inputs": {"obs[3]": -1.0, "obs[9]": -0.0667},
    "range": 1.5, "tol": 0.05, "to": {"a1": 1.5}},
   {"type": "linear", "name": "ankle_balance_footplace",
    "inputs": {"obs[1]": 0.5, "obs[2]": -0.5, "obs[3]": -0.97, "obs[4]": -1.5,
               "obs[5]": -0.15, "obs[7]": -0.08, "obs[8]": 0.08, "obs[9]": -0.014, "obs[10]": -0.12},
    "range": 1.5, "tol": 0.05, "to": {"a2": 1.0}},
   {"type": "reflex", "name": "ankle_hop_thrust",
    "inputs": {"obs[6]": 1.0}, "threshold": 0.0, "sharpness": 3.0,
    "to": {"a2": -0.2}}
 ]}
```