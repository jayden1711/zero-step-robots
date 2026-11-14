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
    x_vel = obs[5]  # Velocity in x direction (instantaneous rate of change)
    
    # Calculate desired x position to maintain stability
    # We want to keep x_pos around 1.0 (based on the constraint obs[0] > 0.7)
    desired_x = 1.0
    
    # Error calculation for PID controller
    error = desired_x - x_pos
    
    # Simple PID-like control strategy
    # Proportional term
    kp = 2.0
    
    # Integral term (accumulated error)
    ki = 0.1
    
    # Derivative term (rate of change of error)
    kd = 0.5
    
    integral_error += error * 0.008  # dt = 0.008
    derivative_error = (error - previous_error) / 0.008 if previous_error is not None else 0.0
    
    # Calculate control action for x direction
    action_x = kp * error + ki * integral_error + kd * derivative_error
    
    # Limit action to [-1, 1]
    action_x = np.clip(action_x, -1.0, 1.0)
    
    # For y and z directions, try to keep them near zero (stable position)
    # Simple proportional control with gain
    kp_y = 1.5
    kp_z = 1.5
    
    action_y = -kp_y * y_pos
    action_z = -kp_z * z_pos
    
    # Clip actions to [-1, 1]
    action_y = np.clip(action_y, -1.0, 1.0)
    action_z = np.clip(action_z, -1.0, 1.0)
    
    # Store previous values for next iteration
    previous_error = error
    previous_obs = obs
    
    return [action_x, action_y, action_z]
