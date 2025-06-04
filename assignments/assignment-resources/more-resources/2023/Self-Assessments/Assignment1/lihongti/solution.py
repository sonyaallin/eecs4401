#   Look for #IMPLEMENT tags in this file. These tags indicate what has
#   to be implemented to complete the warehouse domain.

#   You may add only standard python imports
#   You may not remove any imports.
#   You may not import or otherwise source any of your own files

import os  # for time functions
import math  # for infinity
import time

from search import *  # for search engines
from sokoban import sokoban_goal_state, SokobanState, Direction, \
    PROBLEMS  # for Sokoban specific classes and problems


# SOKOBAN HEURISTICS COMMENT ------------------------\
# This version of heuristic detect if an obstacles exist in robots' potential path(left, right, up, down)
# then It calculates the all possible distance from robots to boxes, and boxes to storage
# after, find the minimum distance between specific robot, box, and storage
# add that distance to the total cost and remove the box from search list (assume box is in the storage/goal)
# until box is no longer in the search list, terminate the research
def heur_alternate(state: SokobanState):
    # IMPLEMENT
    '''a better heuristic'''
    '''INPUT: a sokoban state'''
    '''OUTPUT: a numeric value that serves as an estimate of the distance of the state to the goal.'''
    # heur_manhattan_distance has flaws.
    # Write a heuristic function that improves upon heur_manhattan_distance to estimate distance between the current state and the goal.
    # Your function should return a numeric value for the estimate of the distance to the goal.
    # EXPLAIN YOUR HEURISTIC IN THE COMMENTS. Please leave this function (and your explanation) at the top of your solution file, to facilitate marking.
    goal_lst = list(state.storage)
    box_lst = list(state.boxes)
    robot_lst = list(state.robots)
    obs_lst = list(state.obstacles)
    total = 0
    while box_lst:
        for rob in robot_lst:
            for obs in obs_lst:
                if near_obstacle(rob, obs):
                    total += 0.5
        robot_dict = froze_to_dict(robot_lst, "R")
        box_dict = froze_to_dict(box_lst, "B")
        goal_dict = froze_to_dict(goal_lst, "S")
        dist_1 = distance_set(robot_dict, box_dict)
        dist_2 = distance_set(box_dict, goal_dict)
        short_dist, r_index, b_index, s_index = shortest_triple(dist_1, dist_2)
        total += short_dist
        robot_lst[r_index] = goal_lst[s_index]
        goal_lst.pop(s_index)
        box_lst.pop(b_index)

    #     print(robot_dict, box_dict, goal_dict)
    # print(total)

    return total


# HELPER FUNCTION 1
def froze_to_dict(tu: list, tag):
    re_dict = {}
    for num, item in enumerate(tu):
        re_dict[tag + str(num)] = item
    return re_dict


# HELPER FUNCTION 2
def distance_set(dict1, dict2):
    '''
    dict example:
    {'R0': (2, 1), 'R1': (2, 2)}
    {'B0': (1, 1), 'B1': (1, 2), 'B2': (4, 1), 'B3': (4, 2)}
    {'R0B0': 1, 'R0B1': 2, 'R0B2': 2, 'R0B3': 3, 'R1B0': 2, 'R1B1': 1, 'R1B2': 3, 'R1B3': 2}
    return:
    '''
    closest_dict = {}
    for k1, v1 in dict1.items():
        for k2, v2 in dict2.items():
            tmp_route = (abs(v1[0] - v2[0]) + abs(v1[1] - v2[1]))
            closest_dict[k1 + k2] = tmp_route
    return closest_dict


# HELPER FUNCTION 3
def shortest_triple(dict1, dict2):
    """
    input:
    {'R0B0': 1, 'R0B1': 2, 'R0B2': 2, 'R0B3': 3, 'R1B0': 2, 'R1B1': 1, 'R1B2': 3, 'R1B3': 2}
    {'B0S0': 2, 'B0S1': 3, 'B0S2': 1, 'B0S3': 2, 'B1S0': 3, 'B1S1': 2, 'B1S2': 2, 'B1S3': 1, 'B2S0': 1, 'B2S1': 2, 'B2S2': 2, 'B2S3': 3, 'B3S0': 2, 'B3S1': 1, 'B3S2': 3, 'B3S3': 2}
    OUT:
    (2, 0, 0, 2) for (min_distance, robot, box, storage)
    """
    all_dict = {}
    re_dict = {}
    for k1, v1 in dict1.items():
        for k2, v2 in dict2.items():
            all_dict[k1 + k2] = v1 + v2

    # filter out result which is not the same box

    for k, v in all_dict.items():
        if k[3] == k[5]:
            re_dict[k] = v

    # find the min key-value pair in the dict
    min_val = math.inf
    tmp_tu = ()
    for k, v in re_dict.items():
        if min_val > v:
            min_val = v
            tmp_tu = (k, v)

    re_tu = tmp_tu[1], int(tmp_tu[0][1]), int(tmp_tu[0][3]), int(tmp_tu[0][7]),
    # print(re_dict)
    return re_tu  # (min_distance, robot, box, storage)


