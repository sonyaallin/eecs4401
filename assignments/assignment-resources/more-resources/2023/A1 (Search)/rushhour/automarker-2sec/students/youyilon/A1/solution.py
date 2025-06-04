#   Look for #IMPLEMENT tags in this file. These tags indicate what has
#   to be implemented to complete the Rush Hour domain.

#   You may add only standard python imports (numpy, itertools are both ok).
#   You may not remove any imports.
#   You may not import or otherwise source any of your own files.

import os  # you will likely want this for timing functions
import math  # for infinity
from search import *  # for search engines
from rushhour import *


def get_goal_vehicles(state):
    """
    Returns all goal vehicles in a parking state.

    @param state: a parking state.
    @return A list of goal vehicles.
    """
    goal_vehicles = []
    for vehicle in state.vehicle_list:
        if vehicle.is_goal:
            goal_vehicles.append(vehicle)
    return goal_vehicles


def get_tail_loc(vehicle, board_size):
    """
    Given a vehicle and the board size, find the coordinates of its tail, taking into account wraparound.

    @param vehicle: a Vehicle object
    @param board_size: a tuple (m, n) where m is the number of rows and n is the number of columns the board has.
    @return the tail coordinates (x, y) of the target vehicle.
    """
    if vehicle.is_horizontal:
        tail_loc = vehicle.loc[0] + vehicle.length - 1
        if tail_loc >= board_size[1]:
            tail_loc -= board_size[1]
        return tail_loc, vehicle.loc[1]
    else:
        tail_loc = vehicle.loc[1] + vehicle.length - 1
        if tail_loc >= board_size[0]:
            tail_loc -= board_size[0]
        return vehicle.loc[0], tail_loc


# RUSH HOUR GOAL TEST
def rushhour_goal_fn(state):
    # IMPLEMENT
    '''a Rush Hour Goal Test'''
    '''INPUT: a parking state'''
    '''OUTPUT: True, if satisfies the goal, else false.'''
    properties = state.board_properties
    # if the vehicle's north or west side needs to be on the goal, directly check whether they collide
    # since the vehicle's loc is the location of its north/west end.
    goal_vehicles = get_goal_vehicles(state)
    if properties[2] == 'N' or properties[2] == 'W':
        for goal_vehicle in goal_vehicles:
            if goal_vehicle.loc == properties[1]:
                return True
    # otherwise, check for whether the coordinates of the tail of the vehicle is the same as the goal.
    else:
        for goal_vehicle in goal_vehicles:
            tail_loc = get_tail_loc(goal_vehicle, properties[0])
            if tail_loc == properties[1]:
                return True
    return False


# RUSH HOUR HEURISTICS
def heur_alternate(state):
    # IMPLEMENT
    '''Only check for the least amount of steps needed for the car to reach the goal with the end that is required.
    For example, if the goal requires "S", only calculate the least number of steps it takes for the South end of
    goal vehicles to reach the goal.'''
    '''INPUT: a tokyo parking state'''
    '''OUTPUT: a numeric value that serves as an estimate of the distance of the state to the goal.'''
    # heur_min_moves has obvious flaws.
    # Write a heuristic function that improves upon heur_min_moves to estimate distance between the current state and the goal.
    # Your function should return a numeric value for the estimate of the distance to the goal.
    # EXPLAIN YOUR HEURISTIC IN THE COMMENTS. Please leave this function (and your explanation) at the top of your solution file, to facilitate marking.  
    properties = state.board_properties
    goal_vehicles = get_goal_vehicles(state)

    minimum = max(properties[0][0], properties[0][1])
    for goal_vehicle in goal_vehicles:
        if properties[2] == "N":
            moves1 = abs(properties[1][1] - goal_vehicle.loc[1])
            moves2 = properties[0][0] - moves1
        elif properties[2] == "W":
            moves1 = abs(properties[1][0] - goal_vehicle.loc[0])
            moves2 = properties[0][1] - moves1
        elif properties[2] == "S":
            tail_loc = get_tail_loc(goal_vehicle, properties[0])
            moves1 = abs(properties[1][1] - tail_loc[1])
            moves2 = properties[0][0] - moves1
        else:
            tail_loc = get_tail_loc(goal_vehicle, properties[0])
            moves1 = abs(properties[1][0] - tail_loc[0])
            moves2 = properties[0][1] - moves1

        smaller = min(moves1, moves2)
        if smaller < minimum:
            minimum = smaller
    return minimum


