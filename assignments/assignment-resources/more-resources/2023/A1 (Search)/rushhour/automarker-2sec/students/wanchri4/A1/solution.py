#   Look for #IMPLEMENT tags in this file. These tags indicate what has
#   to be implemented to complete the Rush Hour domain.

#   You may add only standard python imports (numpy, itertools are both ok).
#   You may not remove any imports.
#   You may not import or otherwise source any of your own files.

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
    board_size, goal_entrance, goal_direction = state.board_properties
    goal_x, goal_y = goal_entrance
    # get the vehicle that is the goal vehicle and has the correct orientation
    for vehicle in state.vehicle_list:
        if vehicle.is_goal and ((not vehicle.is_horizontal and goal_direction in ['N', 'S'])
                                or (vehicle.is_horizontal and goal_direction in ['W', 'E'])):

            vehicle_x, vehicle_y = vehicle.loc
            return goal_x == vehicle_x or goal_y == vehicle_y

    return False

# RUSH HOUR HEURISTICS


def get_manhattan_distance(point1, point2):
    return math.fabs(point1[0] - point2[0]) + math.fabs(point1[1] - point2[1])


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

    # my idea for the heuristic is to assume there are no obstacles and just assume the best/optimal path
    # from a goal vehicle to the goal and take the shortest path out of all possible goal vehicles

    board_size, goal_entrance, goal_direction = state.board_properties
    shortest_dist, shortest_vehicle = math.inf, None

    for vehicle in state.vehicle_list:
        if vehicle.is_goal:
            # calculate distance of wrapping around
            x = math.fabs(vehicle.loc[1] - goal_entrance[1])
            y = math.fabs(vehicle.loc[0] - goal_entrance[0])
            dx = x if x < (board_size[0] / 2) else board_size[0] - x
            dy = y if y < (board_size[1]/2) else board_size[1] - y
            dist2 = math.sqrt((dx * dx) + (dy * dy))

            # calculate manhattan distance
            dist1 = get_manhattan_distance(vehicle.loc, goal_entrance)

            shortest_dist = min(shortest_dist, dist1, dist2)

            # determine if the current vehicle has the smallest distance
            if dist1 <= shortest_dist and dist1 < dist2:
                shortest_vehicle = vehicle

            if dist2 <= shortest_dist and dist2 < dist1:
                shortest_vehicle = vehicle

    # have to consider the length of the vehicle once getting the shortest distance
    if shortest_vehicle:
        if (shortest_vehicle.is_horizontal and (goal_direction in ["W", "E"])) \
                or ((not shortest_vehicle.is_horizontal) and (goal_direction in ["N", "S"])):
            return 0 if shortest_vehicle.length > shortest_dist else shortest_dist

    return shortest_dist


