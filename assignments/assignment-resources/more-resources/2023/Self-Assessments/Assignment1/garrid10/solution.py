#   Look for #IMPLEMENT tags in this file. These tags indicate what has
#   to be implemented to complete the warehouse domain.

#   You may add only standard python imports
#   You may not remove any imports.
#   You may not import or otherwise source any of your own files

import os  # for time functions
import math  # for infinity
from search import *  # for search engines
from sokoban import sokoban_goal_state, SokobanState, Direction, PROBLEMS  # for Sokoban specific classes and problems


def goal_fn(state):
    for box in state.boxes:
        if box not in state.storage:
            return False
    return True


def stuck(state, box, u_storage):
    # returns true if the box is "stuck" (that is the box is not in a storage spot and is cornered or is at an edge
    # and there are no goals in the edges thus it is impossible to move said box to a storage spot)
    northb = (box[1] == state.width - 1 or (box[0], box[1] + 1) in state.obstacles)
    southb = (box[1] == 0 or (box[0], box[1] - 1) in state.obstacles)
    eastb = (box[0] == state.width - 1 or (box[0], box[1] + 1) in state.obstacles)
    westb = (box[0] == 0 or (box[0], box[1] - 1) in state.obstacles)
    # check if the box is cornered in. That is blocked by either a wall or an obstacle in two sides that are not
    # opposites (so the sides blocked must be i.e North and East)
    if (northb or southb) and (eastb or westb):
        return True
    # check if the box is in any edge
    row_edge = box[1] == 0 or box[1] == state.height - 1
    column_edge = box[0] == 0 or box[0] == state.width - 1

    if row_edge:  # if the box is in an edge, in this case either really north or really south, we check if there is an
        # unoccupied storage spot in the same row
        for st in u_storage:
            if st[1] == box[1]:
                return False

    elif column_edge:  # same thing as last if, except with columns.
        for st in u_storage:
            if st[0] == box[0]:
                return False
    # if our box has survived this long it means that there is no unoccupied storage in its row or column. Thus we check
    # if our box is at an edge.
    return row_edge or column_edge


# SOKOBAN HEURISTICS
def heur_alternate(state):
    '''a better heuristic'''
    '''INPUT: a sokoban state'''
    '''OUTPUT: a numeric value that serves as an estimate of the distance of the state to the goal.'''
    # heur_manhattan_distance has flaws.
    # Write a heuristic function that improves upon heur_manhattan_distance to estimate distance between the current state and the goal.
    # Your function should return a numeric value for the estimate of the distance to the goal.
    # EXPLAIN YOUR HEURISTIC IN THE COMMENTS. Please leave this function (and your explanation) at the top of your solution file, to facilitate marking.

    # state.print_state() this is for testing
    x = 0  # this is our heuristic value. We will return this at the end of the program
    # We first want to check if there is any unoccupied storage spots
    unoccupied_stg = []
    for stg in state.storage:
        if stg not in state.boxes:  # We check to see if there is not a box in this storage spot
            unoccupied_stg.append(stg)  # If it is free, we append it

    for box in state.boxes:  # check every box in the state
        if box not in state.storage:  # check if the box is in a storage
            if stuck(state, box, unoccupied_stg):  # check if the box is stuck and thus the puzzle is not solvable
                return 10000000000000000000  # return a ridiculously large number if the state is not solvable
            # we reach this branch of the program if the box we are checking is not in a storage space and it is not
            # stuck.
            x += min(abs(box[0] - stg[0]) + abs(box[1] - stg[1]) for stg in unoccupied_stg) \
                 + min(abs(box[0] - robot[0]) + abs(box[1] - robot[1]) for robot in state.robots)
            # we use the manhattan distance of every box to every storage spot and to every robot to
            # generate a heuristic value
    return x  # we return our heuristic value


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

    minimum_distances = []  # In this list we will store the manhattan distance of each box.
    for box in state.boxes:
        distances = []  # Initiate a list were we will store every distance that a box has to every single storage point
        for stg in state.storage:  # check every box with every storage spot
            distances.append(abs(box[0] - stg[0]) + abs(box[1] - stg[1]))  # add every distance to a list
        minimum_distances.append(min(distances))  # take out the minimum distance of a box with every storage spot
    return sum(minimum_distances)  # return the sum of all the distances.


def fval_function(sN, weight):
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
    '''Provides an implementation of weighted a-star, as described in the HW1 handout'''
    '''INPUT: a sokoban state that represents the start state and a timebound (number of seconds)'''
    '''OUTPUT: A goal state (if a goal is found), else False as well as a SearchStats object'''
    '''implementation of weighted astar algorithm'''

    my_engine = SearchEngine('custom')
    my_engine.init_search(initial_state, goal_fn, heur_fn,
                                   lambda searchNode: fval_function(searchNode, weight))
    my_tup = my_engine.search(timebound)
    return my_tup


def iterative_astar(initial_state, heur_fn, weight=1, timebound=5):  # uses f(n), see how autograder initializes a search line 88
    '''Provides an implementation of realtime a-star, as described in the HW1 handout'''
    '''INPUT: a sokoban state that represents the start state and a timebound (number of seconds)'''
    '''OUTPUT: A goal state (if a goal is found), else False as well as a SearchStats object'''
    '''implementation of iterative astar algorithm'''

    best_sol, searchstats = weighted_astar(initial_state, heur_fn, weight, timebound)
    if not best_sol:
        return best_sol, searchstats
    x = timebound - searchstats.total_time
    my_hval = heur_fn(best_sol)
    my_fval = best_sol.gval + my_hval * weight
    while (x > 0):
        my_engine = SearchEngine('custom')
        my_engine.init_search(initial_state, goal_fn, heur_fn,
                              lambda searchNode: fval_function(searchNode, weight))
        new_sol, searchstats = my_engine.search(x,
                                                (best_sol.gval, my_hval, my_fval))
        x -= searchstats.total_time
        if new_sol:
            new_hval = heur_fn(new_sol)
            new_fval = new_sol.gval + new_hval * weight
            if (new_fval < my_fval):
                best_sol = new_sol
                my_hval = new_hval
                my_fval = new_fval
        else:
            return best_sol, searchstats
    return best_sol, searchstats


def iterative_gbfs(initial_state, heur_fn, timebound=5):  # only use h(n)
    # IMPLEMENT
    '''Provides an implementation of anytime greedy best-first search, as described in the HW1 handout'''
    '''INPUT: a sokoban state that represents the start state and a timebound (number of seconds)'''
    '''OUTPUT: A goal state (if a goal is found), else False'''
    '''implementation of iterative gbfs algorithm'''
    my_engine = SearchEngine('best_first')
    my_engine.init_search(initial_state, goal_fn, heur_fn,
                          lambda searchNode: fval_function(searchNode, 1))
    best_sol, searchstats = my_engine.search(timebound)
    if not best_sol:
        return best_sol, searchstats
    x = timebound - searchstats.total_time
    my_hval = heur_fn(best_sol)
    my_fval = best_sol.gval + my_hval
    while (x > 0):
        new_sol, searchstats = my_engine.search(x,
                                                (best_sol.gval, my_hval, my_fval))
        x -= searchstats.total_time
        if new_sol:
            new_hval = heur_fn(new_sol)
            new_fval = new_sol.gval + new_hval
            if (new_fval < my_fval):
                best_sol = new_sol
                my_hval = new_hval
                my_fval = new_fval
        else:
            return best_sol, searchstats
    return best_sol, searchstats




