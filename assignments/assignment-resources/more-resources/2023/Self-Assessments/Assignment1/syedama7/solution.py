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

    # IDEA: a heuristic that will search for the nearest storage space that is unoccupied for each box and return that distance, it will also
    # account for obstacles and unsolvable cases, it will account for obstacles in the path as having double the cost

    # check if any of the boxes are in a deadlock state
    if is_deadlock(state):
        return math.inf

    available = [storage for storage in state.storage]
    sum = 0
    fulfilled = 0
    # get distances of boxes to storage
    for box in state.boxes:
        # check if box is already at storage space
        if len(available) == 0:
            return math.inf

        # if box is already in storage, remove the storage
        if box in available:
            available.remove(box)
            fulfilled += 1
            continue

        min_dist = math.inf
        for storage in available:
            dist = man_dist(box, storage) + num_obs(state, box, storage) * 2
            min_dist = min(dist, min_dist)
        sum += min_dist

    # all boxes are in storage
    if fulfilled == len(state.boxes):
        return 0

    # get distances of robots to boxes
    for robot in state.robots:
        min_dist = math.inf
        for box in state.boxes:
            dist = man_dist(robot, box) + num_obs(state, robot, box) * 2
            min_dist = min(dist, min_dist)
        sum += min_dist

    return sum

def man_dist(pos1, pos2):
    '''Helper to determine manhatten distance between two points'''
    return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])

def is_deadlock(state):
    '''Helper to check if a position is in a deadlcock state where it cannot be moved'''
    # check if box is against corner and not in goal state
    wall_corners = [(0,0), (state.width-1, 0), (0, state.height-1), (state.width-1, state.height-1)]

    for box in state.boxes:
        if box not in state.storage:
            if box in wall_corners or box_in_corner(state, box) or box_edge_no_storage(state, box):
                return True
    return False

def box_in_corner(state, box):
    obstacles = state.obstacles.union(state.boxes)
    above = (box[0], box[1]+1)
    below = (box[0], box[1]-1)
    left = (box[0]-1, box[1])
    right = (box[0]+1, box[1])

    # box on left or right edge and obstacle in way
    if (box[0] == 0 or box[0] == state.width-1) and (above in obstacles or below in obstacles):
        return True
    # box on top or bottom edge and obstacle in way
    elif (box[1] == 0 or box[1] == state.height-1) and (right in obstacles or left in obstacles):
        return True
    # obstacle above and to left or right of box
    elif (above in obstacles) and ((left in obstacles) or (right in obstacles)):
        return True
    # obstacle below and to left or right of box
    elif (below in obstacles) and ((left in obstacles) or (right in obstacles)):
        return True
    else:
        return False

def box_edge_no_storage(state, box):
    storage_x = [storage[0] for storage in state.storage]
    storage_y = [storage[1] for storage in state.storage]
    right_edge = state.width-1
    left_edge = 0
    top = state.height-1
    bottom = 0

    if box[0] == left_edge and (left_edge not in storage_x):
        return True
    elif box[0] == right_edge and (right_edge not in storage_x):
        return True
    elif box[1] == top and (top not in storage_y):
        return True
    elif box[1] == bottom and (bottom not in storage_y):
        return True
    return False

def num_obs(state, pos1, pos2):
    '''Get the number of objects that are in a straight line distance between pos1 and pos2'''
    obstacles = state.obstacles.union(frozenset(state.robots))
    count = 0
    x_min,x_max = min(pos1[0], pos2[0]),max(pos1[0],pos2[0])
    y_min,y_max = min(pos1[1], pos2[1]),max(pos1[1],pos2[1])
    for obs in obstacles:
        if obs[0] in range(x_min+1, x_max) and obs[1] in range(y_min+1,y_max):
            count += 1
    return count

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
    sum = 0
    for box in state.boxes:
        sum += min([man_dist(box, storage) for storage in state.storage])
    return sum

def fval_function(sN, weight):
    # IMPLEMENT
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
    # IMPLEMENT
    '''Provides an implementation of weighted a-star, as described in the HW1 handout'''
    '''INPUT: a sokoban state that represents the start state and a timebound (number of seconds)'''
    '''OUTPUT: A goal state (if a goal is found), else False as well as a SearchStats object'''
    '''implementation of weighted astar algorithm'''
    search_engine = SearchEngine("custom")
    wrapped_fval_function = (lambda sN: fval_function(sN, weight))
    search_engine.init_search(initial_state, sokoban_goal_state, heur_fn, wrapped_fval_function)
    result = search_engine.search(timebound)
    return result

def iterative_astar(initial_state, heur_fn, weight=1, timebound=5):  # uses f(n), see how autograder initializes a search line 88
    # IMPLEMENT
    '''Provides an implementation of realtime a-star, as described in the HW1 handout'''
    '''INPUT: a sokoban state that represents the start state and a timebound (number of seconds)'''
    '''OUTPUT: A goal state (if a goal is found), else False as well as a SearchStats object'''
    '''implementation of iterative astar algorithm'''
    search_engine = SearchEngine("custom", cc_level="full")
    wrapped_fval_function = (lambda sN: fval_function(sN, weight))
    search_engine.init_search(initial_state, sokoban_goal_state, heur_fn, wrapped_fval_function)

    end_time = os.times()[0]+timebound
    result = False
    stats = None
    delta = 0.0005
    time_remaining = timebound
    costbound_fvalue = math.inf
    while time_remaining > 0:
        goal_state, stats = search_engine.search(time_remaining-0.1, (math.inf, math.inf, costbound_fvalue))
        time_remaining = end_time - os.times()[0]
        weight = weight - delta
        if goal_state:
            result = goal_state
            costbound_fvalue = result.gval
        else:
            break

    return result, stats


def iterative_gbfs(initial_state, heur_fn, timebound=5):  # only use h(n)
    # IMPLEMENT
    '''Provides an implementation of anytime greedy best-first search, as described in the HW1 handout'''
    '''INPUT: a sokoban state that represents the start state and a timebound (number of seconds)'''
    '''OUTPUT: A goal state (if a goal is found), else False'''
    '''implementation of iterative gbfs algorithm'''
    search_engine = SearchEngine("best_first", cc_level="full")
    search_engine.init_search(initial_state, sokoban_goal_state, heur_fn)

    end_time = os.times()[0] + timebound
    result = False
    stats = None
    time_remaining = timebound
    costbound_gvalue = math.inf
    while time_remaining > 0:
        goal_state, stats = search_engine.search(time_remaining - 0.1, (costbound_gvalue, math.inf, math.inf))
        time_remaining = end_time - os.times()[0]
        if goal_state:
            result = goal_state
            costbound_gvalue = result.gval
        else:
            break

    return result, stats

