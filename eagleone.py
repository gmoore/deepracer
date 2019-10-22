def reward_function(params):
    #
    # Using waypoints to judge based on heading
    # 

    import math
    
    # Read input parameters
    track_width = params['track_width']
    distance_from_center = params['distance_from_center']
    all_wheels_on_track = params['all_wheels_on_track']
    progress = params['progress']
    speed = params['speed']
    steering_angle = params['steering_angle']    
    waypoints = params['waypoints']
    closest_waypoints = params['closest_waypoints']
    heading = params['heading']
    
    reward = 0.0
    
    reward += (speed / 50)
    
    if all_wheels_on_track:
        reward += 0.01
    
    # Calculate 3 markers that are at varying distances away from the center line
    marker_1 = 0.1 * track_width
    marker_2 = 0.25 * track_width
    marker_3 = 0.5 * track_width
    too_wide = 0.7 * track_width
    
    # Give higher reward if the car is closer to center line and vice versa
    if distance_from_center <= marker_1:
        reward += (1.0 + (progress / 100))
    elif distance_from_center <= marker_2:
        reward += 0.3
    elif distance_from_center <= marker_3:
        reward += 0.02
    elif distance_from_center <= too_wide:
        reward -= 0.05
    else:
        reward -= 0.30
        
    #If the wheels are straight, reward speed.
    if abs(steering_angle < 5.0):
        reward += (speed / 50)

    # Let's check out some waypoints
    next_point = waypoints[closest_waypoints[1]]
    prev_point = waypoints[closest_waypoints[0]]
    
    # Never, ever thought I'd use arctan ever again
    # Ripped from: https://docs.aws.amazon.com/deepracer/latest/developerguide/deepracer-reward-function-input.html#reward-function-input-closest_waypoints

    track_direction = math.atan2(next_point[1] - prev_point[1], next_point[0] - prev_point[0]) 

    # Convert to degree
    track_direction = math.degrees(track_direction)

    # Calculate the difference between the track direction and the heading direction of the car
    direction_diff = abs(track_direction - heading)
    if direction_diff > 180:
        direction_diff = 360 - direction_diff

    # Penalize the reward if the difference is too large
    DIRECTION_THRESHOLD = 10.0
    if direction_diff > DIRECTION_THRESHOLD:
        reward *= 0.5

    return reward

    return float(reward)