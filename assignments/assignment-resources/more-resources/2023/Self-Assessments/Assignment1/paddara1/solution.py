#   Look for #IMPLEMENT tags in this file. These tags indicate what has
#   to be implemented to complete the warehouse domain.

#   You may add only standard python imports
#   You may not remove any imports.
#   You may not import or otherwise source any of your own files

import os  # for time functions
import math  # for infinity
from search import *  # for search engines
from sokoban import sokoban_goal_state, SokobanState, Direction, PROBLEMS  # for Sokoban specific classes and problems

STATE_TO_HEUR = dict()  # maps (state.boxes, state.obstacles) to its heuristic

# SOKOBAN HEURISTICS
def heur_alternate(state):
    '''a better heuristic'''
    '''INPUT: a sokoban state'''
    '''OUTPUT: a numeric value that serves as an estimate of the distance of the state to the goal.'''
    # heur_manhattan_distance has flaws.
    # Write a heuristic function that improves upon heur_manhattan_distance to estimate distance between the current state and the goal.
    # Your function should return a numeric value for the estimate of the distance to the goal.
    # EXPLAIN YOUR HEURISTIC IN THE COMMENTS. Please leave this function (and your explanation) at the top of your solution file, to facilitate marking.
    boxes_obs = (state.boxes, state.obstacles)
    if boxes_obs in STATE_TO_HEUR:
        return STATE_TO_HEUR[boxes_obs]
    if sokoban_goal_state(state):
        return 0
    unused_storage_points = set()
    for storage_point in state.storage:
        unused_storage_points.add(storage_point)
    ans = 0
    corners = {(0, 0), (state.width - 1, state.height - 1), (state.width - 1, 0), (0, state.height - 1)}
    storage_in_corner = False  # True iff there is a storage point in a corner
    for corner in corners:
        if corner in state.storage:
            storage_in_corner = True

    if adjacent_boxes_along_edge(state) and len(state.storage) == len(state.boxes):
        return math.inf

    for box in state.boxes:
        if len(state.storage) == len(state.boxes) and box not in state.storage:
            if is_in_corner(box, state) or is_box_stuck(box, state):
                # if box is stuck in corner or
                # if box is stuck along edge (adj to obstacle)
                return math.inf
        elif box in state.storage:
            if storage_in_corner and box not in corners:
                ans += 1

        dist, storage_point = get_nearest_storage_point(box, unused_storage_points)
        ans += dist
        unused_storage_points.remove(storage_point)
    STATE_TO_HEUR[boxes_obs] = ans
    return ans
    # heur_manhattan_distance assumes that many boxes can be stored at one location, which is incorrect
    # heur_alternate avoids this by keeping track of storage points we have used so far, and ensuring that another
    # box is not put in these storage points
    # Also, if there is a box is in a non-corner storage point, and there is an empty storage point in the corner
    # increase the heuristic. This is because in most puzzles with storage points in corners, these must be filled first
    # in order to fill the other storage points


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
    ans = 0
    for box in state.boxes:
        if box not in state.storage:
            ans += get_nearest_storage_point(box, state.storage)[0]
    return ans

def fval_function(sN, weight):
    """
    Provide a custom formula for f-value computation for Anytime Weighted A star.
    Returns the fval of the state contained in the sNode.

    @param sNode sN: A search node (containing a SokobanState)
    @param float weight: Weight given by Anytime Weighted A star
    @rtype: float
    """
    return sN.gval + (weight * sN.hval)

# SEARCH ALGORITHMS
def weighted_astar(initial_state, heur_fn, weight, timebound):
    '''Provides an implementation of weighted a-star, as described in the HW1 handout'''
    '''INPUT: a sokoban state that represents the start state and a timebound (number of seconds)'''
    '''OUTPUT: A goal state (if a goal is found), else False as well as a SearchStats object'''
    '''implementation of weighted astar algorithm'''
    engine = SearchEngine("custom", "default")
    wrapped_fval_function = (lambda sN: fval_function(sN, weight))
    engine.init_search(initial_state, sokoban_goal_state, heur_fn, wrapped_fval_function)
    goal_node, stats = engine.search(timebound=timebound)
    return goal_node, stats

