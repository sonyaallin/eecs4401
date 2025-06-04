#   Look for #IMPLEMENT tags in this file. These tags indicate what has
#   to be implemented to complete the Rush Hour domain.

#   You may add only standard python imports (numpy, itertools are both ok).
#   You may not remove any imports.
#   You may not import or otherwise source any of your own files.

# Explanation for my heuristics:
# I basically took my heur_min_dist and acounted for orientation. In my heur_min_dist, I considered moving both the "head" of the car and the "tail"
# of the car onto the goal location. I also did not consider the car's orientation with respect to the goal's orientation (ie, I did not consider that 
# N means car needs to be vertical.) In heur_alternate, I put those factors into consideration.
# 1. The vehicle's orientation must match the orientation of the goal. (ie, N/S and vertical or E/W and horizontal)
# 2a. If the goal orientation is N or W, the "head" of the car (the one that vehicle.loc is pointed to) needs to be on the goal.
# 2b. If the goal orientation is S or E, the "tail" of the car (the coordinate of the car that is furthest away from head) needs to be on the goal.

import os  # you will likely want this for timing functions
import math # for infinity
from search import *  # for search engines
from rushhour import *

# RUSH HOUR GOAL TEST
def rushhour_goal_fn(state): 
    '''a Rush Hour Goal Test'''
    '''INPUT: a parking state'''
    '''OUTPUT: True, if satisfies the goal, else false.'''

    board_state = state.get_board_properties()
    (board_y, board_x) = board_state[0]
    goal = (board_state[1], board_state[2])
    for vehicle in state.vehicle_list:
        if vehicle.is_goal:
            win_condition = set()
            x, y = vehicle.loc[0], vehicle.loc[1]
            if vehicle.is_horizontal:
                win_condition.add(((x, y), 'W'))
                win_condition.add((((x + vehicle.length - 1) % board_x, y), 'E'))
            else:
                win_condition.add(((x, y), 'N'))
                win_condition.add(((x, (y + vehicle.length - 1) % board_y), 'S'))
            if goal in win_condition:
                return True
    return False

# RUSH HOUR HEURISTICS
def heur_alternate(state):
    '''a better heuristic'''
    '''INPUT: a tokyo parking state'''
    '''OUTPUT: a numeric value that serves as an estimate of the distance of the state to the goal.'''
    # heur_min_moves has obvious flaws.
    # Write a heuristic function that improves upon heur_min_moves to estimate distance between the current state and the goal.
    # Your function should return a numeric value for the estimate of the distance to the goal.
    # EXPLAIN YOUR HEURISTIC IN THE COMMENTS. Please leave this function (and your explanation) at the top of your solution file, to facilitate marking.  

    (board_y, board_x), (goal_x, goal_y), orientation = state.get_board_properties()
    goal_distances = set()

    for vehicle in state.vehicle_list:
        if vehicle.is_goal:
            x, y = vehicle.loc
            head = (x, y)
            tail = ((x + vehicle.length - 1) % board_x, y) if vehicle.is_horizontal else (x, (y + vehicle.length - 1) % board_y)

            # check if vehicle lines up with the goal location
            if vehicle.is_horizontal and (orientation == 'N' or orientation == 'S'):
                continue
            elif (not vehicle.is_horizontal) and (orientation == 'W' or orientation == 'E'):
                continue

            if vehicle.is_horizontal:
                if orientation == 'W':
                    euclid_dist_head = abs(goal_x - head[0])
                    head_dist = min(euclid_dist_head, board_x - euclid_dist_head)
                    goal_distances.add(head_dist)
                else:
                    euclid_dist_tail = abs(goal_x - tail[0])
                    tail_dist = min(euclid_dist_tail, board_x - euclid_dist_tail)
                    goal_distances.add(tail_dist)
            else:
                if orientation == 'N':
                    euclid_dist_head = abs(goal_y - head[1])
                    head_dist = min(euclid_dist_head, board_y - euclid_dist_head)
                    goal_distances.add(head_dist)
                else:
                    euclid_dist_tail = abs(goal_y - tail[1])
                    tail_dist = min(euclid_dist_tail, board_y - euclid_dist_tail)
                    goal_distances.add(tail_dist)
    return min(goal_distances)

