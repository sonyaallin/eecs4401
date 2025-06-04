#   Look for #IMPLEMENT tags in this file. These tags indicate what has
#   to be implemented to complete the warehouse domain.

#   You may add only standard python imports
#   You may not remove any imports.
#   You may not import or otherwise source any of your own files

from dis import dis
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
    distance = 0

    # we want boxes to be closer to storage spots
    distance += heur_manhattan_distance(state)

    # we want robots to be closer to boxes so they can move them
    # multiply by 2 to for priority
    distance += robot_distance(state) * 2

    # we don't want to move boxes to a wall because it limits possible box movements
    # storage spots can be next to walls, so only consider boxes that are not in a storage spot
    # multiply by 2 to for priority
    distance += wall_distance(state) * 2

    return distance

def wall_distance(state):
    '''INPUT: a sokoban state'''
    '''OUTPUT: the number of walls that each box is touching'''
    num_walls = 0
    for box in (state.boxes - state.storage):
        if box[0] == 0 or box[0] == state.width - 1:
            num_walls += 1
        if box[1] == 0 or box[1] == state.height - 1:
            num_walls += 1
    return num_walls

def robot_distance(state):
    '''INPUT: a sokoban state'''
    '''OUTPUT: the sum of the distance of each robots to the closest box'''
    sum = 0
    for robot in state.robots:
        min_distance = math.inf
        for box in state.boxes:
            distance = abs(robot[0] - box[0]) + abs(robot[1] - box[1])
            if (distance < min_distance):
                min_distance = distance
        sum += min_distance
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
        min_distance = math.inf
        for storage in state.storage:
            distance = abs(box[0] - storage[0]) + abs(box[1] - storage[1])
            if (distance < min_distance):
                min_distance = distance
        sum += min_distance
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
    wrapped_fval_function = (lambda sN : fval_function(sN, weight))
    se = SearchEngine('astar', 'full')
    se.init_search(initial_state, sokoban_goal_state, heur_fn, wrapped_fval_function)
    return se.search(timebound, None)

def iterative_astar(initial_state, heur_fn, weight=1, timebound=5):  # uses f(n), see how autograder initializes a search line 88
    # IMPLEMENT
    '''Provides an implementation of realtime a-star, as described in the HW1 handout'''
    '''INPUT: a sokoban state that represents the start state and a timebound (number of seconds)'''
    '''OUTPUT: A goal state (if a goal is found), else False as well as a SearchStats object'''
    '''implementation of iterative astar algorithm'''
    costbound = None
    state = None
    stats = None

    total_time = 0
    while (total_time < timebound):
        wrapped_fval_function = (lambda sN : fval_function(sN, weight))
        se = SearchEngine('astar', 'full')
        se.init_search(initial_state, sokoban_goal_state, heur_fn, wrapped_fval_function)

        # time the search
        start_time = os.times()[0]
        temp_state, temp_stats = se.search(timebound - total_time, costbound)
        end_time = os.times()[0]
        total_time += end_time - start_time

        # update the weight
        weight = math.ceil(weight / 2)

        # update goal state, SearchStats object, and costbound as necessary
        if state is None or temp_state:
            state = temp_state
            stats = temp_stats
        if temp_state:
            costbound = (state.gval, heur_fn(state), 0)

    return state, stats

def iterative_gbfs(initial_state, heur_fn, timebound=5):  # only use h(n)
    # IMPLEMENT
    '''Provides an implementation of anytime greedy best-first search, as described in the HW1 handout'''
    '''INPUT: a sokoban state that represents the start state and a timebound (number of seconds)'''
    '''OUTPUT: A goal state (if a goal is found), else False'''
    '''implementation of iterative gbfs algorithm'''
    costbound = None
    state = None
    stats = None

    total_time = 0
    while (total_time < timebound):
        se = SearchEngine('best_first', 'full')
        se.init_search(initial_state, sokoban_goal_state, heur_fn)

        # time the search
        start_time = os.times()[0]
        temp_state, temp_stats = se.search(timebound - total_time, costbound)
        end_time = os.times()[0]
        total_time += end_time - start_time

        # update goal state, SearchStats object, and costbound as necessary
        if state is None or temp_state:
            state = temp_state
            stats = temp_stats
        if temp_state:
            costbound = (state.gval, 0, 0)

    return state, stats
