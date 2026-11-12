I can't simulate this, so the design below rests on rigid-body reasoning about the Hopper model, not on testing. Treat it as a reasoned first attempt, not a validated gait.

**How it works**

- **Joint conventions.** The joints rotate about −y. Positive torso angle means leaning back. The hip (≤0) only lets the thigh swing behind the torso, and the knee (≤0) only flexes. So the leg can't be swung forward in flight. The torso is also far too light to act as a reaction mass, since the leg and foot weigh about 12 kg against 3.7 kg for the torso. The stride therefore has to come from rotation produced at the ankle during stance.
- **Knee (a1).** A stiff PD with a bias holds the knee straight against its 0° limit. The ground force passes ahead of the knee, which also helps keep it locked.
- **Hip (a0).** This servos the torso to about −0.05 rad, nearly upright. The leg is free to lean further forward (hip ≈ −0.2), which puts the body's centre of mass over the front of the foot.
- **Ankle (a2), balance part.** This is a PD on the leg's world pitch (obs[1]+obs[2]+obs[3]). With the foot flat, the effective gains are 1.0 /rad and 0.12 /(rad/s), against a gravity stiffness of about 0.39. It also includes:
  - a spring and damper on the foot's world angle, so the foot lands roughly flat after a flight;
  - a velocity term that reduces the forward lean as speed rises.

  The resulting lean target is about −0.29 rad at rest and −0.21 rad at 0.5 m/s.
- **Ankle (a2), hop pulses.** A 2.5 Hz oscillator gates a 0.4 (80 N·m) plantarflex pulse during about 25% of each cycle. Each pulse lifts the heel and launches a small hop. It also gives the body a backward spin, so in flight the leg rotates back and lands further forward. The body then vaults over the foot and the next pulse fires. The pulse lasts longer when the leg leans further forward and cuts off as the leg rotates back, which keeps the backward rotation within the torso limit.
- **Soft start.** Two zero-frequency oscillators form a ramp: one locks the other to π/2, so `sin(ramp) = tanh(1.5·t)`. This phases in the forward-lean target and enables the hop pulses over about 1 s, so the robot doesn't lurch at t = 0.

```json
{"target": "cpg", "obs_dim": 11, "act_dim": 3, "hidden": 16,
 "oscillators": [
   {"name": "anchor", "freq_hz": 0.001, "phase0": 0.0},
   {"name": "ramp", "freq_hz": 0.001, "phase0": 0.0},
   {"name": "cpg", "freq_hz": 2.5, "phase0": 3.14159}
 ],
 "couplings": [
   {"from": "anchor", "to": "ramp", "weight": 1.5, "phase_lag": -1.5708}
 ],
 "bias": {"a0": 0.05, "a1": 0.2, "a2": -0.2},
 "units": [
   {"type": "linear", "name": "torso_servo_hip",
    "inputs": {"obs[1]": 1.0, "obs[7]": 0.12},
    "range": 1.0, "tol": 0.05, "to": {"a0": 1.0}},
   {"type": "linear", "name": "knee_lock",
    "inputs": {"obs[3]": -1.5, "obs[9]": -0.1},
    "range": 1.0, "tol": 0.05, "to": {"a1": 1.0}},
   {"type": "linear", "name": "ankle_balance",
    "inputs": {"obs[1]": 0.4, "obs[2]": 0.4, "obs[3]": 0.4, "obs[4]": -0.6,
               "obs[7]": 0.06, "obs[8]": 0.06, "obs[9]": 0.06, "obs[10]": -0.06,
               "obs[5]": -0.1, "sin(ramp)": 0.18},
    "range": 1.5, "tol": 0.03, "to": {"a2": 1.0}},
   {"type": "reflex", "name": "hop_pulse",
    "inputs": {"cos(cpg)": 1.0, "sin(ramp)": 1.0, "obs[1]": -1.5, "obs[2]": -1.5, "obs[3]": -1.5},
    "threshold": 2.1, "sharpness": 10.0, "to": {"a2": -0.2}}
 ]}
```