#   Look for #IMPLEMENT tags in this file. These tags indicate what has
#   to be implemented to complete the Rush Hour domain.

#   You may add only standard python imports (numpy, itertools are both ok).
#   You may not remove any imports.
#   You may not import or otherwise source any of your own files.

import os  # you will likely want this for timing functions
import math # for infinity
# import numpy as np
from search import *  # for search engines
from rushhour import *

"""
Our heuristic begins by determining the direction of the goal, and designate the coordinate of the goal vehicle
i.e if goal pointing west, we want the x value of our head coordinate
or if goal pointing south, we want the y value of our tail coordinate (head plus length)

Next we will check the two paths from our relevant coordinate to the goal coordinate,
the direct path, and the wrap-around path, marked inner and outer respectively.

All of this is to return a direction dependent shortest path from vehicle to goal, and the interval between them.

We then use a helper function, and detect all vehicles that are within/out that interval, that are also obstructing the goal vehicle.
If we do find one, find the two distances from the obstruction point to each end of the vehicle, and find the smallest
number of moves to clear the path.
We do this for every vehicle, and their moves estimates are combined with the shortest distance, to fianlly get our heuristic.
"""

# RUSH HOUR GOAL TEST
def rushhour_goal_fn(state: Rushhour): 
    # IMPLEMENT
    '''a Rush Hour Goal Test'''
    '''INPUT: a parking state'''
    '''OUTPUT: True, if satisfies the goal, else false.'''
    prop = state.get_board_properties()
    goal_vehicle_index = list(filter((lambda v: v[4]), state.get_vehicle_statuses()))
    
    board_dim = prop[0]
    goal_coord = prop[1]
    goal_dir = prop[2]
    
    
    if ( goal_dir == 'N') or (goal_dir == 'W'):
        for vehicle in goal_vehicle_index:
            if (vehicle[3] and goal_dir == 'W') or (not vehicle[3] and goal_dir == 'N'):
                if vehicle[1] == goal_coord:
                    return True
        return False

    else:
        if (goal_dir == 'E'):
            for vehicle in goal_vehicle_index:
                vehicle_x = vehicle[1][0] + vehicle[2]-1
                if vehicle_x >= board_dim[0]:
                    vehicle_x = 0
                if (vehicle[3] and goal_dir == 'E') and ((vehicle_x, vehicle[1][1]) == goal_coord):
                    return True

        else:
            for vehicle in goal_vehicle_index:
                vehicle_y = vehicle[1][1] + vehicle[2]-1
                if vehicle_y >= board_dim[1]:
                    vehicle_y = 0
                if (not vehicle[3] and goal_dir == 'S') and (vehicle[1][0], vehicle_y) == goal_coord:
                    return True
                
        return False
    
