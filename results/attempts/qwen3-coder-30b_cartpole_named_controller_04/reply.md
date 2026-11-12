```python
import numpy as np

# PID controller parameters
Kp = 10.0
Ki = 0.1
Kd = 1.0

# Integrator and derivative terms
integral = 0.0
prev_error = 0.0
prev_time = None

def reset():
    global integral, prev_error, prev_time
    integral = 0.0
    prev_error = 0.0
    prev_time = None

def act(obs):
    global integral, prev_error, prev_time
    
    # Extract observations
    cart_pos, pole_angle, cart_vel, pole_vel = obs
    
    # Target angle is 0 (vertical)
    target_angle = 0.0
    error = target_angle - pole_angle
    
    # Time step calculation
    current_time = 0  # We don't have access to actual time, so we'll use a simple approach
    if prev_time is None:
        dt = 0.04  # Fixed time step as given in problem description
    else:
        dt = 0.04
    
    # Update integral term (with anti-windup)
    integral += error * dt
    # Limit integral term to prevent windup
    integral = np.clip(integral, -10.0, 10.0)
    
    # Calculate derivative term
    if prev_time is not None:
        derivative = (error - prev_error) / dt
    else:
        derivative = 0.0
    
    # PID control law
    action = Kp * error + Ki * integral + Kd * derivative
    
    # Clip action to allowed range
    action = np.clip(action, -3.0, 3.0)
    
    # Update for next iteration
    prev_error = error
    prev_time = current_time
    
    return [action]
```