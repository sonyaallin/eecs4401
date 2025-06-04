#   Look for #IMPLEMENT tags in this file. These tags indicate what has
#   to be implemented to complete the warehouse domain.

#   You may add only standard python imports
#   You may not remove any imports.
#   You may not import or otherwise source any of your own files

from __future__ import annotations
import os  # for time functions
import math  # for infinity
from search import *  # for search engines
from sokoban import sokoban_goal_state, SokobanState, Direction, PROBLEMS  # for Sokoban specific classes and problems
import itertools

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

    # ATTEMPT 1: tried to get closer to optimal heuristic by storing the distance between each node and storage space
    # in a dictionary of min heaps, to extract the closest (non-occupied) space for each node if conflict for storage
    # space was present. Implementation was too slow with O(n^2 * logn) worst-case runtime.

    # NOTES:
    # We want to avoid over-estimating the distance whilst getting closer to the optimal distance to achieve
    # a better heuristic. By accounting for obstacles such as other boxes, or walls, we can hopefully achieve
    # a heuristic closer to the optimal one. We do this beacuse it is very unlikely that the path to the goal
    # for any sokoban room will be obstacle-less. Hence, the manhattan distance is a very optimistic which
    # we want to avoid. 

    # ATTEMPT 2: Take into account obstacles that obstruct a robots ability to move. Include obstruction
    # caused by other boxes in certain cases where the other box is ALSO immovable. 

    # This attempt garnered better results, but it does not reach benchmark :( 

    total_dist = 0

    for box in state.boxes:
        remaining_storage = get_remaining_storage(box, state)

        # box is already in position; no need to check
        if len(remaining_storage) == 0:
            continue

        # Box cannot reach goal, abandon this searchSpace as no sltn will be found
        if at_edge(box, remaining_storage, state) or at_corner(box, state):
            return float("inf")

        min_man_dist = float("inf")

        # find minimum man dist. from this box as usual
        for space in state.storage:
            x0, y0 = box[0], box[1]
            x1, y1 = space[0], space[1]

            if x0 == x1 and y0 == y1:
                min_man_dist = 0
                break

            man_dist = abs(x0-x1) + abs(y0-y1)

            if man_dist < min_man_dist:
                min_man_dist = man_dist

        # improved heuristic by incorporating obstacles in the manhattan path
        # from nearest robot to this box into the value of our heuristic. The logic
        # behind this is that if there are obstacles in the path, the cost required
        # is likely to increase as a result, hence we are adding it to the total.
        total_dist += min_man_dist + obstacles_in_man_path(box, state) 

    return total_dist
        

def obstacles_in_man_path(box: tuple[int, int], state: SokobanState) -> int:
    """ This function finds the number of obstacles in the MANHATTAN PATH
    of the nearest robot to the specified box. The paths are simple L shaped paths
    going up then left/right or down then left/right. 

    INTENDED PURPOSE: wanted to also calculate obstacles from box to nearest storage
    space, but this added complexity presumably increased the runtime of my impl.
    which reduced the number of test cases solved by 1 :(  ...
    """
    min_man_bot_dist = float("inf")
    closest_bot = None
    bx, by = box[0], box[1]

    for robot in state.robots:
        if robot not in state.storage:
            rx, ry = robot[0], robot[1]
            min_man_bot_dist = min(abs(bx-rx) + abs(by-ry), min_man_bot_dist)
            closest_bot = robot

    min_man_store_dist = float("inf")
    closest_store = None
    remaining_storage = get_remaining_storage(box, state)
    for store in remaining_storage:
        sx, sy = store[0], store[1]
        min_man_store_dist = min(abs(bx-sx) + abs(by-sy), min_man_store_dist)
        closest_store = store

    obstacle_ctr = 0 

    if closest_bot is not None and closest_store is not None:
        # bot to box (vertical)
        rx, ry = closest_bot[0], closest_bot[1]
        for i in range(min(rx, bx), max(rx, bx)+1):
            # take into account both upper and lower paths
            if (i, ry) in state.obstacles:
                obstacle_ctr += 1
            if (i, by) in state.obstacles:
                obstacle_ctr += 1

        # bot to box (horizontal)
        for i in range(min(ry, by), max(ry, by)+1):
            # take into account both left and right paths
            if (rx, i) in state.obstacles:
                obstacle_ctr += 1
            if (bx, i) in state.obstacles:
                obstacle_ctr += 1

        # box to store (vertical) (uncommenting this reduces no. of solved probs :( ))
        # for i in range(min(bx, sx), max(bx, sx)+1):
        #     if (i, by) in state.obstacles:
        #         obstacle_ctr += 1
        #     if (i, sy) in state.obstacles:
        #         obstacle_ctr += 1

        # box to store (horizontal) (uncommenting this reduces no. of solved probs :( ))
        # for i in range(min(by, sy), max(by, sy)+1):
        #     if (bx, i) in state.obstacles:
        #         obstacle_ctr += 1
        #     if (sx, i) in state.obstacles:
        #         obstacle_ctr += 1

    return obstacle_ctr



