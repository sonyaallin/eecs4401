#   Look for #IMPLEMENT tags in this file. These tags indicate what has
#   to be implemented to complete the warehouse domain.

#   You may add only standard python imports
#   You may not remove any imports.
#   You may not import or otherwise source any of your own files

from asyncio.windows_events import NULL
import os  # for time functions
import math
import re  # for infinity
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

    ########################
    # Function Explanation #
    ########################
    # 1) Check if state is already a goal_state
    # 2) Check if any box is trapped by the obstacles (if the box is trapped robots will not be able to move it - thus heuristics will be infinite)
    # 3) Find the best heuristics from robot to the closest box
    # 4) Compare storage and boxes' locations - if there is a match it means that the box is already placed in storage
    # and therefore there is no need to calculate heuristics for that box (and we can eliminate storage place as well) 
    # 5) Find the best heuristics from box to the closest storage
    ########################
    if sokoban_goal_state(state):
        return 0

    #state.print_state()

    if isTrapped(state):
        return float('inf')

    heur = robotHeur(state)
    storage_occupied = list(set(state.storage).intersection(state.boxes))

    for box_loc in state.boxes:
        if sokoban_goal_state(state):
            return heur     
               
        if box_loc not in storage_occupied:
            minimal = float('inf')
            stored = None

            for storage_loc in state.storage:
                if storage_loc not in storage_occupied:
                    calc = abs(storage_loc[0] - box_loc[0]) + abs(storage_loc[1] - box_loc[1])
                    if (calc < minimal):
                        minimal = calc
                        stored = storage_loc
            heur += minimal
            storage_occupied.append(stored)
    
    return heur

### Helper functions for heur_alternate() ###

def robotHeur(state):
    """
    Return minimal heuristic from one of the robots to box_loc
    """
    heur = 0
    busy_boxes = []

    for robot in state.robots:
        min_r = float('inf')
        box = None
        for box_loc in state.boxes:
            if box_loc not in busy_boxes:
                calc = abs(robot[0] - box_loc[0]) + abs(robot[1] - box_loc[1])
                if (calc < min_r):
                    min_r = calc
                    box = box_loc
        heur += min_r
        busy_boxes.append(box)

    return heur


def isTrapped(state):
    """
    Check all boxes' positions and determine whether at least one of them, is trapped
    """
    for box in state.boxes:
        box_p = {"top"          : (box[0], box[1] - 1),      # top cell
                 "right"        : (box[0] + 1, box[1]),      # right cell
                 "bottom"       : (box[0], box[1] + 1),      # bottom cell         
                 "left"         : (box[0] - 1, box[1])}      # left cell
        
                     
        if (box_p["top"] in state.obstacles) and (box_p["right"] in state.obstacles):
            return True
        elif (box_p["top"] in state.obstacles) and (box_p["left"] in state.obstacles):
            return True
        elif (box_p["bottom"] in state.obstacles) and (box_p["right"] in state.obstacles):
            return True
        elif (box_p["bottom"] in state.obstacles) and (box_p["left"] in state.obstacles):
            return True

    return False

### Helper functions END ###

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
    heur = 0

    for box_loc in state.boxes:
        minimal = float('inf')
        for storage_loc in state.storage:
            minimal = min(abs(storage_loc[0] - box_loc[0]) + abs(storage_loc[1] - box_loc[1]), minimal)
        heur += minimal
    
    return heur

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
    wrapped_fval_function = (lambda sN : fval_function(sN, weight)) 
    search_engine.init_search(initial_state, sokoban_goal_state, heur_fn, wrapped_fval_function)

    return search_engine.search(timebound)

def iterative_astar(initial_state, heur_fn, weight=1, timebound=5):  # uses f(n), see how autograder initializes a search line 88
    # IMPLEMENT
    '''Provides an implementation of realtime a-star, as described in the HW1 handout'''
    '''INPUT: a sokoban state that represents the start state and a timebound (number of seconds)'''
    '''OUTPUT: A goal state (if a goal is found), else False as well as a SearchStats object'''
    '''implementation of iterative astar algorithm'''
    search_engine = SearchEngine("custom")
    wrapped_fval_function = (lambda sN : fval_function(sN, weight)) 
    search_engine.init_search(initial_state, sokoban_goal_state, heur_fn, wrapped_fval_function)

    time_left = timebound
    costbound = (float('inf'), float('inf'), float('inf'))

    solution = (False, None)

    while time_left > 0:
        tmp_solution = search_engine.search(timebound, costbound)

        if solution[0] is False:
            solution = tmp_solution
        elif (solution[0]) and sokoban_goal_state(solution[0]):
            return solution
        elif (tmp_solution[0]) and (tmp_solution[0].gval + heur_fn(tmp_solution[0]) < solution[0].gval + heur_fn(solution[0])):
            solution = tmp_solution
            costbound = (solution[0].gval - 1, float('inf'), float('inf'))

        weight = max(0, weight - 0.1)
        time_left -= tmp_solution[1].total_time

    return solution

def iterative_gbfs(initial_state, heur_fn, timebound=5):  # only use h(n)
    # IMPLEMENT
    '''Provides an implementation of anytime greedy best-first search, as described in the HW1 handout'''
    '''INPUT: a sokoban state that represents the start state and a timebound (number of seconds)'''
    '''OUTPUT: A goal state (if a goal is found), else False'''
    '''implementation of iterative gbfs algorithm'''
    time_record = os.times()[0] + timebound
    time_left = timebound

    search_engine = SearchEngine("best_first")
    search_engine.init_search(initial_state, sokoban_goal_state, heur_fn)

    solution = (False, None)
    costbound = (float('inf'), float('inf'), float('inf'))

    time_left = time_record - os.times()[0]

    while time_left > 0:
        tmp_solution = search_engine.search(time_left - 0.1, costbound)

        time_left = time_record - os.times()[0]

        if tmp_solution[0]:
            if (solution[0]) and sokoban_goal_state(solution[0]):
                return solution
            solution = tmp_solution
            costbound = (solution[0].gval - 1, float('inf'), float('inf'))
        else:
            return (False, None)
    
    return solution




