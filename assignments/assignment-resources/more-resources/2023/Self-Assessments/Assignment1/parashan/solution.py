#   Look for #IMPLEMENT tags in this file. These tags indicate what has
#   to be implemented to complete the warehouse domain.

#   You may add only standard python imports
#   You may not remove any imports.
#   You may not import or otherwise source any of your own files

import os  # for time functions
import math # for infinity
from search import *  # for search engines
from sokoban import sokoban_goal_state, SokobanState, Direction, PROBLEMS  # for Sokoban specific classes and problems

# SOKOBAN HEURISTICS
def is_near_x(object, others, others2 = {}, others3 = {}):
    right = (object[0] + 1, object[1])
    left = (object[0] - 1, object[1]) 
    if  right in others or \
        right in others2 or \
        right in others3: # check right OR
        return True
    elif left in others or \
        left in others2 or \
        left in others3: # check left
        return True
    return False

def is_near_y(object, others, others2 = {}, others3 = {}):
    down = (object[0], object[1] + 1)
    up = (object[0], object[1] - 1) 
    if  down in others or \
        down in others2 or \
        down in others3: # check up OR
        return True
    elif up in others or \
        up in others2 or \
        up in others3: # check down
        return True
    return False

def is_corner(box, width, height, obstacles, robots = {}, boxes = {}):
   
    stuck_x = is_near_x(box, obstacles, boxes) or box[0] == 0 or box[0] == width - 1
    stuck_y = is_near_y(box, obstacles, boxes) or box[1] == 0 or box[1] == height - 1
    if stuck_x and stuck_y:
        return True
    return False

def heur_alternate(state):
    '''
    This heuristic has two main components:
    1. Compute smallest manhattan distance from a box -> storage
        a. Ensure a box only gets mapped to a single storage
    2. Penalize a box ending up in a corner
        a. I recognize a box is in a corner if there is one wall/obstacle/box to the right/left of a box + one wall/obstacle/box to the up/down of a box
    Probably not monotonic heuristic
    '''
    '''INPUT: a sokoban state'''
    '''OUTPUT: a numeric value that serves as an estimate of the distance of the state to the goal.'''
    # heur_manhattan_distance has flaws.
    # Write a heuristic function that improves upon heur_manhattan_distance to estimate distance between the current state and the goal.
    # Your function should return a numeric value for the estimate of the distance to the goal.
    # EXPLAIN YOUR HEURISTIC IN THE COMMENTS. Please leave this function (and your explanation) at the top of your solution file, to facilitate marking.
    distance_sum = 0
    boxes = state.boxes
    storage = set(state.storage)
    for box in boxes:
        if box in storage:
            storage.remove(box)
            continue
        if is_corner(box, state.width, state.height, state.obstacles, state.robots, state.boxes):
            distance_sum += float('inf')
            continue
        min_dist = float('inf')
        min_store = None
        for store in storage:
            dist = abs(store[0] - box[0]) + abs(store[1] - box[1])
            if dist < min_dist:
                min_store = store
                min_dist = dist
        if min_store:
            distance_sum += min_dist
            storage.remove(min_store)
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
    boxes = state.boxes
    storage = state.storage
    for box in boxes:
        smallest_dist = float('inf')
        for store in storage:
            dist = abs(store[0] - box[0]) + abs(store[1] - box[1])
            smallest_dist = min(dist, smallest_dist)
        distance_sum += smallest_dist
    return distance_sum 

def fval_function(sN, weight):
    """
    Provide a custom formula for f-value computation for Anytime Weighted A star.
    Returns the fval of the state contained in the sNode.

    @param sNode sN: A search node (containing a SokobanState)
    @param float weight: Weight given by Anytime Weighted A star
    @rtype: float
    """
    f = sN.gval + weight * sN.hval
    return f

# SEARCH ALGORITHMS
def weighted_astar(initial_state, heur_fn, weight, timebound):
    '''Provides an implementation of weighted a-star, as described in the HW1 handout'''
    '''INPUT: a sokoban state that represents the start state and a timebound (number of seconds)'''
    '''OUTPUT: A goal state (if a goal is found), else False as well as a SearchStats object'''
    '''implementation of weighted astar algorithm'''
    se = SearchEngine('custom', 'full')
    fval = lambda sN : fval_function(sN, weight)
    se.init_search(initial_state, goal_fn=sokoban_goal_state, heur_fn=heur_fn, fval_function=fval)
    final, stats = se.search(timebound)
    return final, stats

def iterative_astar(initial_state, heur_fn, weight=1, timebound=5):  # uses f(n), see how autograder initializes a search line 88
    '''Provides an implementation of realtime a-star, as described in the HW1 handout'''
    '''INPUT: a sokoban state that represents the start state and a timebound (number of seconds)'''
    '''OUTPUT: A goal state (if a goal is found), else False as well as a SearchStats object'''
    '''implementation of iterative astar algorithm'''
    costbound = float('inf')
    se = SearchEngine('custom', 'full')
    current_final, current_stats = False, None
    costbound = None
    weight = 100
    while timebound > 0:
        fval = lambda sN : fval_function(sN, weight)
        se.init_search(initial_state, goal_fn=sokoban_goal_state, heur_fn=heur_fn, fval_function=fval)
        if current_final:
            hval = heur_fn(current_final)
            costbound=(current_final.gval - 1, hval - 1, current_final.gval + weight *  hval -1)
        
        final, stats = se.search(timebound, costbound = costbound)

        timebound -= stats.total_time
        if final:
            current_final, current_stats = final, stats
            if weight > 10:
                weight = weight / 2
            else:
                weight -= 1

    return current_final, current_stats

def iterative_gbfs(initial_state, heur_fn, timebound=5):  # only use h(n)
    '''Provides an implementation of anytime greedy best-first search, as described in the HW1 handout'''
    '''INPUT: a sokoban state that represents the start state and a timebound (number of seconds)'''
    '''OUTPUT: A goal state (if a goal is found), else False'''
    '''implementation of iterative gbfs algorithm'''
    costbound = float('inf')
    se = SearchEngine('best_first', 'full')
    current_final, current_stats = False, None
    costbound = None
    timebound = 5
    while timebound > 0:
        se.init_search(initial_state, goal_fn=sokoban_goal_state, heur_fn=heur_fn)
        if current_final:
            hval = heur_fn(current_final)
            costbound=(current_final.gval-1, hval-1, current_final.gval + hval - 1)
        
        final, stats = se.search(timebound, costbound = costbound)
        
        timebound -= stats.total_time
        if final:
            current_final, current_stats = final, stats

    return current_final, current_stats

if __name__=='__main__':
    s0 = PROBLEMS[0]  # Problems get harder as i gets bigger
    se = SearchEngine('best_first', 'full')
    se.init_search(s0, goal_fn=sokoban_goal_state, heur_fn=heur_alternate)
    final, stats = se.search(4)

