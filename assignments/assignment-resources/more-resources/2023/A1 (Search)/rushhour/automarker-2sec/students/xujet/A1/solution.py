#   Look for #IMPLEMENT tags in this file. These tags indicate what has
#   to be implemented to complete the Rush Hour domain.

#   You may add only standard python imports (numpy, itertools are both ok).
#   You may not remove any imports.
#   You may not import or otherwise source any of your own files.

# HEURISTIC IMPLEMENTATION/EXPLANATION
# The heuristic function that I implemented takes into consideration the orientation of the goal direction, as well as
# the distances from either end of the vehicle to the goal entrance if you were to wrap around the board. For instance,
# If the goal orientation was 'N' but the goal entrance was south of the goal vehicle, then the function calculates the
# total number of moves from going to the top of the board, wrap around to the bottom, then continue until the north
# part of the vehicle touches the goal entrance. It will also consider just moving the car backwards until the north
# part of the vehicle touches the goal entrance. The function considers all of these possible scenarios, and takes the
# lowest cost of each distance and adds it to a list. Since there are multiple vehicles, the process continues for all
# goal vehicles. Then in the list, the lowest cost (or fewest number of moves to the goal) is returned.

import os  # you will likely want this for timing functions
import math # for infinity
from search import *  # for search engines
from rushhour import *

# RUSH HOUR GOAL TEST
def rushhour_goal_fn(state): 
    # IMPLEMENT
    '''a Rush Hour Goal Test'''
    '''INPUT: a parking state'''
    '''OUTPUT: True, if satisfies the goal, else false.'''
    if state is None:
        return False

    goal_vehicles = []
    for v in state.get_vehicle_statuses():
        if v[4]:
            goal_vehicles.append(v)

    satisfy = False

    bp = state.get_board_properties()

    board_dim = bp[0]
    true_board = (board_dim[1], board_dim[0])
    g_entrance = bp[1]
    g_direction = bp[2]

    for gv in goal_vehicles:

        #Get the front of the goal vehicle's location on the board

        vehicle_front_position = gv[1]

        if gv[3]:
            vehicle_back_position = (gv[1][0] + gv[2] - 1, gv[1][1])
            if vehicle_back_position[0] >= true_board[0]:
                vehicle_back_position = (gv[1][0] + gv[2] - 1 - true_board[0], gv[1][1])
        else:
            vehicle_back_position = (gv[1][0], gv[1][1] + gv[2] - 1)
            if vehicle_back_position[1] >= true_board[1]:
                vehicle_back_position = (gv[1][0], gv[1][1] + gv[2] - 1 - true_board[1])


        if vehicle_front_position == g_entrance or vehicle_back_position == g_entrance:
            satisfy = True

    return satisfy


