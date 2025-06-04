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

    """
    soln1
    Find manhattan distance between a box_loc and a storage and then remove the
    storage point so that every box has its unique storage. 
    
    
    total_m_dis = 0
    lst_sp = list(state.storage)
    for box in state.boxes:
        curr_sp = shortest_manhattan_distance_storage(box, lst_sp)
        m_dis = calc_manhattan_distance(box, curr_sp)
        total_m_dis += m_dis
        lst_sp.remove(curr_sp)

    return total_m_dis  # CHANGE THIS
    """


    """
    soln2
    Find manhattan distance between a robot and a box plus the manhattan distance
    between a box and a storage point. Whenever encountering an obstacle along 
    the path from box to storage point, add one to the total step count.
    """
    step_count = 0
    infinity = float("inf")
    # check if current state has any available movement
    if check_corner(state):
        return infinity

    # calculate the cumulative manhattan distance from a robot to a box and add
    # the number of obstacles in the area
    for box in state.boxes:
        min_c = infinity
        sp = available_storage(box, state)
        for storage in sp:
            min_c = min(calc_manhattan_distance(box, storage) +
                        num_of_obs(box, storage, state), min_c)
        step_count += min_c

    # calculate the cumulative manhattan distance from a box to a obstacle and
    # add the number of obstacles in the area
    for robot in state.robots:
        min_c = infinity
        for box in state.boxes:
            min_c = min(calc_manhattan_distance(robot, box) +
                        num_of_obs(robot, box, state), min_c)
        step_count += min_c

    return step_count


def num_of_obs(start, end, state):
    """
    Return the number of obstacles in rectangle area formed by start and end
    positions.
    """
    # making the rectangle area
    start_x = start[0]
    start_y = start[1]
    end_x = end[0]
    end_y = end[1]
    upper = max(start_y, end_y)
    lower = min(start_y, end_y)
    left = min(start_x, end_x)
    right = max(start_x, end_x)

    count = 0

    for obs in state.obstacles:
        if (left < obs[0] < right) and (lower < obs[1] < upper):
            count += 1
    return count


def check_corner_wall(box_loc, state):
    """
    Check if box_loc is at the corner of the map.
    Return True if box_loc is at such corner.
    """
    x = box_loc[0]
    y = box_loc[1]
    if ((x == 0) and (y == 0 or y == state.height - 1)) \
            or ((y == 0) and (x == 0 or x == state.width - 1)):
        return True
    return False


def check_corner_obstacle(box_loc, state):
    """
    Check if box_loc is at the corner of two obstacles.
    Return True if box_loc is at such corner.
    """
    x = box_loc[0]
    y = box_loc[1]
    left = (x - 1, y)
    right = (x + 1, y)
    up = (x, y + 1)
    down = (x, y - 1)
    obs = state.obstacles

    if ((left in obs) and (up in obs or down in obs)) \
            or ((up in obs) and (left in obs or right in obs)):
        return True
    return False


def check_corner_boxes(box_loc, state):
    """
    Check if box_loc is at the corner of two boxes.
    Return True if box_loc is at such corner.
    """
    x = box_loc[0]
    y = box_loc[1]
    left = (x - 1, y)
    right = (x + 1, y)
    up = (x, y + 1)
    down = (x, y - 1)
    boxes = state.boxes

    if ((left in boxes) and (up in boxes or down in boxes)) \
            or ((up in boxes) and (left in boxes or right in boxes)):
        return True
    return False


def check_corner_wall_obstacle(box_loc, state):
    """
    Check if box_loc is at the corner of wall and a obstacle.
    Return True if box_loc is at such corner.
    """
    x = box_loc[0]
    y = box_loc[1]
    left = (x - 1, y)
    right = (x + 1, y)
    up = (x, y + 1)
    down = (x, y - 1)
    obs = state.obstacles

    # wall and a obstacle or a box
    if ((x == 0) and (up in obs or down in obs)) \
            or ((x == state.width -1 ) and (up in obs or down in obs)):
        return True
    if ((y == 0) and (left in obs or right in obs)) \
            or ((y == state.width -1 ) and (left in obs or right in obs)):
        return True
    return False


def check_corner_wall_with_no_sp(box_loc, state):
    """
    Check if box_loc is at the side of the wall which has not storage point.
    Return True if there is no such storage point.
    """
    x = box_loc[0]
    y = box_loc[1]
    sp = state.storage

    if (x == 0) or (y == 0) or (x == state.width - 1) or (y == state.height - 1):
        for storage in sp:
            if ((storage[0] == 0) and (x == 0)) \
                    or ((storage[1] == 0) and (y == 0)) \
                    or (storage[0] == state.width - 1 and x == state.width - 1) \
                    or (storage[1] == state.height - 1 and y == state.height - 1):
                return False
        return True
    return False


def available_storage(box_loc, state):
    """
    Return a list of storage points currently available for box_loc.
    """
    sp = list(state.storage)

    if box_loc in sp:
        return [box_loc]
    for box in state.boxes:
        if (box != box_loc) and (box in sp):
            sp.remove(box)
    return sp


