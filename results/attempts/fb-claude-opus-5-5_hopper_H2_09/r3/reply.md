## Round 3: lean slightly forward, add speed feedback, and make the hop bigger

**What round 2 shows.** The balance loop now works: all 10 episodes survived the full 8 s. But the robot only stands and sways; it does not travel.

- **Steady backward lean.** The torso settled at about −0.065 rad. That is about −0.2 / 3, so the −0.2 bias on a0 against the torso gain of −3 set that lean. The equilibrium lean is roughly the a0 bias divided by the balance gain. That gives me a direct dial for lean.
- **The hop is too weak.** The foot was on the ground on 99% of steps. Each rhythm cycle moved x back and forth by about 2 cm, but with the backward lean there was no net progress.

**Changes:**

1. **Forward lean.** The a0 bias goes from −0.2 to +0.1. With the stronger torso gain below, the target lean is about +0.025 rad when standing still. The ankle balance term still pulls the lean toward 0, so the robot shouldn't run away forward.
2. **Speed regulation through lean.** A new unit adds −0.1·obs[5] to a0. As forward speed rises, the lean target shrinks; at about 1 m/s the lean target is back to upright. This should stop it from accelerating into a forward fall.
3. **Stronger, better-damped balance.** The torso term is now −4·(obs[1] + 0.3·obs[7]). Larger hops will disturb the torso more than standing did.
4. **A real hop.**
   - Leg push-off goes from 0.3 to 0.6, foot from 0.1 to 0.4.
   - Leg stiffness drops from −2 to −1.5, so the rhythm can move the joint further.
   - Thigh swing goes from 0.1 to 0.25.
   - Frequency stays at 2.5 Hz.

**How to read the round-3 results:**

- **Survives and moves forward but slowly:** next round I'll raise the lean bias and hop amplitude.
- **Moves backward:** I'll flip the thigh swing sign (the phase relationship) and add more lean.
- **Falls forward:** I'll cut the bias back to about +0.03 and strengthen the speed term.
- **Falls in an oscillating way:** I'll pull the amplitudes halfway back toward round 2.

```json
{"target": "cpg", "obs_dim": 11, "act_dim": 3, "hidden": 16,
 "oscillators": [{"name": "hop", "freq_hz": 2.5, "phase0": 0.0}],
 "bias": {"a0": 0.1, "a1": -0.1},
 "units": [
   {"type": "linear", "name": "torso_pd", "inputs": {"obs[1]": 1.0, "obs[7]": 0.3},
    "range": 3.0, "tol": 0.02, "to": {"a0": -4.0}},
   {"type": "linear", "name": "speed_lean", "inputs": {"obs[5]": 1.0},
    "range": 5.0, "tol": 0.02, "to": {"a0": -0.1}},
   {"type": "linear", "name": "thigh_hold", "inputs": {"obs[2]": 1.0, "obs[8]": 0.1},
    "range": 3.0, "tol": 0.02, "to": {"a0": -1.0}},
   {"type": "linear", "name": "thigh_swing", "inputs": {"cos(hop)": 1.0},
    "range": 1.2, "tol": 0.01, "to": {"a0": 0.25}},
   {"type": "linear", "name": "leg_hold", "inputs": {"obs[3]": 1.0, "obs[9]": 0.1},
    "range": 3.0, "tol": 0.02, "to": {"a1": -1.5}},
   {"type": "linear", "name": "foot_hold", "inputs": {"obs[4]": 1.0, "obs[10]": 0.1},
    "range": 2.0, "tol": 0.02, "to": {"a2": -2.0}},
   {"type": "linear", "name": "ankle_balance", "inputs": {"obs[1]": 1.0, "obs[7]": 0.2},
    "range": 3.0, "tol": 0.02, "to": {"a2": -1.0}},
   {"type": "linear", "name": "pushoff", "inputs": {"sin(hop)": 1.0},
    "range": 1.2, "tol": 0.01, "to": {"a1": 0.6, "a2": 0.4}}
 ]}
```