# RUSH HOUR HEURISTICS
def heur_alternate(state):
    # IMPLEMENT
    '''a better heuristic'''
    '''INPUT: a tokyo parking state'''
    '''OUTPUT: a numeric value that serves as an estimate of the distance of the state to the goal.'''
    # heur_min_moves has obvious flaws.
    # Write a heuristic function that improves upon heur_min_moves to estimate distance between the current state and the goal.
    # Your function should return a numeric value for the estimate of the distance to the goal.
    # EXPLAIN YOUR HEURISTIC IN THE COMMENTS. Please leave this function (and your explanation) at the top of your solution file, to facilitate marking.  
    goal_vehicles = [] #EXPLANATION WILL BE AT THE TOP OF THE SUBMISSION
    other_vehicles = []
    for v in state.get_vehicle_statuses():
        if v[4]:
            goal_vehicles.append(v)
        else:
            other_vehicles.append(v)

    bp = state.get_board_properties()

    board_dim = bp[0] # Board dimensions
    true_board = (board_dim[1], board_dim[0]) #ACTUAL BOARD DIMENSIONS
    g_entrance = bp[1] # Goal entrance
    g_direction = bp[2] # Goal orientation (N, S, E, W)

    # gv_min_dist = [] MINIMUM DISTANCE
    gv_blocked_cars = []
    other_car_positions = [] # Get the positions of all the other cars on the board

    best_distance = [] # Closest distance of all goal vehicles to the goal entrance

    # VERY IMPORTANT: TRY COUNTING NUMBER OF BLOCKED CARS FROM THE GOAL VEHICLE AND THE POSITION
    for ov in other_vehicles:
        front_ov = ov[1]

        if ov[3]:
            back_ov = (ov[1][0] + ov[2] - 1, ov[1][1])
            if back_ov[0] >= true_board[0]:
                back_ov = (ov[1][0] + ov[2] - 1 - true_board[0], ov[1][1])
        else:
            back_ov = (ov[1][0], ov[1][1] + ov[2] - 1)
            if back_ov[1] >= true_board[1]:
                back_ov = (ov[1][0], ov[1][1] + ov[2] - 1 - true_board[1])

        other_car_positions.append((front_ov, back_ov, ov[3])) # The list contains a tuple with each vehicle's front and back positions

    for gv in goal_vehicles:
        obstacle_distance = 0
        dist_type = ''
        true_distance = 0 #Get closest distance between goal vehicle and goal entrance
        # GET FRONT AND BACK OF VEHICLE
        # ALSO GET COORDINATES OF BACK VEHICLE IF IT WRAPS AROUND BOARD
        front_vehicle = gv[1]

        if gv[3]:
            back_vehicle = (gv[1][0] + gv[2] - 1, gv[1][1])
            if back_vehicle[0] >= true_board[0]:
                back_vehicle = (gv[1][0] + gv[2] - 1 - true_board[0], gv[1][1])
        else:
            back_vehicle = (gv[1][0], gv[1][1] + gv[2] - 1)
            if back_vehicle[1] >= true_board[1]:
                back_vehicle = (gv[1][0], gv[1][1] + gv[2] - 1 - true_board[1])

        # GET THE DISTANCE WITHOUT OBSTACLES
        wd = wrap_around_dist(gv[3], g_direction, g_entrance, true_board, front_vehicle, back_vehicle)
        ed = 0
        if g_direction == 'N':
            ed = euclidean_distance(gv[3], g_entrance, front_vehicle)
            if g_entrance[1] > front_vehicle[1]: # N goal below the vehicle
                true_distance = wd # calculate distance when wrapping around the board
                dist_type = 'WRAP'
            elif g_entrance[1] <= front_vehicle[1]: # N goal is above the vehicle
                true_distance = ed # just get euclidean distance
                dist_type = 'EUCLID'
        elif g_direction == 'S':
            ed = euclidean_distance(gv[3], g_entrance, back_vehicle)
            if g_entrance[1] < back_vehicle[1]: # S goal is above the vehicle
                true_distance = wd
                dist_type = 'WRAP'
            elif g_entrance[1] >= back_vehicle[1]: # S goal is below the vehicle
                true_distance = ed
                dist_type = 'EUCLID'
        elif g_direction == 'W':
            ed = euclidean_distance(gv[3], g_entrance, front_vehicle)
            if g_entrance[0] > front_vehicle[0]: # W goal east of the vehicle
                true_distance = wd
                dist_type = 'WRAP'
            elif g_entrance[0] <= front_vehicle[0]: # W goal is west of the vehicle
                true_distance = ed
                dist_type = 'EUCLID'
        elif g_direction == 'E':
            ed = euclidean_distance(gv[3], g_entrance, back_vehicle)
            if g_entrance[0] < back_vehicle[0]: # E goal is west of the vehicle
                true_distance = wd
                dist_type = 'WRAP'
            elif g_entrance[0] >= back_vehicle[0]: # E goal is east of the vehicle
                true_distance = ed
                dist_type = 'EUCLID'

        # obstacle_distance = total_obs_distance(other_car_positions, dist_type, board_dim, g_entrance, g_direction, front_vehicle, back_vehicle)
        best_distance.append(true_distance + obstacle_distance)

    return min(best_distance) #REPLACE THIS!!

def euclidean_distance(is_horizontal, goal_entrance, gv_position):
    '''
    Return the euclidean distance between the goal entrance and any goal vehicle's position on the board, whether it
    be front or back of the vehicle.
    '''
    if is_horizontal:
        return abs(goal_entrance[0] - gv_position[0])
    else:
        return abs(goal_entrance[1] - gv_position[1])

def wrap_around_dist(is_horizontal, goal_direction, goal_entrance, true_board, gv_front, gv_back):
    '''
    Return the distance given the fact that the goal orientation is on the other side of the vehicle, so we must wrap
    around the board in order to touch the goal with the side of the vehicle that is initially supposed to touch it.
    '''
    wrap_dist = 0
    if is_horizontal:
        if goal_direction == 'W':
            wrap_dist = gv_front[0] + true_board[0] - goal_entrance[0]
        elif goal_direction == 'E':
            wrap_dist = true_board[0] - gv_back[0] + goal_entrance[0]
    else:
        if goal_direction == 'N':
            wrap_dist = gv_front[1] + true_board[1] - goal_entrance[1]
        elif goal_direction == 'S':
            wrap_dist = true_board[1] - gv_back[1] + goal_entrance[1]

    return wrap_dist

