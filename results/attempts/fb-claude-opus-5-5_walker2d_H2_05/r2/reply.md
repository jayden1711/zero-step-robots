The torso still pitched backward and fell. The thighs sat pinned at about 0 rad, and their action was saturated positive 61% of the time.

**Why it fell.** With thigh angles limited to 0 or below, a thigh can only point along the torso line or behind it. If the torso is upright, the feet can only be under the hip or behind it. My positive torques pushed both thighs into the 0 stop. The body then became one rigid stick with its feet ahead of its mass, and it tipped back. Once a thigh is against its limit, hip torque can no longer move the torso, so the stronger feedback did nothing.

The same problem was in round 0. I asked for a 0.05 rad forward lean, which forced the thighs toward their limit. In round 0 the torso settled near −0.35 rad, and with the thighs near 0 the feet stayed in front of the body, so it walked backward.

**Changes for round 2.** The posture is designed so that the thighs work in the middle of their range:

- **Torso setpoint becomes −0.2 rad (leaning slightly back).** Thigh angle minus torso angle gives the leg's angle from vertical. A slight backward lean is what lets the swing foot land up to about 0.2 rad in front of the hip.
- **Thigh target becomes θ_d = −0.35 − 0.3·cos φ, which spans −0.65 to −0.05 rad.** The thighs stay off the 0 stop. Each leg sweeps from about 0.15 rad in front of vertical to about 0.45 rad behind.
  - Gains: Kp 1.5, Kd 0.15.
  - Torso feedback: −3·(torso angle + 0.2) − 0.4·(torso angular velocity).
  - The bias cancels both constant terms, so the net thigh torque is zero at the nominal posture.
- **Knee torque becomes 0.2 − 0.5·sin φ − 0.4·cos φ.** It starts flexing at toe-off (φ ≈ 0), flexes most in early-to-mid swing, extends hard before touchdown (φ ≈ π), and stays straight through stance.
- **Feet:** the position gain on each foot goes from 1 to 2, giving stiffer ankles.

```json
{"target": "cpg", "obs_dim": 17, "act_dim": 6, "hidden": 16,
 "oscillators": [
   {"name": "R", "freq_hz": 1.0, "phase0": 0.0},
   {"name": "L", "freq_hz": 1.0, "phase0": 3.14159}
 ],
 "couplings": [
   {"from": "R", "to": "L", "weight": 2.0, "phase_lag": 3.14159},
   {"from": "L", "to": "R", "weight": 2.0, "phase_lag": 3.14159}
 ],
 "bias": {"a0": -1.125, "a3": -1.125, "a1": 0.2, "a4": 0.2},
 "units": [
   {"type": "linear", "name": "R_thigh",
    "inputs": {"cos(R)": -0.45, "obs[2]": -1.5, "obs[11]": -0.15, "obs[1]": -3.0, "obs[10]": -0.4},
    "range": 4.0, "tol": 0.05, "to": {"a0": 1.0}},
   {"type": "linear", "name": "L_thigh",
    "inputs": {"cos(L)": -0.45, "obs[5]": -1.5, "obs[14]": -0.15, "obs[1]": -3.0, "obs[10]": -0.4},
    "range": 4.0, "tol": 0.05, "to": {"a3": 1.0}},
   {"type": "linear", "name": "R_knee",
    "inputs": {"sin(R)": -0.5, "cos(R)": -0.4, "obs[12]": -0.05},
    "range": 1.5, "tol": 0.05, "to": {"a1": 1.0}},
   {"type": "linear", "name": "L_knee",
    "inputs": {"sin(L)": -0.5, "cos(L)": -0.4, "obs[15]": -0.05},
    "range": 1.5, "tol": 0.05, "to": {"a4": 1.0}},
   {"type": "linear", "name": "R_foot",
    "inputs": {"obs[4]": -2.0, "obs[13]": -0.1},
    "range": 2.0, "tol": 0.05, "to": {"a2": 1.0}},
   {"type": "linear", "name": "L_foot",
    "inputs": {"obs[7]": -2.0, "obs[16]": -0.1},
    "range": 2.0, "tol": 0.05, "to": {"a5": 1.0}}
 ]}
```