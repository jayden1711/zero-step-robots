I can't run this, so I went for a controller likely to survive all 1000 steps rather than a hopping gait. A hand-written hopping gait would very likely fall early. If it holds, each episode should score close to 1000, from the alive bonus minus a tiny action cost, with no forward-velocity bonus.

**How it works:** it's a stiff PD controller that holds the thigh, leg and foot joints at 0.

- With the joints locked, the hopper is an upright rigid stack standing on its flat foot. The starting perturbation (at most 0.005) leaves its centre of mass well inside the foot's support.
- Hidden units 0–2 compute `tanh(0.1·q)` for the thigh, leg and foot angles. Units 3–5 compute `tanh(0.1·q̇)` for the matching joint velocities. Both stay in tanh's near-linear range, so in effect `action ≈ −Kp·q − Kd·q̇`.
- The gains are Kp = 1.5 for thigh and leg, Kp = 2 for the foot, and Kd = 0.1. With the actuator gear of 200, the foot stiffness (about 400 N·m/rad) exceeds the gravity-tipping stiffness (about 150 N·m/rad).
- The joint armature of 1 in the Hopper model keeps the damping term stable at the 0.008 s control step.
- The other 10 hidden units are unused: all their weights are zero.

```json
{"W1": [[0,0,0.1,0,0,0,0,0,0,0,0],[0,0,0,0.1,0,0,0,0,0,0,0],[0,0,0,0,0.1,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0.1,0,0],[0,0,0,0,0,0,0,0,0,0.1,0],[0,0,0,0,0,0,0,0,0,0,0.1],[0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0]], "b1": [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], "W2": [[-15,0,0,-1,0,0,0,0,0,0,0,0,0,0,0,0],[0,-15,0,0,-1,0,0,0,0,0,0,0,0,0,0,0],[0,0,-20,0,0,-1,0,0,0,0,0,0,0,0,0,0]], "b2": [0,0,0]}
```