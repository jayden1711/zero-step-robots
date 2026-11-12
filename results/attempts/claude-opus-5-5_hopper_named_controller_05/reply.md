This is a conservative balance controller. It does not try to hop. A blind-tuned hopping gait usually falls within a few dozen steps and scores about 50–200. Staying healthy for all 1000 steps scores about 1000 per episode. I couldn't run it, so the gains below come from rough physics estimates, not tuning.

**How it works**

- **Hip and knee:** Stiff PD control holds the thigh and leg joints at 0, the straight-leg pose they start in. Both joint ranges end at 0, so the joint limit braces one side and the PD controller braces the other. The body then behaves like one rigid inverted pendulum standing on the flat foot.
- **Ankle:** PD control on the whole-body lean, with lean = torso + thigh + leg angle. The joint axes point along −y, so a positive angle means leaning backward. A positive foot torque pushes the body forward, which is why the foot action has the same sign as the lean.
- **Gain estimates:** The total mass is about 15.8 kg with the centre of mass about 0.7 m up. Gravity therefore needs about 108 Nm per radian, which is 0.54 in action units with gear 200. I chose Kp = 2.0, which gives a stiffness margin of roughly 4×. Kd = 0.5 is about critical damping for a body inertia around the ankle of roughly 9 kg·m².
- **Foot limit:** The foot torque is capped at ±0.15. A larger ankle torque would lift the toe or heel off the ground.

```python
import numpy as np

# Joint PD gains (action units; actuator gear = 200)
KP_JOINT = 5.0
KD_JOINT = 0.25

# Ankle balance gains on whole-body lean (positive lean = leaning back)
KP_LEAN = 2.0
KD_LEAN = 0.5
FOOT_LIMIT = 0.15

THIGH_TARGET = 0.0
LEG_TARGET = 0.0


def reset():
    pass


def act(obs):
    o = np.asarray(obs, dtype=float)
    torso, thigh, leg = o[1], o[2], o[3]
    torso_w, thigh_w, leg_w = o[7], o[8], o[9]

    # Keep hip and knee rigid and straight
    a_thigh = -KP_JOINT * (thigh - THIGH_TARGET) - KD_JOINT * thigh_w
    a_leg = -KP_JOINT * (leg - LEG_TARGET) - KD_JOINT * leg_w

    # Ankle strategy: balance the rigid body over the flat foot
    lean = torso + thigh + leg
    lean_w = torso_w + thigh_w + leg_w
    a_foot = KP_LEAN * lean + KD_LEAN * lean_w
    a_foot = float(np.clip(a_foot, -FOOT_LIMIT, FOOT_LIMIT))

    a = np.clip([a_thigh, a_leg, a_foot], -1.0, 1.0)
    return [float(a[0]), float(a[1]), float(a[2])]
```

If it works as intended, each episode should run the full 1000 steps and score just under 1000. The forward-velocity term is close to zero and the action penalty is negligible. The main risk is the ankle sign. If my reading of the joint axes is wrong, the hopper will tip within the first second, and flipping the sign of `KP_LEAN` and `KD_LEAN` would fix it.