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

    # Since in original Manhattan distance function, we ignore the fact that one storage can only accept one box,
    # so, in this method, i add this feature to avoid repeatedly using one storage which might cause inefficiency.
    # The running time is reduced and the accuracy is also increased.
    manhattan_dist_sum = 0
    # used_storage to store already occupied storage space
    used_storage = []
    # if there is more boxes than storage, return infinity
    if len(list(state.boxes)) > len(list(state.storage)):
        return math.inf
    # check edge cases before distance calculation
    boxes_lst = list(state.boxes)
    obstacle_lst = list(state.obstacles)
    for box in state.boxes:
        box_x = box[0]
        box_y = box[1]
        # check consecutive boxes along the edges
        if box not in state.storage:
            # check left end and right end:
            if box_x == 0 or box_x == state.width - 1:
                top_box = (box_x, box_y - 1)
                bottom_box = (box_x, box_y + 1)
                if top_box in boxes_lst or bottom_box in boxes_lst or \
                        (top_box in obstacle_lst or bottom_box in obstacle_lst):
                    return math.inf
            # check top and bottom:
            if box_y == 0 or box_y == state.height - 1:
                left_box = (box_x - 1, box_y)
                right_box = (box_x + 1, box_y)
                if left_box in boxes_lst or right_box in boxes_lst or \
                        (left_box in obstacle_lst or right_box in obstacle_lst):
                    return math.inf
            # check if the box is in four corners and not in storage:
            if (box_x == 0 and box_y == 0) or (box_x == state.width - 1 and box_y == state.height - 1) or \
                    (box_x == 0 and box_y == state.height - 1) or (box_x == state.width - 1 and box_y == 0):
                return math.inf

    for box in state.boxes:
        # store which storage is used
        min_dist_idx = -1
        # store the minimum distance from one box to their supposed storage
        min_dist_value = math.inf
        # box and storage overlaps, take it directly
        if box in state.storage:
            min_dist_idx = list(state.storage).index(box)
            min_dist_value = 0
        else:
            box_x = box[0]
            box_y = box[1]
            i = 0
            while i < len(list(state.storage)):
                # if storage is used, then pass this round and jump to next storage
                if i in used_storage:
                    i += 1
                    pass
                # this storage is available, check the distance
                else:
                    storage = list(state.storage)[i]
                    storage_x = storage[0]
                    storage_y = storage[1]
                    manhattan_distance = abs(box_x - storage_x) + abs(box_y - storage_y)
                    # compare the which storage will make the shortest distance
                    if min_dist_value > manhattan_distance:
                        min_dist_value = manhattan_distance
                        min_dist_idx = i
                    i += 1
                # 1 is the shortest distance it can have
                if min_dist_value == 1:
                    break
        # increment the overall result
        manhattan_dist_sum += min_dist_value
        # add occupied storage to list
        used_storage.append(min_dist_idx)
    return manhattan_dist_sum

def heur_zero(state):
    '''Zero Heuristic can be used to make A* search perform uniform cost search'''
    return 0

def heur_manhattan_distance(state):
    # IMPLEMENT
    '''admissible sokoban puzzle heuristic: manhattan distance'''
    '''INPUT: a sokoban state'''
    '''OUTPUT: a numeric value that serves as an estimate of the distance of the state to the goal.'''
    # We want an admissible heuristic, which is an optimistic heuristic.
    # It must never overestimate the cost to get from the current state to the goal.
    # The sum of the Manhattan distances between each box that has yet to be stored and the storage point nearest to it is such a heuristic.
    # When calculating distances, assume there are no obstacles on the grid.
    # You should implement this heuristic function exactly, even if it is tempting to improve it.
    # Your function should return a numeric value; this is the estimate of the distance to the goal.

    distances = []
    for box in state.boxes:
        box_x = box[0]
        box_y = box[1]
        temp_distance = []
        for storage in state.storage:
            storage_x = storage[0]
            storage_y = storage[1]
            manhattan_distance = abs(box_x - storage_x) + abs(box_y - storage_y)
            temp_distance.append(manhattan_distance)
        distances.append(temp_distance)
    manhattan_dist_sum = 0
    for distance_list in distances:
        manhattan_dist_sum += min(distance_list)
    return manhattan_dist_sum

