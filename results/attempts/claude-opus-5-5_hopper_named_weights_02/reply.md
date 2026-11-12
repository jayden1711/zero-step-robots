These weights make the hopper stand still and balance rather than hop. I couldn't run them, so the score is a prediction. A balanced, healthy hopper earns about 1 per step, so a full 1000 steps would score close to 1000. Hopping forward would earn more, but I didn't think hand-written hopping weights were likely to work.

**How it works:** only three of the 16 hidden units are used. Each one is a PD (proportional-derivative) controller. The first-layer weights are small, so tanh stays nearly linear. The output weight of 10 then scales each unit back up to the intended gain.

1. **Hip unit (thigh torque):** keeps the torso upright, because the hopper fails if the torso tilts 0.2 radians. Torque = 0.5·(torso angle) + 0.05·(torso angular velocity). A positive hip torque turns the torso back toward upright, which is why both gains are positive.
2. **Knee unit (leg torque):** holds the knee straight. Torque = −(knee angle) − 0.1·(knee angular velocity).
3. **Ankle unit (foot torque):** balances the whole body over the foot like an inverted pendulum. The lean angle is φ = torso angle + thigh angle + leg angle. Torque = 1.0·φ + 0.25·(rate of change of φ).
   - The ankle stiffness is 200 Nm/rad, above the roughly 85 Nm/rad that gravity needs, so the body is pushed back upright.
   - The damping is about 0.8 of critical.
   - Ankle torque is limited because too much tips the foot onto its heel or toe. These gains stay within that limit while the lean is small, and the starting perturbation is tiny.

The output biases are zero, so the upright pose is the resting point.

```json
{"W1": [[0, 0.05, 0, 0, 0, 0, 0, 0.005, 0, 0, 0], [0, 0, 0, -0.1, 0, 0, 0, 0, 0, -0.01, 0], [0, 0.1, 0.1, 0.1, 0, 0, 0, 0.025, 0.025, 0.025, 0], [0,0,0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0,0,0,0]], "b1": [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], "W2": [[10,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],[0,10,0,0,0,0,0,0,0,0,0,0,0,0,0,0],[0,0,10,0,0,0,0,0,0,0,0,0,0,0,0,0]], "b2": [0,0,0]}
```