def total_obs_distance(other_car_positions, dist_type, board_dim, g_entrance, g_direction, gv_front, gv_back):
    all_obs_dist = 0
    ov_wrapped = False
    for ov in other_car_positions:
        ov_front = ov[0]
        ov_back = ov[1]
        ov_horizontal = ov[2]

        if ov_horizontal:
            if ov_back[0] < ov_front[0]: #This vehicle has wrapped around the board
                ov_wrapped = True

            if dist_type == 'WRAP' and g_direction == 'N': #The goal is wrapped around south of goal vehicle
                if ov_front[1] < gv_front[1] or ov_front[1] >= g_entrance[1]: #vehicle is leveled between front of vehicle and goal entrance
                    if ov_wrapped:
                        if ov_front[0] <= gv_front[0]: #front of obs vehicle is in the way of goal vehicle
                            all_obs_dist += abs(gv_front[0] - ov_front[0] + 1)
                        elif ov_back[0] >= gv_front[0]: #back of obs vehicle is in the way of goal vehicle
                            all_obs_dist += abs(gv_front[0] - ov_back[0] + 1)
                    else:
                        if ov_front[0] <= gv_front[0] <= ov_back[0]: #obs is not wrapped, so just find min distance from front goal vehicle to either end of obs
                            all_obs_dist += min(abs(gv_front[0] - ov_front[0] + 1), abs(gv_front[0] - ov_back[0] + 1))
            elif dist_type == 'EUCLID' and g_direction == 'N': #straight line distance between front vehicle and goal
                if g_entrance[1] <= ov_front[1] < gv_front[1]: # obstacle is leveled between goal and goal vehicle
                    if ov_wrapped:
                        if ov_front[0] <= gv_front[0]:
                            all_obs_dist += abs(gv_front[0] - ov_front[0] + 1)
                        elif ov_back[0] >= gv_front[0]:
                            all_obs_dist += abs(gv_front[0] - ov_back[0] + 1)
                    else:
                        if ov_front[0] <= gv_front[0] <= ov_back[0]:
                            all_obs_dist += min(abs(gv_front[0] - ov_front[0] + 1), abs(gv_front[0] - ov_back[0] + 1))
            elif dist_type == 'WRAP' and g_direction == 'S':
                if ov_front[1] > gv_front[1] or ov_front[1] <= g_entrance[1]: #leveled between
                    if ov_wrapped:
                        if ov_front[0] <= gv_back[0]:
                            all_obs_dist += abs(gv_back[0] - ov_front[0] + 1)
                        elif ov_back[0] >= gv_back[0]:
                            all_obs_dist += abs(gv_back[0] - ov_back[0] + 1)
                    else:
                        if ov_front[0] <= gv_back[0] <= ov_back[0]:
                            all_obs_dist += min(abs(gv_back[0] - ov_front[0] + 1), abs(gv_back[0] - ov_back[0] + 1))
            elif dist_type == 'EUCLID' and g_direction == 'S': # straight line distance between back of goal and goal entrance
                if gv_back[1] < ov_back[1] <= g_entrance[1]: #leveled between
                    if ov_wrapped:
                        if ov_front[0] <= gv_back[0]:
                            all_obs_dist += abs(gv_back[0] - ov_front[0] + 1)
                        elif ov_back[0] >= gv_back[0]:
                            all_obs_dist += abs(gv_back[0] - ov_back[0] + 1)
                    else:
                        if ov_front[0] <= gv_back[0] <= ov_back[0]:
                            all_obs_dist += min(abs(gv_back[0] - ov_front[0] + 1), abs(gv_back[0] - ov_back[0] + 1))
        else:
            if ov_back[1] < ov_front[1]:
                ov_wrapped = True

            if dist_type == 'WRAP' and g_direction == 'W': #The goal is wrapped around south of goal vehicle
                if ov_front[0] < gv_front[0] or ov_front[0] >= g_entrance[0]: #vehicle is leveled between front of vehicle and goal entrance
                    if ov_wrapped:
                        if ov_front[1] <= gv_front[1]: #front of obs vehicle is in the way of goal vehicle
                            all_obs_dist += abs(gv_front[1] - ov_front[1] + 1)
                        elif ov_back[0] >= gv_front[0]: #back of obs vehicle is in the way of goal vehicle
                            all_obs_dist += abs(gv_front[1] - ov_back[1] + 1)
                    else:
                        if ov_front[1] <= gv_front[1] <= ov_back[1]: #obs is not wrapped, so just find min distance from front goal vehicle to either end of obs
                            all_obs_dist += min(abs(gv_front[1] - ov_front[1] + 1), abs(gv_front[1] - ov_back[1] + 1))
            elif dist_type == 'EUCLID' and g_direction == 'W': #straight line distance between front vehicle and goal
                if g_entrance[0] <= ov_front[0] < gv_front[0]: # obstacle is leveled between goal and goal vehicle
                    if ov_wrapped:
                        if ov_front[1] <= gv_front[1]:
                            all_obs_dist += abs(gv_front[1] - ov_front[1] + 1)
                        elif ov_back[0] >= gv_front[1]:
                            all_obs_dist += abs(gv_front[1] - ov_back[1] + 1)
                    else:
                        if ov_front[1] <= gv_front[1] <= ov_back[1]:
                            all_obs_dist += min(abs(gv_front[1] - ov_front[1] + 1), abs(gv_front[1] - ov_back[1] + 1))
            elif dist_type == 'WRAP' and g_direction == 'E':
                if ov_front[0] > gv_front[0] or ov_front[0] <= g_entrance[0]: #leveled between
                    if ov_wrapped:
                        if ov_front[1] <= gv_back[1]:
                            all_obs_dist += abs(gv_back[1] - ov_front[1] + 1)
                        elif ov_back[1] >= gv_back[1]:
                            all_obs_dist += abs(gv_back[1] - ov_back[1] + 1)
                    else:
                        if ov_front[1] <= gv_back[1] <= ov_back[1]:
                            all_obs_dist += min(abs(gv_back[1] - ov_front[1] + 1), abs(gv_back[1] - ov_back[1] + 1))
            elif dist_type == 'EUCLID' and g_direction == 'E': # straight line distance between back of goal and goal entrance
                if gv_back[0] < ov_back[0] <= g_entrance[0]: #leveled between
                    if ov_wrapped:
                        if ov_front[1] <= gv_back[1]:
                            all_obs_dist += abs(gv_back[1] - ov_front[1] + 1)
                        elif ov_back[1] >= gv_back[1]:
                            all_obs_dist += abs(gv_back[1] - ov_back[1] + 1)
                    else:
                        if ov_front[1] <= gv_back[1] <= ov_back[1]:
                            all_obs_dist += min(abs(gv_back[1] - ov_front[1] + 1), abs(gv_back[1] - ov_back[1] + 1))

    return all_obs_dist

        # COPY AND PASTE THE IF STATEMENTS ABOVE, CHANGE ORIENTATIONS AND POSITIONS FOR W AND E

