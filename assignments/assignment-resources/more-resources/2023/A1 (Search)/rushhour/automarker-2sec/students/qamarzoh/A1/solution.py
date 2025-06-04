#   Look for #IMPLEMENT tags in this file. These tags indicate what has
#   to be implemented to complete the Rush Hour domain.

#   You may add only standard python imports (numpy, itertools are both ok).
#   You may not remove any imports.
#   You may not import or otherwise source any of your own files.

import os  # you will likely want this for timing functions
import math # for infinity
from search import *  # for search engines
from rushhour import *


# RUSH HOUR GOAL TEST
def rushhour_goal_fn(state):
    # IMPLEMENT
    '''a Rush Hour Goal Test'''
    '''INPUT: a parking state'''
    '''OUTPUT: True, if satisfies the goal, else false.'''

    for v in state.vehicle_list:
        if v.is_goal:
            if not v.is_horizontal:
                if state.get_board_properties()[2] == "N" and v.loc == state.get_board_properties()[1]:
                    return True
                if state.get_board_properties()[2] == "S" and v.loc[1] + v.length - 1 == state.get_board_properties()[1][0]:
                    return True
            if v.is_horizontal:
                if state.get_board_properties()[2] == "W" and v.loc == state.get_board_properties()[1]:
                    return True
                if state.get_board_properties()[2] == "E" and v.loc[0] + v.length - 1 == state.get_board_properties()[1][1]:
                    return True

            else:
                return False


# RUSH HOUR HEURISTICS
def heur_alternate(state):
    # IMPLEMENT
    '''a better heuristic'''
    '''INPUT: a tokyo parking state'''
    '''OUTPUT: a numeric value that serves as an estimate of the distance of the state to the goal.'''
    # heur_min_moves has obvious flaws.
    # Write a heuristic function that improves upon heur_min_moves to estimate distance between the current state and the goal.
    # Your function should return a numeric value for the estimate of the distance to the goal.
    # EXPLAIN YOUR HEURISTIC IN THE COMMENTS. Please leave this function (and your explanation) at the top of your solution file, to facilitate marking.

    # similar to heur_min, but takes direction into consideration
    e = 0
    size, gl, gd, = state.get_board_properties()
    for v in state.get_vehicle_statuses():
        if v[4]:  # if gv
            # state.print_state()
            # print(state.get_board_properties())
            vn, vloc, vlength, h, g = v

            # print(v)
            if v[3]:  # if horizontal
                if gl[0] <= vloc[0]:
                    if gd == "W":
                        # closest distance (from head)
                        e = abs((gl[0]) - (vloc[0]))
                    if gd == "E":
                        # other direction
                        e = size[1] - (abs((gl[0]) - (vloc[0]))) - 1

                else:
                    if gd == "E":
                        # closest distance (from tail)
                        e = abs((gl[0]) - (vloc[0] + (vlength - 1)))
                    if gd == "W":
                        # other direction
                        e = size[1] - (abs((gl[0]) - (vloc[0] + (vlength - 1)))) - 1

            if not v[3]:  # if not horizontal
                if gl[0] <= vloc[0]:
                    if gd == "N":
                        # closest distance (from head)
                        e = abs((gl[1]) - (vloc[1]))
                    if gd == "S":
                        # other direction
                        e = size[0] - (abs((gl[1]) - (vloc[1]))) - 1

                else:
                    if gd == "S":
                        # closest distance (from tail)
                        e = abs((gl[1]) - (vloc[1] + (vlength - 1)))
                    if gd == "N":
                        # other direction
                        e = size[0] - (abs((gl[1]) - (vloc[1] + (vlength - 1)))) - 1

            return e


def heur_min_dist(state):
    #IMPLEMENT
    '''admissible tokyo parking puzzle heuristic'''
    '''INPUT: a tokyo parking state'''
    '''OUTPUT: a numeric value that serves as an estimate of the distance of the state to the goal.'''
    # We want an admissible heuristic, which is an optimistic heuristic.
    # It must never overestimate the cost to get from the current state to the goal.
    # Getting to the goal requires one move for each tile of distance.
    # Since the board wraps around, there will be two different directions that lead to a goal.
    # NOTE that we want an estimate of the number of moves required from our current state
    # 1. Proceeding in the first direction, let MOVES1 =
    #    number of moves required to get to the goal if it were unobstructed and if we ignore the orientation of the goal
    # 2. Proceeding in the second direction, let MOVES2 =
    #    number of moves required to get to the goal if it were unobstructed and if we ignore the orientation of the goal
    #
    # Our heuristic value is the minimum of MOVES1 and MOVES2 over all goal vehicles.
    # You should implement this heuristic function exactly, and you can improve upon it in your heur_alternate
    moves1 = 0
    moves2 = 0

    for v in state.get_vehicle_statuses():
        if v[4]:  # if gv
            # state.print_state()
            # print(state.get_board_properties())

            # print(v)
            if v[3]:  # if horizontal
                # closest distance
                if state.get_board_properties()[1][0] <= v[1][0]:
                    # distance from head
                    moves1 = abs((state.get_board_properties()[1][0]) - (v[1][0]))
                else:
                    # distance from tail
                    moves1 = abs((state.get_board_properties()[1][0]) - (v[1][0] + (v[2] - 1)))

                # other direction
                moves2 = state.get_board_properties()[0][1] - moves1 - 1
            if not v[3]:  # if not horizontal
                # closest distance
                if state.get_board_properties()[1][1] <= v[1][1]:
                    # distance from head
                    moves1 = abs(state.get_board_properties()[1][1] - v[1][1])
                else:
                    # distance from tail
                    moves1 = abs(state.get_board_properties()[1][1] - (v[1][1]+(v[2] - 1)))

                # other direction
                moves2 = state.get_board_properties()[0][0] - moves1 - 1

            # print(moves1, moves2)
            return min(moves1, moves2)


