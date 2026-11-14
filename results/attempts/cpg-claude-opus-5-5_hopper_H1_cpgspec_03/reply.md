This is a hand-designed hopping controller. I couldn't simulate it, so the gains come from rough estimates of the model's masses, the joint armature and the 200 Nm actuator gear. The parts of the design are:

**One oscillator, `hop`, at 2.5 Hz, sets the gait rhythm.**
- **Knee (`a1`):** gets `0.1 + 0.3·sin ψ`. Its peak torque is 80 Nm. The knee pushes into its straight limit during the push half of the cycle and flexes slightly in the other half.
- **Ankle push-off (`a2`):** a gated push driven by `sin(ψ − 0.5)`, so it comes slightly after the knee extension. It gives about −0.4 (toe press) in the push window and roughly 0 elsewhere.
- **Leg swing:** two paired reflex units act as a hip controller on the absolute leg angle (`obs[1]+obs[2]`). The pair is switched on only around `sin ψ ≈ −1`, the expected flight phase, and gives roughly zero output otherwise.
  - The target foot placement shifts forward with speed (Raibert-style): `−0.08 + 0.175·v` rad.
  - So the foot lands behind the body when the robot is slow, which makes it speed up, and further forward when it is fast, which makes it brake.

**Balance feedback, running all the time:**
- **Torso:** the hip torque follows `a0 = 1.5·(obs[1] + 0.13·obs[7]) + bias`, which holds the torso at a slight forward lean. Since every joint rotates about −y, a positive hip torque in stance pitches the torso forward, so this sign corrects a backward lean.
- **Speed through lean:** a term of `−0.12·v` on `a0` with a matching bias sets the torso target to about −0.1 rad when stopped and −0.04 rad at 0.8 m/s. Going faster than that makes the torso lean back.
- **Emergency torso reflexes:** strong hip corrections kick in when `|obs[1]|` passes 0.12 rad. Their constant offsets cancel each other.
- **Ankle, foot levelling:** the foot is kept level with the ground (absolute angle 0). This has little effect while the foot is flat in stance, and it lines the foot up for landing while in the air.
- **Ankle, body lean:** the ankle responds to the shank's lean. Leaning back gives a toe-up torque that tips the body forward. Leaning forward late in stance gives a toe press, which corrects the lean and also adds push-off.

```json
{"target": "cpg", "obs_dim": 11, "act_dim": 3, "hidden": 16,
 "oscillators": [{"name": "hop", "freq_hz": 2.5, "phase0": 3.6}],
 "couplings": [],
 "bias": {"a0": 0.156, "a1": 0.1, "a2": -0.2},
 "units": [
   {"type": "linear", "name": "torso_pd", "inputs": {"obs[1]": 1.0, "obs[7]": 0.13},
    "range": 1.0, "tol": 0.05, "to": {"a0": 1.5}},
   {"type": "linear", "name": "speed_lean", "inputs": {"obs[5]": 1.0},
    "range": 3.0, "tol": 0.05, "to": {"a0": -0.12}},
   {"type": "linear", "name": "foot_level", "inputs": {"obs[1]": 1.0, "obs[2]": 1.0, "obs[3]": 1.0, "obs[4]": 1.0, "obs[7]": 0.03, "obs[8]": 0.03, "obs[9]": 0.03, "obs[10]": 0.03},
    "range": 1.2, "tol": 0.05, "to": {"a2": -0.5}},
   {"type": "linear", "name": "ankle_balance", "inputs": {"obs[1]": 1.0, "obs[2]": 1.0, "obs[3]": 1.0, "obs[7]": 0.2, "obs[8]": 0.2, "obs[9]": 0.2},
    "range": 1.2, "tol": 0.05, "to": {"a2": 0.3}},
   {"type": "linear", "name": "knee_rhythm", "inputs": {"sin(hop)": 1.0},
    "range": 1.0, "tol": 0.02, "to": {"a1": 0.3}},
   {"type": "reflex", "name": "ankle_pushoff", "inputs": {"sin(hop)": 0.878, "cos(hop)": -0.479},
    "threshold": 0.3, "sharpness": 4.0, "to": {"a2": -0.2}},
   {"type": "reflex", "name": "swing_gate_pos", "inputs": {"obs[1]": -1.0, "obs[2]": -1.0, "obs[5]": 0.175, "sin(hop)": -0.8},
    "threshold": 0.88, "sharpness": 3.3, "to": {"a0": 0.3}},
   {"type": "reflex", "name": "swing_gate_neg", "inputs": {"obs[1]": 1.0, "obs[2]": 1.0, "obs[5]": -0.175, "sin(hop)": -0.8},
    "threshold": 0.72, "sharpness": 3.3, "to": {"a0": -0.3}},
   {"type": "reflex", "name": "torso_back_guard", "inputs": {"obs[1]": 1.0},
    "threshold": 0.12, "sharpness": 15.0, "to": {"a0": 0.25}},
   {"type": "reflex", "name": "torso_fwd_guard", "inputs": {"obs[1]": -1.0},
    "threshold": 0.12, "sharpness": 15.0, "to": {"a0": -0.25}}
 ]}
```