def heur_min_dist(state):
    #IMPLEMENT
    '''admissible tokyo parking puzzle heuristic'''
    '''INPUT: a tokyo parking state'''
    '''OUTPUT: a numeric value that serves as an estimate of the distance of the state to the goal.'''
    # We want an admissible heuristic, which is an optimistic heuristic.
    # It must never overestimate the cost to get from the current state to the goal.
    # Getting to the goal requires one move for each tile of distance.
    # Since the board wraps around, there will be two different directions that lead to a goal.
    # NOTE that we want an estimate of the number of moves required from our current state
    # 1. Proceeding in the first direction, let MOVES1 =
    #    number of moves required to get to the goal if it were unobstructed and if we ignore the orientation of the goal
    # 2. Proceeding in the second direction, let MOVES2 =
    #    number of moves required to get to the goal if it were unobstructed and if we ignore the orientation of the goal
    #
    # Our heuristic value is the minimum of MOVES1 and MOVES2 over all goal vehicles.
    # You should implement this heuristic function exactly, and you can improve upon it in your heur_alternate
    goal_vehicles = []
    for v in state.get_vehicle_statuses():
        if v[4]:
            goal_vehicles.append(v)

    bp = state.get_board_properties()

    board_dim = bp[0]
    true_board = (board_dim[1], board_dim[0])
    g_entrance = bp[1]
    g_direction = bp[2]

    gv_min_dist = []

    for gv in goal_vehicles:

        # GET FRONT AND BACK OF VEHICLE
        # ALSO GET COORDINATES OF BACK VEHICLE IF IT WRAPS AROUND BOARD
        front_vehicle = gv[1]

        if gv[3]:
            back_vehicle = (gv[1][0] + gv[2] - 1, gv[1][1])
            if back_vehicle[0] >= true_board[0]:
                back_vehicle = (gv[1][0] + gv[2] - 1 - true_board[0], gv[1][1])
        else:
            back_vehicle = (gv[1][0], gv[1][1] + gv[2] - 1)
            if back_vehicle[1] >= true_board[1]:
                back_vehicle = (gv[1][0], gv[1][1] + gv[2] - 1 - true_board[1])

        # CHECK ALL CONDITIONS TO DETERMINE MINIMUM DISTANCE
        temp_dist_front = 0
        temp_dist_back = 0
        dist_front_wrap = 0
        dist_back_wrap = 0

        true_dist = 0
        # ALTERNATE SOLUTION: JUST CALCULATE RELATIVE DISTANCE

        if gv[3]:
            temp_dist_front = abs(front_vehicle[0] - g_entrance[0])
            temp_dist_back = abs(back_vehicle[0] - g_entrance[0])
            if g_entrance[0] > front_vehicle[0]:
                dist_front_wrap = front_vehicle[0] + true_board[0] - g_entrance[0]
            if g_entrance[0] < back_vehicle[0]:
                dist_back_wrap = true_board[0] - back_vehicle[0] + g_entrance[0]

            if dist_front_wrap == 0 and dist_back_wrap != 0:
                true_dist = min(temp_dist_front, temp_dist_back, dist_back_wrap)
            elif dist_front_wrap != 0 and dist_back_wrap == 0:
                true_dist = min(temp_dist_front, temp_dist_back, dist_front_wrap)
            elif dist_front_wrap == 0 and dist_back_wrap == 0:
                true_dist = min(temp_dist_front, temp_dist_back)
            else:
                true_dist = min(temp_dist_front, temp_dist_back, dist_front_wrap, dist_back_wrap)
        else:
            temp_dist_front = abs(front_vehicle[1] - g_entrance[1])
            temp_dist_back = abs(back_vehicle[1] - g_entrance[1])
            if g_entrance[1] > front_vehicle[1]:
                dist_front_wrap = front_vehicle[1] + true_board[1] - g_entrance[1]
            if g_entrance[1] < back_vehicle[1]:
                dist_back_wrap = true_board[1] - back_vehicle[1] + g_entrance[1]

            if dist_front_wrap == 0 and dist_back_wrap != 0:
                true_dist = min(temp_dist_front, temp_dist_back, dist_back_wrap)
            elif dist_front_wrap != 0 and dist_back_wrap == 0:
                true_dist = min(temp_dist_front, temp_dist_back, dist_front_wrap)
            elif dist_front_wrap == 0 and dist_back_wrap == 0:
                true_dist = min(temp_dist_front, temp_dist_back)
            else:
                true_dist = min(temp_dist_front, temp_dist_back, dist_front_wrap, dist_back_wrap)

        # FIRST SOLUTION: CALCULATE MIN DISTANCE GIVEN THE FRONT AND BACK'S POSITIONS
        # gv_min_dist.append(min(temp_dist_front, temp_dist_back, dist_front_wrap, dist_back_wrap))
        gv_min_dist.append(true_dist)
        '''
        print(front_vehicle)
        print(back_vehicle)
        print(g_entrance)
        print(board_dim)
        print("Euclidean Distance from front: " + str(temp_dist_front))
        print("Wrapped Distance from front: " + str(dist_front_wrap))
        print("Euclidean Distance from back: " + str(temp_dist_back))
        print("Wrapped Distance from front: " + str(dist_back_wrap))
        '''

    return min(gv_min_dist)


