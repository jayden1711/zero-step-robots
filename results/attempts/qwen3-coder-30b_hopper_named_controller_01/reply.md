```python
import numpy as np

# PID controller parameters for each joint
Kp = [50.0, 50.0, 50.0]  # Proportional gains
Ki = [10.0, 10.0, 10.0]  # Integral gains
Kd = [5.0, 5.0, 5.0]     # Derivative gains

# Joint angle targets (in radians)
target_angles = [0.0, 0.0, 0.0]

# State variables for PID controllers
integral_errors = [0.0, 0.0, 0.0]
previous_errors = [0.0, 0.0, 0.0]

def reset():
    global integral_errors, previous_errors
    integral_errors = [0.0, 0.0, 0.0]
    previous_errors = [0.0, 0.0, 0.0]

def act(obs):
    global integral_errors, previous_errors
    
    # Extract state variables
    torso_height = obs[0]
    torso_angle = obs[1]
    thigh_angle = obs[2]
    leg_angle = obs[3]
    foot_angle = obs[4]
    torso_x_vel = obs[5]
    torso_z_vel = obs[6]
    
    # Joint angles and velocities
    joint_angles = [thigh_angle, leg_angle, foot_angle]
    joint_velocities = [obs[8], obs[9], obs[10]]
    
    # Compute desired joint angles based on torso movement
    # Keep the torso upright (angle near 0) and move legs forward
    target_thigh = -torso_angle * 0.5  # Counteract torso tilt
    target_leg = -torso_angle * 0.3   # Counteract torso tilt
    target_foot = 0.0                 # Keep foot flat
    
    targets = [target_thigh, target_leg, target_foot]
    
    # PID control for each joint
    actions = []
    for i in range(3):
        error = targets[i] - joint_angles[i]
        integral_errors[i] += error * 0.008  # dt = 0.008
        derivative = (error - previous_errors[i]) / 0.008
        
        # Clamp integral term to prevent windup
        integral_errors[i] = np.clip(integral_errors[i], -10.0, 10.0)
        
        action = Kp[i] * error + Ki[i] * integral_errors[i] + Kd[i] * derivative
        
        # Clip action to [-1, 1]
        action = np.clip(action, -1.0, 1.0)
        
        previous_errors[i] = error
        actions.append(action)
    
    return actions
```