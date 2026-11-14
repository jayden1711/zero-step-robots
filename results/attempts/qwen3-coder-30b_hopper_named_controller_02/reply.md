```python
import numpy as np

# PID controller parameters for each joint
# These are tuned to balance stability and forward velocity
Kp = [10.0, 15.0, 20.0]  # Proportional gains
Ki = [0.1, 0.2, 0.3]     # Integral gains  
Kd = [5.0, 8.0, 10.0]    # Derivative gains

# Joint angle targets (in radians)
target_angles = [0.0, 0.0, 0.0]

# State for PID controllers
integral_errors = [0.0, 0.0, 0.0]
previous_errors = [0.0, 0.0, 0.0]

def reset():
    global integral_errors, previous_errors
    integral_errors = [0.0, 0.0, 0.0]
    previous_errors = [0.0, 0.0, 0.0]

def act(obs):
    global integral_errors, previous_errors
    
    # Extract relevant observations
    torso_height = obs[0]
    torso_angle = obs[1]
    thigh_angle = obs[2]
    leg_angle = obs[3] 
    foot_angle = obs[4]
    torso_x_vel = obs[5]
    
    # Joint angles in order: thigh, leg, foot
    joint_angles = [thigh_angle, leg_angle, foot_angle]
    
    # Update integral and previous errors for PID control
    action = []
    
    # For each joint, calculate PID control signal
    for i in range(3):
        # Calculate desired angle based on torso angle and velocity
        # We want to maintain balance while moving forward
        target = target_angles[i]
        
        error = target - joint_angles[i]
        integral_errors[i] += error
        derivative = error - previous_errors[i]
        
        # PID calculation
        control_signal = Kp[i] * error + Ki[i] * integral_errors[i] + Kd[i] * derivative
        
        # Clamp the control signal to [-1, 1]
        control_signal = np.clip(control_signal, -1.0, 1.0)
        
        action.append(control_signal)
        previous_errors[i] = error
    
    return action
```