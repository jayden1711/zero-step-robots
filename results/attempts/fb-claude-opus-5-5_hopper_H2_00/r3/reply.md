# Round 3: stabilise the whole body through the ankle, then add the hop

## What rounds 0–2 show

The evidence points to a different failure than the one I diagnosed in rounds 1–2. **The whole robot topples forward over its toe, and the hip cannot prevent that.**

- **The angles only add up if the heel lifted.** If the foot were flat, the joint angles would satisfy obs[1] = −(obs[2] + obs[3] + obs[4]).
  - Round 2: the torso reached about −0.19 rad and the thigh −0.235 rad, with the leg about straight and the foot at most +0.04.
  - Those angles cannot all hold with a flat foot. The heel must have lifted, so the body was rolling forward over the toe.
- **The hip only moves momentum between body parts.** Hip torque cannot change the body's total angular momentum about the foot contact. Only gravity and the ankle (foot–ground) torque can.
  - Round 2 used the physically correct hip sign: positive a0 tips the torso towards −obs[1]. It tilted the torso back by pushing the leg forward, which sped up the forward topple.
  - Round 0 lasted longer for a different reason. Its positive a0 pressed the thigh against its 0 rad joint limit, so the robot was nearly rigid and fell slowly.
- **The rhythm torques were too large for the foot.** The foot reaches about 0.26 m in front of the ankle and 0.13 m behind it. With about 155 N of body weight, the foot can only resist about ±20–40 N·m of ankle torque before the heel or toe lifts. That is an action of about 0.1–0.2.
  - The foot rhythm alone, 0.15–0.3, was 30–60 N·m. That is enough to roll the foot.
- **The gains were not the problem.** With armature 1 on every joint, gains around Kp = 2 and Kd = 0.25 are well damped and stable at 0.008 s steps. Round 1's instability explanation was wrong.

## Round 3: a standing-balance test with no rhythm

The aim is to confirm the robot can stay up for 8 s before adding the hop in rounds 4 and 5.

- **Ankle balance (the main loop).**
  - It controls the world tilt of the lower leg, φ = obs[1] + obs[2] + obs[3], with feedback a2 = 1.2·φ + 0.25·φ̇ + 0.072.
  - The target is φ ≈ −0.06, a slight forward lean that puts the centre of mass over the middle of the foot.
  - When the leg tips forward (φ falls), the foot pushes the toe down and moves the body back.
  - The stiffness (240 N·m/rad) exceeds the toppling stiffness from gravity (about 80 N·m/rad). Damping ratio is about 0.7. Small errors need only small torques, well within what the foot can hold.
- **Hip, torso upright in world angle.**
  - a0 = 2·obs[1] + 0.25·obs[7] + 0.06. This is the physically correct sign, and the target torso angle is −0.03.
  - That target keeps the thigh slightly off its 0 limit, about −0.03 rad, so the hip can apply torque in both directions.
  - The ankle loop now absorbs the reaction on the leg.
- **Knee held straight:** a PD controller plus a +0.2 bias holds the knee against its 0 limit, so the leg is rigid.
- **No rhythm this round.** This isolates whether balance works.

```json
{"target": "cpg", "obs_dim": 11, "act_dim": 3, "hidden": 16,
 "oscillators": [{"name": "cpg", "freq_hz": 2.0, "phase0": 0.0}],
 "couplings": [],
 "bias": {"a0": 0.06, "a1": 0.2, "a2": 0.072},
 "units": [
   {"type": "linear", "name": "hip_torso", "inputs": {"obs[1]": 2.0, "obs[7]": 0.25},
    "range": 1.5, "tol": 0.05, "to": {"a0": 1.0}},
   {"type": "linear", "name": "knee_hold", "inputs": {"obs[3]": -2.0, "obs[9]": -0.2},
    "range": 2.0, "tol": 0.05, "to": {"a1": 1.0}},
   {"type": "linear", "name": "ankle_balance",
    "inputs": {"obs[1]": 1.2, "obs[2]": 1.2, "obs[3]": 1.2, "obs[7]": 0.25, "obs[8]": 0.25, "obs[9]": 0.25},
    "range": 1.0, "tol": 0.05, "to": {"a2": 1.0}},
   {"type": "linear", "name": "foot_damp", "inputs": {"obs[10]": -0.05},
    "range": 0.5, "tol": 0.05, "to": {"a2": 1.0}}
 ]}
```

**How I'll read the result:**
- **It survives:** round 4 adds the hop on top of this base. The hop is a knee crouch and extend, the thigh swings forward in flight, and the ankle loop is gated off in flight.
- **It falls forward slowly with the heel up:** the ankle gain or lean target needs adjusting.
- **The torso oscillates fast:** the hip and ankle loops are fighting each other, so I'll cut the hip gain.