def heur_min_dist(state):
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

    (board_y, board_x), (goal_x, goal_y), orientation = state.get_board_properties()
    goal_distances = set()

    for vehicle in state.vehicle_list:
        if vehicle.is_goal:
            x, y = vehicle.loc
            head = (x, y)
            tail = ((x + vehicle.length - 1) % board_x, y) if vehicle.is_horizontal else (x, (y + vehicle.length - 1) % board_y)

            # check if vehicle lines up with the goal location
            if vehicle.is_horizontal and (goal_y != head[1]):
                continue
            elif (not vehicle.is_horizontal) and (goal_x != head[0]):
                continue

            if vehicle.is_horizontal:
                # check if goal is "in" the vehicle, if yes then return 0
                tail_x_no_boundary = x + vehicle.length - 1
                if tail_x_no_boundary >= board_x:
                    if (head[0] <= goal_x) or (goal_x <= tail[0]):
                        return 0
                else:
                    if (head[0] <= goal_x) and (goal_x <= tail[0]):
                        return 0
                euclid_dist_head = abs(goal_x - head[0])
                head_dist = min(euclid_dist_head, board_x - euclid_dist_head)
                euclid_dist_tail = abs(goal_x - tail[0])
                tail_dist = min(euclid_dist_tail, board_x - euclid_dist_tail)
                goal_distances.add(min(head_dist, tail_dist))
            else:
                # check if goal is "in" the vehicle, if yes then return 0
                tail_y_no_boundary = y + vehicle.length - 1
                if tail_y_no_boundary >= board_y:
                    if (head[1] <= goal_y) or (goal_y <= tail[1]):
                        return 0
                else:
                    if (head[1] <= goal_y) and (goal_y <= tail[1]):
                        return 0
                euclid_dist_head = abs(goal_y - head[1])
                head_dist = min(euclid_dist_head, board_y - euclid_dist_head)
                euclid_dist_tail = abs(goal_y - tail[1])
                tail_dist = min(euclid_dist_tail, board_y - euclid_dist_tail)
                goal_distances.add(min(head_dist, tail_dist))
    return min(goal_distances)

def heur_zero(state):
    '''Zero Heuristic can be used to make A* search perform uniform cost search'''
    return 0

def fval_function(sN, weight):
    """
    Provide a custom formula for f-value computation for Weighted A star.
    Returns the fval of the state contained in the sNode.

    @param sNode sN: A search node (containing a SokobanState)
    @param float weight: Weight given by Weighted A star
    @rtype: float
    """
    return sN.gval + weight * sN.hval

def fval_function_XUP(sN, weight):
    """
    Another custom formula for f-value computation for Weighted A star.
    Returns the fval of the state contained in the sNode.
    XUP causes the best-first search to explore near-optimal paths near the end of a path.

    @param sNode sN: A search node (containing a RushHour State)
    @param float weight: Weight given by Weighted A star
    @rtype: float
    """
    return (1/(2 * weight)) * (sN.gval + sN.hval + math.sqrt((sN.gval + sN.hval)**2 + 4 * weight * (weight - 1) * sN.hval**2))

def fval_function_XDP(sN, weight):
    """
    A third custom formula for f-value computation for Weighted A star.
    Returns the fval of the state contained in the sNode.
    XDP causes the best-first search to explore near-optimal paths near the start of a path. 

    @param sNode sN: A search node (containing a RushHour State)
    @param float weight: Weight given by Weighted A star
    @rtype: float
    """
    return (1/(2 * weight)) * (sN.gval + (2 * weight - 1) * sN.hval + math.sqrt((sN.gval - sN.hval)**2 + 4 * weight * sN.gval * sN.hval))

# SEARCH ALGORITHMS
def weighted_astar(initial_state, heur_fn, weight, timebound, costbound = (float(math.inf), float(math.inf), float(math.inf))):
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
    def fval_with_weight(sN):
        return fval_function(sN, weight)
    se = SearchEngine('custom', 'full')
    se.init_search(initial_state, goal_fn=rushhour_goal_fn, heur_fn=heur_fn, fval_function=fval_with_weight)
    final, stats = se.search(timebound, costbound)
    return final, stats
    
def iterative_astar(initial_state, heur_fn, weight=1, timebound=5):  # uses f(n), see how autograder initializes a search
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
    curr_cost = math.inf
    prev_final = False
    prev_stats = None
    while weight >= 1:
        if timebound <= 0:
            break
        call_time = os.times()[0]
        final, stats = weighted_astar(initial_state, heur_fn, weight, timebound, costbound = (float(math.inf), float(math.inf), curr_cost))
        finish_time = os.times()[0]
        if (not final):
            break
        if final.gval < curr_cost:
            curr_cost = final.gval
            prev_final = final
            prev_stats = stats
        weight = weight * 0.7 # subject to change
        timebound -= finish_time - call_time
    return prev_final, prev_stats

def iterative_gbfs(initial_state, heur_fn, timebound=5):  # only use h(n)
    """
    Provides an implementation of anytime greedy best-first search, as described in the HW1 handout
    INPUT: a rush hour state that represents the start state and a timebound (number of seconds)
    OUTPUT: A goal state (if a goal is found), else False

    @param initial_state: A RushHour State
    @param heur_fn: The heuristic to use
    @param timebound: The timebound to enforce
    @rtype: (Rushour State, SearchStats) if solution is found, else (False, SearchStats)
    """    
    curr_cost = math.inf
    prev_final = False
    prev_stats = None
    while timebound > 0:
        se = SearchEngine('best_first', 'full')
        se.init_search(initial_state, goal_fn=rushhour_goal_fn, heur_fn=heur_fn)
        call_time = os.times()[0]
        final, stats = se.search(timebound, costbound = (curr_cost, float(math.inf), float(math.inf)))
        finish_time = os.times()[0]
        if final:
            if final.gval < curr_cost:
                curr_cost = final.gval
                prev_final = final
                prev_stats = stats
        if prev_final == False:
            prev_stats = stats
        timebound -= finish_time - call_time
    return prev_final, prev_stats