def heur_zero(state):
    '''Zero Heuristic can be used to make A* search perform uniform cost search'''
    return 0


def fval_function(sN, weight):
    # IMPLEMENT
    """
    Provide a custom formula for f-value computation for Weighted A star.
    Returns the fval of the state contained in the sNode.

    @param sNode sN: A search node (containing a SokobanState)
    @param float weight: Weight given by Weighted A star
    @rtype: float
    """
    return weight*sN.hval+sN.gval


def fval_function_XUP(sN, weight):
    #IMPLEMENT
    """
    Another custom formula for f-value computation for Weighted A star.
    Returns the fval of the state contained in the sNode.
    XUP causes the best-first search to explore near-optimal paths near the end of a path.

    @param sNode sN: A search node (containing a RushHour State)
    @param float weight: Weight given by Weighted A star
    @rtype: float
    """
    return (1/(2*weight)) * (sN.gval + sN.hval + ((sN.gval+sN.hval)**2 + 4*weight*(weight-1)*sN.hval**2)**(1/2))


def fval_function_XDP(sN, weight):
    #IMPLEMENT
    """
    A third custom formula for f-value computation for Weighted A star.
    Returns the fval of the state contained in the sNode.
    XDP causes the best-first search to explore near-optimal paths near the start of a path.

    @param sNode sN: A search node (containing a RushHour State)
    @param float weight: Weight given by Weighted A star
    @rtype: float
    """
    return (1/(2*weight)) * (sN.gval + ((2*weight)-1)*sN.hval + ((sN.gval-sN.hval)**2 + 4*weight*sN.gval*sN.hval)**(1/2))


# SEARCH ALGORITHMS
def weighted_astar(initial_state, heur_fn, weight, timebound, costbound = (float(math.inf), float(math.inf), float(math.inf))):
    # IMPLEMENT
    """
    Provides an implementation of weighted a-star, as described in the HW1 handout'''
    INPUT: a rushhour state that represents the start state and a timebound (number of seconds)
    OUTPUT: A goal state (if a goal is found), else False as well as a SearchStats object
    implementation of weighted astar algorithm

    @param initial_state: A RushHour State
    @param heur_fn: The heuristic to use
    @param weight: The weight to use
    @param timebound: The timebound to enforce
    @param costbound: The costbound to enforce, if any
    @rtype: (Rushour State, SearchStats) if solution is found, else (False, SearchStats)
    """

    s = SearchEngine("custom")
    s.init_search(initial_state, lambda st: rushhour_goal_fn(st), heur_fn, lambda sN: fval_function(sN, weight))
    return s.search(timebound, costbound)
    #return False, None #REPLACE THIS!!


def iterative_astar(initial_state, heur_fn, weight=1, timebound=5):  # uses f(n), see how autograder initializes a search
    # IMPLEMENT
    """
    Provides an implementation of iterative a-star, as described in the HW1 handout
    INPUT: a rushhour state that represents the start state and a timebound (number of seconds)
    OUTPUT: A goal state (if a goal is found), else False as well as a SearchStats object
    implementation of weighted astar algorithm

    @param initial_state: A RushHour State
    @param heur_fn: The heuristic to use
    @param weight: The weight to begin with during the first iteration (this should change)
    @param timebound: The timebound to enforce
    @rtype: (Rushour State, SearchStats) if solution is found, else (False, SearchStats)
    """

    r = weighted_astar(initial_state, heur_fn, weight, timebound)
    t = r[1].total_time
    while t < timebound:
        r = weighted_astar(initial_state, heur_fn, weight, timebound - t, (r[0].index, r[0].index, math.inf))
        t += r[1].total_time
    return r
    # return False, None #REPLACE THIS!!


def iterative_gbfs(initial_state, heur_fn, timebound=5):  # only use h(n)
    # IMPLEMENT
    """
    Provides an implementation of anytime greedy best-first search, as described in the HW1 handout
    INPUT: a rush hour state that represents the start state and a timebound (number of seconds)
    OUTPUT: A goal state (if a goal is found), else False

    @param initial_state: A RushHour State
    @param heur_fn: The heuristic to use
    @param timebound: The timebound to enforce
    @rtype: (Rushour State, SearchStats) if solution is found, else (False, SearchStats)
    """

    s = SearchEngine("best_first")
    s.init_search(initial_state, lambda st: rushhour_goal_fn(st), heur_fn)
    r = s.search(timebound)
    t = r[1].total_time
    while t < timebound:
        s.init_search(initial_state, lambda st: rushhour_goal_fn(st), heur_fn)
        r = s.search(timebound, (r[0].index, math.inf, math.inf))
        t += r[1].total_time
    return r
    #return False, None #REPLACE THIS!!

