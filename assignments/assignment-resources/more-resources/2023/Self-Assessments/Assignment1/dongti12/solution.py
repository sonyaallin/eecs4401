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
    result = 0

    # a storage will be removed for each box-storage pairing as we run through the algorithm
    storage_copy = [s for s in state.storage]

    for box in state.boxes:
        if box in storage_copy: # if box is already in storage position, then we skip it and remove the storage from the
            # available storage units
            storage_copy.remove((box[0], box[1]))
            continue

        # check for edge cases if the box is stuck in a between 2 obstacles/walls, then it cant move
        if _check_for_edge_cases(state, box, state.width, state.height):
            return float('inf')

        # As an estimate, for each obstacle that is within a rectangle formed by the box and a storage,
        # add 2 to the distance (on top of the manhattan distance). Then, choose the storage closest to the box with this
        # heuristic and pair it with the box (unique pairing because each box can only be in one slot)
        result += _realistic_distance(state, storage_copy, box)

        # find the robot nearest to the box
        result += _nearest_robot(box, state.robots)

    return result


def _check_for_edge_cases(state, box, width, height):
    left, right, top, bottom = (box[0] - 1, box[1]), (box[0] + 1, box[1]), (box[0], box[1] + 1), (box[0], box[1] - 1)

    red_zone = set() # a set of all the walls and obstacles
    obstacles_copy = [o for o in state.obstacles]
    bottom_walls = set([(i, -1) for i in range(width)])
    top_walls = set([(i, height) for i in range(width)])
    left_walls = set([(-1, i) for i in range(height)])
    right_walls = set([(width+1, i) for i in range(height)])

    red_zone = red_zone.union(obstacles_copy).union(bottom_walls).union(top_walls).union(left_walls).union(right_walls)

    # if there are two walls/obstacles adjacent to the box, then it can't move
    if (left in red_zone and top in red_zone) or (left in red_zone and bottom in red_zone) or \
            (right in red_zone and top in red_zone) or (right in red_zone and bottom in red_zone):
        return True

    return False


def _realistic_distance(state, storage_copy, box):
    # for each obstacle that is within a rectangle formed by the box and its state, add 2 to the distance
    minimum = float('inf')
    node_selected = (0, 0)
    for storage in storage_copy:
        # set cur to manhanttan distance ignoring everything
        curr_dist = abs(box[0] - storage[0]) + abs(box[1] - storage[1])
        for obstacle in state.obstacles:
            left_most = min(box[0], storage[0])
            right_most = max(box[0], storage[0])
            top_most = max(box[1], storage[1])
            bottom_most = min(box[1], storage[1])
            if left_most <= obstacle[0] <= right_most and bottom_most <= obstacle[1] <= top_most:
                curr_dist += 2

        if curr_dist < minimum:
            node_selected = (storage[0], storage[1])
            minimum = curr_dist

    # also removes the node selected so no other box can be in this storage position
    storage_copy.remove(node_selected)
    return minimum


def _nearest_robot(box, robots):
    min_dist = float("inf")
    for r in robots:
        temp = abs(box[0] - r[0]) + abs(box[1] - r[1])
        if temp < min_dist:
            min_dist = temp

    return min_dist


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
    total = 0

    for box in state.boxes:
        cur_min_dist = float("inf")
        for storage in state.storage:
            temp = abs(box[0] - storage[0]) + abs(box[1] - storage[1])
            if temp < cur_min_dist:
                cur_min_dist = temp

        total += cur_min_dist

    return total

def fval_function(sN, weight):
    # IMPLEMENT
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
    # IMPLEMENT    
    '''Provides an implementation of weighted a-star, as described in the HW1 handout'''
    '''INPUT: a sokoban state that represents the start state and a timebound (number of seconds)'''
    '''OUTPUT: A goal state (if a goal is found), else False as well as a SearchStats object'''
    '''implementation of weighted astar algorithm'''

    se = SearchEngine('custom', 'full')
    se.init_search(initial_state, sokoban_goal_state, heur_fn, (lambda sN: fval_function(sN, weight)))

    costbound = (float('inf'), float('inf'), float('inf'))
    time_left = timebound
    best_result = None
    best_time = 10000

    while time_left > 0:
        result = se.search(time_left, costbound)

        if result[0] is not False:
            if result[1].total_time < best_time:
                best_result = result
            time_left -= result[1].total_time
            costbound = (result[0].gval, result[0].gval, result[0].gval) # prune based on g values
        else:
            if best_result is not None:
                return best_result
            return result

    return best_result

def iterative_astar(initial_state, heur_fn, weight=1, timebound=5):  # uses f(n), see how autograder initializes a search line 88
    # IMPLEMENT
    '''Provides an implementation of realtime a-star, as described in the HW1 handout'''
    '''INPUT: a sokoban state that represents the start state and a timebound (number of seconds)'''
    '''OUTPUT: A goal state (if a goal is found), else False as well as a SearchStats object'''
    '''implementation of iterative astar algorithm'''
    # se = SearchEngine()
    # se.set_strategy('astar')
    # se.init_search(initial_state, sokoban_goal_state, heur_fn, fval_function)
    # return se.search(timebound)

    se = SearchEngine('custom', 'full')
    se.init_search(initial_state, sokoban_goal_state, heur_fn, (lambda sN: fval_function(sN, weight)))

    costbound = (float('inf'), float('inf'), float('inf'))
    time_left = timebound
    best_result = None
    best_time = 10000

    while time_left > 0:
        result = se.search(time_left, costbound)

        if result[0] is not False:
            if result[1].total_time < best_time:
                best_result = result
            time_left -= result[1].total_time
            costbound = (result[0].gval, result[0].gval, float('inf')) # prune based on g values
        else:
            if best_result is not None:
                return best_result
            return result

    return best_result


def iterative_gbfs(initial_state, heur_fn, timebound=5):  # only use h(n)
    # IMPLEMENT
    '''Provides an implementation of anytime greedy best-first search, as described in the HW1 handout'''
    '''INPUT: a sokoban state that represents the start state and a timebound (number of seconds)'''
    '''OUTPUT: A goal state (if a goal is found), else False'''
    '''implementation of iterative gbfs algorithm'''
    se = SearchEngine('best_first', 'full')
    se.init_search(initial_state, sokoban_goal_state, heur_fn)
    costbound = (float('inf'), float('inf'), float('inf'))

    time_left = timebound
    best_result = None
    best_time = 10000

    while time_left > 0:
        result = se.search(time_left, costbound)

        if result[0] is not False:
            if result[1].total_time < best_time:
                best_result = result
            time_left -= result[1].total_time
            costbound = (result[0].gval, float('inf'), float('inf')) # prune based on h values
        else:
            if best_result is not None:
                return best_result
            return result

    return best_result