def heur_zero(state):
    '''Zero Heuristic can be used to make A* search perform uniform cost search'''
    return 0

def fval_function(sN, weight):
    # IMPLEMENT
    """
    Provide a custom formula for f-value computation for Weighted A star.
    Returns the fval of the state contained in the sNode.

    @param sNode sN: A search node (containing a SokobanState)
    @param float weight: Weight given by Weighted A star
    @rtype: float
    """
    return sN.gval + weight * sN.hval

def fval_function_XUP(sN, weight):
    #IMPLEMENT
    """
    Another custom formula for f-value computation for Weighted A star.
    Returns the fval of the state contained in the sNode.
    XUP causes the best-first search to explore near-optimal paths near the end of a path.

    @param sNode sN: A search node (containing a RushHour State)
    @param float weight: Weight given by Weighted A star
    @rtype: float
    """
    first_part = sN.gval + sN.hval
    second_part = (sN.gval + sN.hval) ** 2
    third_part = 4 * weight * (weight-1) * sN.hval**2

    return (1 / (2 * weight)) * (first_part + math.sqrt(second_part + third_part))

def fval_function_XDP(sN, weight):
    #IMPLEMENT
    """
    A third custom formula for f-value computation for Weighted A star.
    Returns the fval of the state contained in the sNode.
    XDP causes the best-first search to explore near-optimal paths near the start of a path. 

    @param sNode sN: A search node (containing a RushHour State)
    @param float weight: Weight given by Weighted A star
    @rtype: float
    """
    first_part = sN.gval + (2 * weight - 1) * sN.hval
    second_part = (sN.gval - sN.hval) ** 2
    third_part = 4 * weight * sN.gval * sN.hval

    return (1 / (2 * weight)) * (first_part + math.sqrt(second_part + third_part))

