#   Look for #IMPLEMENT tags in this file. These tags indicate what has
#   to be implemented to complete the warehouse domain.

#   You may add only standard python imports
#   You may not remove any imports.
#   You may not import or otherwise source any of your own files

import os  # for time functions
import math  # for infinity
from search import *  # for search engines
from sokoban import sokoban_goal_state, SokobanState, Direction, PROBLEMS
# for Sokoban specific classes and problems


# SOKOBAN HEURISTICS
def heur_alternate(state):
    # IMPLEMENT
    """a better heuristic
    INPUT: a sokoban state
    OUTPUT: a numeric value that serves as an estimate of the distance of the
            state to the goal."""
    # heur_manhattan_distance has flaws.
    # Write a heuristic function that improves upon heur_manhattan_distance to
    # estimate distance between the current state and the goal.
    # Your function should return a numeric value for the estimate of the
    # distance to the goal.
    # EXPLAIN YOUR HEURISTIC IN THE COMMENTS. Please leave this function (and
    # your explanation) at the top of your solution file, to facilitate marking.

    # ######################################################################## #
    # #########################   Explanation   ############################## #
    # ######################################################################## #

    # For my alternate heuristic, I will be using euclidean distance. The issue
    # With Manhattan distance is that to use a "ladder" movement pattern
    # (assuming no obstacles) means that the robots have to take extra moves
    # between each movement of the boxes. Euclidean distance takes care of this
    # because if two box-storage pairs have the same manhattan distance,
    # euclidean distance will punish the one with longer triangle side length
    # and reward the one with a more straight line path.

    # Another issue with the first approach is that it doesnt take into account
    # whether multiple boxes are being stored on top of each other. This must
    # also be fixed.

    # We also want to take into consideration the mobility of the boxes. If a
    # box is in the corner but it isn't on a spot, its impossible to move. For
    # this reason if its stuck in the corner, it will be infinity, otherwise,
    # we add punishment for each side in contact with obstacles or boxes.

    return heur_help(list(state.boxes), list(state.storage)) # + heur_mob(state)


def heur_mob(state: SokobanState) -> int:
    acc = 0

    for box in state.boxes:
        print('hello')
        # if box is in the corner:
        #     return math.infinity
        # Check for obstacles and incrment the acc

    return acc

"""
def heur_help(boxes, storages) -> float:
    ""
    Takes in boxes and storages, and finds the lowest euclidean total distance
    where boxes dont overlap.
    ""
    # Base case where there are no boxes (and no spots)
    temp_acc = 0

    if len(boxes) < 2:
        for box in boxes:
            temp = []
            for stor in storages:
                temp.append(euc_dist(box, stor))
            temp_acc += min(temp)
        return temp_acc

    # Will store temp heuristics for each path
    acc = []

    for i in range(len(boxes)):
        boxes_left = boxes[:i] + boxes[i + 1:]
        box = boxes[i]
        for j in range(len(storages)):
            stores_left = storages[:j] + storages[j + 1:]
            stor = storages[j]
            acc.append(euc_dist(box, stor) + heur_help(boxes_left, stores_left))

    return min(acc)



def heur_help(boxes, storages) -> float:
    ""
    Takes in boxes and storages, and finds the lowest euclidean total distance
    where boxes dont overlap.
    ""
    # Base case where there are no boxes (and no spots)

    if len(boxes) == 0:
        return 0

    # Will store temp heuristics for each path
    acc = []

    for i in range(len(boxes)):
        boxes_left = boxes[:i] + boxes[i + 1:]
        box = boxes[i]
        temp = {}
        for j in range(len(storages)):
            stor = storages[j]
            temp[euc_dist(box, stor)] = j
        dist, index = min(temp.keys()), temp[min(temp.keys())]
        stores_left = storages[:index] + storages[index + 1:]
        acc.append(dist + heur_help(boxes_left, stores_left))

    return min(acc)
"""


def heur_help(boxes, storages) -> float:
    """
    Takes in boxes and storages, and finds the lowest euclidean total distance
    where boxes dont overlap.
    """
    # Base case where there are no boxes (and no spots)

    if len(boxes) == 0:
        return 0

    # Will store temp heuristics for each path

    boxes_left = boxes[1:]
    box = boxes[0]
    temp = {}
    for j in range(len(storages)):
        stor = storages[j]
        temp[euc_dist(box, stor)] = j
    dist, index = min(temp.keys()), temp[min(temp.keys())]
    stores_left = storages[:index] + storages[index + 1:]
    return dist + heur_help(boxes_left, stores_left)


def euc_dist(point1, point2):
    """
    Helper function that takes two coordinates and returns the manhattan
    distance between them
    """
    return math.sqrt((point1[0] - point2[0])**2 + (point1[1] - point2[1])**2)


