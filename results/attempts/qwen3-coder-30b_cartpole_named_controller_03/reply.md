```python
import numpy as np

# PID controller parameters for balancing the pole
Kp = 50.0   # Proportional gain
Ki = 10.0   # Integral gain  
Kd = 5.0    # Derivative gain

# State variables for PID controller
integral_error = 0.0
previous_error = 0.0
previous_time = None

def reset():
    global integral_error, previous_error, previous_time
    integral_error = 0.0
    previous_error = 0.0
    previous_time = None

def act(obs):
    global integral_error, previous_error, previous_time
    
    # Extract observations
    cart_pos, pole_angle, cart_vel, pole_vel = obs
    
    # Target angle is 0 (vertical)
    target_angle = 0.0
    error = target_angle - pole_angle
    
    # PID controller
    dt = 0.04  # Time step
    
    # Integral term
    integral_error += error * dt
    
    # Derivative term
    if previous_time is not None:
        derivative_error = (error - previous_error) / dt
    else:
        derivative_error = 0.0
    
    # Compute control action
    action = Kp * error + Ki * integral_error + Kd * derivative_error
    
    # Clip action to valid range
    action = np.clip(action, -3.0, 3.0)
    
    # Update state for next iteration
    previous_error = error
    previous_time = 0.0  # We don't actually use time, but keep it for consistency
    
    return [action]
```