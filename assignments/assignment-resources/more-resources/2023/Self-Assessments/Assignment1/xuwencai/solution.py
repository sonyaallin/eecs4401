#   Look for #IMPLEMENT tags in this file. These tags indicate what has
#   to be implemented to complete the warehouse domain.

#   You may add only standard python imports
#   You may not remove any imports.
#   You may not import or otherwise source any of your own files

import os  # for time functions
import math
from re import A  # for infinity
from search import *  # for search engines
from sokoban import sokoban_goal_state, SokobanState, Direction, PROBLEMS  # for Sokoban specific classes and problems


def heur_alternate(state: SokobanState):
    # IMPLEMENT
    '''a better heuristic'''
    '''INPUT: a sokoban state'''
    '''OUTPUT: a numeric value that serves as an estimate of the distance of the state to the goal.'''

    all_obstacles = get_all_obstacles(state)
    score = 0

    for box in state.boxes:
        if box not in state.storage:
            # what I am doing here is try to prune all the state
            # that can never win in this game, # if I find a box
            # that can never reach to storage point, # it means can never
            # win, then no need to expand more state
            top, bottom = (box[0] - 1, box[1]), (box[0] + 1, box[1])
            left, right = (box[0], box[1] - 1), (box[1] + 1)
            if top in all_obstacles and left in all_obstacles:
                return float('inf')
            if top in all_obstacles and right in all_obstacles:
                return float('inf')
            if bottom in all_obstacles and left in all_obstacles:
                return float('inf')
            if bottom in all_obstacles and right in all_obstacles:
                return float('inf')


            # the heuristic value is based on both the minimum distance
            # from box to storage point, and also the minimum distance
            # from robot to box.
            # I think this really makes sense, since for this game
            # moving from box to 
            # storage point also needs cost, and moving from robot to box need cost
        
            box_to_storage_min_dist = float("inf")
            for point in state.storage:
                cur_dist = abs(box[0] - point[0]) + abs(box[1] - point[1])
                box_to_storage_min_dist  = min(cur_dist, box_to_storage_min_dist )
            score += box_to_storage_min_dist

            robot_to_box_min_dist = float("inf")
            for robot in state.storage:
                cur_dist = abs(box[0] - robot[0]) + abs(box[1] - robot[1])
                robot_to_box_min_dist  = min(cur_dist, robot_to_box_min_dist )
            score += robot_to_box_min_dist
        
    return score


def get_all_obstacles(state: SokobanState):
    # get all the obstacles in the state
    walls = {(-1, j) for j in range(state.width + 1)} | {(i, -1) for i in range(state.height + 1)} \
    |  {(state.height, j) for j in range(state.width + 1)} \
        | {(i, state.width) for i in range(state.height + 1)}

    obstacles = state.obstacles.union(walls).union(state.boxes)

    return obstacles



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
    result = 0
    for box in state.boxes:
        min_dist = float("inf")
        if box not in state.storage:
            for point in state.storage:
                cur_dist = abs(box[0] - point[0]) + abs(box[1] - point[1])
                min_dist = min(cur_dist, min_dist)
        result += min_dist
    return result
        

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

    engine = SearchEngine('custom', 'default')
    wrapped_fval_function = (lambda node : fval_function(node,weight)) 
    engine.init_search(initial_state, sokoban_goal_state, heur_fn, wrapped_fval_function)
    costbound = (float('inf'), float('inf'), float('inf'))
    result = engine.search(timebound, costbound)
    return result


def iterative_astar(initial_state, heur_fn, weight=1, timebound=5):  # uses f(n), see how autograder initializes a search line 88
    # IMPLEMENT
    '''Provides an implementation of realtime a-star, as described in the HW1 handout'''
    '''INPUT: a sokoban state that represents the start state and a timebound (number of seconds)'''
    '''OUTPUT: A goal state (if a goal is found), else False as well as a SearchStats object'''
    '''implementation of iterative astar algorithm'''

    engine = SearchEngine('custom', 'default')

    #init engine

   
    search_timebound = timebound
    costbound = (float('inf'), float('inf'), float('inf'))
 
    best_result = False, None
    start_time, end_time = os.times()[0], os.times()[0] + timebound

    while start_time < end_time:

        engine.init_search(initial_state, sokoban_goal_state, heur_fn, (lambda node : fval_function(node,weight)))
        result = engine.search(search_timebound, costbound)

        start_time, search_timebound = os.times()[0], end_time - os.times()[0]

        if not result[0]:
            return best_result
        
        if result[0].gval < costbound[0]:
            costbound = (result[0].gval, float('inf'), result[0].gval)
            best_result = result
        
        weight *= 0.8

        
            
    return best_result

def iterative_gbfs(initial_state, heur_fn, timebound=5):  # only use h(n)
    # IMPLEMENT
    '''Provides an implementation of anytime greedy best-first search, as described in the HW1 handout'''
    '''INPUT: a sokoban state that represents the start state and a timebound (number of seconds)'''
    '''OUTPUT: A goal state (if a goal is found), else False'''
    '''implementation of iterative gbfs algorithm'''

    engine = SearchEngine('best_first', 'full')

    #init engine

    
    search_timebound = timebound
    costbound = (float('inf'), float('inf'), float('inf'))
    engine.init_search(initial_state, sokoban_goal_state, heur_fn)

    best_result = False, None

    start_time, end_time = os.times()[0], os.times()[0] + timebound

    while start_time < end_time and not engine.open.empty():
        
        result = engine.search(search_timebound, costbound)

        

        if not result[0]:  # if a goal is not found
            return best_result


        if result[0].gval < costbound[0]:
            costbound = (result[0].gval, float('inf'), float('inf'))
            best_result = result
        
        start_time, search_timebound = os.times()[0], end_time - os.times()[0]
    
    return best_result
