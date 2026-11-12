This observation and action layout looks like a planar one-legged hopper: obs[0] is torso height, obs[1] is torso angle, obs[2:5] are the three joint angles, obs[5:11] are the velocities, and there are three torque actions. I can't test anything, so I chose a robust controller over an aggressive one.

**Strategy.** In the initial pose every joint sits at its neutral angle and the body is upright. The center of mass is over the ankle, inside the flat foot's footprint. If the joints are held rigid, the hopper is statically stable and survives all 1000 steps, which earns about 1000 points.

A hand-tuned forward hopping gait could score more, but a blind gait almost certainly falls early and scores far less. So the controller is a well-damped PD loop that holds every joint at zero:

- **Stiffness and damping.** It uses moderate stiffness and roughly critical damping, sized for actuators that likely produce about 200× the action value as torque.
- **Upright correction.** A small torso-angle term on the hip keeps the torso upright. It is sign-consistent because the torso's world angle is the root angle, and the hip torque acts between the torso and the thigh.
- **Low control cost.** The actions stay tiny, so the control-cost penalty is negligible.

```python
import numpy as np

# PD gains in action units (actuator torque ~ gear * action)
KP = np.array([2.0, 2.0, 2.0])
KD = np.array([0.25, 0.25, 0.25])
TARGET = np.array([0.0, 0.0, 0.0])

# small extra term on the hip to keep the torso upright
K_TORSO_P = 0.5
K_TORSO_D = 0.05


def reset():
    pass


def act(obs):
    o = np.asarray(obs, dtype=float)
    q = o[2:5]
    qd = o[8:11]

    a = -KP * (q - TARGET) - KD * qd

    # torso angle / angular velocity: if the torso pitches, rotate the hip so the
    # torso is pushed back toward upright (reaction torque acts on torso)
    torso = o[1]
    torso_d = o[7]
    a[0] += K_TORSO_P * torso + K_TORSO_D * torso_d

    a = np.clip(a, -1.0, 1.0)
    return [float(a[0]), float(a[1]), float(a[2])]
```

**Expected score: about 1000 per episode.** That is the healthy bonus on every step, minus a near-zero control cost and a negligible velocity term from tiny sway.

**Main risk: the sign of the hip torso term.** If it is wrong, the gain is small next to the joint-holding PD terms, so the posture should still stay well within the |angle| < 0.2 health limit.