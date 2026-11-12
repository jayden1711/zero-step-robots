## Round 4: rhythm phased to cancel its own pitch disturbance, and a forward-leaning stance

**What round 3 shows.** The torso dipped backward in every cycle, and the dips grew each time:
- −0.10 at 0.4 s
- −0.14 at 0.8 s
- fall at 1.17 s

The dips came in the second half of each cycle (sin(hop) < 0). Two things pushed the torso back at the same time in that half:

1. **Knee crouch geometry.** The thigh joint cannot go above 0, and it already sat at its stop (max +0.016). When the knee bends, the thigh's lower end moves forward. With the thigh at its stop, the torso has to rotate back by about half the knee angle. The knee reached −0.30 and the torso dipped about −0.14, which matches.
2. **Foot rhythm sign.** The foot rhythm was +0.4·sin, so in this half it pushed the toes down. With the toe ahead of the centre of mass, that also pitches the body back.

The thigh swing used cos, so it was a quarter cycle off and never opposed either effect. Round 2 survived because its rhythm was too small for these effects to matter.

**Changes:**

1. **Every rhythm term now opposes the pitch the knee causes.** The knee uses a1 = +0.6·sin, so it crouches when sin < 0 and extends when sin > 0.
   - **Thigh:** a0 rhythm is −0.25·sin. During the crouch it adds +0.25, which pitches the torso forward. During extension it adds −0.25, which drives hip extension and the push.
   - **Foot:** a2 rhythm is −0.2·sin, with the sign flipped from round 3. During the crouch the toes push up, which pitches the body forward. During extension the toes push down, which adds lift.
2. **The thigh is held off its stop.** The thigh is held near −0.15 rad, using a hold gain of 1.0 and an a0 bias of −0.15. That gives the crouch room before the torso is forced back.
3. **The shin leans forward.** The foot is held near +0.1 rad (toes up relative to the shin), using a2 bias +0.1 with a foot hold gain of 1.5. With the foot flat, this tilts the shin forward and puts the foot slightly behind the hip. The push-off then has a forward component, which is where propulsion should come from.
4. **Stronger ankle balance.** The ankle term goes from −1·(θ+0.2ω) to −2·(θ+0.2ω). The ankle is the only joint that can stop the whole body from tipping over the foot.
5. **Kept from round 3:**
   - torso balance: −4·(θ+0.3ω)
   - speed term: −0.1·obs[5]
   - frequency: 2.5 Hz
   - The leg hold is softer (−1.2 instead of −1.5), so the crouch is deeper.

**How to read the round-4 results:**

- **Survives and moves forward:** round 5 scales up the knee rhythm, or the lean, for speed.
- **Falls forward:** round 5 reduces the shin lean and the a0 bias.
- **Still dips back each cycle:** round 5 shrinks the knee amplitude and moves the thigh target lower.
- **Falls quickly in some unexpected way:** round 5 falls back toward round 2 with mild versions of these phase fixes.

```json
{"target": "cpg", "obs_dim": 11, "act_dim": 3, "hidden": 16,
 "oscillators": [{"name": "hop", "freq_hz": 2.5, "phase0": 0.0}],
 "bias": {"a0": -0.15, "a1": -0.1, "a2": 0.1},
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
    "range": 3.0, "tol": 0.02, "to": {"a2": -2.0}},
   {"type": "linear", "name": "hop_rhythm", "inputs": {"sin(hop)": 1.0},
    "range": 1.2, "tol": 0.01, "to": {"a0": -0.25, "a1": 0.6, "a2": -0.2}}
 ]}
```