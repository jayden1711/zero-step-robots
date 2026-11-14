## Round 5 (final): add forward lean, cancel the backward dip, and make the hop bigger

**What round 4 shows.** The posture fixes worked: all 10 episodes survived the full 8 s. The robot still made no progress, though.

- **No net travel.** x swung about ±0.2 m within each cycle and finished near 0.
- **The foot never left the ground.** It was in contact on 99% of steps, and torso height never rose above its starting value. So there was no real hop, only rocking.
- **The torso stayed behind upright the whole time.** Its maximum was −0.005 rad. It dipped to about −0.15 to −0.18 rad near phase 0, which is a quarter cycle after the deepest crouch (sin minimum at 4.71). That is close to the −0.2 limit.

Round 4 as it stands scores about 0.04 m, so it fails either way. For the final round I'm accepting some fall risk in exchange for a real chance of forward travel.

**Changes:**

1. **Cancel the dip with a phase-advanced thigh rhythm.** The thigh rhythm becomes −0.3·sin + 0.25·cos. The cos part adds about +0.25 thigh torque at phase 0, exactly where the backward dip peaks, which pitches the torso forward (positive thigh torque pitches it forward).
2. **Forward lean.**
   - The a0 bias goes from −0.15 to −0.05.
   - Ankle balance is softened from −2 to −1.5, so the body is allowed to tip over the foot and travel instead of being held still.
   - The speed term (−0.1·obs[5]) stays, as the brake on running away.
3. **A bigger, slower hop to get airborne.**
   - Frequency drops from 2.5 to 2.0 Hz, giving each crouch and push more time.
   - Knee rhythm goes from 0.6 to 0.85.
   - Foot push goes from −0.2 to −0.3·sin, so the toes push down during extension for more lift and forward drive.
4. **Kept from round 4:** torso balance −4·(θ+0.3ω), the holds, and the foot bias that leans the shin forward.

```json
{"target": "cpg", "obs_dim": 11, "act_dim": 3, "hidden": 16,
 "oscillators": [{"name": "hop", "freq_hz": 2.0, "phase0": 0.0}],
 "bias": {"a0": -0.05, "a1": -0.1, "a2": 0.1},
 "units": [
   {"type": "linear", "name": "torso_pd", "inputs": {"obs[1]": 1.0, "obs[7]": 0.3},
    "range": 3.0, "tol": 0.02, "to": {"a0": -4.0}},
   {"type": "linear", "name": "speed_lean", "inputs": {"obs[5]": 1.0},
    "range": 5.0, "tol": 0.02, "to": {"a0": -0.1}},
   {"type": "linear", "name": "thigh_hold", "inputs": {"obs[2]": 1.0, "obs[8]": 0.1},
    "range": 3.0, "tol": 0.02, "to": {"a0": -1.0}},
   {"type": "linear", "name": "leg_hold", "inputs": {"obs[3]": 1.0, "obs[9]": 0.1},
    "range": 3.0, "tol": 0.02, "to": {"a1": -1.2}},
   {"type": "linear", "name": "foot_hold", "inputs": {"obs[4]": 1.0, "obs[10]": 0.1},
    "range": 2.0, "tol": 0.02, "to": {"a2": -1.5}},
   {"type": "linear", "name": "ankle_balance", "inputs": {"obs[1]": 1.0, "obs[7]": 0.2},
    "range": 3.0, "tol": 0.02, "to": {"a2": -1.5}},
   {"type": "linear", "name": "hop_rhythm", "inputs": {"sin(hop)": 1.0},
    "range": 1.2, "tol": 0.01, "to": {"a0": -0.3, "a1": 0.85, "a2": -0.3}},
   {"type": "linear", "name": "dip_cancel", "inputs": {"cos(hop)": 1.0},
    "range": 1.2, "tol": 0.01, "to": {"a0": 0.25}}
 ]}
```

**Expectation.** This design is untested, and passing the 3 m threshold is unlikely given how far round 4 was from it. Where it could go wrong:

- The bigger knee rhythm could deepen the backward dip faster than the cos term cancels it. That would end episodes early, which costs almost nothing compared with round 4's ~0.04 m.
- The added lean could tip the robot forward instead.