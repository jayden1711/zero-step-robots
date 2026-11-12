```python
import numpy as np

# PID controller parameters for each joint
# These are tuned to balance stability and forward velocity
Kp = [10.0, 15.0, 20.0]  # Proportional gains
Ki = [0.1, 0.1, 0.1]     # Integral gains  
Kd = [5.0, 5.0, 5.0]     # Derivative gains

# State for integral and derivative terms
integral = [0.0, 0.0, 0.0]
derivative = [0.0, 0.0, 0.0]
prev_error = [0.0, 0.0, 0.0]

def reset():
    global integral, derivative, prev_error
    integral = [0.0, 0.0, 0.0]
    derivative = [0.0, 0.0, 0.0]
    prev_error = [0.0, 0.0, 0.0]

def act(obs):
    global integral, derivative, prev_error
    
    # Target angles for each joint (based on desired stable posture)
    # The hopper should maintain a slight forward lean and keep joints near neutral
    target_angles = [0.0, 0.0, 0.0]
    
    # For stability, we also consider the torso angle and velocity
    torso_angle = obs[1]
    torso_vel = obs[6]
    
    # Adjust targets slightly based on current state to maintain balance
    target_angles[0] = -torso_angle * 0.5  # Thigh angle should counteract torso tilt
    target_angles[1] = -torso_angle * 0.3  # Leg angle should follow
    target_angles[2] = -torso_angle * 0.1  # Foot angle should follow
    
    # Joint angles from observation (index 2,3,4)
    current_angles = [obs[2], obs[3], obs[4]]
    
    # Joint angular velocities from observation (index 8,9,10)  
    current_velocities = [obs[8], obs[9], obs[10]]
    
    # Compute errors for each joint
    errors = [target_angles[i] - current_angles[i] for i in range(3)]
    
    # PID control for each joint
    actions = []
    for i in range(3):
        # Update integral term (clamped to prevent windup)
        integral[i] += errors[i] * 0.008  # dt = 0.008
        integral[i] = np.clip(integral[i], -10.0, 10.0)
        
        # Compute derivative term
        derivative[i] = (errors[i] - prev_error[i]) / 0.008
        
        # PID action
        action = Kp[i] * errors[i] + Ki[i] * integral[i] + Kd[i] * derivative[i]
        
        # Clamp action to [-1, 1]
        action = np.clip(action, -1.0, 1.0)
        actions.append(action)
        
        # Update previous error
        prev_error[i] = errors[i]
    
    return actions
```