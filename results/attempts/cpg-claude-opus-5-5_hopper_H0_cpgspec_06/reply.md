This is designed from first principles and has not been tested, so it may not pass.

**Design**
- **Torso balance:** the hip runs a PD controller on torso angle `obs[1]` and its rate `obs[7]`, aiming slightly forward (+0.03 rad). With the leg planted, a positive `a0` pitches the torso forward.
- **Posture:** the knee and ankle run PD controllers towards a crouched, forward-leaning stance:
  - knee at −0.25 rad, ankle at +0.5 rad;
  - this puts the hip well ahead of the ankle;
  - the whole-body centre of mass sits about 0.20 m in front of the ankle, still behind the toe (about 0.32 m);
  - the ankle term also cancels about 28 Nm of gravity load.
- **Speed regulation:** the ankle takes forward-velocity feedback around a 0.8 m/s target. Going too slowly adds dorsiflexion, so it leans and falls forward more. Going too fast plantarflexes, which moves the centre of pressure towards the toe and slows it down.
- **Soft start:** the robot starts straight, so the stance must not be imposed at once.
  - Oscillator `R` is phase-locked by a frozen oscillator `Z`. Its sine rises from 0 to 1 over about 1 s, then stays there.
  - All posture targets are scaled by `sin(R)`.
  - The hopping drive is gated by `sin(R)` inside its tanh, and its constant offset is cancelled through the bias and the `sin(R)` terms.
- **Hopping:** oscillator `C` runs at 2.2 Hz and drives a near-square wave into the knee and ankle together.
  - Push phase: the ankle plantarflexes (heel lift and vertical push) while the knee extends, which drives the hip forward over the planted foot.
  - Return phase: both reverse, and the PD controllers restore the stance during flight.

```json
{"target": "cpg", "obs_dim": 11, "act_dim": 3, "hidden": 16,
 "oscillators": [
   {"name": "Z", "freq_hz": 0.0, "phase0": 1.0472},
   {"name": "R", "freq_hz": 0.1, "phase0": 0.0},
   {"name": "C", "freq_hz": 2.2, "phase0": 0.0}
 ],
 "couplings": [
   {"from": "Z", "to": "R", "weight": 1.2566, "phase_lag": 0.0}
 ],
 "bias": {"a0": 0.03, "a1": 0.15, "a2": -0.35},
 "units": [
   {"type": "linear", "name": "hip_torso_pd",
    "inputs": {"obs[1]": -1.0, "obs[7]": -0.15},
    "range": 1.0, "tol": 0.02, "to": {"a0": 1.0}},
   {"type": "linear", "name": "knee_pd_ramped",
    "inputs": {"obs[3]": -1.0, "obs[9]": -0.1, "sin(R)": -0.4},
    "range": 1.5, "tol": 0.02, "to": {"a1": 1.0}},
   {"type": "linear", "name": "ankle_pd_speed_ramped",
    "inputs": {"obs[4]": -1.5, "obs[10]": -0.25, "obs[5]": -0.2, "sin(R)": 1.12},
    "range": 2.0, "tol": 0.03, "to": {"a2": 1.0}},
   {"type": "reflex", "name": "gated_hop_drive",
    "inputs": {"sin(C)": 1.0, "sin(R)": 2.0},
    "threshold": 2.0, "sharpness": 2.5,
    "to": {"a1": 0.15, "a2": -0.35}}
 ]}
```