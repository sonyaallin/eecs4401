#   Look for #IMPLEMENT tags in this file. These tags indicate what has
#   to be implemented to complete the warehouse domain.

#   You may add only standard python imports
#   You may not remove any imports.
#   You may not import or otherwise source any of your own files

import os  # for time functions
import math  # for infinity
from search import *  # for search engines
from sokoban import sokoban_goal_state, SokobanState, Direction, PROBLEMS  # for Sokoban specific classes and problems

# SOKOBAN HEURISTICS
def heur_alternate(state):
    # IMPLEMENT
    '''a better heuristic'''
    '''INPUT: a sokoban state'''
    '''OUTPUT: a numeric value that serves as an estimate of the distance of the state to the goal.'''
    # heur_manhattan_distance has flaws.
    # Write a heuristic function that improves upon heur_manhattan_distance to estimate distance between the current state and the goal.
    # Your function should return a numeric value for the estimate of the distance to the goal.
    # EXPLAIN YOUR HEURISTIC IN THE COMMENTS. Please leave this function (and your explanation) at the top of your solution file, to facilitate marking.
    total = 0
    # Determine which storages are currently filled with a box
    occupied = [False] * len(state.storage)
    for b in state.boxes:
        occupied.append(b in state.storage)

    for box in state.boxes:
        if box in state.storage:
            continue

        # Find the closest unoccupied storage space for the box
        closest_s = math.inf
        s_i = 0
        for s in state.storage:
            if not occupied[s_i]:           # Boxes should only be able to enter unoccupied storage spaces
                distance = abs(box[0] - s[0]) + abs(box[1] - s[1])
                if distance < closest_s:
                    closest_s = distance
            s_i += 1
        total += closest_s

        # Find the closest robot and distance of it from the box and add that to estimate
        closest_r = math.inf
        r_i = 0
        for r in state.robots:
            distance = abs(box[0] - r[0]) + abs(box[1] - r[1]) - 1
            if distance < closest_r:
                closest_r = distance
            r_i += 1
        total += closest_r

    return total

# Another failed addition to the heuristic. This function was detecting obstacles directly around the box
# and the main heuristic function would return inf if the box was stuck in a corner
def against_obstacle(state, box):
    # Return True,True if the box is in a corner, one True if the box is up against an obstacle or another box
    # or return all False if the box is surrounded by open space or robots
    x,y = box
    left = (x - 1, y)
    right = (x + 1, y)
    up = (x, y + 1)
    down = (x, y - 1)

    if box[0] != 0 or box[0] != state.width - 1:
        stuck_x = left in state.obstacles or left in state.boxes or right in state.obstacles or right in state.boxes
    else:
        stuck_x = True

    if box[1] != 0 or box[1] != state.height - 1:
        stuck_y = up in state.obstacles or up in state.boxes or down in state.obstacles or down in state.boxes
    else:
        stuck_y = True

    return stuck_x,stuck_y

# This function reduced the solved puzzles so I could not use it in the heuristic
def robot_to_box(storage_loc, box, robot_loc):
    # Find the distance the robot must move to reach the correct position beside
    # a box such that it can be pushed towards a storage space
    total = 0
    if storage_loc[0] > box[0]:
        total += abs(robot_loc[0] - box[0] - 1) + abs(robot_loc[1] - box[1])
        # For adjusting the robot position to fix the box y position after fixing the x position
        if storage_loc[1] != box[1]:
            total += 2
    elif storage_loc[0] < box[0]:
        total += abs(robot_loc[0] - box[0] + 1) + abs(robot_loc[1] - box[1])
        if storage_loc[1] != box[1]:
            total += 2
    # Only calculated if the x position of the box is already correct
    elif storage_loc[1] > box[1]:
        total += abs(robot_loc[0] - box[0]) + abs(robot_loc[1] - box[1] - 1)
    elif storage_loc[1] < box[1]:
        total += abs(robot_loc[0] - box[0]) + abs(robot_loc[1] - box[1] + 1)
    return total

def heur_zero(state):
    '''Zero Heuristic can be used to make A* search perform uniform cost search'''
    return 0

