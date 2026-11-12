This controller is designed from first principles only. I couldn't simulate it, so whether it passes is uncertain.

**Structure:** one 2.5 Hz oscillator drives all three joints. Each joint is a PD servo that tracks a target set by the oscillator. Balance and speed feedback are added on the thigh.

**Sign conventions** (from the Hopper MJCF: every hinge is about −y):
- A positive joint angle swings the lower end of a link forward.
- A positive torso angle means the torso leans back.
- A positive torque increases the joint angle.
- In stance, a positive thigh torque pitches the torso forward.

**Knee (a1)**
- Target: −0.45 + 0.25·cos φ, with gains Kp 3 and Kd 0.2, plus a +0.15 bias against gravity.
- At 2.5 Hz this swings the hip about ±5 cm. That gives a peak acceleration above g, so the foot briefly leaves the ground near φ ≈ 0.
- Compression happens for φ ∈ (0, π) and extension for φ ∈ (π, 2π).

**Thigh (a0)**
- The main term is torso pitch PD: 2.5·(θ − θd) + 0.2·θ̇.
- The target lean is θd = −0.04 + 0.05·(v − 0.8). The torso leans further forward when the robot is slower than 0.8 m/s and straightens up when it is faster.
- A weaker thigh-joint PD (Kp 1, Kd 0.1) tracks −0.15 + 0.1·cos(φ − 1). This swings the leg forward during flight and toward landing, and sweeps it back during stance.

**Foot (a2)**
- Ankle PD (Kp 0.8, Kd 0.08) tracks 0.45 + 0.2·cos(φ − 1.8).
- The toes point up around landing, which keeps the foot flat on the bent leg.
- In late stance the ankle plantarflexes (toes down) for push-off. Rotating the foot about the toe lifts the ankle up and forward.

**Start:** the oscillator starts at φ0 = π/2, the mid-crouch point, to soften the initial drop.

```json
{"target": "cpg", "obs_dim": 11, "act_dim": 3, "hidden": 16,
 "oscillators": [{"name": "hop", "freq_hz": 2.5, "phase0": 1.5708}],
 "couplings": [],
 "bias": {"a0": 0.05, "a1": -1.2, "a2": 0.36},
 "units": [
   {"type": "linear", "name": "thigh_balance_and_swing",
    "inputs": {"obs[1]": 2.5, "obs[7]": 0.2, "obs[2]": -1.0, "obs[8]": -0.1, "obs[5]": -0.125,
               "cos(hop)": 0.054, "sin(hop)": 0.084},
    "range": 1.5, "tol": 0.02, "to": {"a0": 1.0}},
   {"type": "linear", "name": "knee_hop_servo",
    "inputs": {"obs[3]": -3.0, "obs[9]": -0.2, "cos(hop)": 0.75},
    "range": 4.0, "tol": 0.02, "to": {"a1": 1.0}},
   {"type": "linear", "name": "ankle_pushoff_servo",
    "inputs": {"obs[4]": -0.8, "obs[10]": -0.08, "cos(hop)": -0.0363, "sin(hop)": 0.1558},
    "range": 1.5, "tol": 0.02, "to": {"a2": 1.0}}
 ]}
```