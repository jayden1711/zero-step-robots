import numpy as np

# Global variables to maintain state between calls
integral_error = 0.0
previous_obs = None

def reset():
    global integral_error, previous_obs
    integral_error = 0.0
    previous_obs = None

def act(obs):
    global integral_error, previous_obs
    
    # Extract relevant observations
    x_pos = obs[0]  # Position in x direction
    y_pos = obs[1]  # Position in y direction
    z_pos = obs[2]  # Position in z direction
    x_vel = obs[5]  # Velocity in x direction (instantaneous rate of change)
    
    # Simple PD controller for x position
    desired_x = 1.0  # Target x position
    error_x = desired_x - x_pos
    kp_x = 2.0
    kd_x = 1.0
    
    # Simple PI controller for y position
    desired_y = 0.0  # Target y position (center)
    error_y = desired_y - y_pos
    ki_y = 0.1
    integral_error += error_y * 0.008  # dt = 0.008
    
    # Calculate control signals
    action_x = kp_x * error_x + kd_x * (-x_vel)  # Negative velocity for feedback
    action_y = kp_x * error_y + ki_y * integral_error  # PI controller for y
    
    # Limit the actions to [-1, 1]
    action_x = np.clip(action_x, -1.0, 1.0)
    action_y = np.clip(action_y, -1.0, 1.0)
    
    # For z direction, we use a simple proportional controller
    desired_z = 0.0  # Target z position (center)
    error_z = desired_z - z_pos
    kp_z = 1.0
    
    action_z = kp_z * error_z
    action_z = np.clip(action_z, -1.0, 1.0)
    
    # Return the actions
    return [action_x, action_y, action_z]
