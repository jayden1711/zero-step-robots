import numpy as np

# PID controller parameters for each joint
# These values were tuned to balance stability and forward velocity
Kp = [5.0, 5.0, 5.0]   # Proportional gains
Ki = [0.1, 0.1, 0.1]   # Integral gains  
Kd = [1.0, 1.0, 1.0]   # Derivative gains

# Joint angle targets (in radians)
target_angles = [0.0, 0.0, 0.0]

# State for PID controllers
integral_errors = [0.0, 0.0, 0.0]
previous_errors = [0.0, 0.0, 0.0]

def reset():
    global integral_errors, previous_errors
    integral_errors = [0.0, 0.0, 0.0]
    previous_errors = [0.0, 0.0, 0.0]

def act(obs):
    global integral_errors, previous_errors
    
    # Extract relevant observations
    torso_height = obs[0]
    torso_angle = obs[1]
    thigh_angle = obs[2]
    leg_angle = obs[3] 
    foot_angle = obs[4]
    torso_x_vel = obs[5]
    
    # Adjust target angles based on posture to maintain balance
    # When torso is tilted forward, we want to move the joints to counteract
    target_angles[0] = -torso_angle * 0.5  # Thigh angle proportional to torso tilt
    target_angles[1] = -torso_angle * 0.3  # Leg angle 
    target_angles[2] = -torso_angle * 0.2  # Foot angle
    
    # Get current joint angles
    current_angles = [thigh_angle, leg_angle, foot_angle]
    
    # Calculate action using PID control for each joint
    actions = []
    for i in range(3):
        error = target_angles[i] - current_angles[i]
        
        # PID calculation
        integral_errors[i] += error
        derivative = error - previous_errors[i]
        
        # Apply PID with gains
        action = Kp[i] * error + Ki[i] * integral_errors[i] + Kd[i] * derivative
        
        # Clip to valid range
        action = np.clip(action, -1.0, 1.0)
        
        # Store previous error for next iteration
        previous_errors[i] = error
        
        actions.append(action)
    
    # Add some forward bias to encourage movement in x-direction
    actions[0] += 0.2 * torso_x_vel  # Bias thigh joint based on forward velocity
    
    return actions
