import numpy as np

# PID controller parameters
Kp = 2.0
Ki = 0.5
Kd = 0.1

# Integrator and derivative terms
integral = 0.0
derivative = 0.0
previous_error = 0.0

def reset():
    global integral, derivative, previous_error
    integral = 0.0
    derivative = 0.0
    previous_error = 0.0

def act(obs):
    global integral, derivative, previous_error
    
    # Target is to keep obs[1] (position) close to 0
    target = 0.0
    current_position = obs[1]
    
    # Calculate error
    error = target - current_position
    
    # Update integrator
    integral += error * 0.04  # dt = 0.04
    
    # Update derivative
    derivative = (error - previous_error) / 0.04
    
    # PID control law
    action = Kp * error + Ki * integral + Kd * derivative
    
    # Clip action to [-3, 3]
    action = np.clip(action, -3.0, 3.0)
    
    # Store previous error for next iteration
    previous_error = error
    
    return [action]