def get_remaining_storage(box: tuple[int, int], state: SokobanState) -> set[tuple]:
    """ Return a set of all unoccupied storage spaces available to the box.
    Returns empty set if it is already on a storage spot.
    """

    # Check whether this box is in a storage spot already
    if box in state.storage:
        return set()

    res = set(state.storage)

    # Check if any other storage spaces have been occupied
    rest = state.boxes - {box}
    for box in rest:
        if box in state.storage:
            res.remove(box)

    return res


def at_edge(box: tuple[int, int], rem_storage_spaces: set, state: SokobanState) -> bool:
    """ Returns true if this box is at the edge and there are no storage spaces along 
    the edge that it is up against. Also returns True if this box is at edge and is 
    restricted in its movement in up/down direction or left/right direction by any 
    obstacles, depending on the edge. This includes other boxes that are also pressed
    up against the same edge. Returns False otherwise.
    """
    room_width = state.width
    room_height = state.height

    x, y = box[0], box[1]

    storage_x_vals = [s[0] for s in rem_storage_spaces]
    storage_y_vals = [s[1] for s in rem_storage_spaces]
    x_set = frozenset(storage_x_vals)
    y_set = frozenset(storage_x_vals)

    all_obstacles = state.obstacles.union(state.boxes)

    # Check if any storage spaces are up against the left or right wall
    if x == 0 or x == room_width - 1:
        # Check if any storage spots have the same x value meaning they are 
        # along left or right wall
        if x not in x_set:
            return True 

        # vertical edge, check top and bottom of box for obstacles
        if (x, y+1) in all_obstacles or (x, y-1) in all_obstacles:
            return True

    # Check if any storage spaces are up against the top or bottom wall
    if y == 0 or y == room_height - 1:
        # Similarly but for top and bottom of wall
        if y not in y_set:
            return True

        # horizontal edge, check left and right of box for obstacles
        if (x+1, y) in all_obstacles or (x-1, y) in all_obstacles:
            return True

    return False

def at_corner_room(box: tuple[int, int], state: SokobanState) -> bool:
    """ Returns True if this box is in any of the four corners of the room.
    Returns False otherwise.
    """
    room_width = state.width
    room_height = state.height
    x, y = box[0], box[1]

    if x == 0 or x == room_width - 1:
        if y == 0 or y == room_height - 1:
            return True

    return False

def at_corner_obs(box: tuple[int, int], state: SokobanState) -> bool:
    """ Returns True if this box is in any corner formed by immovable obstacless.
    Returns False otherwise.
    """
    x, y = box[0], box[1]
    top, bottom = (x, y+1), (x, y-1)
    left, right = (x-1, y), (x+1, y)


    # top+left or top+right occupied
    if top in state.obstacles:
        if left in state.obstacles or right in state.obstacles:
            return True
    # bottom+left or bottom+right occupied
    if bottom in state.obstacles:
        if left in state.obstacles or right in state.obstacles:
           return True

    return False


