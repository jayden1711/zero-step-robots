```python
import numpy as np

# PID controller parameters
Kp = 50.0
Ki = 10.0
Kd = 5.0

# Integrator and derivative terms
integral = 0.0
derivative = 0.0
prev_error = 0.0

def reset():
    global integral, derivative, prev_error
    integral = 0.0
    derivative = 0.0
    prev_error = 0.0

def act(obs):
    global integral, derivative, prev_error
    
    # Extract observations
    cart_pos, pole_angle, cart_vel, pole_ang_vel = obs
    
    # Target angle is 0 (vertical)
    target_angle = 0.0
    
    # Calculate error
    error = target_angle - pole_angle
    
    # Update integral term
    integral += error * 0.04  # dt = 0.04
    
    # Update derivative term
    derivative = (error - prev_error) / 0.04
    
    # PID control law
    action = Kp * error + Ki * integral + Kd * derivative
    
    # Clip action to [-3, 3]
    action = np.clip(action, -3.0, 3.0)
    
    # Update previous error for next iteration
    prev_error = error
    
    return [action]
```