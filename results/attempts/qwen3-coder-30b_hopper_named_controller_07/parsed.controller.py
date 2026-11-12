import numpy as np

# PID controller parameters for each joint
# These were tuned to balance stability and forward velocity
Kp = [5.0, 5.0, 5.0]  # Proportional gains
Ki = [0.1, 0.1, 0.1]  # Integral gains
Kd = [2.0, 2.0, 2.0]  # Derivative gains

# Joint angle targets (desired angles)
target_angles = [0.0, 0.0, 0.0]

# PID integrator and derivative terms
integral = [0.0, 0.0, 0.0]
derivative = [0.0, 0.0, 0.0]

# Previous error for derivative calculation
previous_errors = [0.0, 0.0, 0.0]

def reset():
    global integral, derivative, previous_errors
    integral = [0.0, 0.0, 0.0]
    derivative = [0.0, 0.0, 0.0]
    previous_errors = [0.0, 0.0, 0.0]

def act(obs):
    global integral, derivative, previous_errors
    
    # Extract relevant observations
    torso_height = obs[0]
    torso_angle = obs[1]
    thigh_angle = obs[2]
    leg_angle = obs[3]
    foot_angle = obs[4]
    torso_x_vel = obs[5]
    
    # Joint angles and velocities
    joint_angles = [thigh_angle, leg_angle, foot_angle]
    joint_velocities = [obs[8], obs[9], obs[10]]
    
    # Set target angles for stability
    # The idea is to keep the robot upright and moving forward
    # Target angles are adjusted based on current state
    target_angles[0] = -torso_angle * 0.5  # Counteract torso tilt
    target_angles[1] = -torso_angle * 0.3  # Balance leg
    target_angles[2] = -torso_angle * 0.1  # Adjust foot
    
    # Simple proportional controller for forward motion
    # Try to maintain forward velocity by adjusting thigh joint
    target_vel = 2.0  # Target x-velocity
    vel_error = target_vel - torso_x_vel
    target_angles[0] += vel_error * 0.1
    
    # Calculate PID control for each joint
    actions = []
    for i in range(3):
        error = target_angles[i] - joint_angles[i]
        
        # Integral term
        integral[i] += error
        
        # Derivative term
        derivative[i] = error - previous_errors[i]
        previous_errors[i] = error
        
        # PID output
        action = Kp[i] * error + Ki[i] * integral[i] + Kd[i] * derivative[i]
        
        # Clip to valid range
        action = np.clip(action, -1.0, 1.0)
        actions.append(action)
    
    return actions
