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

def _check_for_walls(start, stop, state):
    # Checks for any obstacles that might lie in the path from start to stop. It also accounts for the fact
    # that the presence of a wall may not always result in an increased path length, as the entity might have to move
    # in that direction anyways. The function returns 0 if extra moves exceed the said buffer, or it returns the
    # number of extra moves the bot might have to make.
    x_len = abs(start[0] - stop[0])
    y_len = abs(start[1] - stop[1])
    extra_moves = -1 * y_len
    x_range = range(min(start[0], stop[0]), max(start[0], stop[0]) + 1)
    y_range = range(min(start[1], stop[1]), max(start[1], stop[1]) + 1)
    if x_len < y_len:
        extra_moves = -1 * x_len
        for y in y_range:
            for x in x_range:
                wall_len = 0
                if (x, y) != start and (x, y) != stop and \
                        ((x, y) in state.obstacles or ((x, y) in state.robots) or ((x, y) in state.boxes)):
                    extra_moves += 1
                    if x_len == 0:
                        extra_moves += 1
    else:
        for x in x_range:
            for y in y_range:
                if (x, y) != start and (x, y) != stop and \
                        ((x, y) in state.obstacles or ((x, y) in state.robots) or ((x, y) in state.boxes)):
                    extra_moves += 1
                    if y_len == 0:
                        extra_moves += 1

    if extra_moves < 0:
        return 0
    return extra_moves



def heur_alternate(state):
    # IMPLEMENT
    '''a better heuristic'''
    '''INPUT: a sokoban state'''
    '''OUTPUT: a numeric value that serves as an estimate of the distance of the state to the goal.'''
    # heur_manhattan_distance has flaws.
    # Write a heuristic function that improves upon heur_manhattan_distance to estimate distance between the current state and the goal.
    # Your function should return a numeric value for the estimate of the distance to the goal.
    # EXPLAIN YOUR HEURISTIC IN THE COMMENTS. Please leave this function (and your explanation) at the top of your solution file, to facilitate marking.

    # Explanation: By just finding the manhattan distance of boxes to the closest storage location, we are ignoring the
    # fact that only one box can be stored at one location. This heuristic is not as accurate as it could be since
    # multiple boxes could point to the same storage location, which will give the algorithm an inaccurate idea as to
    # how much more work needs to be done, as it is not possible to store multiple boxes in the same storage.
    # One improvement that can be made is to assign unique pairs of storages and locations, to give the algorithm a
    # more accurate idea. I am going to use a greedy approach - find the smallest distance for the first nth box,
    # remove that location from available locations, and continue. Even though this might not give the most optimal
    # combination of storage and box pairs, comparing every single box and storage location combination is not feasible
    # as this task would require computational complexity of O(b!), where b is the number of boxes, as we would need to
    # find every possible permutation of boxes assigned to specific storage locations. It is much more practical
    # to trade the slight accuracy improvement for much better operation speeds, therefore, greedy would be the better
    # option. The greedy approach's result will not be the most accurate, however, it still will be a much bigger
    # improvement overall than the previous heuristic, as it accounts for the fact that only one box can be stored at a
    # location.
    # Another improvement I've made is to find which robot lies the closest to a given storage box, based on where
    # robot needs to end up to push the box in the required direction. This gives a more accurate idea of how many
    # moves the robot needs to make to push the robot to its final position.
    # I also account for all the obstacles that are present in the path of the box on its way to the storage, and the
    # robot on the way to its desired position, and add a penalty to their distance scores.
    # Finally, I add up these distances along with penalties to h if and only if the current box is not right next to
    # its target destination and there is no robot next to it to push it into its final destination. I repeat this
    # process for each box, sum up these values to h and then finally return h.
    h = 0

    storages_used = set()
    for box in state.boxes:
        smallest_distance = float('inf')
        selected_storage = None
        for storage in state.storage:
            if storage in storages_used:
                continue
            storage_distance = abs(box[0] - storage[0]) + abs(box[1] - storage[1])
            # If there are obstacles in the path add them to distance, we need to deviate by atleast 1 for each obstacle
            storage_distance += _check_for_walls(box, storage, state)
            if smallest_distance > storage_distance:
                smallest_distance = storage_distance
                selected_storage = storage
        if selected_storage not in state.boxes:
            storages_used.add(selected_storage)
        bot_locations = []
        if (selected_storage[0] < box[0]) and (
                box[0] + 1 < state.width and (box[0] + 1, box[1]) not in state.obstacles and
                (box[0] + 1, box[1]) not in state.boxes and (
                        box[0] + 1, box[1]) not in state.robots and (
                box[0] - 1, box[1]) not in state.obstacles):  # storage is to the left
            bot_locations.append((box[0] + 1, box[1]))
        if selected_storage[0] > box[0] and (
                box[0] - 1 >= 0 and (box[0] - 1, box[1]) not in state.obstacles and
                (box[0] - 1, box[1]) not in state.boxes and (box[0] - 1, box[1]) not in state.robots
                and (box[0] + 1, box[1]) not in state.obstacles):  # storage is to the right
            bot_locations.append((box[0] - 1, box[1]))
        if selected_storage[1] < box[1] and (
                box[1] + 1 < state.height and (box[0], box[1] + 1) not in state.obstacles and
                (box[0], box[1] + 1) not in state.boxes and (box[1], box[1] + 1) not in state.robots and
                (box[0], box[1] - 1) not in state.obstacles):  # storage is upwards
            bot_locations.append((box[0], box[1] + 1))
        if selected_storage[1] > box[1] and (
                box[1] - 1 >= 0 and (box[0], box[1] - 1) not in state.obstacles and
                (box[0], box[1] - 1) not in state.boxes and (box[0], box[1] - 1) not in state.robots
                and (box[0], box[1] + 1) not in state.obstacles):  # storage is downwards
            # Punish the bot below by 2, as it would take at least two more steps to get to the right of the box
            bot_locations.append((box[0], box[1] - 1))
        # Find the distance to the closest bot
        closest_robot = float('inf')
        selected_bot = None
        for robot in state.robots:
            bot_distance = 0
            for loc in bot_locations:
                bot_distance = abs(loc[0] - robot[0]) + abs(loc[1] - robot[1])
                bot_distance += _check_for_walls(robot, loc, state)
            if bot_distance < closest_robot:
                closest_robot = bot_distance
                selected_bot = robot
        if not (selected_bot in bot_locations and smallest_distance == 1):
            h += smallest_distance + closest_robot
    return h



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
    h = 0
    for box in state.boxes:
        smallest_distance = float('inf')
        for storage in state.storage:
            smallest_distance = min(smallest_distance, abs(box[0] - storage[0]) + abs(box[1] - storage[1]))
        h += smallest_distance
    return h