# RUSH HOUR HEURISTICS
def heur_alternate(state: Rushhour):
    # IMPLEMENT
    '''a better heuristic'''
    '''INPUT: a tokyo parking state'''
    '''OUTPUT: a numeric value that serves as an estimate of the distance of the state to the goal.'''
    # heur_min_moves has obvious flaws.
    # Write a heuristic function that improves upon heur_min_moves to estimate distance between the current state and the goal.
    # Your function should return a numeric value for the estimate of the distance to the goal.
    # EXPLAIN YOUR HEURISTIC IN THE COMMENTS. Please leave this function (and your explanation) at the top of your solution file, to facilitate marking.
    prop = state.get_board_properties()
    board_dims = prop[0]
    goal_coord = prop[1]
    goal_dir = prop[2]
    vehicles = state.get_vehicle_statuses()
    goal_vehicle_index = list(filter((lambda v: v[4]), vehicles))

    distance = float(math.inf)
    interval = None
    
    if (goal_dir == 'N') or (goal_dir == 'S'):
        dim = 1
    else:
        dim = 0
    
    for vehicle in goal_vehicle_index:
        
        x, y = vehicle[1]
        
        length = vehicle[2] - 1
        
        if (goal_dir == 'N'):
            relevant_car_coord = y
        elif (goal_dir == 'W'):
            relevant_car_coord = x
        elif (goal_dir == 'S'):
            relevant_car_coord = y + length
        else:
            relevant_car_coord = x + length
            
        goal_dim = goal_coord[dim]
        board_dim = board_dims[1 - dim]
        
        distance = float(math.inf)
            
        if goal_dim < relevant_car_coord:
            inner_distance = (relevant_car_coord - goal_dim)
            outer_distance = ((board_dim - relevant_car_coord) + goal_dim)
        elif goal_dim > relevant_car_coord:
            inner_distance = (goal_dim - relevant_car_coord)
            outer_distance = ((board_dim - goal_dim) + relevant_car_coord)
        else:
            return 0
            
        if inner_distance < outer_distance:
    
            new_distance = inner_distance
        else:
            new_distance = outer_distance
            
        if new_distance < distance:
            if (goal_dir == 'S') or (goal_dir == 'E'):
                interval = (min(relevant_car_coord + 1, goal_dim), max(relevant_car_coord - vehicle[2], goal_dim))
            else:
                interval = (min(relevant_car_coord + vehicle[2], goal_dim), max(relevant_car_coord - 1, goal_dim))
            distance = new_distance
            if inner_distance < outer_distance:
                detect = 'inner'
            else:
                detect = 'outer'
            
        if dim == 0:
            horizontal = True
        else:
            horizontal = False
 
    obstructing_count = map((lambda v: check_vehicle_obstruct(v, interval, detect, horizontal, goal_coord[1-dim], board_dims[dim])), vehicles)
    return distance + sum(obstructing_count) #REPLACE THIS!!


def check_vehicle_obstruct(vehicle, interval, detect, horizontal, alt_axis, alt_board_dim):
    if horizontal:
        dim = 0
    else:
        dim = 1
    
    if (not vehicle[4]) and (vehicle[3] != horizontal):
        if ((detect == 'inner') and (interval[0] <= vehicle[1][dim] <= interval[1])) or ((detect == 'outer') and ((vehicle[1][dim] <= interval[0]) or (vehicle[1][dim] >= interval[1]))):
            head_coord = vehicle[1][1-dim]
            tail_coord = (vehicle[1][1-dim] + (vehicle[2] - 1)) % (alt_board_dim)
            
            if (head_coord <= tail_coord) and (head_coord <= alt_axis <= tail_coord):
                return min(alt_axis - (head_coord - 1), tail_coord - (alt_axis - 1))
            elif (head_coord > tail_coord) and (((tail_coord >= alt_axis) and (alt_axis < head_coord)) or ((alt_axis >= head_coord) and (tail_coord < alt_axis))):
                if (tail_coord >= alt_axis):
                    return min(tail_coord - (alt_axis - 1), vehicle[2] - (tail_coord - (alt_axis)))
                elif (alt_axis >= head_coord):
                    return min(alt_axis - (head_coord - 1), vehicle[2] - (alt_axis - (head_coord)))
            else:
                return 0
    return 0

def heur_min_dist(state: Rushhour):
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
    
    prop = state.get_board_properties()
    board_dims = prop[0]
    goal_coord = prop[1]
    goal_vehicle_index = list(filter((lambda v: v[4]), state.get_vehicle_statuses()))
    distance = float(math.inf)
    
    for vehicle in goal_vehicle_index:
        if vehicle[3]:
            dim = 0
        else:
            dim = 1
        
        goal_dim = goal_coord[dim]
        vehicle_dim = vehicle[1][dim]
        vehicle_length = vehicle[2] - 1
        board_dim = board_dims[1 - dim]
        if goal_dim < vehicle_dim:
            new_distance = min((vehicle_dim - goal_dim), ((board_dim - (vehicle_dim + vehicle_length)) + goal_dim))
        elif goal_dim > (vehicle_dim + vehicle_length):
            new_distance = min((goal_dim - (vehicle_dim + vehicle_length)), ((board_dim - goal_dim) + vehicle_dim))
        else:
            new_distance = min((goal_dim - vehicle_dim), ((vehicle_dim + vehicle_length) - goal_dim))
            
        if new_distance < distance:
            distance = new_distance
            
    return distance       

