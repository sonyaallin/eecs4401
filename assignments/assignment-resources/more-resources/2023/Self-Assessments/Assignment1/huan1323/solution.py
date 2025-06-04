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
LAST_STATE_BOX = None
LAST_STATE_STORAGE = None
LAST_H = 9999


# SOKOBAN HEURISTICS
def heur_alternate(state):
    # IMPLEMENT
    '''a better heuristic'''
    '''INPUT: a sokoban state'''
    '''OUTPUT: a numeric value that serves as an estimate of the distance of 
    the state to the goal. '''
    # heur_manhattan_distance has flaws. Write a heuristic function that
    # improves upon heur_manhattan_distance to estimate distance between the
    # current state and the goal. Your function should return a numeric value
    # for the estimate of the distance to the goal. EXPLAIN YOUR HEURISTIC IN
    # THE COMMENTS. Please leave this function (and your explanation) at the
    # top of your solution file, to facilitate marking.
    """
    Main Estimation:
    Step 1: 
    In this heuristic estimation, it firstly calculates the shortest path from
    each box to each storage and stores the costs in a n x n matrix-like list. 
    Notice that not every pair of box and storage has a valid path between them. 
    For instance, box in corner and box at edge have a restriction on moving. 
    When there is no valid for a pair, set the cost to 9999 as a very large cost.
    Step 2:
    After we get the matrix, we want to assign each box to a storage that other 
    box are not assigned and calculate the sum cost of these pairs. To calculate 
    that, I initially sum up the minima in each row in the matrix. 
    Simultaneously, update each row by subtracting its minimum value to every 
    elements. Since each row repersents a box and each column repersents a 
    storage, this operation set a closest storage to each box. However, some 
    boxes can be set to the same storage when these boxes has the same closest 
    storage. Therefore, I do the same subtraction to each column. If the column 
    has a zero in it, nothing change. If a column has no zero, the subtraction 
    will make a zero there. These two steps make sures each column and row has a 
    0 in it which means this box can be set to this storage. Therefore, adding 
    up the subtracted values of rows and columns gives me the shortest cost of 
    each box going to a specific storage.
    
    Additional runtime Optimizing:
    When the search working, it always move robots around without pushing any 
    box. Since we only cares about the position of boxes and storages, I stores 
    the last time state and returned value in a global variable. In the 
    beginning, the code will compare the input state to the last time state and 
    return the last time output if the two state are same.
    
    Things I have tried:
    1. Robot distance is something I tried first. I have tried setting robots 
    paths to boxes, giving a robot with not box nearby a penalty cost of 1 and 
    so on. However, these approaches makes the heuristic worse. The search 
    algorithm can easily stuck in some situations like, do not leave after 
    pushing a box to the storage and sending multiple robots to push one box and 
    block each other. Therefore, I give up on these approaches.
    2. Setting some storages to be filled first. There are some storages in the
    corner need to be filled first. Otherwise, fill up other storages can block
    the way to that storage. This is a pretty good thought, but I need to match
    this storages to boxes first. Otherwise, the search algorithm can choose a 
    box on the edge and it is never going to make it. However, matching boxes 
    and storage solved tis problem. When a box blocks the way, the heuristic 
    will be called and gives a new match. Therefore, the search algorithm knows
    this box needs to fill that storage first, so I delete the codes about this
    part and decide to write the matching matrix.
     
    
    """
    global LAST_STATE_BOX
    global LAST_STATE_STORAGE
    global LAST_H
    if LAST_STATE_BOX:
        if state.boxes == LAST_STATE_BOX and state.storage == LAST_STATE_STORAGE:
            return LAST_H

    dist_boxes_to_goal = []
    for box in state.boxes:
        sub_dist = []
        for storage in state.storage:
            if in_corner(state, box):
                if box == storage:
                    sub_dist.append(0)
                else:
                    sub_dist.append(9999)
            elif box[0] == 0 or box[0] == state.width-1:
                if storage[0] == box[0]:
                    sub_dist.append(abs(storage[1] - box[1]))
                else:
                    sub_dist.append(9999)
            elif box[1] == 0 or box[1] == state.height-1:
                if storage[1] == box[1]:
                    sub_dist.append(abs(storage[0] - box[0]))
                else:
                    sub_dist.append(9999)
            else:
                sub_dist.append(
                    abs(storage[0] - box[0]) + abs(storage[1] - box[1]))
        dist_boxes_to_goal.append(sub_dist)

    d = assign_lowest_path(dist_boxes_to_goal)
    LAST_STATE_BOX = state.boxes
    LAST_STATE_STORAGE = state.storage
    LAST_H = d
    return d


def robot_penalty(state):
    for robot in state.robots:
        for i in range(-1, 2):
            for j in range(-1, 2):
                if (robot[0]+i, robot[1]+j) in state.boxes:
                    return 1
    return 0


def assign_lowest_path(matrix):
    distance = 0
    for row in range(len(matrix)):
        minima = minrow(row, matrix)
        for col in range(len(matrix[row])):
            matrix[row][col] -= minima
        distance += minima
    for col in range(len(matrix)):
        minima = mincol(col, matrix)
        for row in range(len(matrix)):
            matrix[row][col] -= minima
        distance += minima
    return distance


