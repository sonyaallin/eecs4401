#   Look for #IMPLEMENT tags in this file. These tags indicate what has
#   to be implemented to complete the warehouse domain.

#   You may add only standard python imports
#   You may not remove any imports.
#   You may not import or otherwise source any of your own files

import os  # for time functions
import math
from time import time  # for infinity
from search import *  # for search engines
from sokoban import sokoban_goal_state, SokobanState, Direction, PROBLEMS  # for Sokoban specific classes and problems
import numpy as np

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
    # IMPROVE
    est_dist = 0
    boxes = list(state.boxes.difference(state.storage))
    storages = list(state.storage.difference(state.boxes))
    chosen_storages = []
    for box in boxes:
        # Get storage distance
        s = []
        for storage in storages:
            s.append(np.sqrt((box[0] - storage[0]) ** 2 + (box[1] - storage[1]) ** 2))
        chosen_storages.append(s)

        # Get best robot
        min_dist = float('inf')
        r = None
        for robot in state.robots:
            dist = np.sqrt((box[0] - robot[0]) ** 2 + (box[1] - robot[1]) ** 2)
            
            if dist < min_dist:
                min_dist = dist
                r = robot
            
        est_dist += min_dist
            
        # Check if box is surrounded
        surrounded = 0
        for obstacle in state.obstacles:
            if np.abs(box[0] - obstacle[0]) + np.abs(box[1] - obstacle[1]) == 1: surrounded += 1
        if surrounded >= 2: return float('inf') # Box is in corner so it is impossible to get to goal
    chosen_storages = np.array(chosen_storages).T
    for i in range(len(boxes)):
        m = np.argmin(chosen_storages[i])
        est_dist += chosen_storages[i, m]
        chosen_storages[:, m] = float('inf')
    return est_dist
    """
    There are multiple things I tried:
    - Manhattan Distance between each box and its closest storage
    - Euclidean Distance between each box and its closest storage
    - Manhattan Distance between each box and its closest storage and robot
    - Euclidean Distance between each box and its closest storage and robot
    - Other mixes of euclidean and manhattan
    - Adding edge case of being at an edge

    I ended up using Euclidean Distance between each box and its closest storage and robot. This gave me the best result
    of 14 solved problems. The idea is that to push a box into the storage we first need a robot to get to that box. From there
    the robot should push the box into the storage so we essentially have 2 distances to calculate. I use euclidean distance
    as that is what seemed to work best. I then found at that trying to estimate the best storage to put each box into while
    only allowing one box per storage gave an even more accurate result (in the game only one box per storage). I do this
    by calculating the euclidean distance between each box and storage. Then I go through every storage and give it the closest
    box and then remove that box from the list of available boxes.
    I then noticed that if a box was pushed into a corner it made a solution impossible and so I added a case for this so that
    my algorithms would avoid putting a box in a corner. This is done by returning infinity if a box is cornered.
    """

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
    est_dist = 0
    boxes = state.boxes.difference(state.storage)
    storages = state.storage
    for box in boxes:
        min_dist = float('inf')
        for storage in storages:
            dist = np.abs(box[0] - storage[0]) + np.abs(box[1] - storage[1])
            if dist < min_dist:
                min_dist = dist
        est_dist += min_dist
    return est_dist

def fval_function(sN, weight):
    # IMPLEMENT
    """
    Provide a custom formula for f-value computation for Anytime Weighted A star.
    Returns the fval of the state contained in the sNode.

    @param sNode sN: A search node (containing a SokobanState)
    @param float weight: Weight given by Anytime Weighted A star
    @rtype: float
    """
    return weight*sN.hval + sN.gval

# SEARCH ALGORITHMS
def weighted_astar(initial_state, heur_fn, weight, timebound):
    # IMPLEMENT    
    '''Provides an implementation of weighted a-star, as described in the HW1 handout'''
    '''INPUT: a sokoban state that represents the start state and a timebound (number of seconds)'''
    '''OUTPUT: A goal state (if a goal is found), else False as well as a SearchStats object'''
    '''implementation of weighted astar algorithm'''
    wrapped_fval = lambda sN : fval_function(sN,weight)
    se = SearchEngine(strategy='custom')
    se.init_search(initial_state, sokoban_goal_state, heur_fn, wrapped_fval)
    return se.search(timebound)

def iterative_astar(initial_state, heur_fn, weight=1, timebound=5):  # uses f(n), see how autograder initializes a search line 88
    # IMPLEMENT
    '''Provides an implementation of realtime a-star, as described in the HW1 handout'''
    '''INPUT: a sokoban state that represents the start state and a timebound (number of seconds)'''
    '''OUTPUT: A goal state (if a goal is found), else False as well as a SearchStats object'''
    '''implementation of iterative astar algorithm'''
    weight=2.5
    ss = None
    best = StateSpace(None, float('inf'), None)
    costbound = (float('inf'),float('inf'),float('inf'))
    start_time = os.times()[0]
    end_time = start_time + timebound
    se = SearchEngine(strategy='custom')
    while os.times()[0] < end_time:
        wrapped_fval = lambda sN : fval_function(sN,weight)
        se.init_search(initial_state, sokoban_goal_state, heur_fn, wrapped_fval)
        goal, ss = se.search(end_time-os.times()[0], costbound)
        if goal and best.gval > goal.gval:
            best = goal
            costbound = (float('inf'),float('inf'),best.gval)
        weight = max(1, weight*0.95)
    return False if best.gval == float('inf') else best, ss

def iterative_gbfs(initial_state, heur_fn, timebound=5):  # only use h(n)
    # IMPLEMENT
    '''Provides an implementation of anytime greedy best-first search, as described in the HW1 handout'''
    '''INPUT: a sokoban state that represents the start state and a timebound (number of seconds)'''
    '''OUTPUT: A goal state (if a goal is found), else False'''
    '''implementation of iterative gbfs algorithm'''
    ss = None
    best = StateSpace(None, float('inf'), None)
    costbound = (float('inf'),float('inf'),float('inf'))
    start_time = os.times()[0]
    end_time = start_time + timebound
    se = SearchEngine(strategy='best_first')
    se.init_search(initial_state, sokoban_goal_state, heur_fn, heur_fn)
    while os.times()[0] < end_time:
        goal, ss = se.search(end_time-os.times()[0], costbound)
        if goal and best.gval > goal.gval:
            costbound = (goal.gval,float('inf'),float('inf'))
            best = goal
    return False if best.gval == float('inf') else best, ss



