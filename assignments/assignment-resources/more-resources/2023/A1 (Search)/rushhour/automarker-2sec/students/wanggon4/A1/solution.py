#   Look for #IMPLEMENT tags in this file. These tags indicate what has
#   to be implemented to complete the Rush Hour domain.

#   You may add only standard python imports (numpy, itertools are both ok).
#   You may not remove any imports.
#   You may not import or otherwise source any of your own files.

import os  # you will likely want this for timing functions
import math  # for infinity
from search import *  # for search engines
from rushhour import *


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
    """
    The obvious flaws of heur_min_dist is that it does not take the orientation of the exit into account.
    So the alternate heuristic function should take that when estimate the cost of a state.
    Also, it should probably take the number of obscure into account.
    Therefore, we need to traverse through all the car and count the number of car that is in the way of the goal vehicle

    Also, to speed up the process, I kept the time complexity to O(nlogn) where n is the number of cars in total

    Here is how the calculation goes: 
    1. Sort the vehicle status in a way that all the non-goal vehicle are at the 
    front of the list 
    2. Determine where it can block goal vehicle by calculating if it occupy the same x-coordinate 
    (if direction is N or S) or y-coordinate (if direction is W or E) as the goal. If so, record its x/y 
    3. For each goal vehicle, determine the minimum move it takes to reach the exit according to orientation plus the 
    number of blocking vehicle on that way
    4. Return the minimum value

    """
    move = float(math.inf)
    vehicle_statuses = sorted(state.get_vehicle_statuses(), key=lambda x: x[-1], reverse=False)
    (goal_x, goal_y) = state.get_board_properties()[1]
    (m, n) = state.get_board_properties()[0]
    direction = state.get_board_properties()[2]
    blocks = []
    for vs in vehicle_statuses:
        if vs[-1]:
            # if vehicle is horizontal
            if vs[3]:
                # calculate the distance between the front of the vehicle and the goal (W)
                if direction == 'W':
                    blocks_between = len(
                        [i for i in blocks if i in range(min(goal_x, vs[1][0]), max(goal_x, vs[1][0]))])
                    move = min(move, min(abs(goal_x - vs[1][0]) + blocks_between,
                                         n - abs(goal_x - vs[1][0]) + (len(blocks) - blocks_between)))
                # calculate the distance between the tail of the vehicle and the goal (E)
                else:
                    blocks_between = len([i for i in blocks if i in range(min(goal_x, ((vs[1][0] + vs[2] - 1) % n)),
                                                                          max(goal_x, ((vs[1][0] + vs[2] - 1) % n)))])
                    move = min(move, min(abs(goal_x - ((vs[1][0] + vs[2] - 1) % n)) + blocks_between,
                                         n - abs(goal_x - ((vs[1][0] + vs[2] - 1) % n)) + (
                                                     len(blocks) - blocks_between)))
            else:
                # calculate the distance between the front of the vehicle and the goal (N)
                if direction == 'N':
                    blocks_between = len(
                        [i for i in blocks if i in range(min(goal_y, vs[1][1]), max(goal_y, vs[1][1]))])
                    move = min(move, min(abs(goal_y - vs[1][1]) + blocks_between,
                                         m - abs(goal_y - vs[1][1]) + (len(blocks) - blocks_between)))
                # calculate the distance between the tail of the vehicle and the goal (S)
                else:
                    blocks_between = len([i for i in blocks if i in range(min(goal_y, ((vs[1][1] + vs[2] - 1) % m)),
                                                                          max(goal_y, ((vs[1][1] + vs[2] - 1) % m)))])
                    move = min(move, min(abs(goal_y - ((vs[1][1] + vs[2] - 1) % m)) + blocks_between,
                                         m - abs(goal_y - ((vs[1][1] + vs[2] - 1) % m)) + (
                                                     len(blocks) - blocks_between)))
        else:
            if (direction == 'N' or direction == 'S') and vs[3] and (vs[1][0] <= goal_x <= (vs[1][0] + vs[2] - 1) or (
                    vs[1][0] > goal_x and (vs[1][0] + vs[2] - 1) - n >= goal_x)):
                blocks.append(vs[1][1])
            elif (direction == 'E' or direction == 'W') and not vs[3] and (
                    vs[1][1] <= goal_y <= (vs[1][1] + vs[2] - 1) or (
                    vs[1][1] > goal_y and (vs[1][1] + vs[2] - 1) - m >= goal_y)):
                blocks.append(vs[1][0])
    return move

# RUSH HOUR GOAL TEST
def rushhour_goal_fn(state: Rushhour):
    # IMPLEMENT
    '''a Rush Hour Goal Test'''
    '''INPUT: a parking state'''
    '''OUTPUT: True, if satisfies the goal, else false.'''
    direction = state.get_board_properties()[2]
    (m, n) = state.get_board_properties()[0]
    (goal_x, goal_y) = state.get_board_properties()[1]
    vehicle_statuses = state.get_vehicle_statuses()

    if direction == 'N' or direction == 'W':
        for vs in vehicle_statuses:
            if vs[-1] and vs[1] == (goal_x, goal_y):
                return True
        return False
    else:
        for vs in vehicle_statuses:
            if vs[-1] and not vs[3] and (vs[1][0], (vs[1][1] + vs[2] - 1) % m) == (goal_x, goal_y):
                return True
            elif vs[-1] and vs[3] and ((vs[1][0] + vs[2] - 1) % n, vs[1][1]) == (goal_x, goal_y):
                return True
        return False

