I can't simulate this, so the numbers below come from estimating the Hopper's masses and inertias and a Raibert-style hopping argument. They are a reasoned best guess, not tuned values.

**What the controller does**

- **Rhythm:** one oscillator `hop` runs at 2.5 Hz, so one hop takes 0.4 s. Phase θ = 0 is roughly landing. Stance is about θ ∈ (0, π) and flight about θ ∈ (π, 2π).
- **Thigh (a0):** this joint only keeps the torso upright, using a stiff PD on torso angle and angular velocity (about 500 Nm/rad, about 40 Nm·s/rad).
  - In flight the torso is roughly 5× lighter rotationally than the leg. A thigh rhythm would mostly pitch the torso, so I left it out.
  - The torso lean target shifts slightly backward as speed rises (−0.05 rad per m/s, centred on 0.6 m/s).
- **Knee (a1):** a PD (Kp 2, Kd 0.15) follows the setpoint −0.62 + 0.3·cos(θ + π/4) + 0.2·v.
  - During stance the knee flexes, down to about −0.8 at θ = 0.75π. This sweeps the ankle backward, so the body rides forward over the foot.
  - It then extends from late stance through flight. This gives thrust, then swings the foot forward for the next landing.
  - At higher speed the knee extends further, which places the foot further forward and slows the robot down.
- **Ankle (a2):**
  - A PD holds the foot level in the world (target foot angle = φ − q_thigh − q_leg), so the robot lands flat-footed.
  - A sharp toe-down push-off pulse (a reflex unit) fires around θ ≈ 0.8π, at the same time as the knee starts extending. Its constant +1 term is cancelled through the bias, so it is zero outside the pulse.
  - A small speed term (−0.2·(v − 0.6)) moves the centre of pressure to brake when too fast and push when too slow.

```json
{"target": "cpg", "obs_dim": 11, "act_dim": 3, "hidden": 16,
 "oscillators": [{"name": "hop", "freq_hz": 2.5, "phase0": 0.0}],
 "couplings": [],
 "bias": {"a0": 0.075, "a1": -1.24, "a2": -0.23},
 "units": [
   {"type": "linear", "name": "torso_posture_pd",
    "inputs": {"obs[1]": -2.5, "obs[7]": -0.2, "obs[5]": -0.125},
    "range": 3.0, "tol": 0.02, "to": {"a0": 1.0}},
   {"type": "linear", "name": "knee_pd_rhythm",
    "inputs": {"obs[3]": -2.0, "obs[9]": -0.15, "cos(hop)": 0.424, "sin(hop)": -0.424, "obs[5]": 0.4},
    "range": 4.0, "tol": 0.02, "to": {"a1": 1.0}},
   {"type": "linear", "name": "ankle_flat_foot_and_speed",
    "inputs": {"obs[4]": -0.8, "obs[2]": -0.8, "obs[3]": -0.8, "obs[1]": 0.8,
               "obs[10]": -0.08, "obs[8]": -0.08, "obs[9]": -0.08, "obs[7]": 0.08,
               "obs[5]": -0.2},
    "range": 3.0, "tol": 0.02, "to": {"a2": 1.0}},
   {"type": "reflex", "name": "ankle_pushoff_pulse",
    "inputs": {"cos(hop)": -0.809, "sin(hop)": 0.588},
    "threshold": 0.5, "sharpness": 5.0, "to": {"a2": -0.35}}
 ]}
```