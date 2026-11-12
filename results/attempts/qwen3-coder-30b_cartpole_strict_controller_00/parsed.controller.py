import numpy as np

# PID controller parameters
Kp = 2.0
Ki = 0.5
Kd = 0.1

# State variables for PID controller
integral = 0.0
previous_error = 0.0
previous_obs = None

def reset():
    global integral, previous_error, previous_obs
    integral = 0.0
    previous_error = 0.0
    previous_obs = None

def act(obs):
    global integral, previous_error, previous_obs
    
    # Target is to keep obs[1] (position) around 0
    target = 0.0
    current_position = obs[1]
    
    # Calculate error
    error = target - current_position
    
    # PID calculation
    global integral, previous_error
    
    # Update integral term
    integral += error * 0.04  # dt = 0.04
    
    # Calculate derivative term
    if previous_obs is not None:
        derivative = (current_position - previous_obs[1]) / 0.04
    else:
        derivative = 0.0
    
    # PID output
    action = Kp * error + Ki * integral + Kd * derivative
    
    # Clip action to [-3, 3]
    action = np.clip(action, -3.0, 3.0)
    
    # Store previous values for next iteration
    previous_obs = obs
    previous_error = error
    
    return [action]
