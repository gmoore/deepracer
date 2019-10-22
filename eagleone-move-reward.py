def reward_function(params):
    #
    # Reward being on the inside of the track
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
    is_left_of_center = params['is_left_of_center']
    
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
        reward += 0.8
    elif distance_from_center <= marker_2:
        reward += 0.3
    elif distance_from_center <= marker_3:
        reward += 0.02
    elif distance_from_center <= too_wide:
        reward -= 0.05
    else:
        reward -= 0.30
        
    #If the wheels are straight, reward speed.
    # Speed. I am speed.
    if abs(steering_angle < 5.0):
        reward += (speed / 50)

    # Let's check out some waypoints

    next_next_waypoint_index = closest_waypoints[1]+1
    if next_next_waypoint_index > (len(waypoints) - 1):
        next_next_waypoint_index = 0

    next_next_point = waypoints[next_next_waypoint_index]
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


    # SHAKE AND BAKE

    # track_direction is great, and it sort of tells us where the car should be sort of pointing
    # but it doesn't tell us where we should be RELATIVE TO THE TRACK. Also doesn't tell us
    # when the track curves etc... (could be on a straightaway but the heading is -145 degrees)
    # we want to be on the inside of the track when the track curves
    #
    # Plus, I know Cole. He always goes to the outside.
    #
    # Normalize our points around prev_point
    next_next_point = (next_next_point[0] - prev_point[0], next_next_point[1] - prev_point[1])
    next_point      = (next_point[0] - prev_point[0],next_point[1] - prev_point[1])
    prev_point      = (0,0)

    # Now that we have our next two points normalized around a third point, let's calculate
    # the angles to those two points
    #
    # atan2 gives us results in radians from pi to -pi
    # also note that atan2 is (y,x) not (x,y) which is infuriating
    prev_to_next        = math.atan2(next_point[1], next_point[0])
    prev_to_next_next   = math.atan2(next_next_point[1], next_next_point[0])

    # Convert that to degrees, 180 to -180
    prev_to_next        = math.degrees(prev_to_next)
    prev_to_next_next   = math.degrees(prev_to_next_next)

    # Then convert that to a 360 degree space
    prev_to_next        = prev_to_next % 360
    prev_to_next_next   = prev_to_next_next % 360

    # Calculate the distance between the angles, moving clockwise
    diff = ((prev_to_next_next - prev_to_next) % 360)

    # These numbers will only ever be in two quadrants of the space, (x,y) and (x,-y)
    # either 0-90 or 270-360
    # 0-90 means we're turning left, 270-360 means we're turning right
    # print("The diff is " + str(diff))

    if ((diff < 0.95) or (360-diff < 0.95)):
        # We should be in the middle. Reward the middle
        if distance_from_center <= marker_1:
            reward += 0.2
    elif (diff < 180):
        if (is_left_of_center) :
            reward += 0.2
    elif (diff > 180):
        if (not is_left_of_center) :
            reward += 0.2

    return float(reward)