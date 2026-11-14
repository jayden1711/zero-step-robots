```python
import numpy as np

# PID controller parameters
Kp = 50.0
Ki = 10.0
Kd = 5.0

# Integral and derivative terms for PID
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
    
    # Time step (0.04 seconds)
    current_time = 0.0  # We'll use a simple approximation for time derivative
    dt = 0.04
    
    # PID control
    integral += error * dt
    derivative = (error - prev_error) / dt if prev_time is not None else 0.0
    
    # Calculate action using PID
    action = Kp * error + Ki * integral + Kd * derivative
    
    # Clip action to [-3, 3]
    action = np.clip(action, -3.0, 3.0)
    
    # Update for next iteration
    prev_error = error
    prev_time = current_time
    
    return [action]
```