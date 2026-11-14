import numpy as np

# Global state variables
prev_obs = None
prev_v = 0.0

def reset():
    global prev_obs, prev_v
    prev_obs = None
    prev_v = 0.0

def act(obs):
    global prev_obs, prev_v
    
    # Initialize if first call
    if prev_obs is None:
        prev_obs = obs
        return [0.0, 0.0, 0.0]
    
    # Calculate v as the change in x coordinate over the step
    # obs[0] appears to be the x coordinate based on typical control problems
    dx = obs[0] - prev_obs[0]
    dt = 0.008
    v = dx / dt
    
    # Use a simple PD controller for the x position (obs[0])
    # Target is to keep x near 1.0 (a reasonable target based on constraints)
    target_x = 1.0
    error_x = target_x - obs[0]
    
    # Derivative term using change in x
    deriv_x = (obs[0] - prev_obs[0]) / dt
    
    # Control law: proportional + derivative
    # We want to control the x position, so we'll use action 0 for this
    action_0 = 2.0 * error_x + 1.0 * deriv_x
    
    # For actions 1 and 2, we try to keep other states near zero
    # obs[1] seems to be a y coordinate or similar
    target_y = 0.0
    error_y = target_y - obs[1]
    
    # Simple PD for y position
    action_1 = 2.0 * error_y
    
    # Use obs[5] which is related to instantaneous rate of change
    # We'll use this to influence the third action
    action_2 = -0.5 * obs[5]
    
    # Apply clipping to actions
    action_0 = np.clip(action_0, -1.0, 1.0)
    action_1 = np.clip(action_1, -1.0, 1.0)
    action_2 = np.clip(action_2, -1.0, 1.0)
    
    # Update previous observation
    prev_obs = obs
    prev_v = v
    
    return [action_0, action_1, action_2]
