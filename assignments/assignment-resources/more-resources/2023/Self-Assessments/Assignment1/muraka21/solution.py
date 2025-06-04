#   Look for #IMPLEMENT tags in this file. These tags indicate what has
#   to be implemented to complete the warehouse domain.

#   You may add only standard python imports
#   You may not remove any imports.
#   You may not import or otherwise source any of your own files

import os  # for time functions
import math  # for infinity
import time

from search import *  # for search engines
from sokoban import sokoban_goal_state, SokobanState, Direction, PROBLEMS  # for Sokoban specific classes and problems


# ---------------- start of helper functions -----------------
def frozen2list(fs):
    lst = []
    for item in fs:
        lst.append(item)
    return lst

def manhattan_dist(cord1, cord2):
    return abs(cord1[0] - cord2[0]) + abs(cord1[1] - cord2[1])

def path(cord1, cord2):
    path1 = []
    path2 = []
    #vertical moves
    vert = abs(cord1[1] - cord2[1])
    for i in range(vert):
        tup = cord1
        if cord1[1] < cord2[1]:
            tup = (cord1[0], cord1[1] + 1)
        elif cord1[1] > cord2[1]:
            tup = (cord1[0], cord1[1] - 1)
        path1.append(tup)
    path2 = path1[:]
    #horizontal moves
    hori = abs(cord1[0] - cord2[0])
    for i in range(vert):
        tup = cord1
        if cord1[0] < cord2[0]:
            tup = (cord1[0] + 1, cord1[1])
        elif cord1[1] > cord2[1]:
            tup = (cord1[0] - 1, cord1[1])
        path1.append(tup)
        path2.insert(0, tup)
    return frozenset(path1), frozenset(path2)

# ---------------- end of helper functions -----------------


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

    # EXPLANATION:
    # In order to improve the heuristic from heur_manhattan_distance I should take the barriers in the grid
    # into consideration. Another thing that should be taken into consideration is to make sure that we
    # have only one box in one storage, and not match a box to storage that was already used to calculate
    # the distance to a box. So, my approach to achieve this new heuristic is:
    # 1. Create a copy of the storages and make sure that when a distance is measured using a storage, then
    #    that storage is removed from the list, and cannot be used anymore to calculate the distance between
    #    it and a box.
    # 2. I will use the manhattan distance to find the distance between a box and a storage. I will also use
    #    a helper function to find the path from that box to the storage, if there is a barrier in the path
    #    I add 2 to the manhattan distance because it is the minimum required to deviate and reach the goal.
    #    Also note that the helper for the paths returns 2 paths one starting by moving in the x-axis first
    #    and one that starts moving in the y-axis first.

    sum = 0
    storage_cpy = frozen2list(state.storage)
    # loop through all boxes and find the nearest storage to calculate the manhattan distance
    for box in state.boxes:
        # assigning value to min_dist to be compared
        min_dist = state.height + state.width
        # finding the closest storage to the box
        for storage in storage_cpy:
            dist = manhattan_dist(box, storage)
            if dist < min_dist:
                final_storage = storage
                min_dist = dist
        # removing storage from list since it was used already
        storage_cpy.remove(final_storage)
        # here I am seeing if there is an obstacle in the way of the manhattan path, and if there is I will add 2 to the distance,
        # because it is the minimum required to deviate and reach the target
        # the two paths are either start by walking in the horizontal direction or start in the vertical direction
        paths = path(box, final_storage)
        if paths[0].isdisjoint(state.obstacles) or paths[1].isdisjoint(state.obstacles):
            sum += min_dist
        else:
            sum += min_dist + 2

    return sum  # CHANGE THIS

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
    # loop through all boxes and find the nearest storage to calculate the manhattan distance
    for box in state.boxes:
        # assigning value to min_dist to be compared
        min_dist = state.height + state.width
        # finding the closest storage to the box
        for storage in state.storage:
            dist = manhattan_dist(box, storage)
            if dist < min_dist:
                min_dist = dist
        # updating sum
        sum += min_dist
    return sum  # CHANGE THIS

def fval_function(sN, weight):
    # IMPLEMENT
    """
    Provide a custom formula for f-value computation for Anytime Weighted A star.
    Returns the fval of the state contained in the sNode.

    @param sNode sN: A search node (containing a SokobanState)
    @param float weight: Weight given by Anytime Weighted A star
    @rtype: float
    """
    # f(node) = g(node) + w * h(node)
    return sN.gval + weight * sN.hval #CHANGE THIS

# SEARCH ALGORITHMS
def weighted_astar(initial_state, heur_fn, weight, timebound):
    # IMPLEMENT
    '''Provides an implementation of weighted a-star, as described in the HW1 handout'''
    '''INPUT: a sokoban state that represents the start state and a timebound (number of seconds)'''
    '''OUTPUT: A goal state (if a goal is found), else False as well as a SearchStats object'''
    '''implementation of weighted astar algorithm'''

    wrapped_fval_function = (lambda sN : fval_function(sN, weight))
    search_engine = SearchEngine('custom')
    search_engine.init_search(initial_state, sokoban_goal_state, heur_fn, wrapped_fval_function)
    result = search_engine.search(timebound)
    return result[0], result[1]  # CHANGE THIS

def iterative_astar(initial_state, heur_fn, weight=1, timebound=5):  # uses f(n), see how autograder initializes a search line 88
    # IMPLEMENT
    '''Provides an implementation of realtime a-star, as described in the HW1 handout'''
    '''INPUT: a sokoban state that represents the start state and a timebound (number of seconds)'''
    '''OUTPUT: A goal state (if a goal is found), else False as well as a SearchStats object'''
    '''implementation of iterative astar algorithm'''

    start_time = time.time()
    # performing weighted A*
    wrapped_fval_function = (lambda sN : fval_function(sN, weight))
    search_engine = SearchEngine('custom')
    search_engine.init_search(initial_state, sokoban_goal_state, heur_fn, wrapped_fval_function)
    result = search_engine.search(timebound)
    if result[0] == False:
        return result
    cost = result[0].gval
    better_result = result
    costbound = [0, 0, cost]
    while (time.time() - start_time) < timebound:
        new_result = search_engine.search(timebound, costbound)
        if new_result[0] != False:
            new_cost = new_result[0].gval
            if cost < new_cost:
                better_result = new_result
    return better_result #CHANGE THIS


def iterative_gbfs(initial_state, heur_fn, timebound=5):  # only use h(n)
    # IMPLEMENT
    '''Provides an implementation of anytime greedy best-first search, as described in the HW1 handout'''
    '''INPUT: a sokoban state that represents the start state and a timebound (number of seconds)'''
    '''OUTPUT: A goal state (if a goal is found), else False'''
    '''implementation of iterative gbfs algorithm'''
    start_time = time.time()
    wrapped_fval_function = (lambda sN : fval_function(sN, 1))
    search_engine = SearchEngine('best_first')
    search_engine.init_search(initial_state, sokoban_goal_state, heur_fn, wrapped_fval_function)
    result = search_engine.search(timebound)
    if result[0] == False:
        return result
    cost = result[0].gval
    better_result = result
    costbound = [cost, 0, 0]
    while (time.time() - start_time) < timebound:
        new_result = search_engine.search(timebound, costbound)
        if new_result[0] != False:
            new_cost = new_result[0].gval
            if cost < new_cost:
                better_result = new_result
    return better_result  # CHANGE THIS