def fval_function(sN, weight):
    # IMPLEMENT
    """
    Provide a custom formula for f-value computation for Anytime Weighted A star.
    Returns the fval of the state contained in the sNode.

    @param sNode sN: A search node (containing a SokobanState)
    @param float weight: Weight given by Anytime Weighted A star
    @rtype: float
    """
    return sN.gval + (weight * sN.hval)


# SEARCH ALGORITHMS
def weighted_astar(initial_state, heur_fn, weight, timebound):
    # IMPLEMENT
    '''Provides an implementation of weighted a-star, as described in the HW1 handout'''
    '''INPUT: a sokoban state that represents the start state and a timebound (number of seconds)'''
    '''OUTPUT: A goal state (if a goal is found), else False as well as a SearchStats object'''
    '''implementation of weighted astar algorithm'''
    search = SearchEngine(strategy='custom')
    wrapped_fval_function = (lambda sN: fval_function(sN, weight))
    search.init_search(initial_state, sokoban_goal_state, heur_fn, wrapped_fval_function)
    return search.search(timebound=timebound)


def iterative_astar(initial_state, heur_fn, weight=1,
                    timebound=5):  # uses f(n), see how autograder initializes a search line 88
    # IMPLEMENT
    '''Provides an implementation of realtime a-star, as described in the HW1 handout'''
    '''INPUT: a sokoban state that represents the start state and a timebound (number of seconds)'''
    '''OUTPUT: A goal state (if a goal is found), else False as well as a SearchStats object'''
    '''implementation of iterative astar algorithm'''
    start_time = os.times()[0]
    state, stats = None, None
    cost_cap = None
    search = SearchEngine(strategy='custom')
    wrapped_fval_function = (lambda sN: fval_function(sN, weight))
    while True:
        search.init_search(initial_state, sokoban_goal_state, heur_fn, wrapped_fval_function)
        new_state, new_stats = search.search(timebound=timebound - (os.times()[0] - start_time), costbound=cost_cap)
        if new_state is not False:
            state, stats = new_state, new_stats
            cost_cap = (float('inf'), float('inf'), new_state.gval)
        if os.times()[0] - start_time >= timebound:
            return state, stats


def iterative_gbfs(initial_state, heur_fn, timebound=5):  # only use h(n)
    # IMPLEMENT
    '''Provides an implementation of anytime greedy best-first search, as described in the HW1 handout'''
    '''INPUT: a sokoban state that represents the start state and a timebound (number of seconds)'''
    '''OUTPUT: A goal state (if a goal is found), else False'''
    '''implementation of iterative gbfs algorithm'''
    start_time = os.times()[0]
    state, stats = None, None
    cost_cap = None
    search = SearchEngine(strategy='best_first')
    while True:
        search.init_search(initial_state, sokoban_goal_state, heur_fn)
        new_state, new_stats = search.search(timebound=timebound - (os.times()[0] - start_time), costbound=cost_cap)
        if new_state is not False:
            state, stats = new_state, new_stats
            cost_cap = (new_state.gval, float('inf'), float('inf'))
        if os.times()[0] - start_time >= timebound:
            return state, stats
