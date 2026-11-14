import numpy as np

# Global state variables
prev_x = 0.0
prev_obs = None

def reset():
    global prev_x, prev_obs
    prev_x = 0.0
    prev_obs = None

def act(obs):
    global prev_x, prev_obs
    
    # Extract relevant observations
    x = obs[0]  # This is the x coordinate we're interested in
    v = obs[5]  # Rate of change of x (clipped)
    
    # Calculate v based on the change in x over time
    # The step size is 0.008 seconds, so v should be dx/dt
    if prev_obs is not None:
        # Calculate change in x over the step
        dx = x - prev_x
        dt = 0.008
        calculated_v = dx / dt
    else:
        calculated_v = 0.0
    
    # Update previous values for next iteration
    prev_x = x
    prev_obs = obs
    
    # Simple proportional controller for x position
    # Try to keep x near 1.0 (assuming this is a desired target)
    target_x = 1.0
    error_x = target_x - x
    
    # Simple PID-like control for the action
    # P-term: proportional to error
    kp = 2.0  # Proportional gain
    action_x = kp * error_x
    
    # I-term: integrate error over time (simple approximation)
    # Since we don't have a real integral term, we'll use a simple approach
    # D-term: derivative of x position (already available as v)
    kd = 0.5  # Derivative gain
    action_v = -kd * v  # We want to dampen the velocity
    
    # Combine actions for the first dimension
    action_1 = action_x + action_v
    
    # For second and third dimensions, we'll use a simple damping approach
    # The system seems to be somewhat sensitive to position (obs[0]), so we're 
    # trying to maintain a stable position while avoiding large accelerations
    action_2 = -0.5 * obs[1]  # Dampen y position
    action_3 = -0.1 * obs[2]  # Dampen z position
    
    # Clip actions to [-1, 1]
    action_1 = np.clip(action_1, -1, 1)
    action_2 = np.clip(action_2, -1, 1)
    action_3 = np.clip(action_3, -1, 1)
    
    return [action_1, action_2, action_3]