def check_corner(state):
    """
    Check if state is a dead state: no movement of boxes available.
    Return True if state is at a dead state
    """
    for box in state.boxes:
        sp_available = available_storage(box, state)
        if (box not in sp_available) \
                and (check_corner_wall(box, state)
                     or check_corner_boxes(box, state)
                     or check_corner_obstacle(box, state)
                     or check_corner_wall_obstacle(box, state)
                     or check_corner_wall_with_no_sp(box, state)):
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

    m_dis_sum = 0
    for box in state.boxes:
        curr_m_dis = shortest_manhattan_distance(box, tuple(state.storage))
        m_dis_sum += curr_m_dis

    return m_dis_sum  # CHANGE THIS


def calc_manhattan_distance(box_loc, storage_point):
    """
    @param box_loc: a tuple that stores the location of a box
    @param storage_point: a tuple that stores the location of a storage point
    @return: the manhattan_distance between box_loc and storage point.
    """
    x_distance = abs(box_loc[0] - storage_point[0])
    y_distance = abs(box_loc[1] - storage_point[1])
    total_distance = x_distance + y_distance
    return total_distance


def shortest_manhattan_distance(box_loc, tp_sp):
    """
    @param box_loc: a tuple that stores the location of a box
    @param tp_sp: a tuple of tuples that store the locations of one or
    multiple storage point
    @return: the shortest manhattan distance between box_loc and the storage
    point in tp_sp
    """
    curr_dis = calc_manhattan_distance(box_loc, tp_sp[0])
    curr_i = 0

    for i in range(1, len(tp_sp)):
        m_dis = calc_manhattan_distance(box_loc, tp_sp[i])
        if m_dis < curr_dis:
            curr_dis = m_dis
            curr_i = i
    return calc_manhattan_distance(box_loc, tp_sp[curr_i])


def fval_function(sN, weight):
    # IMPLEMENT
    """
    Provide a custom formula for f-value computation for Anytime Weighted A star.
    Returns the fval of the state contained in the sNode.

    @param sNode sN: A search node (containing a SokobanState)
    @param float weight: Weight given by Anytime Weighted A star
    @rtype: float
    """
    return sN.gval + weight*sN.hval  #CHANGE THIS


# SEARCH ALGORITHMS
def weighted_astar(initial_state, heur_fn, weight, timebound):
    # IMPLEMENT
    '''Provides an implementation of weighted a-star, as described in the HW1 handout'''
    '''INPUT: a sokoban state that represents the start state and a timebound (number of seconds)'''
    '''OUTPUT: A goal state (if a goal is found), else False as well as a SearchStats object'''
    '''implementation of weighted astar algorithm'''

    # search engine
    wrapped_fval_function = (lambda sN: fval_function(sN, weight))
    se = SearchEngine(strategy='custom', cc_level='default')
    se.init_search(initial_state, sokoban_goal_state(initial_state), heur_fn,
                   wrapped_fval_function)

    inf = float('inf')
    costbound = (inf, inf, inf)
    res = se.search(timebound, costbound)

    return res[0]


def iterative_astar(initial_state, heur_fn, weight=1, timebound=5):  # uses f(n), see how autograder initializes a search line 88
    # IMPLEMENT
    '''Provides an implementation of realtime a-star, as described in the HW1 handout'''
    '''INPUT: a sokoban state that represents the start state and a timebound (number of seconds)'''
    '''OUTPUT: A goal state (if a goal is found), else False as well as a SearchStats object'''
    '''implementation of iterative astar algorithm'''

    wrapped_fval_function = (lambda sN: fval_function(sN, weight))

    # search engine
    se = SearchEngine(strategy='custom', cc_level='default')
    se.init_search(initial_state, sokoban_goal_state, heur_fn, wrapped_fval_function)

    # time
    curr_time = os.times()[0]
    end_time = curr_time + timebound
    new_timebound = timebound

    # cost
    inf = float('inf')
    ideal_cost = inf
    cost_bound = (inf, inf, ideal_cost)

    # setting ideal result and path
    ideal_res = False

    # start searching
    while curr_time < end_time:
        curr_state = se.search(new_timebound, cost_bound)
        time_diff = os.times()[0] - curr_time
        curr_time = os.times()[0]
        new_timebound = new_timebound - time_diff

        if curr_state[0]:
            ideal_res = curr_state[0]
            ideal_cost = curr_state.gval + weight * heur_fn(ideal_res[0])
            weight = weight * 0.8
        else:
            break

    return ideal_res  # CHANGE THIS


def iterative_gbfs(initial_state, heur_fn, timebound=5):  # only use h(n)
    # IMPLEMENT
    '''Provides an implementation of anytime greedy best-first search, as described in the HW1 handout'''
    '''INPUT: a sokoban state that represents the start state and a timebound (number of seconds)'''
    '''OUTPUT: A goal state (if a goal is found), else False'''
    '''implementation of iterative gbfs algorithm'''
    # search engine
    se = SearchEngine(strategy='best_first', cc_level='default')
    se.init_search(initial_state, sokoban_goal_state, heur_fn)

    # time
    curr_time = os.times()[0]
    end_time = curr_time + timebound
    new_timebound = timebound

    # cost
    inf = float('inf')
    cost_bound = (inf, inf, inf)

    # setting ideal result and path
    ideal_res = False

    # start searching
    while curr_time < end_time:
        curr_state = se.search(new_timebound, cost_bound)
        time_diff = os.times()[0] - curr_time
        curr_time = os.times()[0]
        new_timebound = new_timebound - time_diff

        if curr_state[0]:
            ideal_res = curr_state[0]
            cost_bound = (ideal_res.gval, inf, inf)
        else:
            break

    return ideal_res  # CHANGE THIS