def in_corner(state, box):
    vertical_edge = box[0] == 0 or box[0] == state.width - 1
    horizontal_edge = box[1] == 0 or box[1] == state.height - 1
    vertical_obstacles = (box[0] + 1, box[1]) in state.obstacles or (box[0] - 1, box[1]) in state.obstacles
    horizontal_obstacles = (box[0], box[1] + 1) in state.obstacles or (box[0], box[1] - 1) in state.obstacles
    vertical_walls = vertical_edge or vertical_obstacles
    horizontal_walls = horizontal_edge or horizontal_obstacles
    left_box = (box[0] - 1, box[1]) in state.boxes
    right_box = (box[0] + 1, box[1]) in state.boxes
    up_box = (box[0], box[1] - 1) in state.boxes
    down_box = (box[0], box[1] + 1) in state.boxes
    up_left = (box[0]-1, box[1]-1)
    up_right = (box[0]+1, box[1]-1)
    down_left = (box[0]-1, box[1]+1)
    down_right = (box[0]+1, box[1]+1)

    if vertical_walls and horizontal_walls:
        return True
    if vertical_walls and (up_box or down_box):
        return True
    if horizontal_walls and (left_box or right_box):
        return True
    if left_box and up_box and (up_left in state.boxes or up_left in state.obstacles):
        return True
    if left_box and down_box and (down_left in state.boxes or down_left in state.obstacles):
        return True
    if right_box and up_box and (up_right in state.boxes or up_right in state.obstacles):
        return True
    if right_box and down_box and (down_right in state.boxes or down_right in state.obstacles):
        return True
    return False


def mincol(col, matrix):
    m = matrix[0][col]
    for row in range(len(matrix)):
        if matrix[row][col] < m:
            m = matrix[row][col]
    return m


def minrow(row, matrix):
    m = matrix[row][0]
    for col in range(len(matrix)):
        if matrix[row][col] < m:
            m = matrix[row][col]
    return m


def heur_zero(state):
    '''Zero Heuristic can be used to make A* search perform uniform cost
    search '''
    return 0


def heur_manhattan_distance(state):
    # IMPLEMENT
    '''admissible sokoban puzzle heuristic: manhattan distance'''
    '''INPUT: a sokoban state'''
    '''OUTPUT: a numeric value that serves as an estimate of the distance of 
    the state to the goal. '''
    # We want an admissible heuristic, which is an optimistic heuristic. It
    # must never overestimate the cost to get from the current state to the
    # goal. The sum of the Manhattan distances between each box that has yet
    # to be stored and the storage point nearest to it is such a heuristic.
    # When calculating distances, assume there are no obstacles on the grid.
    # You should implement this heuristic function exactly, even if it is
    # tempting to improve it. Your function should return a numeric value;
    # this is the estimate of the distance to the goal.
    distance = 0
    for box in state.boxes:
        shorter_distance = state.width + state.height
        for point in state.storage:
            curr_distance = abs(point[0] - box[0]) + abs(point[1] - box[1])
            if curr_distance < shorter_distance:
                shorter_distance = curr_distance
        distance += shorter_distance
    return distance


def fval_function(sN, weight):
    # IMPLEMENT
    """
    Provide a custom formula for f-value computation for Anytime Weighted A star.
    Returns the fval of the state contained in the sNode.

    @param sNode sN: A search node (containing a SokobanState)
    @param float weight: Weight given by Anytime Weighted A star
    @rtype: float
    """
    return sN.gval + weight * sN.hval  # CHANGE THIS


# SEARCH ALGORITHMS
def weighted_astar(initial_state, heur_fn, weight, timebound):
    # IMPLEMENT
    '''Provides an implementation of weighted a-star, as described in the HW1
    handout '''
    '''INPUT: a sokoban state that represents the start state and a timebound 
    (number of seconds) '''
    '''OUTPUT: A goal state (if a goal is found), else False as well as a 
    SearchStats object '''
    '''implementation of weighted astar algorithm'''
    se = SearchEngine('custom')
    def f(sN):
        return sN.gval + weight * sN.hval
    se.init_search(initial_state, sokoban_goal_state, heur_fn, f)
    final, stats = se.search(timebound)
    return final, stats  # CHANGE THIS


def iterative_astar(initial_state, heur_fn, weight=1, timebound=5):
    # uses f(n), see how autograder
    # initializes a search line 88
    # IMPLEMENT
    '''Provides an implementation of realtime a-star, as described in the HW1
    handout '''
    '''INPUT: a sokoban state that represents the start state and a timebound 
    (number of seconds) '''
    '''OUTPUT: A goal state (if a goal is found), else False as well as a SearchStats object'''
    '''implementation of iterative astar algorithm'''
    final, stats = weighted_astar(initial_state, heur_fn, weight, timebound)  # CHANGE THIS
    timebound -= stats.total_time

    def f(sN):
        return sN.gval + weight * sN.hval
    while timebound > 0:
        se = SearchEngine('custom')
        se.init_search(initial_state, sokoban_goal_state, heur_fn, f)
        curr_final, curr_stats = se.search(timebound, (final.gval, final.gval, final.gval-1))
        if curr_final:
            final = curr_final
            stats = curr_stats
        else:
            break
        weight = weight/2
        timebound -= curr_stats.total_time
    return final, stats


def iterative_gbfs(initial_state, heur_fn, timebound=5):  # only use h(n)
    # IMPLEMENT
    '''Provides an implementation of anytime greedy best-first search,
    as described in the HW1 handout '''
    '''INPUT: a sokoban state that represents the start state and a timebound 
    (number of seconds) '''
    '''OUTPUT: A goal state (if a goal is found), else False'''
    '''implementation of iterative gbfs algorithm'''
    se = SearchEngine('best_first')
    se.init_search(initial_state, sokoban_goal_state, heur_fn)
    final, stats = se.search(timebound)
    timebound -= stats.total_time

    while timebound > 0:
        se = SearchEngine('best_first')
        se.init_search(initial_state, sokoban_goal_state, heur_fn)
        curr_final, curr_stats = se.search(timebound, (final.gval, final.gval, final.gval-1))
        if curr_final:
            final = curr_final
            stats = curr_stats
        else:
            break
        timebound -= curr_stats.total_time
    return final, stats
