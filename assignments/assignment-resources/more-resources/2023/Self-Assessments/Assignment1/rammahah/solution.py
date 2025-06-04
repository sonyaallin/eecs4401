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
    # Step 1: Same as Manhattan except keep track of which storage points are in
    #         use.
    # Step 2: Identify closest storage point to each box and identify the spot
    #         that the robot would need to push from. Add the distance that the
    #         robot would have to move to get to that spot
    # Step 3: Identify all the locations that robots need to push from as well
    #         as the estimated end point once the box is pushed into the
    #         storage. Also, keep track of the locations of all the robots.
    #         From there calculate the approximate shortest distance
    #         between a robot and a push point. Assume the robot pushes that box
    #         to it's assigned storage spot and update that robots location to
    #         the estimated end point. Keep track of which boxes have reached
    #         their target destination. Repeat given the new robot locations.
    #
    hval = 0
    filled = [0] * len(state.storage)
    max_dist = state.width + state.height
    push_loc = []
    end_loc = []
    for box in state.boxes:
        curr_storage = 0
        min_storage = 0
        min_dist = max_dist
        closest = (0, 0)
        for target in state.storage:
            if filled[curr_storage] == 0:
                dist = abs(box[0] - target[0]) + abs(box[1] - target[1])
                if dist < min_dist:
                    min_dist = dist
                    min_storage = curr_storage
                    closest = (target[0], target[1])

            curr_storage += 1

        filled[min_storage] = 1
        hval += min_dist

        h_push = (-1, -1)
        v_push = (-1, -1)
        h_end = (-1, -1)
        v_end = (-1, -1)

        if min_dist > 0:
            if closest[0] > box[0]:
                h_push = (max(box[0] - 1, 0), box[1])
                h_end = (closest[0] - 1, closest[1])
            elif closest[0] < box[0]:
                h_push = (min(box[0] + 1, state.width), box[1])
                h_end = (closest[0] + 1, closest[1])

            elif closest[1] > box[1]:
                v_push = (box[0], max(box[1] - 1, 0))
                v_end = (closest[0], closest[1] - 1)
            elif closest[1] < box[1]:
                v_push = (box[0], min(box[1] + 1, state.height))
                v_end = (closest[0], closest[1] - 1)

            if h_push[0] != -1:
                push_loc.append(h_push)
                if v_push[0] != -1:
                    hval += 2
                    end_loc.append(v_end)
                else:
                    end_loc.append(h_end)
            else:
                push_loc.append(v_push)
                end_loc.append(v_end)

    travel_dist = 0
    curr_locations = []
    count = len(push_loc)
    reached = [0] * count
    curr_count = 0
    for robot in state.robots:
        curr_locations.append((robot[0], robot[1]))
    while curr_count < count:
        bot = 0
        min_bot = 0
        min_dist = max_dist
        min_loc = 0
        for curr in curr_locations:
            curr_loc = 0
            while curr_loc < count:
                if reached[curr_loc] == 0:
                    dist = abs(curr[0] - push_loc[curr_loc][0]) + abs(
                        curr[1] - push_loc[curr_loc][1])
                    if dist < min_dist:
                        min_dist = dist
                        min_loc = curr_loc
                        min_bot = bot
                curr_loc += 1
            bot += 1
        reached[min_loc] = 1
        curr_locations[min_bot] = end_loc[min_loc]
        travel_dist += min_dist
        curr_count += 1
    hval += travel_dist
    return hval

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
    hval = 0
    for box in state.boxes:
        min_dist = state.width + state.height
        for target in state.storage:
            dist = abs(box[0] - target[0]) + abs(box[1] - target[1])
            if dist < min_dist:
                min_dist = dist
        hval += min_dist
    return hval


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
    custom = SearchEngine('custom', 'full')
    custom.init_search(initial_state, sokoban_goal_state, heur_fn,
                       wrapped_fval_function)
    return custom.search(timebound)


def iterative_astar(initial_state, heur_fn, weight=1,
                    timebound=5):  # uses f(n), see how autograder initializes a search line 88
    # IMPLEMENT
    '''Provides an implementation of realtime a-star, as described in the HW1 handout'''
    '''INPUT: a sokoban state that represents the start state and a timebound (number of seconds)'''
    '''OUTPUT: A goal state (if a goal is found), else False as well as a SearchStats object'''
    '''implementation of iterative astar algorithm'''
    w = 10
    wrapped_fval_function = (lambda sN: fval_function(sN, w))
    custom = SearchEngine('custom', 'full')
    custom.init_search(initial_state, sokoban_goal_state, heur_fn,
                       wrapped_fval_function)
    result = custom.search(timebound)
    best = result[0]
    stat = result[1]

    time = timebound - stat.total_time

    while result[0] != False:
        if w > 2:
            w -= 2
        max_val = (best.gval - 1)
        wrapped_fval_function = (lambda sN: fval_function(sN, w))
        custom.init_search(initial_state, sokoban_goal_state, heur_fn,
                           wrapped_fval_function)
        result = custom.search(time, (max_val, max_val, max_val))

        if result[0] != False:
            best = result[0]
            stat = result[1]
            time -= stat.total_time
    return best, stat


def iterative_gbfs(initial_state, heur_fn, timebound=5):  # only use h(n)
    # IMPLEMENT
    '''Provides an implementation of anytime greedy best-first search, as described in the HW1 handout'''
    '''INPUT: a sokoban state that represents the start state and a timebound (number of seconds)'''
    '''OUTPUT: A goal state (if a goal is found), else False'''
    '''implementation of iterative gbfs algorithm'''
    engine = SearchEngine('best_first', 'full')
    engine.init_search(initial_state, sokoban_goal_state, heur_fn)
    result = engine.search(timebound)
    best = result[0]
    stat = result[1]

    time = timebound - stat.total_time

    while result[0] != False:
        max_val = (best.gval - 1)
        engine.init_search(initial_state, sokoban_goal_state, heur_fn)
        result = engine.search(time, (max_val, max_val, max_val))
        if result[0]:
            best = result[0]
            stat = result[1]
            time -= stat.total_time
    return best, stat