def heur_min_dist(state):
    # IMPLEMENT
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
    properties = state.board_properties
    goal_vehicles = get_goal_vehicles(state)

    minimum = max(properties[0][0], properties[0][1])

    for goal_vehicle in goal_vehicles:
        if goal_vehicle.is_horizontal:
            if goal_vehicle.loc[0] >= properties[1][0]:  # front of vehicle at east or on top of goal
                alt_goal_x = properties[1][0] + properties[0][1]  # coordinates of goal, wrapped around to the east
                moves1 = goal_vehicle.loc[0] - properties[1][0]  # west
                moves2 = alt_goal_x - (goal_vehicle.loc[0] + goal_vehicle.length - 1)  # east
            else:  # vehicle at west of goal
                # coordinates of vehicle, wrapped around to the east
                alt_vehicle_x = properties[0][1] + goal_vehicle.loc[0]
                moves1 = alt_vehicle_x - properties[1][0]  # west
                moves2 = properties[1][0] - (goal_vehicle.loc[0] + goal_vehicle.length - 1)  # east
        else:
            if goal_vehicle.loc[1] >= properties[1][1]:  # front of vehicle at south or on top of goal
                alt_goal_x = properties[1][1] + properties[0][0]  # coordinates of goal, wrapped around to the south
                moves1 = goal_vehicle.loc[1] - properties[1][1]  # north
                moves2 = alt_goal_x - (goal_vehicle.loc[1] + goal_vehicle.length - 1)  # south
            else:  # vehicle at north of goal
                # coordinates of vehicle, wrapped around to the south
                alt_vehicle_x = properties[0][0] + goal_vehicle.loc[1]
                moves1 = alt_vehicle_x - properties[1][1]  # north
                moves2 = properties[1][1] - (goal_vehicle.loc[1] + goal_vehicle.length - 1)  # south

        smaller = min(moves1, moves2)
        if smaller < minimum:
            minimum = smaller
    return minimum


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
    # IMPLEMENT
    """
    Another custom formula for f-value computation for Weighted A star.
    Returns the fval of the state contained in the sNode.
    XUP causes the best-first search to explore near-optimal paths near the end of a path.

    @param sNode sN: A search node (containing a RushHour State)
    @param float weight: Weight given by Weighted A star
    @rtype: float
    """
    return (1 / (2 * weight)) * (
                sN.gval + sN.hval + (math.sqrt((sN.gval + sN.hval) ** 2 + 4 * weight * (weight - 1) * (sN.hval) ** 2)))


def fval_function_XDP(sN, weight):
    # IMPLEMENT
    """
    A third custom formula for f-value computation for Weighted A star.
    Returns the fval of the state contained in the sNode.
    XDP causes the best-first search to explore near-optimal paths near the start of a path. 

    @param sNode sN: A search node (containing a RushHour State)
    @param float weight: Weight given by Weighted A star
    @rtype: float
    """
    return (1 / (2 * weight)) * (sN.gval + (2 * weight - 1) * sN.hval + math.sqrt((sN.gval - sN.hval) ** 2
                                                                                  + 4 * weight * sN.gval * sN.hval))



# SEARCH ALGORITHMS
def weighted_astar(initial_state, heur_fn, weight, timebound,
                   costbound=(float(math.inf), float(math.inf), float(math.inf))):
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
    se = SearchEngine("custom")
    se.init_search(initState=initial_state, goal_fn=lambda state: rushhour_goal_fn(state), heur_fn=heur_fn,
                   fval_function=lambda sN: fval_function(sN, weight))
    return se.search(timebound, costbound)


def iterative_astar(initial_state, heur_fn, weight=1,
                    timebound=5):  # uses f(n), see how autograder initializes a search
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
    se = SearchEngine(strategy="custom")
    weight_reduce_interval = 0.7
    costbound = [30, 30, 50]

    se.init_search(initial_state, lambda state: rushhour_goal_fn(state), heur_fn,
                   lambda sN: fval_function(sN, weight))
    result = se.search(timebound, costbound)

    while timebound > 0:
        weight *= weight_reduce_interval
        if weight <= 1:
            weight = 1
        if not result[0]:
            break

        for i in range(3):
            costbound[i] /= 2

        se.init_search(initial_state, lambda state: rushhour_goal_fn(state), heur_fn,
                       lambda sN: fval_function_XDP(sN, weight))
        timebound -= os.times()[0]
        if timebound <= 0:
            break
        temp_result = se.search(timebound, costbound)
        if temp_result[0] and temp_result[1].states_pruned_cost > result[1].states_pruned_cost:
            result = temp_result
    return result


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
    se = SearchEngine("best_first")
    se.init_search(initState=initial_state, goal_fn=lambda state: rushhour_goal_fn(state), heur_fn=heur_fn)
    result = se.search(timebound)
    while timebound > 0:
        timebound -= os.times()[0]
        if timebound <= 0:
            break
        temp_result = se.search(timebound, [result[0].gval, 999, 999])
        if temp_result[0] and temp_result[0].gval < result[0].gval:
            result = temp_result
    return result


# delete after done
def debug(s0):
    print("---------------------------------------------")
    print(s0.get_board_properties())
    for a in get_goal_vehicles(s0):
        print(a.loc, a.length)
    s0.print_state()
    print("---------------------------------------------")
