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

    # My heuristic is the sum of the averages of:
    #       Manhattan distance of each box to nearest unused storage point and
    #       Manhattan Distance of each box to the nearest robot
    # taking into consideration blockages that get a terrible heuristic ie stuck boxes
    s_man_dist = 0
    d_boxes = set(state.boxes).intersection(set(state.storage))
    r_boxes = set(state.boxes).difference(d_boxes)
    r_storage = set(state.storage).difference(d_boxes)
    for box in r_boxes:
        no_move_d = (box[1] == 0) or (Direction('down', (0, 1)).move(box) in (state.obstacles or r_boxes or d_boxes))
        no_move_u = (box[1] == state.height) or (Direction('up', (0, -1)).move(box) in (
                state.obstacles or r_boxes or d_boxes))

        no_move_l = (box[0] == 0) or (Direction('left', (-1, 0)).move(box) in (state.obstacles or r_boxes or d_boxes))
        no_move_r = (box[0] == state.width) or (Direction('right', (1, 0)).move(box) in (state.obstacles or r_boxes or
                                                                                      d_boxes))

        if (no_move_u and no_move_d) or (no_move_l and no_move_r):
            return math.inf
        curr_min = math.inf
        c_rb = None
        for rb in state.robots:
            if not c_rb:
                c_rb = rb
            else:
                if (abs(rb[0] - box[0]) + abs(rb[1] - box[1])) < (abs(c_rb[0] - box[0]) + abs(c_rb[1] - box[1])):
                    c_rb = rb

        for storage in r_storage:
            side_wall_stuck = ((box[0] == 0) or (box[0] == state.width)) and (box[0] - storage[0] != 0)
            top_bot_wall_stuck = ((box[1] == state.height) or (box[1] == 0)) and (box[1] - storage[1] != 0)
            if side_wall_stuck or top_bot_wall_stuck:
                return math.inf

            curr = abs(box[0] - storage[0]) + abs(box[1] - storage[1])
            if curr < curr_min:
                curr_min = curr

        s_man_dist += ((curr_min + abs(c_rb[0] - box[0]) + abs(c_rb[1] - box[1])) / 2)
    return s_man_dist  # Change this


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
    s_man_dist = 0
    for box in state.boxes:
        curr_min = math.inf
        for storage in state.storage:
            curr = abs(box[0] - storage[0]) + abs(box[1] - storage[1])
            if curr < curr_min:
                curr_min = curr
        if curr_min != math.inf:
            s_man_dist += curr_min
    return s_man_dist


def fval_function(sN, weight):
    # IMPLEMENT
    """
    Provide a custom formula for f-value computation for Anytime Weighted A star.
    Returns the fval of the state contained in the sNode.

    @param sNode sN: A search node (containing a SokobanState)
    @param float weight: Weight given by Anytime Weighted A star
    @rtype: float
    """
    r = sN.gval + (weight * sN.hval)
    return r


# SEARCH ALGORITHMS
def weighted_astar(initial_state, heur_fn, weight, timebound):
    # IMPLEMENT    
    '''Provides an implementation of weighted a-star, as described in the HW1 handout'''
    '''INPUT: a sokoban state that represents the start state and a timebound (number of seconds)'''
    '''OUTPUT: A goal state (if a goal is found), else False as well as a SearchStats object'''
    '''implementation of weighted astar algorithm'''

    wrapped_fval_function = (lambda sN: fval_function(sN, weight))
    se = SearchEngine('custom', 'default')

    se.init_search(initial_state, sokoban_goal_state, heur_fn, wrapped_fval_function)

    return se.search(timebound)


def iterative_astar(initial_state, heur_fn, weight=1,
                    timebound=5):  # uses f(n), see how autograder initializes a search line 88
    # IMPLEMENT
    '''Provides an implementation of realtime a-star, as described in the HW1 handout'''
    '''INPUT: a sokoban state that represents the start state and a timebound (number of seconds)'''
    '''OUTPUT: A goal state (if a goal is found), else False as well as a SearchStats object'''
    '''implementation of iterative astar algorithm'''
    # Time management
    time = os.times()[0]
    end = time + timebound
    new = timebound
    # Initial weighted_astar search
    best = weighted_astar(initial_state, heur_fn, weight, timebound)
    cost = (math.inf, math.inf, math.inf)
    new_w = weight * 0.36 # change weight for more optimality
    if best[0]: # improving cost boundaries if possible
        gval = best[0].gval
        hval = heur_fn(best[0])
        fval = gval + hval
        cost = (math.inf, math.inf, fval)
    while time < end: # Continue searching if time not up
        diff_time = os.times()[0] - time
        time = os.times()[0]  # Get current time
        new -= diff_time
        res = weighted_astar(initial_state, heur_fn, new_w, new)
        if res[0]:
            res_gval = res[0].gval
            res_hval = heur_fn(res[0])
            if res_hval + res_gval <= cost[2]:
                cost = (math.inf, math.inf, res_hval + res_gval)
                best = res
        new_w *= 0.6  # change weight for more optimality
    return best



def iterative_gbfs(initial_state, heur_fn, timebound=5):  # only use h(n)
    # IMPLEMENT
    '''Provides an implementation of anytime greedy best-first search, as described in the HW1 handout'''
    '''INPUT: a sokoban state that represents the start state and a timebound (number of seconds)'''
    '''OUTPUT: A goal state (if a goal is found), else False'''
    '''implementation of iterative gbfs algorithm'''

    # Time management
    time = os.times()[0]
    end = time + timebound
    new = timebound

    # Initialize search engine
    se = SearchEngine('best_first', 'default')
    se.init_search(initial_state, sokoban_goal_state, heur_fn)
    cost = (math.inf, math.inf, math.inf)

    best = se.search(new, cost) # initial search
    if best[0]: # improve cost for optimality if possible
        cost = (best[0].gval, math.inf, math.inf)
    while time < end: # keep running till time runs out
        diff_time = os.times()[0] - time
        time = os.times()[0]  # Get current time
        new -= diff_time
        res = se.search(new, cost)
        if res[0] and res[0].gval <= cost[0]: # update cost and best when better solution is found
            cost = (res[0].gval, math.inf, math.inf)
            best = res
    return best