def heur_alternate(state):
    # IMPLEMENT
    '''a better heuristic'''
    '''INPUT: a tokyo parking state'''
    '''OUTPUT: a numeric value that serves as an estimate of the distance of the state to the goal.'''
    # heur_min_moves has obvious flaws.
    # Write a heuristic function that improves upon heur_min_moves to estimate distance between the current state and the goal.
    # Your function should return a numeric value for the estimate of the distance to the goal.
    # EXPLAIN YOUR HEURISTIC IN THE COMMENTS. Please leave this function (and your explanation) at the top of your solution file, to facilitate marking.

    board_size, goal_entrance, goal_direction = state.board_properties

    goal_vehicle = []
    # If the orientation of the goal vehicle are not similar to the orientation of the goal remove it from the list
    for vehicle in state.vehicle_list:
        if vehicle.is_goal and ((not vehicle.is_horizontal and goal_direction in ['N', 'S'])
                                or (vehicle.is_horizontal and goal_direction in ['W', 'E'])):
            goal_vehicle.append(vehicle)

    # if the list is empty return infinity because there is no vehicles that can reach the goal
    if not goal_vehicle:
        return math.inf

    shortest_dist, shortest_vehicle = math.inf, None

    for vehicle in goal_vehicle:
        # calculate distance of wrap
        x = math.fabs(vehicle.loc[1] - goal_entrance[1])
        y = math.fabs(vehicle.loc[0] - goal_entrance[0])
        dx = x if x < (board_size[0] / 2) else board_size[0] - x
        dy = y if y < (board_size[1] / 2) else board_size[1] - y
        dist2 = math.sqrt((dx * dx) + (dy * dy))

        # calculate manhattan distance
        dist1 = get_manhattan_distance(vehicle.loc, goal_entrance)

        shortest_dist = min(shortest_dist, dist1, dist2)

        # determine if the current vehicle is the smallest distance
        if dist1 <= shortest_dist and dist1 < dist2:
            shortest_vehicle = vehicle

        if dist2 <= shortest_dist and dist2 < dist1:
            shortest_vehicle = vehicle

    # have to consider the length of the vehicle once getting the shortest distance
    if shortest_vehicle:
        if (shortest_vehicle.is_horizontal and (goal_direction in ["W", "E"])) \
                or ((not shortest_vehicle.is_horizontal) and (goal_direction in ["N", "S"])):
            return 0 if shortest_vehicle.length > shortest_dist else shortest_dist

    return shortest_dist


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
    # from handout
    return sN.gval + (weight * sN.hval)


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
    half_weight = 1 / (2 * weight)
    valueFromSquareRoot = math.sqrt(math.pow(sN.gval + sN.hval, 2) + 4*weight*(weight - 1)*math.pow(sN.hval, 2))
    addition = sN.gval + sN.hval
    return half_weight * (valueFromSquareRoot + addition)


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
    half_weight = 1 / (2 * weight)
    valueFromSquareRoot = math.sqrt(math.pow(sN.gval - sN.hval, 2) + 4*weight*sN.gval*sN.hval)
    addition = sN.gval + (2*weight - 1) * sN.hval
    return half_weight * (valueFromSquareRoot + addition)


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
    # ignore the costbound

    # Engine initializer
    engine = SearchEngine('custom', 'full')
    engine.init_search(initial_state, rushhour_goal_fn, heur_fn, (lambda sN: fval_function(sN, weight)))

    result = engine.search(timebound, costbound)

    return result
    

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
    # Since we will have found a path to the goal after our first search iteration, we can use this solution to help
    # guide our search in subsequent iterations.  More specifically, we can introduce a cost bound for pruning
    # nodes in future iterations: if any node we generate has a g(node)+h(node) value greater than the cost
    # of the best path to the goal found so far, we can prune it.

    # Engine initializer
    engine = SearchEngine('custom', 'full')
    engine.init_search(initial_state, rushhour_goal_fn, heur_fn, (lambda sN: fval_function(sN, weight)))

    # Iterative Weighted A* continues to search until either there are no nodes left to expand
    # (and our best solution is the optimal one) or it runs out of time
    best_path, status = engine.search(timebound)

    # Initialize start time and total time - need to subtract the time it took to perform first search
    remaining_time = timebound - os.times()[0]

    curr = best_path

    if best_path:
        while remaining_time > 0:
            # reduce the weight after each iteration - reducing it by half
            weight = weight * 0.5

            # reduce the weight with an attempt towards finding a better path after already finding a solution
            # perform search
            new_path, new_status = engine.search(remaining_time, (float("inf"), float("inf"), curr.gval + (heur_fn(curr) * weight)))

            # remove the amount of time the search took
            remaining_time -= os.times()[0]

            # set the new best path
            if new_path:
                best_path, status = new_path, new_status
                curr = new_path

    return best_path, status


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
    # Engine initializer
    engine = SearchEngine('best_first', 'full')
    engine.init_search(initial_state, rushhour_goal_fn, heur_fn,)

    time_remaining = timebound
    cost_bound = float("inf")

    # perform the first search
    best_path, status = engine.search(time_remaining, (cost_bound, float("inf"), float("inf")))

    g_val = best_path.gval

    time_remaining -= os.times()[0]

    while time_remaining > 0:

        # perform an new search given the previous gval
        new_path, new_status = engine.search(time_remaining, (g_val, float("inf"), float("inf")))

        if new_path:
            best_path, status = new_path, new_status
            g_val = new_path.gval

        time_remaining -= os.times()[0]

    return best_path, status
    # greedy best-first search expands nodes with lowest h(node) first


    # if a node has g(node) greater than the best path to the goal found so far, we can prune it


    # The algorithm returns either when we have expanded all non-pruned nodes, in which case the best solution found by
    # the algorithm is the optimal solution, or when it runs out of time. We will prune based
    # on the g-value of the node only because greedy best-ﬁrst search is not necessarily run with an admissible heuristic