def heur_zero(state):
    """Zero Heuristic can be used to make A* search perform uniform cost
    search"""
    return 0


def heur_manhattan_distance(state: SokobanState):
    # IMPLEMENT
    """admissible sokoban puzzle heuristic: manhattan distance
    INPUT: a sokoban state
    OUTPUT: a numeric value that serves as an estimate of the distance of the
            state to the goal."""
    #  We want an admissible heuristic, which is an optimistic heuristic.
    #  It must never overestimate the cost to get from the current state to the
    #  goal.
    #  The sum of the Manhattan distances between each box that has yet to be
    #  stored and the storage point nearest to it is such a heuristic.
    #  When calculating distances, assume there are no obstacles on the grid.
    #  You should implement this heuristic function exactly, even if it is
    #  tempting to improve it.
    #  Your function should return a numeric value; this is the estimate of the
    #  distance to the goal.

    accumulator = 0

    for box in state.boxes:
        temp = []
        for stor in state.storage:
            temp.append(man_dist(box, stor))
        accumulator += min(temp)
    return accumulator  # CHANGE THIS


def man_dist(point1, point2):
    """
    Helper function that takes two coordinates and returns the manhattan
    distance between them
    """
    return (abs(point1[0] - point2[0])) + (abs(point1[1] - point2[1]))


def fval_function(sN, weight):
    # IMPLEMENT
    """
    Provide a custom formula for f-value computation for Anytime Weighted A star
    Returns the fval of the state contained in the sNode.

    @param sNode sN: A search node (containing a SokobanState)
    @param float weight: Weight given by Anytime Weighted A star
    @rtype: float
    """

    return sN.gval + (weight * sN.hval)


# SEARCH ALGORITHMS
def weighted_astar(initial_state, heur_fn, weight, timebound):
    # IMPLEMENT
    """Provides an implementation of weighted a-star, as described in the HW1
    handout
    INPUT: a sokoban state that represents the start state and a timebound
           (number of seconds)
    OUTPUT: A goal state (if a goal is found), else False as well as a
            SearchStats object
    implementation of weighted astar algorithm"""

    se = SearchEngine('custom', 'default')

    temp_fval = (lambda sN: fval_function(sN, weight))

    se.init_search(initial_state, sokoban_goal_state, heur_fn, temp_fval)

    # return None, None  # CHANGE THIS
    return se.search(timebound=timebound)


def iterative_astar(initial_state, heur_fn, weight=1, timebound=5):  # uses f(n), see how autograder initializes a search line 88
    # IMPLEMENT
    """Provides an implementation of realtime a-star, as described in the HW1 handout
    INPUT: a sokoban state that represents the start state and a timebound
            (number of seconds)
    OUTPUT: A goal state (if a goal is found), else False as well as a
            SearchStats object
    implementation of iterative astar algorithm"""

    op_state, stats = weighted_astar(initial_state, heur_fn, weight, timebound)
    print(op_state)
    timebound = timebound - stats.total_time

    if op_state:
        costbound = (op_state.gval, op_state.gval, op_state.gval)
    else:
        costbound = (math.inf, math.inf, math.inf)

    print(costbound)

    se = SearchEngine('custom', 'default')
    temp_fval = (lambda sN: fval_function(sN, weight))

    while timebound > 0:
        se.init_search(initial_state, sokoban_goal_state, heur_fn, temp_fval)
        temp_op_state, temp_stats = se.search(timebound, costbound)
        timebound = timebound - temp_stats.total_time
        if temp_op_state:
            op_state = temp_op_state
            costbound = (op_state.gval, op_state.gval, op_state.gval)

        weight = weight * 0.66
        print(op_state)

    return op_state, stats  # CHANGE THIS


def iterative_gbfs(initial_state, heur_fn, timebound=5):  # only use h(n)
    # IMPLEMENT
    """Provides an implementation of anytime greedy best-first search, as
    described in the HW1 handout'''
    INPUT: a sokoban state that represents the start state and a timebound
           (number of seconds)
    OUTPUT: A goal state (if a goal is found), else False
    implementation of iterative gbfs algorithm"""

    se = SearchEngine('best_first', 'default')
    se.init_search(initial_state, sokoban_goal_state, heur_fn)
    op_state, stats = se.search(timebound)
    timebound = timebound - stats.total_time

    if op_state:
        costbound = (op_state.gval, op_state.gval, op_state.gval)
    else:
        costbound = (math.inf, math.inf, math.inf)

    while timebound > 0:
        se.init_search(initial_state, sokoban_goal_state, heur_fn)
        temp_op_state, stats = se.search(timebound, costbound)
        timebound = timebound - stats.total_time
        if temp_op_state:
            op_state = temp_op_state
            costbound = (op_state.gval, op_state.gval, op_state.gval)

    return op_state, stats  # CHANGE THIS



