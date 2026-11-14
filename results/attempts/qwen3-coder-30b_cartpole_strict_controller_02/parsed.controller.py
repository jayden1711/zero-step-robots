import numpy as np

# State for tracking
integral_error = 0.0
previous_error = 0.0

def reset():
    global integral_error, previous_error
    integral_error = 0.0
    previous_error = 0.0

def act(obs):
    global integral_error, previous_error
    
    # We want to keep obs[1] (which appears to be a position) within ±0.2
    # obs[1] is the position we care about
    target_position = 0.0  # Center position we want to maintain
    current_position = obs[1]
    
    # Calculate error
    error = target_position - current_position
    
    # PID parameters (tuned for this specific problem)
    Kp = 2.0
    Ki = 0.5
    Kd = 0.1
    
    # Update integral and derivative terms
    integral_error += error * 0.04  # dt = 0.04
    derivative_error = (error - previous_error) / 0.04
    
    # Calculate control action using PID
    action = Kp * error + Ki * integral_error + Kd * derivative_error
    
    # Clip action to [-3, 3]
    action = np.clip(action, -3.0, 3.0)
    
    # Update previous error for next iteration
    previous_error = error
    
    return [action]
