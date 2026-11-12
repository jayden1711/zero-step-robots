This is a hand-derived feedback controller with a rhythmic knee drive. I could not simulate it, so treat the gains as physically reasoned estimates, not tuned values.

**Sign conventions** (from the Hopper MJCF; all joint axes are −y):
- **Hip:** positive a0 pitches the torso forward relative to the thigh.
- **Knee:** positive a1 straightens the knee (q2 → 0).
- **Ankle:** positive a2 tilts the leg forward over a planted foot.
- **Hip limit:** q1 ≤ 0, so a bent knee always puts the hip ahead of the ankle. The long forward toe (out to x ≈ +0.26) is what supports the centre of mass there.
- **Armature:** every joint has armature 1, so I used slow, heavily damped loops.

**Control structure**
1. **Hip: torso attitude PD.** a0 = −1.0·(θ − (−0.04)) − 0.15·θ̇. I estimate the bandwidth at about 12 rad/s, close to critically damped. The small backward reference keeps the hip away from its q1 = 0 limit.
2. **Knee: stiff PD, gravity feedforward and drive.**
   - The PD holds the knee at q2 = −0.5 with 400 Nm/rad, plus gravity feedforward.
   - A 2.2 Hz oscillator adds ±80 Nm to the knee. With resonance amplification this should give roughly ±0.5 rad knee swing and vertical accelerations above g, so the robot hops.
   - Hopping is the only way the foot can advance. The pushes act along a forward-tilted leg axis, so they produce forward thrust.
3. **Ankle: balance plus foot leveling.**
   - **Balance.** In stance the ankle regulates an estimate of the upper-body centre of mass, linearised from θ, q1 and q2, to about 0.23 m ahead of the ankle. It uses a weak torso-velocity term with a 0.2 m/s target, so it brakes when the robot goes too fast and leans in when it is slow. I estimate the pendulum bandwidth at about 4.7 rad/s.
   - **Gravity feedforward.** A constant term cancels the upper body's tipping torque.
   - **Foot leveling.** A PD term on the foot's absolute angle (θ − q1 − q2 − q3) is exactly zero while the foot is flat. It only acts in flight, where it levels the foot for landing, and when the heel or toe starts to lift.
4. **Safety reflex.** If torso height drops toward 0.85 m, extra knee-extension torque is added. A bias offsets the reflex so it contributes nothing at normal heights.

```json
{"target": "cpg", "obs_dim": 11, "act_dim": 3, "hidden": 16,
 "oscillators": [{"name": "osc", "freq_hz": 2.2, "phase0": 0.0}],
 "couplings": [],
 "bias": {"a0": -0.04, "a1": -0.655, "a2": 0.251},
 "units": [
   {"type": "linear", "name": "hip_torso_pd",
    "inputs": {"obs[1]": -1.0, "obs[7]": -0.15},
    "range": 1.5, "tol": 0.02, "to": {"a0": 1.0}},
   {"type": "linear", "name": "knee_pd",
    "inputs": {"obs[3]": -2.0, "obs[9]": -0.06},
    "range": 2.5, "tol": 0.03, "to": {"a1": 1.0}},
   {"type": "linear", "name": "knee_drive",
    "inputs": {"sin(osc)": 0.4},
    "range": 0.5, "tol": 0.02, "to": {"a1": 1.0}},
   {"type": "linear", "name": "ankle_balance_and_foot_level",
    "inputs": {"obs[1]": -0.083, "obs[2]": -0.029, "obs[3]": -0.418, "obs[4]": -1.0,
               "obs[5]": -0.22, "obs[7]": 0.08, "obs[8]": -0.08, "obs[9]": -0.08, "obs[10]": -0.08},
    "range": 1.5, "tol": 0.03, "to": {"a2": 1.0}},
   {"type": "reflex", "name": "low_height_extend",
    "inputs": {"obs[0]": -1.0}, "threshold": -0.85, "sharpness": 20.0,
    "to": {"a1": 0.3}}
 ]}
```

**Bias breakdown**
- **a1:** −0.955 comes from the knee PD and gravity terms. +0.3 cancels the reflex's resting −0.3 output. Together that gives −0.655.
- **a2:** 0.251 is the constant term from the balance law, feedforward and velocity target.

**Main risks**
- The emergent hop rate and speed are unknown. Forward progress depends on flights carrying the foot, and I estimate ~0.2–0.5 m/s.
- The forward-biased posture could tip the robot past its toe.

If you can run it, check these three things first:
- **Too little speed:** raise the knee drive amplitude, currently 0.4.
- **Falling forward:** lower the 0.251 a2 bias.
- **Torso pitch excursions:** lower the oscillator frequency.