def heur_manhattan_distance(state):
    '''admissible sokoban puzzle heuristic: manhattan distance'''
    '''INPUT: a sokoban state'''
    '''OUTPUT: a numeric value that serves as an estimate of the distance of the state to the goal.'''
    # We want an admissible heuristic, which is an optimistic heuristic.
    # It must never overestimate the cost to get from the current state to the goal.
    # The sum of the Manhattan distances between each box that has yet to be stored and the storage point nearest to it is such a heuristic.
    # When calculating distances, assume there are no obstacles on the grid.
    # You should implement this heuristic function exactly, even if it is tempting to improve it.
    # Your function should return a numeric value; this is the estimate of the distance to the goal.
    total = 0
    for box in state.boxes:
        if box in state.storage:
            continue

        closest_s = math.inf
        for s in state.storage:
            distance = abs(box[0] - s[0]) + abs(box[1] - s[1])
            if distance < closest_s:
                closest_s = distance

        total += closest_s
    return total

def fval_function(sN, weight):
    """
    Provide a custom formula for f-value computation for Anytime Weighted A star.
    Returns the fval of the state contained in the sNode.

    @param sNode sN: A search node (containing a SokobanState)
    @param float weight: Weight given by Anytime Weighted A star
    @rtype: float
    """
    weight_h = weight * sN.hval
    return sN.gval + weight_h

# SEARCH ALGORITHMS
def weighted_astar(initial_state, heur_fn, weight, timebound):
    '''Provides an implementation of weighted a-star, as described in the HW1 handout'''
    '''INPUT: a sokoban state that represents the start state and a timebound (number of seconds)'''
    '''OUTPUT: A goal state (if a goal is found), else False as well as a SearchStats object'''
    '''implementation of weighted astar algorithm'''
    wrapped_fval_function = (lambda sN: fval_function(sN, weight))

    search_eng = SearchEngine(strategy='custom')
    search_eng.init_search(initial_state, sokoban_goal_state, heur_fn, wrapped_fval_function)
    return search_eng.search(timebound=timebound)

def iterative_astar(initial_state, heur_fn, weight=1, timebound=5):  # uses f(n), see how autograder initializes a search line 88
    '''Provides an implementation of realtime a-star, as described in the HW1 handout'''
    '''INPUT: a sokoban state that represents the start state and a timebound (number of seconds)'''
    '''OUTPUT: A goal state (if a goal is found), else False as well as a SearchStats object'''
    '''implementation of iterative astar algorithm'''
    end_time = os.times()[0] + timebound
    curr_weight = weight
    search_eng = SearchEngine(strategy='custom')
    costbound = (math.inf, math.inf, math.inf)
    sol, stats = False, None

    while os.times()[0] < end_time:
        wrapped_fval_function = (lambda sN: fval_function(sN, curr_weight))
        search_eng.init_search(initial_state, sokoban_goal_state, heur_fn, wrapped_fval_function)
        new_sol, new_stats = search_eng.search(timebound=end_time - os.times()[0], costbound=costbound)

        if new_sol and (not sol or new_sol.gval < sol.gval):
            sol = new_sol
            stats = new_stats
            costbound = (math.inf, math.inf, sol.gval)
            curr_weight = curr_weight * 0.8

    return sol, stats

def iterative_gbfs(initial_state, heur_fn, timebound=5):  # only use h(n)
    '''Provides an implementation of anytime greedy best-first search, as described in the HW1 handout'''
    '''INPUT: a sokoban state that represents the start state and a timebound (number of seconds)'''
    '''OUTPUT: A goal state (if a goal is found), else False'''
    '''implementation of iterative gbfs algorithm'''
    end_time = os.times()[0] + timebound
    search_eng = SearchEngine(strategy='best_first')
    costbound = (math.inf, math.inf, math.inf)
    sol, stats = False, None

    while os.times()[0] < end_time:
        search_eng.init_search(initial_state, sokoban_goal_state, heur_fn)
        new_sol, new_stats = search_eng.search(timebound=end_time - os.times()[0], costbound=costbound)

        if new_sol and (not sol or new_sol.gval < sol.gval):
            sol = new_sol
            stats = new_stats
            costbound = (sol.gval, math.inf, math.inf)

    return sol, stats



