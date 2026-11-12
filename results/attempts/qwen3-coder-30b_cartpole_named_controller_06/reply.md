```python
import numpy as np

# PID controller parameters
Kp = 50.0
Ki = 10.0
Kd = 5.0

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
    
    # Time step (0.04 seconds)
    dt = 0.04
    
    # Update integral term
    integral += error * dt
    
    # Calculate derivative term
    if prev_time is not None:
        derivative = (error - prev_error) / dt
    else:
        derivative = 0.0
    
    # PID control law
    action = Kp * error + Ki * integral + Kd * derivative
    
    # Clip action to [-3, 3]
    action = np.clip(action, -3.0, 3.0)
    
    # Update for next iteration
    prev_error = error
    prev_time = dt
    
    return [action]
```