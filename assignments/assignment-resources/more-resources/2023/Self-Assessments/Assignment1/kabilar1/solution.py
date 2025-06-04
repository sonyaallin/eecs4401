#   Look for #IMPLEMENT tags in this file. These tags indicate what has
#   to be implemented to complete the warehouse domain.

#   You may add only standard python imports
#   You may not remove any imports.
#   You may not import or otherwise source any of your own files

import os  # for time functions
import math  # for infinity
from search import *  # for search engines
from sokoban import sokoban_goal_state, SokobanState, Direction, PROBLEMS  # for Sokoban specific classes and problems

import numpy as np # Allowed Import @24

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
    # Initially I attempted euclidean distance but that only solved 7 of 20
    # And then I improved on euclidean distance 

    # Import all necessary information 
    boxes = np.array(list(state.boxes), dtype="int")
    storage = np.array(list(state.storage), dtype="int")
    # obstacles = np.array(list(state.obstacles), dtype="int")
    # robots = np.asarray(state.robots)
    
    # # Removing all boxes that are in a storage
    # # Removing all storage that already contain boxes
    # unused_boxes = np.sum(np.sum(storage==boxes[:, None], axis=2) == 2, axis=1) != 1
    # unused_storage = np.sum(np.sum(boxes==storage[:, None], axis=2) == 2, axis=1) != 1

    # boxes = boxes[unused_boxes]
    # storage = storage[unused_storage]

    # if boxes.size == 0:
    #     return 0
      
    # Checking if the box is stuck in a corner or an edge
    # for box_x, box_y in boxes:
    #     up, down, right, left = False, False, False, False
    #     if [box_x, box_y-1] in obstacles or [box_x, box_y-1] in boxes or box_y-1 < 0:
    #         up = True
    #     if [box_x, box_y+1] in obstacles or [box_x, box_y+1] in boxes or box_y+1 >= state.height:
    #         down = True
    #     if [box_x-1, box_y] in obstacles or [box_x-1, box_y] in boxes or box_x-1 < 0:
    #         left = True
    #     if [box_x+1, box_y] in obstacles or [box_x+1, box_y] in boxes or box_x+1 >= state.width:
    #         right = True
        
    #     if (up and left) or (up and right) or (down and left) or (down and right):
    #         return np.inf

    #     if box_x == 0 or box_x == state.width-1:
    #         if box_x not in storage[:, 0]:
    #             return np.inf
        
    #     if box_y == 0 or box_y == state.height-1:
    #         if box_y not in storage[:, 1]:
    #             return np.inf

    # Regular manhattan distance with no each box using only one storage
    boxes_x, boxes_y = boxes[:, 0], boxes[:, 1]
    storage_x, storage_y = storage[:, 0], storage[:, 1]

    dist_x = np.abs(boxes_x[:, None] - storage_x)
    dist_y = np.abs(boxes_y[:, None] - storage_y)

    dist = dist_x + dist_y

    # row, col = scipy.optimize.linear_sum_assignment(dist)

    total_dist = 0

    used_storage = np.ones(storage.shape[0]) == 1
    for i in range(boxes.shape[0]):
        total_dist += np.amin(dist[i][used_storage])
        used_storage[np.argmin(dist[i])] = False


    # dist = np.sum(np.amin(dist_x + dist_y, axis=1))

    # Robots' shortest distance to box
    # robots_x, robots_y = robots[:, 0], robots[:, 1]

    # robots_dist_x = np.abs(robots_x[:, None] - storage_x)
    # robots_dist_y = np.abs(robots_y[:, None] - storage_y)

    # robots_dist = np.sum(np.amin(robots_dist_x + robots_dist_y, axis=1))

    return total_dist #+ (robots_dist / 10)


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

    boxes = np.array(list(state.boxes), dtype="int")
    storage = np.array(list(state.storage), dtype="int")

    boxes_x, boxes_y = boxes[:, 0], boxes[:, 1]
    storage_x, storage_y = storage[:, 0], storage[:, 1]

    dist_x = np.abs(boxes_x[:, None] - storage_x)
    dist_y = np.abs(boxes_y[:, None] - storage_y)

    return np.sum(np.amin(dist_x + dist_y, axis=1))


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

    search_engine = SearchEngine(strategy='custom', cc_level='full')
    search_engine.initStats()

    wrapped_fval_func = lambda sN : fval_function(sN, weight)

    search_engine.init_search(initial_state, sokoban_goal_state, heur_fn, wrapped_fval_func)
    goal_node, stats = search_engine.search(timebound=timebound)

    return goal_node, stats

def iterative_astar(initial_state, heur_fn, weight=1, timebound=5):  # uses f(n), see how autograder initializes a search line 88
    # IMPLEMENT
    '''Provides an implementation of realtime a-star, as described in the HW1 handout'''
    '''INPUT: a sokoban state that represents the start state and a timebound (number of seconds)'''
    '''OUTPUT: A goal state (if a goal is found), else False as well as a SearchStats object'''
    '''implementation of iterative astar algorithm'''
    opt_goal_node, opt_stats = 0, 0
    cost_bound = None

    while timebound > 0:

        search_engine = SearchEngine(strategy='custom', cc_level='full')
        search_engine.initStats()

        wrapped_fval_func = lambda sN : fval_function(sN, weight)

        search_engine.init_search(initial_state, sokoban_goal_state, heur_fn, wrapped_fval_func)
        goal_node, stats = search_engine.search(timebound=timebound, costbound=cost_bound)

        timebound -= stats.total_time

        weight -= (weight // 3)

        if goal_node != False:           
            if opt_goal_node == 0 or opt_goal_node.gval > goal_node.gval:
                hval = heur_fn(initial_state)
                cost_bound = [goal_node.gval, hval, goal_node.gval + hval]
                opt_goal_node, opt_stats = goal_node, stats

    return opt_goal_node, opt_stats

def iterative_gbfs(initial_state, heur_fn, timebound=5):  # only use h(n)
    # IMPLEMENT
    '''Provides an implementation of anytime greedy best-first search, as described in the HW1 handout'''
    '''INPUT: a sokoban state that represents the start state and a timebound (number of seconds)'''
    '''OUTPUT: A goal state (if a goal is found), else False'''
    '''implementation of iterative gbfs algorithm'''
    opt_goal_node, opt_stats = 0, 0

    while timebound > 0:
        search_engine = SearchEngine(strategy='best_first', cc_level='full')
        search_engine.initStats()

        search_engine.init_search(initial_state, sokoban_goal_state, heur_fn)
        goal_node, stats = search_engine.search(timebound=timebound)

        timebound -= stats.total_time

        if goal_node != False:          
            if opt_goal_node == 0 or opt_goal_node.gval > goal_node.gval:
                opt_goal_node, opt_stats = goal_node, stats

    return opt_goal_node, opt_stats