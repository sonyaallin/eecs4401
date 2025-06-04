#   Look for #IMPLEMENT tags in this file. These tags indicate what has
#   to be implemented to complete the warehouse domain.

#   You may add only standard python imports
#   You may not remove any imports.
#   You may not import or otherwise source any of your own files

import os  # for time functions
import math  # for infinity
from search import *  # for search engines
# for Sokoban specific classes and problems
from sokoban import sokoban_goal_state, SokobanState, Direction, PROBLEMS

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

    # robot_locs = list(state.robots).copy()
    # h, w = state.height, state.width

    # obstacles = list(state.obstacles).copy()

    # empty_storages = []
    # for storage in state.storage:
    #     x, y = storage
    #     if not((x-1, y) in obstacles and (x+1, y) in obstacles and (x, y-1) in obstacles and (x, y+1) in obstacles):
    #         empty_storages.append(storage)

    # box_list = state.boxes.copy()
    # min_dist = float('inf')
    # for box in state.boxes:
    #     if empty_storages == []:
    #         return float('inf')

    #     x, y = box
    #     # if box is stuck in a corner of obstacles then return infinite
    #     if ((x+1, y) in obstacles or (x-1, y) in obstacles) and ((x, y-1) in obstacles or (x, y+1) in obstacles):
    #         return float('inf')

    #     robot = _find_closest(box, robot_locs)
    #     storage = _find_closest(box, empty_storages)
    #     empty_storages.remove(storage)
    #     robot_locs.remove(robot)
    #     robot_locs.append(storage)
    #     min_dist += calc_dist(robot, box)
    #     min_dist += calc_dist(box, storage)

    # tmp = box_list.pop(0)
    # box_list.append(tmp)

    # while box_list != state.boxes:
    #     total_dist = total_dist_calc(box_list, empty_storages)
    #     if min_dist > total_dist:
    #         min_dist = total_dist
    #     tmp = box_list.pop(0)
    #     box_list.append(tmp)
    # return min_dist
    
    total = 0
    robot_locs = list(state.robots).copy()
    obstacles = list(state.obstacles)
    empty_storages = []
    for storage in state.storage.copy():
        x, y = storage

        # if storage is not surrounded by obstacles (storage is accessable)
        if not((x-1, y) in obstacles and (x+1, y) in obstacles and (x, y-1) in obstacles and (x, y+1) in obstacles):
            empty_storages.append(storage)

    for box in state.boxes:
        # # if all storages are occupied
        if empty_storages == []:
            return float('inf')

        x, y = box
        # if box is stuck in a corner of obstacles then return infinite
        if ((x+1, y) in obstacles or (x-1, y) in obstacles) and ((x, y-1) in obstacles or (x, y+1) in obstacles):
            return float('inf')

        # # if box is stuck in corner of state space
        # if ((x, y) in [(0, 0), (0, state.height-1), (state.width-1, 0), (state.width-1, state.height-1)]):
        #     return float('inf')

        robot = _find_closest(box, robot_locs)
        storage = _find_closest(box, empty_storages)
        empty_storages.remove(storage)  # Remove storage as it is occupied

        total += calc_dist(robot, box)  # Add distance(robot, box) to total
        total += calc_dist(box, storage)  # Add distance(box, storage) to total

        # Update robot position to storage loc
        robot_locs.remove(robot)
        robot_locs.append(storage)

    return total


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
    total = 0
    for box in state.boxes:
        storage = _find_closest(box, state.storage)
        total += calc_dist(box, storage)
    return total


def _find_closest(goal, locations):  # HELPER #################################
    closest_dist = float('inf')
    for loc in locations:
        dist = calc_dist(goal, loc)
        if dist < closest_dist:
            closest_loc = loc
            closest_dist = dist
    return closest_loc


def calc_dist(state1, state2):  # HELPER ###########################
    return abs(state1[0] - state2[0]) + abs(state1[1] - state2[1])


def fval_function(sN, weight):
    # IMPLEMENT
    """
    Provide a custom formula for f-value computation for Anytime Weighted A star.
    Returns the fval of the state contained in the sNode.

    @param sNode sN: A search node (containing a SokobanState)
    @param float weight: Weight given by Anytime Weighted A star
    @rtype: float 
    """
    return sN.gval + (weight * sN.hval)  # CHANGE THIS

# SEARCH ALGORITHMS


def _execute_search(type, initial_state, heur_fn, timebound, costbound=None, weight=None):
    engine = SearchEngine(type)
    if type == 'custom':
        wrapped_fval_function = (lambda sN: fval_function(sN, weight))
        engine.init_search(initial_state, sokoban_goal_state,
                           heur_fn, wrapped_fval_function)
    else:
        engine.init_search(initial_state, sokoban_goal_state, heur_fn)

    return engine.search(timebound, costbound)


def weighted_astar(initial_state, heur_fn, weight, timebound):
    # IMPLEMENT
    '''Provides an implementation of weighted a-star, as described in the HW1 handout'''
    '''INPUT: a sokoban state that represents the start state and a timebound (number of seconds)'''
    '''OUTPUT: A goal state (if a goal is found), else False as well as a SearchStats object'''
    '''implementation of weighted astar algorithm'''

    return _execute_search('custom', initial_state, heur_fn, timebound, None, weight)


# uses f(n), see how autograder initializes a search line 88
def iterative_astar(initial_state, heur_fn, weight=1, timebound=5):
    # IMPLEMENT
    '''Provides an implementation of realtime a-star, as described in the HW1 handout'''
    '''INPUT: a sokoban state that represents the start state and a timebound (number of seconds)'''
    '''OUTPUT: A goal state (if a goal is found), else False as well as a SearchStats object'''
    '''implementation of iterative astar algorithm'''

    best_sol = (initial_state, SearchEngine('custom').initStats())
    costbound = [float('inf'), float('inf'), float('inf')]

    while timebound > 0:
        found_sol = _execute_search('custom',
                                    initial_state, heur_fn, timebound, costbound, weight)
        if found_sol[0] and timebound > found_sol[1].total_time and found_sol[0].gval + heur_fn(found_sol[0]) < costbound[2]:
            costbound[2] = found_sol[0].gval + heur_fn(found_sol[0])
            best_sol = found_sol
        timebound -= found_sol[1].total_time
        weight -= 1
    return best_sol


# only use h(n)
def iterative_gbfs(initial_state, heur_fn, timebound=5):
    # IMPLEMENT
    '''Provides an implementation of anytime greedy best-first search, as described in the HW1 handout'''
    '''INPUT: a sokoban state that represents the start state and a timebound (number of seconds)'''
    '''OUTPUT: A goal state (if a goal is found), else False'''
    '''implementation of iterative gbfs algorithm'''
    best_sol = (initial_state, SearchEngine('best_first').initStats())
    costbound = [float('inf'), float('inf'), float('inf')]

    while timebound > 0:
        found_sol = _execute_search(
            'best_first', initial_state, heur_fn, timebound, costbound)
        if not found_sol[0]:
            return best_sol
        if timebound > found_sol[1].total_time and found_sol[0].gval < costbound[0]:
            costbound[0] = found_sol[0].gval
            best_sol = found_sol
        timebound -= found_sol[1].total_time
    return best_sol
