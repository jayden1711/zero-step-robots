The controller makes the hopper stand still and rigid. Each joint is held at its starting angle of 0 by a proportional-derivative (PD) loop: a torque that pushes back toward the target angle and damps the joint's speed. I couldn't run or test this, so the analysis below is reasoning only. If the hopper stays upright for the full episode, each episode should score about 1000 (1 per step for 1000 steps). It earns almost nothing from forward speed.

**Why standing rigid should be stable.** The hopper starts upright with its centre of mass roughly above the ankle. The foot runs from about −0.13 m to +0.26 m relative to the ankle, so the centre of mass sits well inside the area the foot covers. If the joints are stiff, the robot is effectively one solid object resting on a flat foot, and it should stay put.

**Hidden units:**
- **Units 0–2:** one PD loop per joint, `h = tanh(−q − 0.1·q̇)`, with an output weight of 3 to that joint's motor. For small errors this gives about `action ≈ −3q − 0.3q̇`. Each motor multiplies its action by 200, so that is roughly 600 Nm/rad of stiffness and 60 Nm·s/rad of damping.
- **Unit 3:** a small extra correction from torso angle and torso angular velocity to the hip motor, `+1·tanh(φ + 0.1·φ̇)`. Torque at the hip pushes the torso the opposite way, so this term rotates the torso back toward upright.
- **Units 4–15:** unused (all zeros).

**Why these gains shouldn't oscillate.** I'm relying on two things I recall from the standard hopper model file (I didn't check them): each joint has extra built-in inertia (armature = 1) and some damping. With those values, a control step of 0.008 s works out to about 0.2 for stiffness and 0.5 for damping in the usual stability check, comfortably below the point where the loop starts to oscillate.

```json
{"W1": [[0,0,-1,0,0,0,0,0,-0.1,0,0],[0,0,0,-1,0,0,0,0,0,-0.1,0],[0,0,0,0,-1,0,0,0,0,0,-0.1],[0,1,0,0,0,0,0,0.1,0,0,0],[0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0]],
"b1": [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
"W2": [[3,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0],[0,3,0,0,0,0,0,0,0,0,0,0,0,0,0,0],[0,0,3,0,0,0,0,0,0,0,0,0,0,0,0,0]],
"b2": [0,0,0]}
```