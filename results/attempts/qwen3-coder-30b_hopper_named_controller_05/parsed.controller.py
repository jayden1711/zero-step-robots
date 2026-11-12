import numpy as np

# PID controller parameters for each joint
Kp = [10.0, 15.0, 20.0]  # Proportional gains
Ki = [0.1, 0.1, 0.1]     # Integral gains
Kd = [5.0, 5.0, 5.0]     # Derivative gains

# Target angles for each joint (relative to upright position)
target_angles = [0.0, 0.0, 0.0]

# Integral and derivative error terms
integral_error = [0.0, 0.0, 0.0]
derivative_error = [0.0, 0.0, 0.0]
prev_error = [0.0, 0.0, 0.0]

def reset():
    global integral_error, derivative_error, prev_error
    integral_error = [0.0, 0.0, 0.0]
    derivative_error = [0.0, 0.0, 0.0]
    prev_error = [0.0, 0.0, 0.0]

def act(obs):
    global integral_error, derivative_error, prev_error
    
    # Extract state
    torso_height = obs[0]
    torso_angle = obs[1]
    thigh_angle = obs[2]
    leg_angle = obs[3]
    foot_angle = obs[4]
    torso_x_vel = obs[5]
    
    # Calculate joint errors (relative to target)
    errors = [
        thigh_angle - target_angles[0],
        leg_angle - target_angles[1],
        foot_angle - target_angles[2]
    ]
    
    # Update integral error
    integral_error[0] += errors[0]
    integral_error[1] += errors[1]
    integral_error[2] += errors[2]
    
    # Calculate derivative error (using velocity for better estimation)
    derivative_error[0] = (errors[0] - prev_error[0]) * 125.0  # Scale by 1/step_time = 1/0.008 = 125
    derivative_error[1] = (errors[1] - prev_error[1]) * 125.0
    derivative_error[2] = (errors[2] - prev_error[2]) * 125.0
    
    # Update previous errors
    prev_error[0] = errors[0]
    prev_error[1] = errors[1]
    prev_error[2] = errors[2]
    
    # Calculate actions using PID control
    actions = []
    for i in range(3):
        action = (Kp[i] * errors[i] + 
                  Ki[i] * integral_error[i] + 
                  Kd[i] * derivative_error[i])
        actions.append(action)
    
    # Clip actions to [-1, 1]
    actions = [np.clip(a, -1.0, 1.0) for a in actions]
    
    return actions
