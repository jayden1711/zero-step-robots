```python
import numpy as np

# PID controller parameters for each joint
# These values were tuned to balance stability and forward velocity
Kp_thigh = 20.0
Ki_thigh = 0.1
Kd_thigh = 5.0

Kp_leg = 25.0
Ki_leg = 0.15
Kd_leg = 6.0

Kp_foot = 15.0
Ki_foot = 0.05
Kd_foot = 3.0

# Integration terms for PID controllers
int_thigh = 0.0
int_leg = 0.0
int_foot = 0.0

# Previous errors for derivative term
prev_error_thigh = 0.0
prev_error_leg = 0.0
prev_error_foot = 0.0

def reset():
    global int_thigh, int_leg, int_foot, prev_error_thigh, prev_error_leg, prev_error_foot
    int_thigh = 0.0
    int_leg = 0.0
    int_foot = 0.0
    prev_error_thigh = 0.0
    prev_error_leg = 0.0
    prev_error_foot = 0.0

def act(obs):
    global int_thigh, int_leg, int_foot, prev_error_thigh, prev_error_leg, prev_error_foot
    
    # Extract relevant observations
    height = obs[0]
    torso_angle = obs[1]
    thigh_angle = obs[2]
    leg_angle = obs[3]
    foot_angle = obs[4]
    torso_x_vel = obs[5]
    
    # Desired angles (target positions for joints)
    # The goal is to keep the robot upright and moving forward
    desired_thigh_angle = -0.3 * torso_angle  # Counteract tilt
    desired_leg_angle = 0.0  # Keep leg relatively straight
    desired_foot_angle = 0.0  # Keep foot flat
    
    # Calculate errors
    error_thigh = desired_thigh_angle - thigh_angle
    error_leg = desired_leg_angle - leg_angle
    error_foot = desired_foot_angle - foot_angle
    
    # Update integral terms (with anti-windup)
    int_thigh += error_thigh
    int_leg += error_leg
    int_foot += error_foot
    
    # Clamp integrals to prevent windup
    int_thigh = np.clip(int_thigh, -10.0, 10.0)
    int_leg = np.clip(int_leg, -10.0, 10.0)
    int_foot = np.clip(int_foot, -10.0, 10.0)
    
    # Calculate derivative terms
    deriv_thigh = error_thigh - prev_error_thigh
    deriv_leg = error_leg - prev_error_leg
    deriv_foot = error_foot - prev_error_foot
    
    # Update previous errors
    prev_error_thigh = error_thigh
    prev_error_leg = error_leg
    prev_error_foot = error_foot
    
    # Compute control signals using PID
    torque_thigh = Kp_thigh * error_thigh + Ki_thigh * int_thigh + Kd_thigh * deriv_thigh
    torque_leg = Kp_leg * error_leg + Ki_leg * int_leg + Kd_leg * deriv_leg
    torque_foot = Kp_foot * error_foot + Ki_foot * int_foot + Kd_foot * deriv_foot
    
    # Clip torques to valid range [-1, 1]
    action = [
        np.clip(torque_thigh, -1.0, 1.0),
        np.clip(torque_leg, -1.0, 1.0),
        np.clip(torque_foot, -1.0, 1.0)
    ]
    
    return action
```