def heur_min_dist(state):
    # IMPLEMENT
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
    move1 = float('inf')
    move2 = float('inf')
    vehicle_statuses = state.get_vehicle_statuses()
    (goal_x, goal_y) = state.get_board_properties()[1]
    (m, n) = state.get_board_properties()[0]

    for vs in vehicle_statuses:
        if vs[-1]:
            # if vehicle is horizontal
            if vs[3]:
                # calculate the distance between the front of the vehicle and the goal (W)
                if goal_x <= vs[1][0]:
                    move1 = min(move1, abs(vs[1][0] - goal_x))
                else:
                    move1 = min(move1, vs[1][0] + (n - goal_x))
                # calculate the distance between the tail of the vehicle and the goal (E)
                if goal_x >= ((vs[1][0] + vs[2] - 1) % n):
                    move2 = min(move2, abs(goal_x - ((vs[1][0] + vs[2] - 1) % n)))
                else:
                    move2 = min(move2, (n - (vs[1][0] + vs[2] - 1) % n) + goal_x)
            else:
                # calculate the distance between the front of the vehicle and the goal (N)
                if goal_y <= vs[1][1]:
                    move1 = min(move1, abs(vs[1][1] - goal_y))
                else:
                    move1 = min(move1, vs[1][1] + (m - goal_y))
                # calculate the distance between the tail of the vehicle and the goal (S)
                if goal_y >= ((vs[1][1] + vs[2] - 1) % m):
                    move2 = min(move2, abs(goal_y - ((vs[1][1] + vs[2] - 1) % m)))
                else:
                    move2 = min(move2, (m - (vs[1][1] + vs[2] - 1) % m) + goal_y)
    return min(move1, move2)


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
    return sN.gval + weight * sN.hval


def fval_function_XUP(sN, weight):
    # IMPLEMENT
    """
    Another custom formula for f-value computation for Weighted A star.
    Returns the fval of the state contained in the sNode.
    XUP causes the best-first search to explore near-optimal paths near the end of a path.

    @param sNode sN: A search node (containing a RushHour State)
    @param float weight: Weight given by Weighted A star
    @rtype: float
    """
    return (1 / (2 * weight)) * (sN.gval + sN.hval + math.sqrt(
        pow((sN.gval + sN.hval), 2) + 4 * weight * (weight - 1) * pow(sN.hval, 2)))


def fval_function_XDP(sN, weight):
    # IMPLEMENT
    """
    A third custom formula for f-value computation for Weighted A star.
    Returns the fval of the state contained in the sNode.
    XDP causes the best-first search to explore near-optimal paths near the start of a path. 

    @param sNode sN: A search node (containing a RushHour State)
    @param float weight: Weight given by Weighted A star
    @rtype: float
    """
    return (1 / (2 * weight)) * (sN.gval + (2 * weight - 1) * sN.hval + math.sqrt(
        pow((sN.gval - sN.hval), 2) + 4 * weight * sN.gval * sN.hval))


# SEARCH ALGORITHMS
def weighted_astar(initial_state, heur_fn, weight, timebound,
                   costbound=(float(math.inf), float(math.inf), float(math.inf))):
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
    se = SearchEngine('custom', 'full')
    se.init_search(initial_state, goal_fn=rushhour_goal_fn, heur_fn=heur_fn,
                   fval_function=lambda sN: fval_function(sN, weight))

    return se.search(timebound, costbound)


def iterative_astar(initial_state, heur_fn, weight=1,
                    timebound=5):  # uses f(n), see how autograder initializes a search
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
    end_time = os.times()[0] + timebound
    time_left = timebound
    temp_result, temp_stats = weighted_astar(initial_state, heur_fn, weight, time_left)
    final, stats = temp_result, temp_stats

    while final and time_left > 0 and final.gval > 1:
        time_left = end_time - os.times()[0]
        cost_bound = (final.gval - 1, final.gval - 1, final.gval - 1)
        weight = weight * 0.6
        temp_result, temp_stats = weighted_astar(initial_state, heur_fn, weight, time_left, cost_bound)
        if temp_result:
            final, stats = temp_result, temp_stats
    return final, stats


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
    se = SearchEngine('best_first', 'full')
    end_time = os.times()[0] + timebound
    time_left = timebound
    se.trace_off()
    se.init_search(initial_state, goal_fn=rushhour_goal_fn, heur_fn=heur_fn)

    temp_result, temp_stats = se.search(time_left)

    final, stats = temp_result, temp_stats
    while final and end_time > os.times()[0] and final.gval > 1:
        time_left = end_time - os.times()[0]
        temp_result, temp_stats = se.search(time_left, costbound=(final.gval-1, final.gval-1, final.gval-1))
        if temp_result:
            final, stats = temp_result, temp_stats
    return final, stats
