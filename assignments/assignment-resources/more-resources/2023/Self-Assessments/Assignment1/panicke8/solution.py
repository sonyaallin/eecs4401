#   Look for #IMPLEMENT tags in this file. These tags indicate what has
#   to be implemented to complete the warehouse domain.

#   You may add only standard python imports
#   You may not remove any imports.
#   You may not import or otherwise source any of your own files

from cmath import inf
import os  # for time functions
import math  # for infinity
from search import *  # for search engines
# for Sokoban specific classes and problems
from sokoban import sokoban_goal_state, SokobanState, Direction, PROBLEMS

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

    updated_strg = set(state.storage)  # [list(strg) for strg in state.storage]
    updated_robots = set(state.robots)  # [list(bot) for bot in state.robots]
    # Initially used list comprehensions to mutate elements of the frozensets. Later discovered using set() for efficiency
    final_cost = 0  # Final heuristic value to return

    for box in state.boxes:
        min_box_to_strg = state.width + state.height  # Distance longer than diagonal
        min_box_to_robot = state.width + state.height  # Distance longer than diagonal
        nearest_robot = None  # Resetting the nearest robot for every box iterated through

        for storage in updated_strg:
            temp_box_to_strg = abs(box[0] - storage[0]) + abs(box[1] - storage[1])
            if temp_box_to_strg < min_box_to_strg:
                min_box_to_strg = temp_box_to_strg
                close_storage = storage # Closest storage ready for removal

        updated_strg.remove(close_storage)  # Remove the closest storage location to a box so none other can use it

        if min_box_to_strg == 0:
            continue  # Move onto the next iteration, box is already in a storage location
        elif is_in_vertex(state, box): # Return a high cost if a box is in one of the verticies
            return 1000
        final_cost += min_box_to_strg

        for robot in updated_robots:
            temp_box_to_robot = abs(robot[0] - box[0]) + abs(robot[1] - box[1])
            if temp_box_to_robot < min_box_to_robot:
                min_box_to_robot = temp_box_to_robot
                nearest_robot = robot # Nearest robot ready for removal

        if nearest_robot:
            updated_robots.remove(nearest_robot) # The closest robot shouldn't deal with the remaining boxes
        final_cost += min_box_to_strg
    return final_cost


def is_in_vertex(state, box):
    '''Helper function that checks for boxes trapped in one of the 4 verticies.'''
    left_vertex = ((box[0] - 1, box[1]) in state.obstacles) or (box[0] == 0)

    right_vertex = ((box[0] + 1, box[1])
                    in state.obstacles) or (box[0] == state.width - 1)

    up_vertex = ((box[0], box[1] + 1) in state.obstacles) or (box[1] == 0)

    down_vertex = ((box[0], box[1] - 1)
                   in state.obstacles) or (box[1] == state.height - 1)

    return (left_vertex or right_vertex) and (up_vertex or down_vertex)


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
    total_sum = 0  # | x0 − x1 | + | y0 − y1 |

    for box_x, box_y in state.boxes:
        closest_sum = state.width + state.height  # Distance longer than diagonal
        for strg_x, strg_y in state.storage:
            curr_sum = abs(box_x - strg_x) + abs(box_y - strg_y)
            if curr_sum <= closest_sum:
                closest_sum = curr_sum
        total_sum += closest_sum
    return total_sum


def fval_function(sN, weight):
    # IMPLEMENT
    """
    Provide a custom formula for f-value computation for Anytime Weighted A star.
    Returns the fval of the state contained in the sNode.

    @param sNode sN: A search node (containing a SokobanState)
    @param float weight: Weight given by Anytime Weighted A star
    @rtype: float
    """
    return sN.gval + weight * sN.hval  # fval_function f(node) = g(node) + w * h(node)

# SEARCH ALGORITHMS


def weighted_astar(initial_state, heur_fn, weight, timebound):
    # IMPLEMENT
    '''Provides an implementation of weighted a-star, as described in the HW1 handout'''
    '''INPUT: a sokoban state that represents the start state and a timebound (number of seconds)'''
    '''OUTPUT: A goal state (if a goal is found), else False as well as a SearchStats object'''
    '''implementation of weighted astar algorithm'''
    wrapped_fval_function = (lambda sN: fval_function(sN, weight))

    my_engine = SearchEngine(strategy="custom", cc_level="default")
    my_engine.init_search(initial_state, sokoban_goal_state,
                          heur_fn, wrapped_fval_function)
    search_sol = my_engine.search(timebound)

    return search_sol


# uses f(n), see how autograder initializes a search line 88
def iterative_astar(initial_state, heur_fn, weight=1, timebound=5):
    # IMPLEMENT
    '''Provides an implementation of realtime a-star, as described in the HW1 handout'''
    '''INPUT: a sokoban state that represents the start state and a timebound (number of seconds)'''
    '''OUTPUT: A goal state (if a goal is found), else False as well as a SearchStats object'''
    '''implementation of iterative astar algorithm'''
    time_curr = os.times()[0]
    timebound_new = timebound  # will change later
    time_end = time_curr + timebound

    wrapped_fval_function = (lambda sN: fval_function(sN, weight))

    my_engine = SearchEngine(strategy="custom", cc_level="default")
    my_engine.init_search(initial_state, sokoban_goal_state,
                          heur_fn, wrapped_fval_function)
    search_sol = my_engine.search(timebound)

    good_result = False
    good_stats = search_sol[1]
    max_cost = (inf, inf, inf)

    while time_curr < time_end:
        wrapped_fval_updated = (lambda sN: fval_function(sN, weight * 0.8))
        my_engine.init_search(
            initial_state, sokoban_goal_state, heur_fn, wrapped_fval_updated)
        if search_sol[0] == False:
            return good_result, good_stats

        time_difference = os.times()[0] - time_curr

        timebound_new = timebound_new - time_difference

        if (search_sol[0].gval <= max_cost[0]):
            good_result = search_sol[0]
            good_stats = search_sol[1]
            max_cost = (search_sol[0].gval,
                        search_sol[0].gval, search_sol[0].gval)

        search_sol = my_engine.search(timebound_new, max_cost)  # search again
        time_curr = os.times()[0]
    return good_result, good_stats


def iterative_gbfs(initial_state, heur_fn, timebound=5):  # only use h(n)
    # IMPLEMENT
    '''Provides an implementation of anytime greedy best-first search, as described in the HW1 handout'''
    '''INPUT: a sokoban state that represents the start state and a timebound (number of seconds)'''
    '''OUTPUT: A goal state (if a goal is found), else False'''
    '''implementation of iterative gbfs algorithm'''

    time_curr = os.times()[0]
    timebound_new = timebound  # will change later
    time_end = time_curr + timebound

    my_engine = SearchEngine(strategy="best_first", cc_level="default")
    my_engine.init_search(initial_state, sokoban_goal_state, heur_fn)
    search_sol = my_engine.search(timebound)

    good_result = False
    max_cost = (inf, inf, inf)  # how to best initialize each to max?

    while time_curr < time_end:
        if search_sol[0] == False:
            return good_result, search_sol[1]

        time_difference = os.times()[0] - time_curr
        timebound_new -= time_difference

        if (search_sol[0].gval <= max_cost[0]):
            good_result = search_sol[0]
            max_cost = (search_sol[0].gval,
                        search_sol[0].gval, search_sol[0].gval)

        search_sol = my_engine.search(timebound_new, max_cost)  # search again
        time_curr = os.times()[0]  # Is this necessary?
    return good_result, search_sol[1]
