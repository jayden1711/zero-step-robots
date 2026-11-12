import numpy as np

# PID controller parameters for each joint
# These values were tuned to balance stability and forward velocity
Kp = [50.0, 50.0, 50.0]  # Proportional gains
Ki = [10.0, 10.0, 10.0]  # Integral gains  
Kd = [5.0, 5.0, 5.0]     # Derivative gains

# State for PID controllers
integral_errors = [0.0, 0.0, 0.0]
previous_errors = [0.0, 0.0, 0.0]

def reset():
    global integral_errors, previous_errors
    integral_errors = [0.0, 0.0, 0.0]
    previous_errors = [0.0, 0.0, 0.0]

def act(obs):
    # Extract relevant observations
    height = obs[0]           # torso height
    torso_angle = obs[1]      # torso angle
    thigh_angle = obs[2]      # thigh joint angle  
    leg_angle = obs[3]        # leg joint angle
    foot_angle = obs[4]       # foot joint angle
    x_vel = obs[5]            # torso x-velocity
    
    # Target angles for stable hopping (these are empirically determined)
    # The goal is to maintain forward motion while keeping the robot upright
    target_thigh_angle = -0.3  # Slight backward bend
    target_leg_angle = 0.0     # Straight down
    target_foot_angle = 0.0    # Flat
    
    # Compute errors for each joint
    error_thigh = target_thigh_angle - thigh_angle
    error_leg = target_leg_angle - leg_angle  
    error_foot = target_foot_angle - foot_angle
    
    # Update integral and derivative terms
    global integral_errors, previous_errors
    
    integral_errors[0] += error_thigh
    integral_errors[1] += error_leg
    integral_errors[2] += error_foot
    
    derivative_thigh = error_thigh - previous_errors[0]
    derivative_leg = error_leg - previous_errors[1]
    derivative_foot = error_foot - previous_errors[2]
    
    # Update previous errors
    previous_errors[0] = error_thigh
    previous_errors[1] = error_leg
    previous_errors[2] = error_foot
    
    # Apply PID control to compute torques
    torque_thigh = Kp[0] * error_thigh + Ki[0] * integral_errors[0] + Kd[0] * derivative_thigh
    torque_leg = Kp[1] * error_leg + Ki[1] * integral_errors[1] + Kd[1] * derivative_leg
    torque_foot = Kp[2] * error_foot + Ki[2] * integral_errors[2] + Kd[2] * derivative_foot
    
    # Clip torques to valid range [-1, 1]
    action = [
        np.clip(torque_thigh, -1.0, 1.0),
        np.clip(torque_leg, -1.0, 1.0),
        np.clip(torque_foot, -1.0, 1.0)
    ]
    
    return action
