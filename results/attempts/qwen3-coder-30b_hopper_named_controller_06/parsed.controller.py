import numpy as np

# PID controller parameters for each joint
# These were tuned to balance stability and forward velocity
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
    
    # Target angles for stable hopping
    # These are based on the natural stance of the hopper
    target_angles = [0.0, 0.0, 0.0]  # All joints at neutral position
    
    # Extract current joint angles (indices 2-4)
    current_angles = obs[2:5]
    
    # Calculate errors for each joint
    errors = [target - current for target, current in zip(target_angles, current_angles)]
    
    # PID control calculation
    actions = []
    for i in range(3):  # For each joint
        # Update integral term (clamped to prevent windup)
        integral[i] += errors[i] * 0.008  # dt = 0.008
        integral[i] = np.clip(integral[i], -10.0, 10.0)
        
        # Calculate derivative term
        derivative[i] = (errors[i] - prev_error[i]) / 0.008
        
        # PID action
        action = Kp[i] * errors[i] + Ki[i] * integral[i] + Kd[i] * derivative[i]
        
        # Clip action to valid range
        action = np.clip(action, -1.0, 1.0)
        actions.append(action)
        
        # Update previous error for next iteration
        prev_error[i] = errors[i]
    
    return actions
