import numpy as np

# Global variables to maintain state between calls
integral_error = 0.0
previous_obs = None
previous_v = 0.0

def reset():
    global integral_error, previous_obs, previous_v
    integral_error = 0.0
    previous_obs = None
    previous_v = 0.0

def act(obs):
    global integral_error, previous_obs, previous_v
    
    # Extract relevant observations
    x_pos = obs[0]
    y_pos = obs[1]
    v = obs[5]  # instantaneous rate of change (related to x velocity)
    
    # Define desired setpoints
    desired_x = 1.0  # We want to maintain x position around 1.0
    desired_y = 0.0  # We want to maintain y position around 0.0
    
    # PID controller for x position (using the v observation as feedback)
    error_x = desired_x - x_pos
    integral_error_x = integral_error + error_x
    
    # Derivative of error (use v to estimate rate of change)
    if previous_obs is not None:
        delta_t = 0.008
        derivative_error_x = (v - previous_v) / delta_t
    else:
        derivative_error_x = 0.0
    
    # PID gains (tuned for this specific system)
    kp_x = 10.0
    ki_x = 5.0
    kd_x = 2.0
    
    # Calculate action for x control
    action_x = kp_x * error_x + ki_x * integral_error_x + kd_x * derivative_error_x
    
    # PID controller for y position
    error_y = desired_y - y_pos
    integral_error_y = integral_error + error_y
    
    if previous_obs is not None:
        delta_t = 0.008
        derivative_error_y = (obs[6] - previous_obs[6]) / delta_t  # Use the next observation for derivative
    else:
        derivative_error_y = 0.0
    
    kp_y = 15.0
    ki_y = 7.0
    kd_y = 3.0
    
    # Calculate action for y control
    action_y = kp_y * error_y + ki_y * integral_error_y + kd_y * derivative_error_y
    
    # For the third action, try to maintain stability by reducing sudden changes
    if previous_obs is not None:
        # Simple proportional control on change in v to avoid oscillations
        dv = v - previous_v
        action_z = -0.5 * dv
    else:
        action_z = 0.0
    
    # Apply clipping to actions
    action_x = np.clip(action_x, -1.0, 1.0)
    action_y = np.clip(action_y, -1.0, 1.0)
    action_z = np.clip(action_z, -1.0, 1.0)
    
    # Update previous values
    previous_obs = obs
    previous_v = v
    
    return [action_x, action_y, action_z]