def fval_function(sN, weight):
    # IMPLEMENT
    """
    Provide a custom formula for f-value computation for Anytime Weighted A star.
    Returns the fval of the state contained in the sNode.

    @param sNode sN: A search node (containing a SokobanState)
    @param float weight: Weight given by Anytime Weighted A star
    @rtype: float
    """

    g_node = sN.gval
    h_node = sN.hval
    return g_node + weight * h_node

# SEARCH ALGORITHMS
def weighted_astar(initial_state, heur_fn, weight, timebound):
    # IMPLEMENT    
    '''Provides an implementation of weighted a-star, as described in the HW1 handout'''
    '''INPUT: a sokoban state that represents the start state and a timebound (number of seconds)'''
    '''OUTPUT: A goal state (if a goal is found), else False as well as a SearchStats object'''
    '''implementation of weighted astar algorithm'''

    search_engine = SearchEngine('custom')
    wrapped_fval_function = (lambda sN: fval_function(sN, weight))
    search_engine.init_search(initial_state, goal_fn=sokoban_goal_state, heur_fn=heur_fn,
                              fval_function=wrapped_fval_function)
    return search_engine.search(timebound)

def iterative_astar(initial_state, heur_fn, weight=1, timebound=5):  # uses f(n), see how autograder initializes a search line 88
    # IMPLEMENT
    '''Provides an implementation of realtime a-star, as described in the HW1 handout'''
    '''INPUT: a sokoban state that represents the start state and a timebound (number of seconds)'''
    '''OUTPUT: A goal state (if a goal is found), else False as well as a SearchStats object'''
    '''implementation of iterative astar algorithm'''

    search_engine = SearchEngine('custom')
    best_final = False
    best_stats = None
    costbound = [math.inf, math.inf, math.inf]
    while timebound > 0:
        starting_time = os.times()
        weight = weight / 2
        if weight < 1:
            weight = 1
        wrapped_fval_function = (lambda sN: fval_function(sN, weight))
        search_engine.init_search(initial_state, goal_fn=sokoban_goal_state, heur_fn=heur_fn,
                                  fval_function=wrapped_fval_function)
        final, stats = search_engine.search(timebound, costbound)
        if not (final is False):
            if best_final is False:
                best_final = final
                best_stats = stats
            else:
                if best_final.gval + heur_fn(best_final) > final.gval + heur_fn(final):
                    best_final = final
                    best_stats = stats
            costbound[0] = best_final.gval
        ending_time = os.times()
        timebound -= ending_time[0] - starting_time[0]
    return best_final, best_stats

def iterative_gbfs(initial_state, heur_fn, timebound=5):  # only use h(n)
    # IMPLEMENT
    '''Provides an implementation of anytime greedy best-first search, as described in the HW1 handout'''
    '''INPUT: a sokoban state that represents the start state and a timebound (number of seconds)'''
    '''OUTPUT: A goal state (if a goal is found), else False'''
    '''implementation of iterative gbfs algorithm'''

    search_engine = SearchEngine('custom')
    search_engine.init_search(initial_state, goal_fn=sokoban_goal_state, heur_fn=heur_fn)
    best_final = False
    best_stats = None
    costbound = [math.inf, math.inf, math.inf]
    while timebound > 0:
        starting_time = os.times()
        final, stats = search_engine.search(timebound, costbound)
        if not (final is False):
            if best_final is False:
                best_final = final
                best_stats = stats
            else:
                if best_final.gval > final.gval:
                    best_final = final
                    best_stats = stats
            costbound[0] = best_final.gval
        ending_time = os.times()
        timebound -= ending_time[0] - starting_time[0]
    return best_final, best_stats



