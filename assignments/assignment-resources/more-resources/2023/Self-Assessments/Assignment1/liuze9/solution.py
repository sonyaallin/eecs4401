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

    # heur_manhattan_distance didn't take into account that only 1 box can be in a storage space
    # go through boxes not yet in a storage and find the storage closest to it. remove that storage as a possible option for other boxes

    storages = set(state.storage - state.boxes)
    boxes = state.boxes - state.storage
    m = 0
    for box in boxes:
        if box not in state.storage:
            m2 = math.inf
            s = None
            for storage in storages:
                d = abs(storage[0] - box[0]) + abs(storage[1] - box[1])
                if d < m2:
                    s = storage
                    m2 = d
            storages.remove(s)
            m += m2
    
    return m

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
    m = 0
    for box in state.boxes:
        if box not in state.storage:
            m2 = math.inf
            for storage in state.storage:
                d = abs(storage[0] - box[0]) + abs(storage[1] - box[1])
                m2 = min(d, m2)
            m += m2
    return m

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

    return helper(initial_state, heur_fn, weight, timebound)

def helper(initial_state, heur_fn, weight, timebound, costbound=None):
    '''does weighted_astar but also has an option of giving a costbound'''
    se = SearchEngine('custom', 'full')
    wrapped_fval_function = (lambda sN : fval_function(sN,weight)) 
    se.init_search(initial_state, sokoban_goal_state, heur_fn, wrapped_fval_function)
    if costbound != None:
        final, stats = se.search(timebound)
    else:
        final, stats = se.search(timebound, costbound)
    return final, stats


def iterative_astar(initial_state, heur_fn, weight=1, timebound=5):  # uses f(n), see how autograder initializes a search line 88
    # IMPLEMENT
    '''Provides an implementation of realtime a-star, as described in the HW1 handout'''
    '''INPUT: a sokoban state that represents the start state and a timebound (number of seconds)'''
    '''OUTPUT: A goal state (if a goal is found), else False as well as a SearchStats object'''
    '''implementation of iterative astar algorithm'''
    final, stats = weighted_astar(initial_state, heur_fn, weight, timebound)
    if final != False:
        costbound = final.gval
    f = final
    timebound -= stats.total_time

    while timebound > 0 and f != False:
        weight = weight/2
        f, s = helper(initial_state, heur_fn, weight, timebound, (math.inf, math.inf, costbound))
        timebound -= s.total_time
        if f != False:
            final = f
            stats = s
            costbound = f.gval
    return final, stats

def iterative_gbfs(initial_state, heur_fn, timebound=5):  # only use h(n)
    # IMPLEMENT
    '''Provides an implementation of anytime greedy best-first search, as described in the HW1 handout'''
    '''INPUT: a sokoban state that represents the start state and a timebound (number of seconds)'''
    '''OUTPUT: A goal state (if a goal is found), else False'''
    '''implementation of iterative gbfs algorithm'''
    se = SearchEngine('best_first', 'full')

    se.init_search(initial_state, sokoban_goal_state, heur_fn)
    final, stats = se.search(timebound)
    if final != False:
        costbound = final.gval
    f = final
    timebound -= stats.total_time #since time used is already kept track of in search stats I can just use it

    while timebound > 0 and f != False:
        se.init_search(initial_state, sokoban_goal_state, heur_fn)
        f, s = se.search(timebound, (costbound, math.inf, math.inf))
        timebound -= s.total_time
        if f != False:
            final = f
            stats = s
            costbound = f.gval
    return final, stats