def heur_zero(state):
    '''Zero Heuristic can be used to make A* search perform uniform cost search'''
    return 0

def fval_function(sN: sNode, weight):
    # IMPLEMENT
    """
    Provide a custom formula for f-value computation for Weighted A star.
    Returns the fval of the state contained in the sNode.

    @param sNode sN: A search node (containing a SokobanState)
    @param float weight: Weight given by Weighted A star
    @rtype: float
    """
    return sN.gval + (weight * sN.hval)

def fval_function_XUP(sN: sNode, weight):
    #IMPLEMENT
    """
    Another custom formula for f-value computation for Weighted A star.
    Returns the fval of the state contained in the sNode.
    XUP causes the best-first search to explore near-optimal paths near the end of a path.

    @param sNode sN: A search node (containing a RushHour State)
    @param float weight: Weight given by Weighted A star
    @rtype: float
    """
    return (1/(2 * weight)) * (sN.gval + sN.hval + math.sqrt(((sN.gval + sN.hval) ** 2) + (4 * weight * (weight - 1) * (sN.hval ** 2))))

def fval_function_XDP(sN: sNode, weight):
    #IMPLEMENT
    """
    A third custom formula for f-value computation for Weighted A star.
    Returns the fval of the state contained in the sNode.
    XDP causes the best-first search to explore near-optimal paths near the start of a path. 

    @param sNode sN: A search node (containing a RushHour State)
    @param float weight: Weight given by Weighted A star
    @rtype: float
    """
    return (1/(2 * weight)) * (sN.gval + (((2 * weight) - 1) * sN.hval) + math.sqrt(((sN.gval - sN.hval) ** 2) + 4 * weight * sN.gval * sN.hval))

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
    search_engine = SearchEngine('custom')
    search_engine.init_search(initial_state, rushhour_goal_fn, heur_fn, (lambda sN: fval_function(sN,weight)))
    return search_engine.search(timebound)
    #REPLACE THIS!!
    

def iterative_astar(initial_state, heur_fn, weight=2.5, timebound=5):  # uses f(n), see how autograder initializes a search
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
    time_elapsed = 0
    curr_weight = weight
    final_stats = None
    cost_bound = None
    best_path = False
    
    while (time_elapsed <= timebound) and (curr_weight >= 0):
        
        final, stats = weighted_astar(initial_state, heur_fn, curr_weight, (timebound - time_elapsed), cost_bound)
        
        if final:
            if isinstance(best_path, Rushhour) and final.gval < best_path.gval:
                best_path = final
            elif best_path == False:
                best_path = final
            cost_bound = (float(math.inf), float(math.inf), best_path.gval)
        
        final_stats = stats
        time_elapsed += stats.total_time
        curr_weight -= 2 * (0.1 * curr_weight)
        
        
    return best_path, final_stats #REPLACE THIS!!

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
    time_elapsed = 0
    final_stats = None
    cost_bound = None
    best_path = False
    search_engine = SearchEngine('best_first')
    
    while (time_elapsed <= timebound):
        
        search_engine.init_search(initial_state, rushhour_goal_fn, heur_fn)
        final, stats = search_engine.search((timebound - time_elapsed), cost_bound)
        
        if final:
            if isinstance(best_path, Rushhour) and final.gval < best_path.gval:
                best_path = final
            elif best_path == False:
                best_path = final
            cost_bound = (best_path.gval, float(math.inf), float(math.inf))
        
        final_stats = stats
        time_elapsed += stats.total_time
    
    return best_path, final_stats #REPLACE THIS!!