def iterative_astar(initial_state, heur_fn, weight=1, timebound=5):  # uses f(n), see how autograder initializes a search line 88
    '''Provides an implementation of realtime a-star, as described in the HW1 handout'''
    '''INPUT: a sokoban state that represents the start state and a timebound (number of seconds)'''
    '''OUTPUT: A goal state (if a goal is found), else False as well as a SearchStats object'''
    '''implementation of iterative astar algorithm'''
    goal_node, stats = False, None
    curr_timebound = timebound
    curr_costbound = [math.inf, heur_fn(initial_state), math.inf]
    engine = SearchEngine("custom", "default")
    wrapped_fval_function = (lambda sN: fval_function(sN, weight))
    engine.init_search(initial_state, sokoban_goal_state, heur_fn, wrapped_fval_function)
    weight_change = 0.1
    while curr_timebound > 0:
        goal_node, stats = engine.search(timebound=curr_timebound, costbound=curr_costbound)
        if goal_node:
            gval = goal_node.gval
            hval = heur_fn(goal_node)
            fval = gval + (weight * hval)
            curr_costbound = [gval, hval, fval]
            if weight >= 1 + weight_change:
                weight -= weight_change
            engine.init_search(goal_node, sokoban_goal_state, heur_fn, wrapped_fval_function)
        curr_timebound -= stats.total_time
    return goal_node, stats


def iterative_gbfs(initial_state, heur_fn, timebound=5):  # only use h(n)
    '''Provides an implementation of anytime greedy best-first search, as described in the HW1 handout'''
    '''INPUT: a sokoban state that represents the start state and a timebound (number of seconds)'''
    '''OUTPUT: A goal state (if a goal is found), else False'''
    '''implementation of iterative gbfs algorithm'''
    goal_node, stats = False, None
    curr_timebound = timebound
    curr_costbound = [math.inf, heur_fn(initial_state), math.inf]
    engine = SearchEngine("custom", "default")
    engine.init_search(initial_state, sokoban_goal_state, heur_fn)
    searches = 0
    while curr_timebound > 0:
        goal_node, stats = engine.search(timebound=curr_timebound, costbound=curr_costbound)
        if goal_node:
            searches += 1
            gval = goal_node.gval
            curr_costbound[0] = gval
            engine.init_search(goal_node, sokoban_goal_state, heur_fn)
        curr_timebound -= stats.total_time
    return goal_node, stats


# HELPERS
def get_nearest_storage_point(box, storages):
    """
    Return the manhattan distance of the storage point that is closest to this
    and the storage point as a tuple.
    >>> dist, s = get_nearest_storage_point((1, 1), ((2, 3), (4, 5)))
    >>> dist == 3 and s == (2, 3)
    True
    """
    curr_min_dist = math.inf
    curr_min_storage = None
    for storage in storages:
        dist = abs(box[0] - storage[0]) + abs(box[1] - storage[1])
        if dist < curr_min_dist:
            curr_min_dist = dist
            curr_min_storage = storage
        if curr_min_dist == 0:
            return curr_min_dist, curr_min_storage
    return curr_min_dist, curr_min_storage


def is_box_stuck(box, state: SokobanState) -> bool:
    x, y = box[0], box[1]
    obs = state.obstacles
    if is_in_corner(box, state):
        return True
    if y in [0, state.height - 1]:  # bottom row or top row
        if (x - 1, y) in obs or (x + 1, y) in obs:
            return True
    if x in [0, state.width - 1]:  # first column or last column
        if (x, y - 1) in obs or (x, y + 1) in obs:
            return True
    return False


def is_in_corner(item, state: SokobanState) -> bool:
    """
    Return True iff this item is in a corner.
    """
    return (item[0] in [0, state.width - 1]) and (item[1] in [0, state.height - 1])


def adjacent_boxes_along_edge(state: SokobanState) -> bool:
    """
    Return True iff there are 2 boxes next to each other along an edge and at
    least one of them is not in a storage point.
    """
    boxes = list(state.boxes)
    for i in range(len(boxes)):
        x, y = boxes[i]
        if (x, y) in state.storage:
            return False
        if (y in [0, state.height - 1]) and ((x-1, y) in boxes[i+1:] or (x+1, y) in boxes[i+1:]):
            return True
        if (x in [0, state.width - 1]) and ((x, y-1) in boxes[i+1:] or (x, y+1) in boxes[i+1:]):
            return True
    return False
