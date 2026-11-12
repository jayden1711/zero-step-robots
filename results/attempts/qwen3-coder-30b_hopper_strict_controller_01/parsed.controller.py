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
    
    # Clip observations 5-10 to [-10, 10] as specified
    clipped_obs = obs[:]
    for i in range(5, 11):
        clipped_obs[i] = max(-10, min(10, clipped_obs[i]))
    
    # Extract relevant observations
    x_pos = clipped_obs[0]  # Should be > 0.7 to be healthy
    y_pos = clipped_obs[1]  # Should be < 0.2 in magnitude to be healthy
    z_pos = clipped_obs[2]  # Position in z
    x_vel = clipped_obs[5]  # Velocity in x (related to v)
    
    # Initialize previous observation if needed
    if previous_obs is None:
        previous_obs = clipped_obs[:]
        return [0.0, 0.0, 0.0]
    
    # Calculate change in x position over the step
    dx = x_pos - previous_obs[0]
    dt = 0.008  # Step time
    
    # Estimate v as dx/dt (this is what the reward uses)
    v = dx / dt if dt > 0 else 0.0
    
    # Simple PID-like controller for x position
    target_x = 1.0  # Desired x position
    error_x = target_x - x_pos
    
    # Integral term for steady-state error
    integral_error += error_x * dt
    
    # Derivative term
    dx_dt = x_vel  # Using the observed velocity as derivative
    
    # PID coefficients (tuned heuristically)
    kp = 2.0
    ki = 0.5
    kd = 0.1
    
    # Calculate control signal for x direction
    control_x = kp * error_x + ki * integral_error + kd * (-dx_dt)  # Negative derivative for stability
    
    # Simple controller for y position (keep it near zero)
    target_y = 0.0
    error_y = target_y - y_pos
    control_y = 2.0 * error_y
    
    # Simple controller for z position (keep it near zero)
    target_z = 0.0
    error_z = target_z - z_pos
    control_z = 1.5 * error_z
    
    # Convert to actions
    action_x = control_x
    action_y = control_y
    action_z = control_z
    
    # Clip actions to [-1, 1]
    action_x = max(-1.0, min(1.0, action_x))
    action_y = max(-1.0, min(1.0, action_y))
    action_z = max(-1.0, min(1.0, action_z))
    
    # Store current observation for next step
    previous_obs = clipped_obs[:]
    
    return [action_x, action_y, action_z]