# HELPER FUNCTION 4

def near_obstacle(tu_robot: tuple, tu_obs: tuple):
    """
    input: 2 tuple (int, int) if (1, 2) and (1, 1), near
    out: bool
    """
    x_robot = tu_robot[0]
    y_robot = tu_robot[1]
    test_lst = [(x_robot + 1, y_robot), (x_robot - 1, y_robot),
                (x_robot, y_robot - 1), (x_robot, y_robot + 1)]
    return tu_obs in test_lst


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
    goal_lst = state.storage
    box_lst = state.boxes
    total = 0
    for box in box_lst:
        dist_lst = []
        for g in goal_lst:
            tmp_route = (abs(g[0] - box[0]) + abs(g[1] - box[1]))
            dist_lst.append(tmp_route)
        total += min(dist_lst)

    return total


def fval_function(sN: sNode, weight: float):
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
    se = SearchEngine('custom', 'default')
    wrapped_fval_function = (lambda sN: fval_function(sN, weight))
    se.init_search(initial_state, goal_fn=sokoban_goal_state, heur_fn=heur_fn,
                   fval_function=wrapped_fval_function)
    final, state = se.search(timebound)
    return final, state


# CUSTOM WEIGHT A WITH COST
def custom_weighted_astar(initial_state, heur_fn, weight, timebound, cost_bound):
    # IMPLEMENT
    '''Provides an implementation of weighted a-star, as described in the HW1 handout'''
    '''INPUT: a sokoban state that represents the start state and a timebound (number of seconds)'''
    '''OUTPUT: A goal state (if a goal is found), else False as well as a SearchStats object'''
    '''implementation of weighted astar algorithm'''
    se = SearchEngine('custom', 'default')
    wrapped_fval_function = (lambda sN: fval_function(sN, weight))
    se.init_search(initial_state, goal_fn=sokoban_goal_state, heur_fn=heur_fn,
                   fval_function=wrapped_fval_function)
    final, state = se.search(timebound, costbound=cost_bound)
    return final, state

def iterative_astar(initial_state, heur_fn, weight=1,
                    timebound=5):  # uses f(n), see how autograder initializes a search line 88
    # IMPLEMENT
    '''Provides an implementation of realtime a-star, as described in the HW1 handout'''
    '''INPUT: a sokoban state that represents the start state and a timebound (number of seconds)'''
    '''OUTPUT: A goal state (if a goal is found), else False as well as a SearchStats object'''
    '''implementation of iterative astar algorithm'''
    remain_time = timebound
    weight = 4
    cost = None
    store_lst = []
    final, stat = (False, None)
    while remain_time > 0:

        final, stat = custom_weighted_astar(initial_state, heur_fn, weight,
                                      timebound=remain_time, cost_bound=cost)
        remain_time = remain_time - stat.total_time

        if final is not False:
            store_lst.append((final, stat))
            cost = [final.gval, math.inf, math.inf]
        weight = weight * 0.6
    if len(store_lst) == 0:
        return final, stat
    else:
        return store_lst.pop()


def iterative_gbfs(initial_state, heur_fn, timebound=5):  # only use h(n)
    # IMPLEMENT
    '''Provides an implementation of anytime greedy best-first search, as described in the HW1 handout'''
    '''INPUT: a sokoban state that represents the start state and a timebound (number of seconds)'''
    '''OUTPUT: A goal state (if a goal is found), else False'''
    '''implementation of iterative gbfs algorithm'''
    start_time = os.times()[0]
    remain_time = timebound
    cost = None
    final, stat = (False, None)
    store_lst = []
    while remain_time > 0:
        curr_time = os.times()[0]

        se = SearchEngine("best_first")
        se.init_search(initial_state, goal_fn=sokoban_goal_state, heur_fn=heur_fn)
        final, stat = se.search(remain_time - 0.1, costbound=cost)
        pass_time = curr_time - start_time
        remain_time = remain_time - pass_time
        if final is not False:
            cost = [final.gval, math.inf, math.inf]
            store_lst.append((final, stat))

    if len(store_lst) == 0:
        return final, stat
    else:
        return store_lst.pop()
