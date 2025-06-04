#   Look for #IMPLEMENT tags in this file. These tags indicate what has
#   to be implemented to complete the warehouse domain.

#   You may add only standard python imports
#   You may not remove any imports.
#   You may not import or otherwise source any of your own files

import os  # for time functions
import math
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
    sum = 0
    temp_robots = list(state.robots)
    temp_storage = list(state.storage)
    r_flag = ()
    s_flag = ()
    for box in state.boxes:
        min1 = math.inf
        min2 = math.inf
        #looking for deadlock cases
        if ( ((box[0] - 1, box[1]) in state.obstacles and (box[0], box[1] + 1) in state.obstacles) 
        or ((box[0], box[1] + 1) in state.obstacles and (box[0] + 1, box[1]) in state.obstacles)
        or ((box[0] + 1, box[1]) in state.obstacles and (box[0], box[1] - 1) in state.obstacles)
        or ((box[0], box[1] - 1) in state.obstacles and (box[0] - 1, box[1]) in state.obstacles)):
            return math.inf 
        #looking for the closest robot
        for robot in temp_robots:
            if ((abs(robot[0] - box[0]) + abs(robot[1] - box[1])) < min1):
                min1 = (abs(robot[0] - box[0]) + abs(robot[1] - box[1]))
                r_flag = robot
        sum += min1
        #looking for the closest storage
        for store in temp_storage:
            if ((abs(box[0] - store[0]) + abs(box[1] - store[1])) < min2):
                min2 = (abs(box[0] - store[0]) + abs(box[1] - store[1])) 
                s_flag = store
        sum += min2 
        temp_storage.remove(s_flag)
        temp_robots.remove(r_flag)
        temp_robots.append(s_flag)
    return sum


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
        check = []
        for store in state.storage:
            check.append((abs(box[0] - store[0]) + abs(box[1] - store[1])))
        sum += min(check)
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
    return (sN.gval + (weight * sN.hval))

# SEARCH ALGORITHMS
def weighted_astar(initial_state, heur_fn, weight, timebound):
    # IMPLEMENT    
    '''Provides an implementation of weighted a-star, as described in the HW1 handout'''
    '''INPUT: a sokoban state that represents the start state and a timebound (number of seconds)'''
    '''OUTPUT: A goal state (if a goal is found), else False as well as a SearchStats object'''
    '''implementation of weighted astar algorithm'''
    search_engine = SearchEngine('custom')
    search_engine.initStats()
    wrapped_fval_function = (lambda sN : fval_function(sN,weight))
    search_engine.init_search(initial_state, sokoban_goal_state, heur_fn, wrapped_fval_function)
    return search_engine.search(timebound)

def iterative_astar(initial_state, heur_fn, weight=1, timebound=5):  # uses f(n), see how autograder initializes a search line 88
    # IMPLEMENT
    '''Provides an implementation of realtime a-star, as described in the HW1 handout'''
    '''INPUT: a sokoban state that represents the start state and a timebound (number of seconds)'''
    '''OUTPUT: A goal state (if a goal is found), else False as well as a SearchStats object'''
    '''implementation of iterative astar algorithm'''
    time_check = timebound
    remaining = 0
    se = SearchEngine('custom')
    stats = se.initStats()
    flag = (initial_state, stats)
    costbound = (math.inf, math.inf, initial_state.gval + heur_fn(initial_state))
    while(time_check > 0):
        start_time = os.times()[0]
        search_engine = SearchEngine('custom')
        search_engine.initStats()
        wrapped_fval_function = (lambda sN : fval_function(sN,weight))
        search_engine.init_search(initial_state, sokoban_goal_state, heur_fn, wrapped_fval_function)
        value = search_engine.search(time_check, costbound)
        end_time = os.times()[0]
        remaining = end_time - start_time
        time_check -= remaining
        if (value[0] == False):
            return flag
        if ((value[0].gval + heur_fn(value[0])) < costbound[2]):
            costbound = (math.inf, math.inf, (value[0].gval + heur_fn(value[0]))) 
            flag = value
        weight -= 1
    return flag


def iterative_gbfs(initial_state, heur_fn, timebound=5):  # only use h(n)
    # IMPLEMENT
    '''Provides an implementation of anytime greedy best-first search, as described in the HW1 handout'''
    '''INPUT: a sokoban state that represents the start state and a timebound (number of seconds)'''
    '''OUTPUT: A goal state (if a goal is found), else False'''
    '''implementation of iterative gbfs algorithm'''
    time_check = timebound
    remaining = 0
    se = SearchEngine('best_first')
    stats = se.initStats()
    flag = (initial_state, stats)
    costbound = (math.inf, math.inf, math.inf)
    while(time_check > 0):
        start_time = os.times()[0]
        search_engine = SearchEngine('best_first')
        search_engine.initStats()
        search_engine.init_search(initial_state, sokoban_goal_state, heur_fn=heur_fn)
        value = search_engine.search(time_check, costbound)
        end_time = os.times()[0]
        remaining = end_time - start_time
        time_check -= remaining
        if (value[0] == False):
            return flag
        if (value[0].gval < costbound[0]):
            costbound = (value[0].gval, math.inf, math.inf) 
            flag = value
    return flag



