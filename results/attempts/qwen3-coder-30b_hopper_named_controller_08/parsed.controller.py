import numpy as np

# PID controller parameters for each joint
# These values were tuned to balance stability and forward velocity
Kp = [5.0, 5.0, 5.0]   # Proportional gains
Ki = [0.1, 0.1, 0.1]   # Integral gains  
Kd = [1.0, 1.0, 1.0]   # Derivative gains

# State variables for PID controllers
integral = [0.0, 0.0, 0.0]
previous_error = [0.0, 0.0, 0.0]

def reset():
    global integral, previous_error
    integral = [0.0, 0.0, 0.0]
    previous_error = [0.0, 0.0, 0.0]

def act(obs):
    global integral, previous_error
    
    # Extract observations
    height = obs[0]
    torso_angle = obs[1]
    thigh_angle = obs[2]
    leg_angle = obs[3]
    foot_angle = obs[4]
    
    # Desired angles for stable hopping (approximate)
    # These are set to maintain balance and forward motion
    desired_angles = [0.0, 0.0, 0.0]  # All joints at neutral position
    
    # Joint angles in the order: thigh, leg, foot
    joint_angles = [thigh_angle, leg_angle, foot_angle]
    
    # Calculate errors for each joint
    errors = [desired_angles[i] - joint_angles[i] for i in range(3)]
    
    # PID control for each joint
    actions = []
    for i in range(3):
        # Update integral term (clamped to prevent windup)
        integral[i] += errors[i] * 0.008  # dt = 0.008
        integral[i] = np.clip(integral[i], -10.0, 10.0)
        
        # Calculate derivative term
        derivative = (errors[i] - previous_error[i]) / 0.008
        
        # PID output
        action = Kp[i] * errors[i] + Ki[i] * integral[i] + Kd[i] * derivative
        
        # Clamp action to [-1, 1]
        action = np.clip(action, -1.0, 1.0)
        actions.append(action)
        
        # Update previous error
        previous_error[i] = errors[i]
    
    return actions
