#   Look for #IMPLEMENT tags in this file. These tags indicate what has
#   to be implemented to complete the warehouse domain.

#   You may add only standard python imports
#   You may not remove any imports.
#   You may not import or otherwise source any of your own files

import os  # for time functions
import math  # for infinity
from search import *  # for search engines
from sokoban import sokoban_goal_state, SokobanState, Direction, \
    PROBLEMS  # for Sokoban specific classes and problems


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

    # copied from sokoban.py
    # these can be imported but we are not able to add more imports
    UP = Direction("up", (0, -1))
    RIGHT = Direction("right", (1, 0))
    DOWN = Direction("down", (0, 1))
    LEFT = Direction("left", (-1, 0))

    # previous heuristic value
    global prev

    # check if the box locations are not changed
    # if the box locations are not changed, return previous value directly
    if state.parent is not None and state.boxes == state.parent.boxes:
        return prev

    # final heuristic value
    rst = 0
    # storage locations that has box on it
    occupied = set(state.boxes) & set(state.storage)
    # boxes that are not at storage location
    boxes = set(state.boxes).difference(occupied)

    for box in boxes:
        # up, right, down, left locations of the box
        up = UP.move(box)
        right = RIGHT.move(box)
        down = DOWN.move(box)
        left = LEFT.move(box)
        # x, y coordinates of storage locations
        sx = [x[0] for x in state.storage]
        sy = [x[1] for x in state.storage]

        # check if this is a dead state, return math.inf if this is a dead state
        # dead state means there is a box stuck at the corner between map walls
        # and/or obstacles. Or there is a box beside the map wall, but there are
        # no storage location beside that wall.
        if box not in state.storage and \
                ((up[1] < 0 and left[0] < 0)
                 or (up[1] < 0 and left in state.obstacles)
                 or (up in state.obstacles and left[0] < 0)
                 or (up in state.obstacles and left in state.obstacles)
                 or (up[1] < 0 and right[0] >= state.width)
                 or (up[1] < 0 and right in state.obstacles)
                 or (up in state.obstacles and right[0] >= state.width)
                 or (up in state.obstacles and right in state.obstacles)
                 or (right[0] >= state.width and down[1] >= state.height)
                 or (right[0] >= state.width and down in state.obstacles)
                 or (right in state.obstacles and down[1] >= state.height)
                 or (right in state.obstacles and down in state.obstacles)
                 or (down[1] >= state.height and left[0] < 0)
                 or (down[1] >= state.height and left in state.obstacles)
                 or (down in state.obstacles and left[0] < 0)
                 or (down in state.obstacles and left in state.obstacles)
                 or (up[1] < 0 and 0 not in sy)
                 or (right[0] >= state.width and (state.width - 1) not in sx)
                 or (down[1] >= state.height and (state.height - 1) not in sy)
                 or (left[0] < 0 and 0 not in sx)):
            return math.inf

        # empty storage locations
        empty = list(set(state.storage).difference(occupied))
        # calculate Manhattan distance to each empty storage location
        distances = {x: abs(y[0] - box[0]) + abs(y[1] - box[1]) for x, y in
                     enumerate(empty)}
        # index for minimum Manhattan distance
        min_idx = min(distances, key=distances.get)
        # retrieve the value of minimum Manhattan distance
        lowest_dist = distances[min_idx]
        # add this location to occupied which means it can not be used for other
        # boxes
        occupied.add(empty[min_idx])
        # all 8 surrounding locations of the box
        around = (up, right, down, left, UP.move(RIGHT.move(box)),
                  RIGHT.move(DOWN.move(box)), DOWN.move(LEFT.move(box)),
                  LEFT.move(UP.move(box)))
        # add the minimum Manhattan distance and the number of obstacles around
        # the box. If there are obstacles around the box, it may lead to more
        # steps to go around it
        rst += lowest_dist + len(set(state.obstacles) & set(around))

        # works better for best first search
        # rst += lowest_dist + len(set(state.obstacles) & set(around)) + len(
        #     set(state.boxes) & set(around))

    # store the heuristic value
    prev = rst
    return rst


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
    return sum(map(lambda box: min(
        [abs(x[0] - box[0]) + abs(x[1] - box[1]) for x in state.storage]),
                   state.boxes))


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
    wrapped_fval_function = (lambda sN: fval_function(sN, weight))
    se = SearchEngine('custom')
    se.init_search(initial_state, sokoban_goal_state, heur_fn,
                   wrapped_fval_function)
    return se.search(timebound)


def iterative_astar(initial_state, heur_fn, weight=1,
                    timebound=5):  # uses f(n), see how autograder initializes a search line 88
    # IMPLEMENT
    '''Provides an implementation of realtime a-star, as described in the HW1 handout'''
    '''INPUT: a sokoban state that represents the start state and a timebound (number of seconds)'''
    '''OUTPUT: A goal state (if a goal is found), else False as well as a SearchStats object'''
    '''implementation of iterative astar algorithm'''
    # either there are no nodes left to expand( and our best solution is the
    # optimal one) or it runs out of time. It will do this by running Weighted
    # A * again and again, with increasingly small weights.
    start = os.times()[0]
    buffer = 0.05
    timebound -= buffer
    stop = start + timebound

    se = SearchEngine('custom')
    costbound = None
    goal, stats = False, False
    weight = 100

    while start < stop and weight >= 1:
        wrapped_fval_function = (lambda sN: fval_function(sN, weight))
        se.init_search(initial_state, sokoban_goal_state, heur_fn,
                       wrapped_fval_function)
        goal_state, stats = se.search(timebound, costbound)

        if goal_state:
            costbound = (goal_state.gval, goal_state.gval, goal_state.gval)
            goal = goal_state
        else:
            break

        weight = (weight / 2) if weight > 2 else 1
        timebound -= (os.times()[0] - start)
        start = os.times()[0]
    return goal, stats


def iterative_gbfs(initial_state, heur_fn, timebound=5):  # only use h(n)
    # IMPLEMENT
    '''Provides an implementation of anytime greedy best-first search, as described in the HW1 handout'''
    '''INPUT: a sokoban state that represents the start state and a timebound (number of seconds)'''
    '''OUTPUT: A goal state (if a goal is found), else False'''
    '''implementation of iterative gbfs algorithm'''
    start = os.times()[0]
    buffer = 0.05
    timebound -= buffer
    stop = start + timebound

    se = SearchEngine('best_first')
    costbound = None
    goal, stats = False, False

    while start < stop:
        se.init_search(initial_state, sokoban_goal_state, heur_fn)
        goal_state, stats = se.search(timebound, costbound)

        if goal_state:
            costbound = (goal_state.gval, goal_state.gval, goal_state.gval)
            goal = goal_state
        else:
            break

        timebound -= (os.times()[0] - start)
        start = os.times()[0]

    return goal, stats
