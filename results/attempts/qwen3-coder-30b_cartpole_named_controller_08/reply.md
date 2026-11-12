```python
import numpy as np

# PID controller parameters
Kp = 50.0
Ki = 10.0
Kd = 5.0

# Integral and derivative terms
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
    
    # Extract observations
    cart_pos, pole_angle, cart_vel, pole_ang_vel = obs
    
    # Target is to keep the pole upright (angle = 0)
    target_angle = 0.0
    error = target_angle - pole_angle
    
    # PID control
    global integral, derivative, previous_error
    
    # Proportional term
    proportional = Kp * error
    
    # Integral term
    integral += Ki * error
    # Anti-windup: limit integral term
    integral = np.clip(integral, -10.0, 10.0)
    
    # Derivative term
    derivative = Kd * (error - previous_error)
    previous_error = error
    
    # Compute action
    action = proportional + integral + derivative
    
    # Clip action to allowed range
    action = np.clip(action, -3.0, 3.0)
    
    return [action]
```