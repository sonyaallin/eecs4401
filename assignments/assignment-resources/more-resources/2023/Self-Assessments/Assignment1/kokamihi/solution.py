#   Look for #IMPLEMENT tags in this file. These tags indicate what has
#   to be implemented to complete the warehouse domain.

#   You may add only standard python imports
#   You may not remove any imports.
#   You may not import or otherwise source any of your own files

import os  # for time functions
import math  # for infinity

from typing import List

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
    For my new heuristic what I first did is to check if a box is in a state that
    it is stuck in while also not being already being in a storage slot which
    i accomplished with my helper _find_storage(). To check if a box was stuck
    I had two helpers _is_box_stuck() and _are_boxes_stuck(), the first of these
    checked the positions around the 4 corners of a box (above, below, left, right)
    and checked if they had a wall or obstacle or another box there. If the
    surrounding objects were positioned such to obstruct movement the first helper
    would return True, the second helper (are_boxes_stuck()) would run a loop
    checking each box by putting it into the first helper and if even ONE returned
    to be in a stuck state we obviously can no longer reach our goal so it would
    return True. I would then check _are_boxes_stuck() output in this alt 
    heuristic and if _are_boxes_stuck() is True we know we cannot possibly reach
    the goal and therefore the heuristic calculated can be set to infinity.
    
    Otherwise I do a simple manhattan calculation for the dist from the closest
    robot to the box and then the closest storage for each box and add those
    distances up but unlike our simple manhattan heurisitc we initially did
    I accounted for multiple boxes not being able to be stored in a single
    storage unit.
    
    I initially made a helper _obstacles_in_way() that would do 
    a similar check to _is_box_stuck() to determine how many of the surrounding
    tiles were obstructed to then add that cost the the manhattan cost. But this
    ended up making the program run too slowly and therefore I dropped it"""
    if _are_boxes_stuck(state):
        return float("inf")

    # Sum of shortest distances from robot to box
    robot_box_total = 0
    for robot in state.robots:
        temp1 = []
        for box in state.boxes:
            dist = _distance_helper(robot, box)
            temp1.append(dist)
        robot_box_total += min(temp1)

    # Sum of shortest distances from box to storage
    box_storage_total = 0
    for box in state.boxes:
        available_storage = _find_storage(state, box)
        temp2 = []
        for storage in available_storage:
            dist = _distance_helper(storage, box)
            temp2.append(dist)
        box_storage_total += min(temp2)

    return robot_box_total + box_storage_total


def heur_zero(state):
    '''Zero Heuristic can be used to make A* search perform uniform cost search'''
    return 0


def _obstacles_in_way(state, box):
    # Check if box is in a corner of grid or obstacles
    # Removed this because it didn't work
    pass



def _find_storage(state, box) -> List[tuple]:
    """find and return a list of tuples for free locations where 'box' can be
    stored given the current 'state' space or return a single tuple if the box
    is already at a storage location
    """
    free_storage = []
    # get locations of all storage spaces and store it
    for storage in state.storage:
        free_storage.append(storage)
        if box == storage:
            return [box]  # if the box is already at a storage location

    for boxes in state.boxes:
        if box != boxes:
            if boxes in free_storage:
                free_storage.remove(boxes)
    return free_storage


def _are_boxes_stuck(state):
    for box in state.boxes:
        if box not in _find_storage(state, box):
            if _is_box_stuck(state, box):
                return True
    return False


def _is_box_stuck(state, box) -> bool:
    is_stuck = False

    # Check if box is in a corner of grid or obstacles
    obstacle_above = False
    obstacle_below = False
    obstacle_left = False
    obstacle_right = False

    # Check if the box has obstacles around it
    if (box[0], box[1]+1) in state.obstacles:
        obstacle_above = True

    if (box[0], box[1]-1) in state.obstacles:
        obstacle_below = True

    if (box[0]-1, box[1]) in state.obstacles:
        obstacle_left = True

    if (box[0]+1, box[1]) in state.obstacles:
        obstacle_right = True

    wall_above = False
    wall_below = False
    wall_left = False
    wall_right = False

    # Check if the box has walls around it
    if box[1]+1 == state.height:
        wall_above = True

    if box[1]-1 == -1:
        wall_below = True

    if box[0]-1 == -1:
        wall_left = True

    if box[0]+1 == state.width:
        wall_right = True

    # Check if the box is stuck (in a corner)
    if (wall_left or obstacle_left) and (wall_above or obstacle_above):
        is_stuck = True
        return is_stuck

    elif (wall_right or obstacle_right) and (wall_above or obstacle_above):
        is_stuck = True
        return is_stuck

    elif (wall_right or obstacle_right) and (wall_below or obstacle_below):
        is_stuck = True
        return is_stuck

    elif (wall_left or obstacle_left) and (wall_below or obstacle_below):
        is_stuck = True
        return is_stuck

    # CHECK if two consecutive boxes are against each other and a wall
    # Check if the box we're checking has boxes around it
    box_above = False
    box_below = False
    box_left = False
    box_right = False

    if (box[0], box[1]+1) in state.boxes:
        box_above = True

    if (box[0], box[1]-1) in state.boxes:
        box_below = True

    if (box[0]-1, box[1]) in state.boxes:
        box_left = True

    if (box[0]+1, box[1]) in state.boxes:
        box_right = True

    # Checking if the box has a box/wall stopping its movement
    if (box_above or box_below) and (wall_left or wall_right):
        is_stuck = True
        return is_stuck

    elif (box_left or box_right) and (wall_above or wall_below):
        is_stuck = True
        return is_stuck

    # CHECK if box is along a wall with no storage spaces
    storage_along_top = False
    storage_along_bot = False
    storage_along_left = False
    storage_along_right = False

    for storage in state.storage:
        if storage[1] == state.height - 1:
            storage_along_top = True
        elif storage[1] == 0:
            storage_along_bot = True
        elif storage[0] == 0:
            storage_along_left = True
        elif storage[0] == state.width - 1:
            storage_along_right = True

    # box is along top wall and that wall has no storage slots along it
    if not storage_along_top and wall_above:
        is_stuck = True
        return is_stuck

    # box is along bot wall and that wall has no storage slots along it
    if not storage_along_bot and wall_below:
        is_stuck = True
        return is_stuck

    # box is along left wall and that wall has no storage slots along it
    if not storage_along_left and wall_left:
        is_stuck = True
        return is_stuck

    # box is along right wall and that wall has no storage slots along it
    if not storage_along_right and wall_right:
        is_stuck = True
        return is_stuck

    return is_stuck


def _distance_helper(t1, t2) -> int:
    """calculate the manhattan distance between two coordinates"""
    dist = abs(t1[0] - t2[0]) + abs(t1[1] - t2[1])
    return dist


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
    total = 0
    for box in state.boxes:
        temp = []
        for store in state.storage:
            dist = _distance_helper(box, store)
            temp.append(dist)
        total += min(temp)
    return total


def fval_function(sN, weight):
    # IMPLEMENT
    """
    Provide a custom formula for f-value computation for Anytime Weighted A star.
    Returns the fval of the state contained in the sNode.

    @param sNode sN: A search node (containing a SokobanState)
    @param float weight: Weight given by Anytime Weighted A star
    @rtype: float
    """
    return (weight * sN.hval) + sN.gval


# SEARCH ALGORITHMS
def weighted_astar(initial_state, heur_fn, weight, timebound):
    # IMPLEMENT
    '''Provides an implementation of weighted a-star, as described in the HW1 handout'''
    '''INPUT: a sokoban state that represents the start state and a timebound (number of seconds)'''
    '''OUTPUT: A goal state (if a goal is found), else False as well as a SearchStats object'''
    '''implementation of weighted astar algorithm'''
    s_engine = SearchEngine('custom', 'full')
    wrapped_fval_function = (lambda sN : fval_function(sN, weight))
    s_engine.init_search(initial_state, sokoban_goal_state, heur_fn, wrapped_fval_function)
    return s_engine.search(timebound)

def iterative_astar(initial_state, heur_fn, weight=1, timebound=5):  # uses f(n), see how autograder initializes a search line 88
    # IMPLEMENT
    '''Provides an implementation of realtime a-star, as described in the HW1 handout'''
    '''INPUT: a sokoban state that represents the start state and a timebound (number of seconds)'''
    '''OUTPUT: A goal state (if a goal is found), else False as well as a SearchStats object'''
    '''implementation of iterative astar algorithm'''
    found_solution = False
    least_cost = (float("inf"), float("inf"), float("inf"))
    wrapped_fval_function = (lambda sN : fval_function(sN, weight))
    start_time = os.times()[0]
    time_left = timebound

    # Initialize search
    s_engine = SearchEngine('custom', 'full')
    s_engine.init_search(initial_state, sokoban_goal_state, heur_fn, wrapped_fval_function)

    # Search
    while time_left - 0.1 > 0:
        result, stats = s_engine.search(time_left, least_cost)
        weight = weight*0.5
        time_left -= stats.total_time
        if result:
            least_cost = (result.gval, heur_fn(result), result.gval + weight * heur_fn(result))
            found_solution = result
        else:
            break
    return found_solution, stats


def iterative_gbfs(initial_state, heur_fn, timebound=5):  # only use h(n)
    # IMPLEMENT
    '''Provides an implementation of anytime greedy best-first search, as described in the HW1 handout'''
    '''INPUT: a sokoban state that represents the start state and a timebound (number of seconds)'''
    '''OUTPUT: A goal state (if a goal is found), else False'''
    '''implementation of iterative gbfs algorithm'''
    found_solution = False
    least_cost = (float("inf"), float("inf"), float("inf"))
    best_gval = float("inf")
    time_left = timebound

    # Initialize search
    s_engine = SearchEngine('best_first', 'full')
    s_engine.init_search(initial_state, sokoban_goal_state, heur_fn)

    # Search
    while time_left - 0.1 > 0:
        result, stats = s_engine.search(time_left, least_cost)
        time_left -= stats.total_time
        if result:
            best_gval = min(best_gval, result.gval)
            least_cost = (best_gval, float("inf"), float("inf"))
            found_solution = result
        else:
            break
    return found_solution, stats




