import numpy as np

# Global variables to maintain state between calls
integral_error = 0.0
previous_error = 0.0
previous_obs = None

def reset():
    global integral_error, previous_error, previous_obs
    integral_error = 0.0
    previous_error = 0.0
    previous_obs = None

def act(obs):
    global integral_error, previous_error, previous_obs
    
    # Extract relevant observations
    x_pos = obs[0]  # Position in x direction
    y_pos = obs[1]  # Position in y direction
    z_pos = obs[2]  # Position in z direction
    x_vel = obs[5]  # Velocity in x direction (instantaneous)
    
    # Target position (we want to maintain x around 1.0, y around 0.0, z around 0.0)
    target_x = 1.0
    target_y = 0.0
    target_z = 0.0
    
    # Calculate errors
    error_x = target_x - x_pos
    error_y = target_y - y_pos
    error_z = target_z - z_pos
    
    # PID parameters (tuned for this specific system)
    kp = 2.0
    ki = 0.1
    kd = 0.5
    
    # Calculate integral and derivative terms
    integral_error += error_x
    derivative_error = error_x - previous_error if previous_error != 0 else 0.0
    
    # Compute action using PID control
    action_x = kp * error_x + ki * integral_error + kd * derivative_error
    
    # For y and z, we'll use simpler proportional control
    action_y = kp * error_y
    action_z = kp * error_z
    
    # Clip actions to [-1, 1]
    action_x = np.clip(action_x, -1.0, 1.0)
    action_y = np.clip(action_y, -1.0, 1.0)
    action_z = np.clip(action_z, -1.0, 1.0)
    
    # Store previous values for next iteration
    previous_error = error_x
    previous_obs = obs
    
    return [action_x, action_y, action_z]
