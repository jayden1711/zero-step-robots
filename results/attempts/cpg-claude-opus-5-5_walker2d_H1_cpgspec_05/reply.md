Approach: one oscillator drives both legs, with the left leg using the negated cos and sin (exactly half a cycle apart). Each joint uses PD control. The hips track a scheduled world-frame thigh angle and also carry torso-attitude and forward-speed feedback.

**Sign conventions (from the Walker2d XML).** The torso hinge axis is +y, and the leg hinges are about −y.
- A positive `obs[1]` means the torso leans forward.
- A positive thigh angle swings the foot forward relative to the torso. The thigh range is [−150°, 0].
- A negative knee angle is human-like flexion.

**Why the torso leans back.** The thigh range [−150°, 0] only lets the leg move backward relative to the torso. To put the foot ahead of the hip at touchdown, the torso is held leaning back at −0.35 rad. The torso is light (about 3.7 kg against about 10 kg per leg), so this costs little in balance.

**Hip control.** The world thigh angle is `psi = obs[1] − q_thigh`, where positive means the foot is behind the hip.
- Target: `psi_t = −0.27·cos(phase) − 0.15·(v − 0.8)`. This gives a stride of about ±0.27 rad, and Raibert-style foot placement: when the walker goes too fast, the foot lands further forward and the stance leg brakes.
- Torque: `Kp(psi − psi_t) + Kd(dpsi − dpsi_t) − 3(obs[1] + 0.35) − 0.12·obs[10]`, with Kp = 2 and Kd = 0.4. The desired-velocity part `dpsi_t` comes from the sin term.

**Gait timing.** Stance is when sin(phase) > 0 (the foot sweeps backward), and swing is when sin(phase) < 0.

**Knee control.** A reflex flexes the knee to −0.95 during swing. It starts slightly before liftoff and ends early enough to extend the leg before touchdown. In stance the knee is held almost straight at −0.05.

**Ankle control.** A moderate PD holds the ankle at 0.

**Start-up.** The oscillator starts at phase π/2. The right leg is then at mid-stance and the left at mid-swing, which matches the initial standing pose.

**Gain stability.** I checked the gains for stability at the 0.008 s step, using rough estimates of the link inertias.

I could not test this. The main risk is a mistake in the sign derivation above.

```json
{"target": "cpg", "obs_dim": 17, "act_dim": 6, "hidden": 16,
 "oscillators": [{"name": "gait", "freq_hz": 0.8, "phase0": 1.5708}],
 "couplings": [],
 "bias": {"a0": -1.29, "a1": -1.5, "a3": -1.29, "a4": -1.5},
 "units": [
   {"type": "linear", "name": "right_hip",
    "inputs": {"obs[1]": -1.0, "obs[10]": 0.28, "obs[2]": -2.0, "obs[11]": -0.4, "obs[8]": 0.3, "cos(gait)": 0.54, "sin(gait)": -0.5429},
    "range": 3.0, "tol": 0.05, "to": {"a0": 1.0}},
   {"type": "linear", "name": "left_hip",
    "inputs": {"obs[1]": -1.0, "obs[10]": 0.28, "obs[5]": -2.0, "obs[14]": -0.4, "obs[8]": 0.3, "cos(gait)": -0.54, "sin(gait)": 0.5429},
    "range": 3.0, "tol": 0.05, "to": {"a3": 1.0}},
   {"type": "linear", "name": "right_knee_pd",
    "inputs": {"obs[3]": -3.0, "obs[12]": -0.35},
    "range": 3.0, "tol": 0.05, "to": {"a1": 1.0}},
   {"type": "linear", "name": "left_knee_pd",
    "inputs": {"obs[6]": -3.0, "obs[15]": -0.35},
    "range": 3.0, "tol": 0.05, "to": {"a4": 1.0}},
   {"type": "reflex", "name": "right_knee_swing_flex",
    "inputs": {"sin(gait)": -1.0, "cos(gait)": -0.4},
    "threshold": 0.3, "sharpness": 5.0, "to": {"a1": -1.35}},
   {"type": "reflex", "name": "left_knee_swing_flex",
    "inputs": {"sin(gait)": 1.0, "cos(gait)": 0.4},
    "threshold": 0.3, "sharpness": 5.0, "to": {"a4": -1.35}},
   {"type": "linear", "name": "right_ankle_pd",
    "inputs": {"obs[4]": -1.5, "obs[13]": -0.06},
    "range": 2.0, "tol": 0.05, "to": {"a2": 1.0}},
   {"type": "linear", "name": "left_ankle_pd",
    "inputs": {"obs[7]": -1.5, "obs[16]": -0.06},
    "range": 2.0, "tol": 0.05, "to": {"a5": 1.0}}
 ]}
```