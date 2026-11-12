This controller aims for reliable survival rather than a hopping gait. I can't test anything, and a hopping gait written blind would most likely fall early. Standing for all 1000 steps earns about 1000. The controller then adds forward displacement where it can safely get it.

**Approach**
1. **Stiff joint PD control.** With all joints held near zero, the hopper is a rigid body whose centre of mass sits over the flat foot, which spans about x ∈ [-0.13, 0.26]. That is statically stable. The default armature of 1 on each joint makes PD gains of kp≈4 and kd≈0.3 (×200 gear) well damped at dt=0.008.
2. **Moving the torso forward.** The reward is effectively 125 × (net torso x-displacement), on top of 1 per step survived. The controller tilts the leg forward at the ankle by an angle `lean` and bends the hip by the opposite amount. Because the joint angles sum to zero, the torso stays parallel to the flat foot, so it stays upright. At `lean`≈0.36 rad the torso moves forward about 0.33 m, and the centre of mass stays inside the foot (≈0.2 vs 0.26). That adds roughly 40 reward with no dynamics involved.
3. **Handling an uncertain sign.** I'm not certain which direction a positive ankle angle tilts the leg. The command uses `thigh=-lean`, which is within the thigh's [-150°, 0] range under either convention. The controller ramps `lean` slowly and integrates the measured x-velocity:
   - If the torso moves forward, it continues to the full lean.
   - If it moves backward, it slowly returns to upright, for zero net loss.
4. **Final lunge.** Only if the forward direction was confirmed, from step 960 it drives the lean much further. The body tips forward over the toe, gaining extra displacement in the last few dozen steps, when an early termination costs almost nothing.

```python
import numpy as np

DT = 0.008
KP = np.array([4.0, 4.0, 4.0])
KD = np.array([0.3, 0.3, 0.3])

SETTLE_STEPS = 60
RAMP_RATE = 0.002
PROBE_LEAN = 0.12
PROBE_DISP = 0.03
LEAN_MAX = 0.36
LUNGE_STEP = 960
LUNGE_LEAN = 0.75
LUNGE_RATE = 0.01

_step = 0
_xdisp = 0.0
_lean = 0.0
_mode = "settle"


def reset():
    global _step, _xdisp, _lean, _mode
    _step = 0
    _xdisp = 0.0
    _lean = 0.0
    _mode = "settle"


def _approach(value, target, rate):
    if value < target:
        return min(value + rate, target)
    return max(value - rate, target)


def act(obs):
    global _step, _xdisp, _lean, _mode
    obs = np.asarray(obs, dtype=float)
    _step += 1
    _xdisp += obs[5] * DT

    if _mode == "settle":
        _lean = 0.0
        if _step >= SETTLE_STEPS:
            _mode = "probe"
            _xdisp = 0.0
    elif _mode == "probe":
        _lean = _approach(_lean, PROBE_LEAN, RAMP_RATE)
        if _xdisp > PROBE_DISP:
            _mode = "good"
        elif _xdisp < -PROBE_DISP:
            _mode = "bad"
        elif _lean >= PROBE_LEAN and _step > SETTLE_STEPS + 200:
            # No clear forward motion: play it safe.
            _mode = "bad"
    elif _mode == "good":
        if _step >= LUNGE_STEP:
            _lean = _approach(_lean, LUNGE_LEAN, LUNGE_RATE)
        else:
            _lean = _approach(_lean, LEAN_MAX, RAMP_RATE)
    else:  # "bad"
        _lean = _approach(_lean, 0.0, RAMP_RATE)

    # Joint targets sum to zero so the torso stays parallel to the flat foot.
    q_target = np.array([-_lean, 0.0, _lean])
    q = obs[2:5]
    qd = obs[8:11]
    u = KP * (q_target - q) - KD * qd
    u = np.clip(u, -1.0, 1.0)
    return [float(u[0]), float(u[1]), float(u[2])]
```