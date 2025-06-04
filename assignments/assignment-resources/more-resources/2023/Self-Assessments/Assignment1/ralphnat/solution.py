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


def make_list(f_set):
    lst = []
    for item in f_set:
        lst.append(item)
    return lst


def sort_list(lst):
    # sort lists by x+y
    n = len(lst)
    for i in range(n):
        for j in range(0, n - i - 1):
            if (lst[j][0] + lst[j][1]) > (lst[j + 1][0] + lst[j + 1][1]):
                lst[j], lst[j + 1] = lst[j + 1], lst[j]


def empty_state(state):
    return make_list(state.storage) == []


def heur_alternate(state):
    # IMPLEMENT
    '''a better heuristic'''
    '''INPUT: a sokoban state'''
    '''OUTPUT: a numeric value that serves as an estimate of the distance of the state to the goal.'''
    h_sum = 0
    state_lst = make_list(state.storage)
    bot_lst = make_list(state.robots)
    box_lst = make_list(state.boxes)

    # sort_list(state_lst)
    # sort_list(bot_lst)
    # sort_list(box_lst)

    for box in box_lst:
        i = 0
        min_dist = -1
        bot_loc = -1
        del_goal = -1
        while i < len(state_lst):
            man_dist = abs(box[0] - state_lst[i][0]) + abs(box[1] - state_lst[i][1])

            if man_dist != 0:
                bot_min = -1
                for bot in bot_lst:
                    bot_dist = abs(box[0] - bot[0]) + abs(box[1] - bot[1]) - 1

                    if bot_dist <= bot_min or bot_min == -1:
                        bot_min = bot_dist
                        bot_loc = bot

                man_dist += bot_min

                if man_dist <= min_dist or min_dist == -1:
                    min_dist = man_dist
                    del_goal = state_lst[i]
            else:
                min_dist = 0
                bot_loc = -1
                del_goal = state_lst[i]
                break

            i += 1

        state_lst.remove(del_goal)
        if bot_loc != -1:
            bot_lst[bot_lst.index(bot_loc)] = del_goal
        h_sum += min_dist

    return h_sum


def heur_zero(state):
    '''Zero Heuristic can be used to make A* search perform uniform cost search'''
    return 0


def heur_manhattan_distance(state):
    # IMPLEMENT
    '''admissible sokoban puzzle heuristic: manhattan distance'''
    '''INPUT: a sokoban state'''
    '''OUTPUT: a numeric value that serves as an estimate of the distance of the state to the goal.'''
    man_sum = 0
    for box in state.boxes:
        min_dist = -1
        for storage in state.storage:
            man_dist = abs(box[0] - storage[0]) + abs(box[1] - storage[1])
            if man_dist <= min_dist or min_dist == -1:
                min_dist = man_dist
        man_sum += min_dist
    return man_sum


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
    engine = SearchEngine("custom")  # ??
    wrapped_fval = (lambda sN: fval_function(sN, weight))
    engine.init_search(initial_state, goal_fn=sokoban_goal_state, heur_fn=heur_fn, fval_function=wrapped_fval)
    final, stats = engine.search(timebound)
    if final is None:
        return False, stats
    return final, stats


def iterative_astar(initial_state, heur_fn, weight=1,
                    timebound=5):  # uses f(n), see how autograder initializes a search line 88
    # IMPLEMENT
    '''Provides an implementation of realtime a-star, as described in the HW1 handout'''
    '''INPUT: a sokoban state that represents the start state and a timebound (number of seconds)'''
    '''OUTPUT: A goal state (if a goal is found), else False as well as a SearchStats object'''
    '''implementation of iterative astar algorithm'''

    time_num = os.times()[0]
    final_time = time_num + timebound
    cost = [float("inf"), float("inf"), float("inf")]
    rest_time = timebound

    engine = SearchEngine("custom")  # ??
    wrapped_fval = (lambda sN: fval_function(sN, weight))
    engine.init_search(initial_state, goal_fn=sokoban_goal_state, heur_fn=heur_fn, fval_function=wrapped_fval)
    sol = engine.search(timebound, costbound=cost)

    end = False
    best = sol

    while time_num < final_time and not end:
        weight -= 2

        time_num = os.times()[0]

        if sol[0] is not False:
            best = sol
            x = sol[0].gval
            cost = [x, float("inf"), float("inf")]
            engine.init_search(initial_state, goal_fn=sokoban_goal_state, heur_fn=heur_fn, fval_function=wrapped_fval)
            sol = engine.search(rest_time-0.1, costbound=cost)
        else:
            end = True

        rest_time -= sol[1].total_time
    return best


def iterative_gbfs(initial_state, heur_fn, timebound=5):  # only use h(n)
    # IMPLEMENT
    '''Provides an implementation of anytime greedy best-first search, as described in the HW1 handout'''
    '''INPUT: a sokoban state that represents the start state and a timebound (number of seconds)'''
    '''OUTPUT: A goal state (if a goal is found), else False'''
    '''implementation of iterative gbfs algorithm'''
    engine = SearchEngine("best_first")
    engine.init_search(initial_state, goal_fn=sokoban_goal_state, heur_fn=heur_fn)
    final, stats = engine.search(timebound)
    if final is None:
        return False, stats
    return final, stats
