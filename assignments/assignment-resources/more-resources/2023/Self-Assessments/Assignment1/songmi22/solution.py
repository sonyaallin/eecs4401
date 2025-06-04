#   Look for #IMPLEMENT tags in this file. These tags indicate what has
#   to be implemented to complete the warehouse domain.

#   You may add only standard python imports
#   You may not remove any imports.
#   You may not import or otherwise source any of your own files

import os  # for time functions
import math
from tabnanny import check
from turtle import st  # for infinity
from search import *  # for search engines
from sokoban import UP, sokoban_goal_state, SokobanState, Direction, PROBLEMS  # for Sokoban specific classes and problems

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

    if is_stuck(state):
        return math.inf
    
    sum = 0

    boxes_check = available_box(state)
    storage_check = available_storage(state)

    for box in boxes_check:
        minimum = math.inf
        used_storage = None
        for one_store in storage_check:
            to_cmp = abs(one_store[0] - box[0]) + abs(one_store[1] - box[1]) + check_obstacles(box, one_store, state) * 2
            if to_cmp <  minimum:
                used_storage = one_store
                minimum = to_cmp
        if minimum != math.inf:
            storage_check.remove(used_storage)
            sum += minimum
    return sum

def check_obstacles(box, storage, state):
    ct = 0
    for obstacle in state.obstacles:
        if min(box[0], storage[0]) < obstacle[0] < max(box[0], storage[0]) and min(box[1], storage[1]) < obstacle[1] < max(box[1], storage[1]):
            ct += 2
    return ct
    
def available_storage(state):
    res = []
    for storage in state.storage:
        if storage not in state.boxes:
            res.append(storage)
    return res

def available_box(state):
    res = []
    for box in state.boxes:
        if box not in state.storage:
            res.append(box)
    return res

def is_stuck(state):
    corner = [(0,0), (0, state.height - 1), (state.width - 1, 0), (state.width - 1, state.height - 1)]
    for box in state.boxes:
        if box in state.storage:
            return False
        box_left = (box[0] - 1, box[1])
        box_right = (box[0] + 1, box[1])
        box_up = (box[0], box[1] + 1)
        box_down = (box[0], box[1] - 1)
        if box[0] == 0 or box[0] == state.width - 1 or box[1] == 0 or box[1] == state.height - 1:
            if wall_dead(box, state):
                return True
        if box in corner:
            return True
        else:
            if (box[0] == 0 or box[0] == state.width - 1) and (box_up in state.obstacles or box_down in state.obstacles):
                return True
            elif (box[1] == 0 or box[1] == state.height - 1) and (box_left in state.obstacles or box_right in state.obstacles):
                return True
            elif (box_left in state.obstacles or box_right in state.obstacles) and (box_up in state.obstacles or box_down in state.obstacles):
                return True
            else:
                return False

def wall_dead(box, state):
    for storage in state.storage:
        if storage[0] == box[0] or storage[1] == box[1]:
            return False
    return True

def heur_zero(state):
    '''Zero Heuristic can be used to make A* search perform uniform cost search'''
    return 0

def heur_manhattan_distance(state: SokobanState):
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
        minimum = math.inf
        for one_store in state.storage:
            temp = abs(box[0] - one_store[0]) + abs(box[1] - one_store[1])
            minimum = min(temp, minimum)
        sum += minimum
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
    return sN.gval + weight * sN.hval

# SEARCH ALGORITHMS
def weighted_astar(initial_state, heur_fn, weight, timebound):
    # IMPLEMENT    
    '''Provides an implementation of weighted a-star, as described in the HW1 handout'''
    '''INPUT: a sokoban state that represents the start state and a timebound (number of seconds)'''
    '''OUTPUT: A goal state (if a goal is found), else False as well as a SearchStats object'''
    '''implementation of weighted astar algorithm'''
    new_search = SearchEngine('custom')
    wrapped_fval_function = (lambda sN: fval_function(sN,weight)) 
    new_search.init_search(initial_state, sokoban_goal_state, heur_fn, wrapped_fval_function)
    return new_search.search(timebound)

def iterative_astar(initial_state:StateSpace, heur_fn, weight=1, timebound=5):  # uses f(n), see how autograder initializes a search line 88
    # IMPLEMENT
    '''Provides an implementation of realtime a-star, as described in the HW1 handout'''
    '''INPUT: a sokoban state that represents the start state and a timebound (number of seconds)'''
    '''OUTPUT: A goal state (if a goal is found), else False as well as a SearchStats object'''
    new_search = SearchEngine('custom')
    wrapped_fval_function = (lambda sN: fval_function(sN,weight)) 
    new_search.init_search(initial_state, sokoban_goal_state, heur_fn, wrapped_fval_function)
    init_time = timebound
    cost_bound = (math.inf, math.inf, math.inf)
    prev = None
    while init_time > 0:
        start_time = os.times()[0]
        state, stats = new_search.search(init_time, cost_bound)
        weight *= 0.5
        end_time = os.times()[0]
        init_time = init_time - (start_time - end_time)
        if state:
            prev = state
            cost_bound = (prev.gval, heur_fn(prev), (prev.gval + weight * heur_fn(prev)))
        else:
            break
    return prev, stats

def iterative_gbfs(initial_state, heur_fn, timebound=5):  # only use h(n)
    # IMPLEMENT
    '''Provides an implementation of anytime greedy best-first search, as described in the HW1 handout'''
    '''INPUT: a sokoban state that represents the start state and a timebound (number of seconds)'''
    '''OUTPUT: A goal state (if a goal is found), else False'''
    '''implementation of iterative gbfs algorithm'''
    new_search = SearchEngine('best_first')
    new_search.init_search(initial_state, sokoban_goal_state, heur_fn)
    init_time = timebound
    cost_bound = (math.inf, math.inf, math.inf)
    prev = None
    while init_time > 0:
        start_time = os.times()[0]
        state, stats = new_search.search(init_time, cost_bound)
        end_time = os.times()[0]
        init_time = init_time - (start_time - end_time)
        if state:
            prev = state
            cost_bound = (prev.gval - 1, heur_fn(prev), prev.gval - 1 + heur_fn(prev))
        else:
            break
    return prev, stats