def at_corner(box: tuple[int, int], state: SokobanState) -> bool:
    """ Returns True if this box is any form of corner in the room. 
    Returns False otherwise.
    """
    return at_corner_room(box, state) or at_corner_obs(box, state)   


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

    total_dist = 0

    for box in state.boxes:
        min_man_dist = float("inf")

        for space in state.storage:
            x0, y0 = box[0], box[1]
            x1, y1 = space[0], space[1]

            if x0 == x1 and y0 == y1:
                min_man_dist = 0
                break

            man_dist = abs(x0-x1) + abs(y0-y1)

            if man_dist < min_man_dist:
                min_man_dist = man_dist

        total_dist += min_man_dist

    return total_dist

def fval_function(sN, weight):
    # IMPLEMENT
    """
    Provide a custom formula for f-value computation for Anytime Weighted A star.
    Returns the fval of the state contained in the sNode.

    @param sNode sN: A search node (containing a SokobanState)
    @param float weight: Weight given by Anytime Weighted A star
    @rtype: float
    """
    f = sN.gval + (weight * sN.hval)
    return f

# SEARCH ALGORITHMS
def weighted_astar(initial_state, heur_fn, weight, timebound):
    # IMPLEMENT
    '''Provides an implementation of weighted a-star, as described in the HW1 handout'''
    '''INPUT: a sokoban state that represents the start state and a timebound (number of seconds)'''
    '''OUTPUT: A goal state (if a goal is found), else False as well as a SearchStats object'''
    '''implementation of weighted astar algorithm'''
    search_engine = SearchEngine('custom', 'full')
    wrapped_fval_function = (lambda sN : fval_function(sN, weight))
    search_engine.init_search(initial_state, sokoban_goal_state, heur_fn, wrapped_fval_function)

    return search_engine.search(timebound)

def iterative_astar(initial_state, heur_fn, weight=1, timebound=5):  # uses f(n), see how autograder initializes a search line 88
    # IMPLEMENT
    '''Provides an implementation of realtime a-star, as described in the HW1 handout'''
    '''INPUT: a sokoban state that represents the start state and a timebound (number of seconds)'''
    '''OUTPUT: A goal state (if a goal is found), else False as well as a SearchStats object'''
    '''implementation of iterative astar algorithm'''

    search_engine = SearchEngine('custom', 'full')
    wrapped_fval_function = (lambda sN : fval_function(sN, weight))
    search_engine.init_search(initial_state, sokoban_goal_state, heur_fn, wrapped_fval_function)

    best_path_final_state = False 
    best_path_stats = None
    lowest_f = float("inf")

    time_elapsed = 0
    while time_elapsed < timebound:

        start_time = os.times()[0]

        # if any node has f = g(node) + h(node) value greater than the cost of the best path to goal
        # so far, we can prune it. We prune using index 2 which corresponds to f val
        final_state, stats = search_engine.search(timebound, 
            (float("inf"), float("inf"), lowest_f))
        end_time = os.times()[0]

        time_elapsed += end_time - start_time

        # want to reduce the weight at just the right amount to improve solution
        # fiddled around but this seems to work best
        weight *= 0.5

        if final_state:
            best_path_final_state = final_state
            best_path_stats = stats
            lowest_f = best_path_final_state.gval + heur_fn(best_path_final_state)
        else:
            break

    return best_path_final_state, best_path_stats

def iterative_gbfs(initial_state, heur_fn, timebound=5):  # only use h(n)
    # IMPLEMENT
    '''Provides an implementation of anytime greedy best-first search, as described in the HW1 handout'''
    '''INPUT: a sokoban state that represents the start state and a timebound (number of seconds)'''
    '''OUTPUT: A goal state (if a goal is found), else False'''
    '''implementation of iterative gbfs algorithm'''

    search_engine = SearchEngine('best_first', 'full')
    search_engine.init_search(initial_state, sokoban_goal_state, heur_fn, heur_fn)

    best_path_final_state = False 
    best_path_stats = None
    lowest_cost = float("inf")

    time_elapsed = 0
    while time_elapsed < timebound:

        start_time = os.times()[0]
        # we are pruning using g(node) value this time so use index 0
        final_state, stats = search_engine.search(timebound, 
            (lowest_cost, float("inf"), float("inf")))
        end_time = os.times()[0]

        time_elapsed += end_time - start_time

        if final_state:
            best_path_final_state = final_state
            best_path_stats = stats
            lowest_cost = final_state.gval
        else:
            break

    return best_path_final_state, best_path_stats



