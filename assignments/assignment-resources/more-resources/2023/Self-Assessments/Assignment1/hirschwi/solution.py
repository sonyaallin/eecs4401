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
    '''a better heuristic'''
    '''INPUT: a sokoban state'''
    '''OUTPUT: a numeric value that serves as an estimate of the distance of the state to the goal.'''
    # heur_manhattan_distance has flaws.
    # Write a heuristic function that improves upon heur_manhattan_distance to estimate distance between the current state and the goal.
    # Your function should return a numeric value for the estimate of the distance to the goal.
    # EXPLAIN YOUR HEURISTIC IN THE COMMENTS. Please leave this function (and your explanation) at the top of your solution file, to facilitate marking.
    # First Goal: Manhattan distance, where each storage space can only accept 1 box.
    # Boxes are paired with the closest free storage space, in order of the closest box to any space to the furthest box from any space
    # In the event of a tie, the winner is chosen based on position in the list, with earlier positions having priority

    distance_sum = 0

    # These two lines give us two lists, featuring the boxes not in storage spaces and the spaces without boxes.
    open_storage = [space for space in state.storage if space not in state.boxes]
    free_boxes = [box for box in state.boxes if box not in state.storage]

    while(free_boxes and open_storage): # For security if the number of spaces and boxes are different, we continue while there are any left
        closest_box = 0  # Index of the box closest to a storage space
        closest_space = 0
        closest_distance = math.inf

        for box in free_boxes:
            for space in open_storage:
                curr_dist = abs(box[0] - space[0]) + abs(box[1] - space[1])
                if curr_dist < closest_distance:
                    closest_box = box
                    closest_space = space
                    closest_distance = curr_dist

        free_boxes.remove(closest_box)
        open_storage.remove(closest_space)
        distance_sum += closest_distance

    return distance_sum

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
    distance_sum = 0
    for box in state.boxes:
        distance_sum += min([abs(box[0] - space[0]) + abs(box[1] - space[1]) for space in state.storage])
    return distance_sum

def fval_function(sN, weight):
    """
    Provide a custom formula for f-value computation for Anytime Weighted A star.
    Returns the fval of the state contained in the sNode.

    @param sNode sN: A search node (containing a SokobanState)
    @param float weight: Weight given by Anytime Weighted A star
    @rtype: float
    """
    return sN.gval + weight * sN.hval

# SEARCH ALGORITHMS
def weighted_astar(initial_state, heur_fn, weight, timebound):
    '''Provides an implementation of weighted a-star, as described in the HW1 handout'''
    '''INPUT: a sokoban state that represents the start state and a timebound (number of seconds)'''
    '''OUTPUT: A goal state (if a goal is found), else False as well as a SearchStats object'''
    '''implementation of weighted astar algorithm'''
    wrapped_fval_function = (lambda sN: fval_function(sN, weight))

    se = SearchEngine('custom', 'full')
    se.init_search(initial_state, sokoban_goal_state, heur_fn, wrapped_fval_function)

    return se.search(timebound)

def iterative_astar(initial_state, heur_fn, weight=1, timebound=5):  # uses f(n), see how autograder initializes a search line 88
    '''Provides an implementation of realtime a-star, as described in the HW1 handout'''
    '''INPUT: a sokoban state that represents the start state and a timebound (number of seconds)'''
    '''OUTPUT: A goal state (if a goal is found), else False as well as a SearchStats object'''
    '''implementation of iterative astar algorithm'''

    start = os.times()[0]
    curr = start
    gval = math.inf
    path = False
    stats = None
    while (timebound - (curr - start)) > 0:
        wrapped_fval_function = (lambda sN: fval_function(sN, weight))
        se = SearchEngine('custom', 'full')
        se.init_search(initial_state, sokoban_goal_state, heur_fn, wrapped_fval_function)
        path_tmp, stats_tmp = se.search(timebound - (curr - start), (math.inf, math.inf, gval))
        if path_tmp:
            path, stats = path_tmp, stats_tmp
            gval = path.gval
            weight = weight // 2                # Halve weight every iteration
        curr = os.times()[0]

    if not stats:
        stats = stats_tmp

    return path, stats

def iterative_gbfs(initial_state, heur_fn, timebound=5):  # only use h(n)
    '''Provides an implementation of anytime greedy best-first search, as described in the HW1 handout'''
    '''INPUT: a sokoban state that represents the start state and a timebound (number of seconds)'''
    '''OUTPUT: A goal state (if a goal is found), else False'''
    '''implementation of iterative gbfs algorithm'''

    start = os.times()[0]
    curr = start
    gval = math.inf
    path = False
    stats = None
    while (timebound - (curr - start)) > 0:
        se = SearchEngine('best_first', 'full')
        se.init_search(initial_state, sokoban_goal_state, heur_fn)
        path_tmp, stats_tmp = se.search(timebound - (curr - start), (gval, math.inf, math.inf))
        if path_tmp:
            path, stats = path_tmp, stats_tmp
            gval = path.gval
        curr = os.times()[0]

    if not stats:
        stats = stats_tmp

    return path, stats



