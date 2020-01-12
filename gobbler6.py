# Gobbler-6

def reward_function(params):
    #
    # Reward being on the inside of the track
    # 

    # Math is hard
    import math
    
    # define speeds
    # These need to be changed if the action space changes with respect to top speed
    top_speed = 9
    top_cornering_speed = 5

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

    #Weights
    distance_weight         = 0.19
    speed_straight_weight   = 0.12
    wheel_angle_weight      = 0.16
    waypoint_angle_weight   = 0.16
    sharp_turn_weight       = 0.10
    progress_weight         = 0.04
    speed_weight            = 0.04
    all_wheels_weight       = 0.19

    #Rewards. These get updated as we go
    distance_reward         = 0.0
    speed_straight_reward   = 0.0
    sharp_turn_reward       = 0.0
    wheel_angle_reward      = 0.0
    waypoint_angle_reward   = 0.0
    progress_reward         = 0.0
    speed_reward            = 0.0
    all_wheels_reward       = 0.0


    reward = 0.0
    
    ################################
    # SPEED
    #
    speed_reward = (speed / top_speed)
    

    ################################
    # all wheels on track
    #
    # If we're not on the track, return 0. We're done here
    if all_wheels_on_track:
        all_wheels_reward = 1.0
    else:
        return 0.0
    
    ################################
    # DISTANCE REWARD
    #
    # We will return 0 reward if we are too wide.
    # No use in rewarding a good behavior if we're driving off the track

    # Calculate 3 markers that are at varying distances away from the center line
    marker_1 = 0.1 * track_width
    marker_2 = 0.25 * track_width
    marker_3 = 0.5 * track_width
    too_wide = 0.9 * track_width
    
    # Give higher reward if the car is closer to center line and vice versa
    if distance_from_center <= marker_1:
        distance_reward = 1.0
    elif distance_from_center <= marker_2:
        distance_reward = 0.3
    elif distance_from_center <= marker_3:
        distance_reward = 0.1
    else:
        return 0.0
        
    ################################
    # WHEEL ANGLE REWARD
    #

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

    DIRECTION_THRESHOLD = 5.0
    if direction_diff > DIRECTION_THRESHOLD:
        wheel_angle_reward = 1.0

    ################################
    # WAYPOINT ANGLE REWARD
    #

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
            waypoint_angle_reward = 1.0
    elif (diff < 180):
        if (is_left_of_center) :
            waypoint_angle_reward = 1.0
    elif (diff > 180):
        if (not is_left_of_center) :
            waypoint_angle_reward = 1.0

    #####################################
    # 
    # REWARD PRUDENCE AROUND SHARP CORNERS
    #
    if (diff > 45 and diff < 90) or (diff > 225 and diff < 270):
        if(speed < 3):
            sharp_turn_reward = 1.0



    #####################################
    # PUT IT ALL TOGETHER
    #
    #  We want to reward the following:
    #   if the track is straight
    #   and the wheels are lined up right
    #   and we're going fast
    #   then that's good
    #

    track_is_straight = (diff < 0.95) or (360-diff < 0.95)
    wheels_lined_up_right = direction_diff > DIRECTION_THRESHOLD
    going_fast = speed > top_cornering_speed


    if track_is_straight and wheels_lined_up_right and going_fast:
        speed_straight_reward = speed / top_speed

    reward += distance_reward * distance_weight
    reward += speed_straight_reward * speed_straight_weight
    reward += sharp_turn_reward * sharp_turn_weight
    reward += wheel_angle_reward * wheel_angle_weight
    reward += waypoint_angle_reward * waypoint_angle_weight
    reward += progress_reward * progress_weight
    reward += speed_reward * speed_weight
    reward += all_wheels_reward * all_wheels_weight

    return float(reward)