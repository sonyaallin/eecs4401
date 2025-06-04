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
    #Checks for closeness of robots to target boxes. Checks for distance of boxes to storages. Checks for corner boxes, and for boxes getting stuck on edges.

    boxes = state.boxes
    storages = state.storage
    robots = state.robots
    obstacles = state.obstacles
    unpassable = list(obstacles.union(boxes.union(robots)))

    man_sum = 0
    x = 0
    y = 1

    edge_storages = [False, False, False, False]
    corner_storages = []
    left_side = 0
    right_side = 1
    top = 2
    bottom = 3

    boxes_checked = False
    for j in storages:
        if j[x] == 0:
            edge_storages[left_side] = True
        elif j[x] == state.width - 1:
            edge_storages[right_side] = True
        if j[y] == 0:
            edge_storages[top] = True
        elif j[y] == state.height - 1:
            edge_storages[bottom] = True

        if j[x] == 0 and (j[y] == state.height - 1 or j[y] == 0):
            corner_storages.append(j)
        elif j[x] == state.width - 1 and (j[y] == state.height - 1 or j[y] == 0):
            corner_storages.append(j)

    for j in storages:
        dists = {}
        for i in boxes:
            if not boxes_checked:
                robot_dists = {}
                if not (i in storages):
                    for k in robots:
                        robot_dists[(abs(i[x] - k[x]) + abs(i[y] - k[y]))] = k
                    minrobotdists = min(robot_dists)
#                    man_sum += obstacle_check(robot_dists[minrobotdists], i, unpassable)
                    man_sum += minrobotdists
                if not (i in corner_storages):
                    if i[x] == 0 and (i[y] == state.height - 1 or i[y] == 0):
                        return math.inf
                    if i[x] == state.width - 1 and (i[y] == state.height - 1 or i[y] == 0):
                        return math.inf
                if i[x] == 0:
                    if not edge_storages[left_side]:
                        return math.inf
                elif i[x] == state.width - 1:
                    if not edge_storages[right_side]:
                        return math.inf
                elif i[y] == 0:
                    if not edge_storages[top]:
                        return math.inf
                elif i[y] == state.height - 1:
                    if not edge_storages[bottom]:
                        return math.inf
                #
#                if is_perma_blocked(i, state, []):
 #                   return math.inf
            dists[(abs(i[x] - j[x]) + abs(i[y] - j[y]))] = i
        boxes_checked = True
        mindist = min(dists)
#        man_sum += obstacle_check(dists[mindist], j, unpassable)
        man_sum += mindist

    return man_sum  # CHANGE THIS

def between(tup, dims):
    if 0 <= tup[0] and tup[0] < dims[0] and 0 <= tup[1] and tup[1] < dims[1]:
        return True
    return False

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
    boxes = state.boxes
    storages = state.storage

    man_sum = 0

    x = 0
    y = 1
    for i in boxes:
        dists = []
        for j in storages:
            dists.append(abs(i[x] - j[x]) + abs(i[y] - j[y]))
        man_sum = man_sum + min(dists)

    return man_sum  # CHANGE THIS

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

    search_engine = SearchEngine('custom')
    wrapped_fval_function = (lambda sN: fval_function(sN, weight))
    search_engine.init_search(initial_state, sokoban_goal_state, heur_fn, wrapped_fval_function)
    return search_engine.search(timebound)

def weighted_astar_helper(initial_state, heur_fn, weight, timebound, costbound):
    search_engine = SearchEngine('custom')
    wrapped_fval_function = (lambda sN: fval_function(sN, weight))
    search_engine.init_search(initial_state, sokoban_goal_state, heur_fn, wrapped_fval_function)
    return search_engine.search(timebound, costbound)

def iterative_astar(initial_state, heur_fn, weight=1, timebound=5):  # uses f(n), see how autograder initializes a search line 88
    # IMPLEMENT
    '''Provides an implementation of realtime a-star, as described in the HW1 handout'''
    '''INPUT: a sokoban state that represents the start state and a timebound (number of seconds)'''
    '''OUTPUT: A goal state (if a goal is found), else False as well as a SearchStats object'''
    '''implementation of iterative astar algorithm'''

    start_time = os.times()[0]
    w = weight
    time_diff = os.times()[0] - start_time
    solution = weighted_astar(initial_state, heur_fn, w, timebound - time_diff)
    #time_left = time_left - (os.times()[0] - start_time)
    time_diff = os.times()[0] - start_time
    final_solution = solution
    if(solution[0] != False):
        best_cost = []
        best_cost.append(solution[0].gval)
        best_cost.append(solution[0].gval)
        best_cost.append(solution[0].gval)
    #solution_list.append(weighted_astar(initial_state, heur_fn, w, time_diff)[0])
    #time_diff = os.times()[0] - time
    while (solution[0] != False and time_diff < timebound):
        w = 1 + (weight - 1) * ((timebound - time_diff)/timebound)
        solution = weighted_astar_helper(initial_state, heur_fn, w, timebound - time_diff, best_cost)
        if solution[0] != False:
            final_solution = solution
            best_cost[0] = (solution[0].gval)
            best_cost[1] = (solution[0].gval)
            best_cost[2] = (solution[0].gval)
            time_diff = os.times()[0] - start_time

    return final_solution

def iterative_gbfs(initial_state, heur_fn, timebound=5):  # only use h(n)
    # IMPLEMENT
    '''Provides an implementation of anytime greedy best-first search, as described in the HW1 handout'''
    '''INPUT: a sokoban state that represents the start state and a timebound (number of seconds)'''
    '''OUTPUT: A goal state (if a goal is found), else False'''
    '''implementation of iterative gbfs algorithm'''
    return None, None #CHANGE THIS


