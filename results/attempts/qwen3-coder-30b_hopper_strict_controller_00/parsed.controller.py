import numpy as np

# Global state variables
prev_obs = None
total_reward = 0.0

def reset():
    global prev_obs, total_reward
    prev_obs = None
    total_reward = 0.0

def act(obs):
    global prev_obs
    
    # Initialize action
    action = [0.0, 0.0, 0.0]
    
    # If this is the first observation, store it and return zero action
    if prev_obs is None:
        prev_obs = obs.copy()
        return action
    
    # Calculate v as the change in x coordinate over the step
    # The x coordinate is obs[0], so v = (obs[0] - prev_obs[0]) / dt
    dt = 0.008
    v = (obs[0] - prev_obs[0]) / dt
    
    # Use proportional control for action 1 based on v
    # This tries to maintain a desired velocity
    kp_v = 0.5
    action[0] = kp_v * v
    
    # Action 2: try to keep obs[1] near zero (y position)
    kp_y = 1.0
    action[1] = -kp_y * obs[1]
    
    # Action 3: try to keep the system stable by monitoring other states
    # Use a simple feedback based on velocity and position
    kp_vel = 0.2
    action[2] = -kp_vel * obs[5]  # obs[5] is related to instantaneous rate of change
    
    # Clip actions to [-1, 1]
    for i in range(3):
        action[i] = max(-1.0, min(1.0, action[i]))
    
    # Update previous observation
    prev_obs = obs.copy()
    
    return action
