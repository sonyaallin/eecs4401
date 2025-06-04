#   Look for #IMPLEMENT tags in this file. These tags indicate what has
#   to be implemented to complete the warehouse domain.

#   You may add only standard python imports
#   You may not remove any imports.
#   You may not import or otherwise source any of your own files

from cmath import inf
import os  # for time functions
import math

from numpy import object_  # for infinity
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

    # Explanation: This heuristic function uses manhattan distance but does not allow multiple boxes to be stored in the same location. This is done by 
    # choosing the shortest distance between box and all the available storage points. Thus the closest storage point is chosen, which we will then remove
    # from the set of available storage points. This heuristic also checks for edge cases where it would become impossbile to solve the sokoban puzzle. 
    # More specifically, it checks if a box is stuck in a corner while not being on a storage point. And checks if a box is stuck on an edge that does not
    # have a storage point on it. In these cases, infinity is returned by our heuristic function.

    # Some other heuristics I tried were: adding cost for obstacles and taking distance between robots and boxes into consideration 

    # store boxes and storage points in sets
    boxes = set(state.boxes)
    storage_pts = set(state.storage)
    
    total_dist = 0
    # calculate manhattan distance of all boxes (without sharing storage point)
    for box in boxes:
        # call helper function to check for edge cases (box stuck in corner or on edge)
        if check_corners_edges(state, box):
            return inf
        min_dist = inf
        # find closest storage point to this box
        for sp in storage_pts:
            curr = abs(box[0] - sp[0]) + abs(box[1] - sp[1])
            if curr < min_dist:
                min_dist = curr
                to_remove = sp
        # remove closest storage point from the set of available storage points
        storage_pts.remove(to_remove)
        # add the distance between box and storage point to our total
        total_dist += min_dist
    return total_dist

def check_corners_edges(state, box):
    storage_left = False
    storage_right = False
    storage_top = False
    storage_bottom = False

    # check if this box is on an edge
    on_left_edge = (box[0] == 0)
    on_right_edge = (box[0]+1 == state.width)
    on_top_edge = (box[1]+1 == state.height)
    on_bottom_edge = (box[1] == 0)

    # check for obstacle and boxes that surround this box
    object_above = (box[0], box[1]+1) in (state.obstacles).union(state.boxes)
    object_below = (box[0], box[1]-1) in (state.obstacles).union(state.boxes)
    object_right = (box[0]+1, box[1]) in (state.obstacles).union(state.boxes)
    object_left = (box[0]-1, box[1]) in (state.obstacles).union(state.boxes)
    
    # check if this box is stuck in any corner between walls, obstacles and boxes
    if (box not in state.storage) and (on_left_edge or on_right_edge) and (on_top_edge or on_bottom_edge):
        return True
    elif (box not in state.storage) and (on_left_edge or on_right_edge) and (object_above or object_below):
        return True
    elif (box not in state.storage) and (on_top_edge or on_bottom_edge) and (object_right or object_left):
        return True

    # check if there are any storage points on each of the edges
    for sp in set(state.storage):
        if (sp[0] == 0):
            storage_left = True
        if (sp[0] == state.width-1):
            storage_right = True
        if (sp[1] == 0):
            storage_bottom = True
        if (sp[1] == state.height-1):
            storage_top = True

    # check if this box is stuck on any edge without a storage point
    if on_left_edge and not storage_left:
        return True
    elif on_right_edge and not storage_right:
        return True
    elif on_top_edge and not storage_top:
        return True
    elif on_bottom_edge and not storage_bottom:
        return True
    return False
    
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
        closest = inf
        for storage_pt in state.storage:
            curr = abs(box[0] - storage_pt[0]) + abs(box[1] - storage_pt[1])
            if curr < closest:
                closest = curr
        total += closest
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
    return sN.gval + weight*sN.hval

# SEARCH ALGORITHMS
def weighted_astar(initial_state, heur_fn, weight, timebound):
    # IMPLEMENT    
    '''Provides an implementation of weighted a-star, as described in the HW1 handout'''
    '''INPUT: a sokoban state that represents the start state and a timebound (number of seconds)'''
    '''OUTPUT: A goal state (if a goal is found), else False as well as a SearchStats object'''
    '''implementation of weighted astar algorithm'''
    wrapped_fval_function = (lambda sN: fval_function(sN, weight))
    s = SearchEngine('custom')
    s.init_search(initial_state, sokoban_goal_state, heur_fn, wrapped_fval_function)
    return s.search(timebound)

def iterative_astar(initial_state, heur_fn, weight=1, timebound=5):  # uses f(n), see how autograder initializes a search line 88
    # IMPLEMENT
    '''Provides an implementation of realtime a-star, as described in the HW1 handout'''
    '''INPUT: a sokoban state that represents the start state and a timebound (number of seconds)'''
    '''OUTPUT: A goal state (if a goal is found), else False as well as a SearchStats object'''
    '''implementation of iterative astar algorithm'''
    costbound = (inf, inf, inf)
    prev_result, prev_stats = None, None
    while timebound > 0:
        wrapped_fval_function = (lambda sN: fval_function(sN, weight))
        s = SearchEngine('custom')
        s.init_search(initial_state, sokoban_goal_state, heur_fn, wrapped_fval_function)
        result, stats =  s.search(timebound, costbound)

        if result is False and prev_result is None:
            return result, stats
        elif result is False:
            return prev_result, prev_stats
        prev_result = result
        prev_stats = stats

        timebound -= prev_stats.total_time
        costbound = (inf, inf, prev_result.gval + heur_fn(prev_result))
        weight = weight * 0.5
    return prev_result, prev_stats

def iterative_gbfs(initial_state, heur_fn, timebound=5):  # only use h(n)
    # IMPLEMENT
    '''Provides an implementation of anytime greedy best-first search, as described in the HW1 handout'''
    '''INPUT: a sokoban state that represents the start state and a timebound (number of seconds)'''
    '''OUTPUT: A goal state (if a goal is found), else False'''
    '''implementation of iterative gbfs algorithm'''
    s = SearchEngine('best_first')
    s.init_search(initial_state, sokoban_goal_state, heur_fn)
    prev_result, prev_stats = None, None
    costbound = (inf, inf, inf)
    while timebound > 0:
        result, stats =  s.search(timebound, costbound)
        
        if result is False and prev_result is None:
            return result, stats
        elif result is False:
            return prev_result, prev_stats
        prev_result = result
        prev_stats = stats

        timebound -= prev_stats.total_time
        costbound = (prev_result.gval, inf, inf)
    return prev_result, prev_stats