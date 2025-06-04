#   Look for #IMPLEMENT tags in this file. These tags indicate what has
#   to be implemented to complete the warehouse domain.

#   You may add only standard python imports
#   You may not remove any imports.
#   You may not import or otherwise source any of your own files

import os  # for time functions
import math
from sre_parse import State
from turtle import distance
from unicodedata import east_asian_width  # for infinity
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
    '''
    The hueristic takes into account the distance of the boxes to individual storages, the distance from a robot to a box, 
    and boxes getting stuck.
    '''
    distance = 0
    storages = list(state.storage.copy())
    storage_n = [s[0] for s in storages]
    storage_m = [s[1] for s in storages]
    # check if box is stuck
    for box in state.boxes:
        if box not in state.storage:
            n, m = box
            # box on wall and no storage
            if (n == 0 and 0 not in storage_n) or (n == state.width - 1 and state.width - 1 not in storage_n):
                return float("inf")
            if (m == 0 and 0 not in storage_m) or (m == state.height - 1 and state.height - 1 not in storage_m):
                return float("inf")
            # if box in corner of board
            if (n == 0 and (m == 0 or m == state.height - 1)) or (n == state.width - 1 and (m == 0 or m == state.height - 1)):
                return float("inf")
            # if box unmoveable
            all_obstacles = state.obstacles.union(state.boxes)
            north = n, m + 1
            east = n + 1, m
            south = n, m - 1
            west = n - 1, m
            if (n == 0 or n == state.width - 1) and (north in all_obstacles or south in all_obstacles):
                return float("inf")
            if (m == 0 or m == state.height - 1 or north in all_obstacles or south in all_obstacles) and (east in all_obstacles or west in all_obstacles):
                return float("inf")
        storage_distances = []
        robot_distances = []
        # storage distance from box
        for storage in storages:
            storage_distances.append(abs(box[0] - storage[0]) + abs(box[1] - storage[1]))
        if storage_distances:
            i = storage_distances.index(min(storage_distances))
            distance += min(storage_distances)
            storages.pop(i)
        #distance from robots to box
        for robot in state.robots:
            robot_distances.append(abs(box[0] - robot[0]) + abs(box[1] - robot[1]))
        if robot_distances:
            distance += min(robot_distances)
    return distance

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
    distance = 0
    for box in state.boxes:
        storage_distances = []
        for storage in state.storage:
            storage_distances.append(abs(box[0] - storage[0]) + abs(box[1] - storage[1]))
        if len(storage_distances) > 0:
            distance += min(storage_distances)
    return distance

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
    search_engine = SearchEngine('custom', 'full')
    search_engine.init_search(initial_state, sokoban_goal_state, heur_fn, (lambda sN: fval_function(sN, weight)))

    state = search_engine.search(timebound)

    return state  # CHANGE THIS

def iterative_astar(initial_state, heur_fn, weight=1, timebound=5):  # uses f(n), see how autograder initializes a search line 88
    # IMPLEMENT
    '''Provides an implementation of realtime a-star, as described in the HW1 handout'''
    '''INPUT: a sokoban state that represents the start state and a timebound (number of seconds)'''
    '''OUTPUT: A goal state (if a goal is found), else False as well as a SearchStats object'''
    '''implementation of iterative astar algorithm'''
    state = weighted_astar(initial_state, heur_fn, weight, timebound)

    if state[0]:
        cb = state[0].gval + heur_fn(state[0])
        time_left = timebound - state[1].total_time
        while time_left > 0:
            search_engine = SearchEngine('custom', 'full')
            search_engine.init_search(initial_state, sokoban_goal_state, heur_fn, (lambda sN: fval_function(sN, weight)))
            next_state = search_engine.search(time_left, (float("inf"), float("inf"), cb))
            time_left -= next_state[1].total_time
            if next_state[0]:
                cb = next_state[0].gval + heur_fn(next_state[0])
                state = next_state
    return state

def iterative_gbfs(initial_state, heur_fn, timebound=5):  # only use h(n)
    # IMPLEMENT
    '''Provides an implementation of anytime greedy best-first search, as described in the HW1 handout'''
    '''INPUT: a sokoban state that represents the start state and a timebound (number of seconds)'''
    '''OUTPUT: A goal state (if a goal is found), else False'''
    '''implementation of iterative gbfs algorithm'''
    search_engine = SearchEngine('best_first', 'full')
    search_engine.init_search(initial_state, sokoban_goal_state, heur_fn)
    state = search_engine.search(timebound)

    if state[0]:
        cb = state[0].gval
        time_left = timebound - state[1].total_time
        while time_left > 0:
            next_state = search_engine.search(time_left, (cb, float("inf"), float("inf")))
            time_left -= next_state[1].total_time
            if next_state[0]:
                cb = next_state[0].gval
                state = next_state
    return state
