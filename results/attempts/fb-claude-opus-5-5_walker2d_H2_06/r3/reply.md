# Round 3: reverse the torso-balance sign, based on what the robot actually did

## What rounds 0 to 2 show

- **Which way is a backward lean.** In every run the torso angle went negative while x decreased, and decreased faster as the angle grew. The robot fell backwards each time. So a negative obs[1] is a backward lean, as the brief says.
- **The balance feedback had the wrong sign in all three rounds.** The net gain from obs[1] to the hips was negative every time: −0.5, −1.5 and −1.0. The hip joint and the torso share one axis, so a hip torque pushes the torso the opposite way. A positive thigh torque therefore pitches the torso to a more negative angle, which is backwards.
  - With a negative gain, a backward lean produced a positive torque.
  - That torque pinned the stance thigh at its 0 limit, which is why the thighs sat near 0 for 30–70% of steps.
  - The reaction then tipped the torso further back, so the feedback made the backward fall worse.
  - The brief's claim that "a negative thigh torque pitches the torso backward" is the opposite of what the data shows.
- **Which way a negative thigh angle moves the foot.** The same shared-axis rule means a negative thigh angle swings the foot forward. That also explains round 2. It held the thighs near −0.35 with the torso at −0.5, which put the feet far ahead and made the robot walk backwards.

## Design for round 3

1. **Balance: +1.0·(obs[1] − θₜ) + 0.1·obs[10] at both hips.** A backward lean now produces a negative hip torque, which pitches the torso forward.
   - With the foot planted, the hip PD on the thigh angle also stabilises the torso.
   - Both terms now act in the same direction.
2. **Forward lean target.** θₜ = 0.3 − 0.1·obs[8], so about 0.25 rad of forward lean at walking speed.
   - Thighs can only bend forward from the torso line, so a forward lean is the only way to get the stance foot behind the hip at push-off.
   - When the robot goes faster, θₜ drops and the torso is brought back, which slows it down.
3. **Thigh target: −0.25 − 0.22·cos φ.**
   - At φ = 0 (foot strike) it is −0.47, foot forward.
   - At φ = π (push-off) it is −0.03.
   - With the torso at 0.25, the stance leg sweeps from about +0.22 rad ahead of vertical to −0.22 behind.
   - Kp = 1.0, Kd = 0.1. Bias = −0.25 − 0.30 = −0.55.
4. **Knee target: −0.05 + 0.65·sin(φ + 0.3).**
   - The knee is held straight (against its limit) through stance.
   - It starts flexing just before push-off, reaches −0.7 in mid-swing, and is straight again before the next strike.
5. **Frequency 0.9 Hz, symmetric start.** The oscillators start at π/2 and 3π/2, so both thigh targets are equal at t = 0. The right leg starts in stance and the left in swing.

**What to check next round:** if the torso now falls forward (angle above +1), the fix is to reduce the lean offset in the bias, not to flip the sign again.

```json
{"target": "cpg", "obs_dim": 17, "act_dim": 6, "hidden": 16,
 "oscillators": [
   {"name": "R", "freq_hz": 0.9, "phase0": 1.5708},
   {"name": "L", "freq_hz": 0.9, "phase0": 4.7124}
 ],
 "couplings": [
   {"from": "R", "to": "L", "weight": 2.0, "phase_lag": 3.14159},
   {"from": "L", "to": "R", "weight": 2.0, "phase_lag": 3.14159}
 ],
 "bias": {"a0": -0.55, "a1": -0.075, "a3": -0.55, "a4": -0.075},
 "units": [
   {"type": "linear", "name": "hip_R",
    "inputs": {"cos(R)": -0.22, "obs[2]": -1.0, "obs[11]": -0.1, "obs[1]": 1.0, "obs[10]": 0.1, "obs[8]": 0.1},
    "range": 2.5, "tol": 0.05, "to": {"a0": 1.0}},
   {"type": "linear", "name": "knee_R",
    "inputs": {"sin(R)": 0.93, "cos(R)": 0.29, "obs[3]": -1.5, "obs[12]": -0.1},
    "range": 3.0, "tol": 0.03, "to": {"a1": 1.0}},
   {"type": "linear", "name": "ankle_R",
    "inputs": {"obs[4]": -0.5, "obs[13]": -0.03},
    "range": 1.0, "tol": 0.03, "to": {"a2": 1.0}},
   {"type": "linear", "name": "hip_L",
    "inputs": {"cos(L)": -0.22, "obs[5]": -1.0, "obs[14]": -0.1, "obs[1]": 1.0, "obs[10]": 0.1, "obs[8]": 0.1},
    "range": 2.5, "tol": 0.05, "to": {"a3": 1.0}},
   {"type": "linear", "name": "knee_L",
    "inputs": {"sin(L)": 0.93, "cos(L)": 0.29, "obs[6]": -1.5, "obs[15]": -0.1},
    "range": 3.0, "tol": 0.03, "to": {"a4": 1.0}},
   {"type": "linear", "name": "ankle_L",
    "inputs": {"obs[7]": -0.5, "obs[16]": -0.03},
    "range": 1.0, "tol": 0.03, "to": {"a5": 1.0}}
 ]}
```