The controller below is a hand-designed PD balancer. It aims for the safe score: stand upright for all 1000 steps, giving about **1000** per episode. I did not try a hand-tuned hopping gait, which is very likely to fall early. I couldn't run it, so this is my best estimate, not a tested result.

**How it works:** In Hopper's XML, the root and all joints share the hinge axis `0 -1 0`. That means absolute segment angles add up: thigh = θ + q₁, leg = θ + q₁ + q₂. A joint torque τ pushes the child segment by +τ and the parent by −τ. The foot spans roughly x ∈ [−0.13, 0.26], so with stiff joints the body's centre of mass stays over the foot.

Three hidden units work as near-linear PD channels. The other 13 are unused.
- **Hip (unit 0):** τ_thigh = 1·tanh(θ + 0.1·ω_torso). This keeps the torso upright, which is what the |θ| < 0.2 health check needs.
- **Ankle (unit 1):** τ_foot = 2·tanh(ψ + 0.2·ψ̇), where ψ = θ + q₁ + q₂ is the leg's absolute angle. This balances the whole body over the foot.
- **Knee (unit 2):** τ_leg = −2·tanh(q₂ + 0.05·q̇₂). This keeps the leg straight.

The gains are sized for the actuator gear (about 200 Nm per action unit) and the joint armature. Under the tiny initial perturbations, the torques stay well within the support limits of the foot.

```json
{
  "W1": [
    [0, 1, 0, 0, 0, 0, 0, 0.1, 0, 0, 0],
    [0, 1, 1, 1, 0, 0, 0, 0.2, 0.2, 0.2, 0],
    [0, 0, 0, 1, 0, 0, 0, 0, 0, 0.05, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
  ],
  "b1": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
  "W2": [
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, -2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
  ],
  "b2": [0, 0, 0]
}
```