# SEARCH ALGORITHMS
def weighted_astar(initial_state, heur_fn, weight, timebound, costbound = (float(math.inf), float(math.inf), float(math.inf))):
    # IMPLEMENT    
    """
    Provides an implementation of weighted a-star, as described in the HW1 handout'''
    INPUT: a rushhour state that represents the start state and a timebound (number of seconds)
    OUTPUT: A goal state (if a goal is found), else False as well as a SearchStats object
    implementation of weighted astar algorithm

    @param initial_state: A RushHour State
    @param heur_fn: The heuristic to use
    @param weight: The weight to use
    @param timebound: The timebound to enforce
    @param costbound: The costbound to enforce, if any
    @rtype: (Rushour State, SearchStats) if solution is found, else (False, SearchStats)
    """
    se = SearchEngine('custom', 'default')
    wrapped_fval_function = (lambda sN: fval_function(sN, weight))
    se.init_search(initial_state, rushhour_goal_fn, heur_fn, wrapped_fval_function)

    return se.search(timebound, costbound) #REPLACE THIS!!
    

def iterative_astar(initial_state, heur_fn, weight=1, timebound=5):  # uses f(n), see how autograder initializes a search
    # IMPLEMENT
    """
    Provides an implementation of iterative a-star, as described in the HW1 handout
    INPUT: a rushhour state that represents the start state and a timebound (number of seconds)
    OUTPUT: A goal state (if a goal is found), else False as well as a SearchStats object
    implementation of weighted astar algorithm
    
    @param initial_state: A RushHour State
    @param heur_fn: The heuristic to use
    @param weight: The weight to begin with during the first iteration (this should change)
    @param timebound: The timebound to enforce
    @rtype: (Rushour State, SearchStats) if solution is found, else (False, SearchStats)
    """
    se = SearchEngine('custom', 'default') #Instantiate search engine

    solutions = ()
    costbound = (10, 10, 10)
    while timebound > 0:
        wrapped_fval_function = (lambda sN: fval_function(sN, weight)) # Create a new fval everytime with different weight
        se.init_search(initial_state, rushhour_goal_fn, heur_fn, wrapped_fval_function) #start the search again
        start_time = os.times()[0]
        optimal_solution = se.search(timebound, costbound)
        end_time = os.times()[0]
        # costbound = (0, 0, optimal_solution[0].gval)
        solutions = optimal_solution
        timebound = timebound - (end_time - start_time)
        weight = weight/3

    return solutions #REPLACE THIS!!

def iterative_gbfs(initial_state, heur_fn, timebound=5):  # only use h(n)
    # IMPLEMENT
    """
    Provides an implementation of anytime greedy best-first search, as described in the HW1 handout
    INPUT: a rush hour state that represents the start state and a timebound (number of seconds)
    OUTPUT: A goal state (if a goal is found), else False

    @param initial_state: A RushHour State
    @param heur_fn: The heuristic to use
    @param timebound: The timebound to enforce
    @rtype: (Rushour State, SearchStats) if solution is found, else (False, SearchStats)
    """
    se = SearchEngine('best_first', 'default')
    solutions = ()
    costbound = (20, 20, 20)
    while timebound > 0:
        se.init_search(initial_state, rushhour_goal_fn, heur_fn)
        start_time = os.times()[0]
        optimal_solution = se.search(timebound, costbound)
        end_time = os.times()[0]
        solutions = optimal_solution
        timebound = timebound - (end_time - start_time)

    return solutions #REPLACE THIS!!

