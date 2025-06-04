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
    """
    explanations:
    If this is a goal state, the heur value must be zero.
    Since the whole sokoban space is a rectangle, we can check whether any box is at the corner.
    If there are any boxes are at the corner, then we will never reach the goal unless corner is the storage.
    We can also check whether the boxes are along the walls and whether surrounded by obstacles.
    If there is no available storage along that wall, then it's a bad end.
    Although it's also a bad end if there is a obstacle between the box and target storage, it's not worth to check it.
    Then, check whether the box is surrounded by obstacles(more than two obstacles or (one obstacle and one wall)).
    """
    if sokoban_goal_state(state):
        return 0
    result = 0
    if check_corner_edge_obstacle != 0:
        return math.inf
    # above code check whether a bad end already
    # And now we need to deal with real distance
    for box in state.boxes:
        dist = math.inf
        # get all available storage for this box
        available_storage = []
        pivot = 0
        for i in state.storage:
            if box == i:
                pivot = 1
                break   # skip this box if it's already stored.
            available_storage.append(i)
        if pivot == 1:
            continue
        for stored_box in state.boxes:
            if stored_box in state.storage:
                available_storage.remove(stored_box)
        for storage in available_storage:
            dist = min(dist, abs(box[0] - storage[0]) + abs(box[1] - storage[1]))
        result += dist
    # above code sum the distances between boxes and the nearest available storage
    # We must not update the available_storage after each iterations, it may end up with running into local maxima
    # and destroy the admissible.
    # My only idea about update by robots are adding "min(max(robot to box)) for robot in robots" to the final result.
    # However, it seems not efficiency at all.
    return result  # CHANGE THIS


def check_surround(box, state, mode="normal"):
    box_up = [box[0], box[1] - 1]
    box_down = [box[0], box[1] + 1]
    box_left = [box[0] - 1, box[1]]
    box_right = [box[0] + 1, box[1]]
    if mode == "left" or mode == "right":
        # box beside the left or right wall
        if box_up in state.obstacles or box_down in state.obstacles:
            return -1
    elif mode == "top" or mode == "down":
        # box beside the top or bottom wall
        if box_left in state.obstacles or box_right in state.obstacles:
            return -1
    elif mode == "normal":
        # box neither at the corner nor beside the wall
        if box_up in state.obstacle and box_left in state.obstacle:
            return -1
        if box_left in state.obstacle and box_down in state.obstacle:
            return -1
        if box_down in state.obstacle and box_right in state.obstacle:
            return -1
        if box_right in state.obstacle and box_up in state.obstacle:
            return -1
    return 0


def check_corner_edge_obstacle(state):
    for box in state.boxes:
        if box == [0, 0] or box == [state.width-1, state.height-1] or box == [0, state.height-1] or box == [state.width-1, 0]:
            if box not in state.storage:
                return -1
        # above code check the corners of wall
        elif box[0] == 0:
            if 0 not in state.storage[:][0]:  # along the left wall
                return -1
            return check_surround(box, state, mode="left")
        elif box[0] == state.width-1:
            if state.width-1 not in state.storage[:][0]:  # along the right wall
                return -1
            return check_surround(box, state, mode='right')
        elif box[1] == 0:
            if 0 not in state.storage[:][1]:  # along top wall
                return -1
            return check_surround(box, state, mode='top')
        elif box[1] == state.height-1:
            if state.height-1 not in state.storage[:][1]:  # along bottom wall
                return -1
            return check_surround(box, state, mode='down')
        # above code check the edges along the wall
        if check_surround(box, state, mode='normal') == -1:
            return -1
        # above code check box that neither at the corner nor beside the wall
    return 0

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
    boxes = state.boxes
    result = 0
    for i in boxes:
        minimum = math.inf
        for j in state.storage:
            dist = abs(i[0] - j[0]) + abs(i[1] - j[1])
            minimum = min(dist, minimum)
        result += minimum
    return result  # CHANGE THIS


def fval_function(sN, weight):
    # IMPLEMENT
    """
    Provide a custom formula for f-value computation for Anytime Weighted A star.
    Returns the fval of the state contained in the sNode.

    @param sNode sN: A search node (containing a SokobanState)
    @param float weight: Weight given by Anytime Weighted A star
    @rtype: float
    """
    return sN.gval + weight * sN.hval #CHANGE THIS


# SEARCH ALGORITHMS
def weighted_astar(initial_state, heur_fn, weight, timebound):
    # IMPLEMENT    
    '''Provides an implementation of weighted a-star, as described in the HW1 handout'''
    '''INPUT: a sokoban state that represents the start state and a timebound (number of seconds)'''
    '''OUTPUT: A goal state (if a goal is found), else False as well as a SearchStats object'''
    '''implementation of weighted astar algorithm'''
    wrapped_fval_function = (lambda sN : fval_function(sN, weight))
    search_engine = SearchEngine("custom", 'full')
    search_engine.init_search(initial_state, goal_fn=sokoban_goal_state, heur_fn=heur_fn, fval_function=wrapped_fval_function)
    result = search_engine.search(timebound=timebound)
    return result  # CHANGE THIS

def iterative_astar(initial_state, heur_fn, weight=1, timebound=5):  # uses f(n), see how autograder initializes a search line 88
    # IMPLEMENT
    '''Provides an implementation of realtime a-star, as described in the HW1 handout'''
    '''INPUT: a sokoban state that represents the start state and a timebound (number of seconds)'''
    '''OUTPUT: A goal state (if a goal is found), else False as well as a SearchStats object'''
    '''implementation of iterative astar algorithm'''
    end_time = os.times().user + timebound
    remain_time = timebound
    wrapped_fval_function = (lambda sN: fval_function(sN, weight))
    search_engine = SearchEngine("custom", 'full')
    search_engine.init_search(initial_state, goal_fn=sokoban_goal_state, heur_fn=heur_fn,
                              fval_function=wrapped_fval_function)
    cost_bound = [math.inf, math.inf, math.inf]
    result = (False, None)
    while remain_time > 0:
        remain_time = end_time - os.times().user
        search_result = search_engine.search(timebound=remain_time-0.1, costbound=cost_bound)
        if search_result[0] is False:
            # time is up
            break
        remain_time = end_time - os.times().user
        cost_bound[2] = search_result[0].gval - 1
        weight = weight * 0.8
        result = search_result

    return result #CHANGE THIS

def iterative_gbfs(initial_state, heur_fn, timebound=5):  # only use h(n)
    # IMPLEMENT
    '''Provides an implementation of anytime greedy best-first search, as described in the HW1 handout'''
    '''INPUT: a sokoban state that represents the start state and a timebound (number of seconds)'''
    '''OUTPUT: A goal state (if a goal is found), else False'''
    '''implementation of iterative gbfs algorithm'''
    end_time = os.times().user + timebound
    remain_time = timebound
    search_engine = SearchEngine("best_first", 'full')
    search_engine.init_search(initial_state, goal_fn=sokoban_goal_state, heur_fn=heur_fn)
    cost_bound = [math.inf, math.inf, math.inf]
    result = (False, None)
    while remain_time > 0:
        search_result = search_engine.search(timebound=remain_time-0.1, costbound=cost_bound)
        if search_result[0] is False:
            # time is up
            break
        remain_time = end_time - os.times().user
        cost_bound[1] = search_result[0].gval - 1
        result = search_result

    return result  # CHANGE THIS



