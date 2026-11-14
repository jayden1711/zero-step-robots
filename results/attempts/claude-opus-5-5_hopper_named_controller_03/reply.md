Standing still is the safest way to score here, so the controller holds the hopper upright on its foot.

- **Standing is worth about 1000.** The healthy bonus pays 1 per step for 1000 steps.
- **A hopping gait is worth more, but only if it works.** It could add a few hundred points over an episode. A gait that hasn't been tuned in simulation usually falls early, and then the episode loses most of that ~1000.

**Why standing is stable:**
- **The rigid pose is self-stable.** With every joint held at 0, the robot is a rigid upright column (torso height about 1.25). Its centre of mass sits over the flat foot, which runs from x≈-0.13 to x≈0.26. That pose is statically stable, so the controller only has to keep the joints stiff and damp out the small starting perturbation.
- **Torso tilt is corrected through the joints.** All joint axes share the torso's rotation sign. A small lean is corrected by spreading the torque over hip, knee and ankle.
- **Gains are moderate.** Action saturates at ±1, which the 200 gear turns into ±200 N·m. Kp≈4 per radian gives about 800 N·m/rad, and Kd≈0.4 gives damping. That is stiff and well damped given the model's joint armature and the 0.002 s internal timestep.
- **Control cost is negligible.** Near the upright pose the gravity torques are tiny, so the actions stay close to 0.

I could not run this. I expect about 999 per episode.

```python
import numpy as np

# Joint-space PD targets (all joints straight -> rigid upright column over the foot)
_Q_TARGET = np.array([0.0, 0.0, 0.0])

_KP = np.array([4.0, 4.0, 3.0])      # stiffness per joint (action units / rad)
_KD = np.array([0.40, 0.40, 0.30])   # damping per joint (action units / (rad/s))

# Torso attitude feedback distributed over the joints (same rotation axis as joints)
_K_TORSO = 2.0
_KD_TORSO = 0.2
_TORSO_SPLIT = np.array([0.5, 0.3, 0.2])


def reset():
    pass


def act(obs):
    o = np.asarray(obs, dtype=float)
    torso_ang = o[1]
    q = o[2:5]
    torso_w = o[7]
    qd = o[8:11]

    # Hold joints stiff at the straight posture.
    a = -_KP * (q - _Q_TARGET) - _KD * qd

    # Small correction to keep the torso upright: if the torso leans with
    # positive angle, push the joints in the positive direction so the
    # torso is rotated back relative to the leg/foot on the ground.
    a += _TORSO_SPLIT * (_K_TORSO * torso_ang + _KD_TORSO * torso_w)

    a = np.clip(a, -1.0, 1.0)
    return [float(a[0]), float(a[1]), float(a[2])]
```