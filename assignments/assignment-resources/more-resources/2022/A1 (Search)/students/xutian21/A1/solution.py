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

    #There are 2 ways to improve it.
    #1. The box might be close to the storage, but then it gets stuck in a corner of obstacles... return infinity in this case so that the search engine knows this is not the best way.
    #2. heur_manhattan_distance specifys that only distance between stirage and box is considered, but how about robot and box? Better to have a robot next to that box to push it rather than a robot halfway across the grid

    sum = 0

    #for checking box stuck
    # x and y coordinates for obstacles
    obstacles = []
    for obstacle in state.obstacles:
        obstacles.append(obstacle)

    # we treat boundaries as obstacles
    for x in range(state.width):
        obstacles.append((x, state.height))
        obstacles.append((x, -1))
    for y in range(state.height):
        obstacles.append((state.width, y))
        obstacles.append((-1, y))

    # add dist of robots to boxes
    for boxes in state.boxes:
        min_dis = math.inf
        # go through all storage and pick the one with least dmanhanttan distance
        for robot in state.robots:
            cur_dis = abs(boxes[0] - robot[0]) + abs(boxes[1] - robot[1])
            if min_dis > cur_dis:
                min_dis = cur_dis
        sum += min_dis

    for box in state.boxes:
        if box_stuck(box, state, obstacles):
            return math.inf
        min_dis = math.inf
        # go through all storage and pick the one with least dmanhanttan distance
        for storage in state.storage:
            cur_dis = abs(box[0] - storage[0]) + abs(box[1] - storage[1])
            if min_dis > cur_dis:
                min_dis = cur_dis
        sum += min_dis

    return sum

def box_stuck(box, state, obstacles):
    '''check if box is stuck'''

    if box in state.storage:
        return False

    #Box cannot be moved ONLY when it's in a corner. if 2 sides are blocked, it can still be pushed

    # top left
    if (box[0] - 1, box[1]) in obstacles and (box[0], box[1] + 1) in obstacles:
        return True
    # top right
    if (box[0] + 1, box[1]) in obstacles and (box[0], box[1] + 1) in obstacles:
        return True
    # bot left
    if (box[0] - 1, box[1]) in obstacles and (box[0], box[1] - 1) in obstacles:
        return True
    # bot right
    if (box[0] + 1, box[1]) in obstacles and (box[0], box[1] - 1) in obstacles:
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

    #The sum of the Manhattan distances between each box that has yet to be stored and the storage point nearest to it
    sum = 0
    for boxes in state.boxes:
        min_dis = math.inf
        #go through all storage and pick the one with least dmanhanttan distance
        for storage in state.storage:
            cur_dis = abs(boxes[0] - storage[0]) + abs(boxes[1] - storage[1])
            if min_dis > cur_dis:
                min_dis = cur_dis
        sum += min_dis

    return sum

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
    customEng = SearchEngine(strategy="custom")
    wrapped_fval_function = (lambda sN: fval_function(sN, weight))
    customEng.init_search(initial_state, sokoban_goal_state, heur_fn, wrapped_fval_function)
    result = customEng.search(timebound=timebound)

    if result[0] == False:
        return result

    return result

def iterative_astar(initial_state, heur_fn, weight=1, timebound=5):  # uses f(n), see how autograder initializes a search line 88
    # IMPLEMENT
    '''Provides an implementation of realtime a-star, as described in the HW1 handout'''
    '''INPUT: a sokoban state that represents the start state and a timebound (number of seconds)'''
    '''OUTPUT: A goal state (if a goal is found), else False as well as a SearchStats object'''
    '''implementation of iterative astar algorithm'''

    #record time
    start = os.times()[0]
    until_end = timebound #some leeway for processing

    #1st iteration
    new_weight = weight
    customEng = SearchEngine(strategy="custom")
    wrapped_fval_function = (lambda sN: fval_function(sN, new_weight))
    customEng.init_search(initial_state, sokoban_goal_state, heur_fn, wrapped_fval_function)
    best_result = customEng.search(timebound=until_end)
    until_end -= (os.times()[0] - start)

    if best_result[0] == False:
        return best_result

    #start iterating
    while until_end > 0:
        new_weight *= 0.5  # decrement weight
        start = os.times()[0]
        customEng.init_search(initial_state, sokoban_goal_state, heur_fn, wrapped_fval_function)
        result = customEng.search(timebound=until_end)
        until_end -= (os.times()[0] - start)
        if(result[0] != False and result[0].gval < best_result[0].gval):
            best_result =  result

    return best_result


def iterative_gbfs(initial_state, heur_fn, timebound=5):  # only use h(n)
    # IMPLEMENT
    '''Provides an implementation of anytime greedy best-first search, as described in the HW1 handout'''
    '''INPUT: a sokoban state that represents the start state and a timebound (number of seconds)'''
    '''OUTPUT: A goal state (if a goal is found), else False'''
    '''implementation of iterative gbfs algorithm'''
    #record time
    start = os.times()[0]
    until_end = timebound

    #1st iteration
    customEng = SearchEngine(strategy="best_first")
    wrapped_fval_function = (lambda sN: fval_function(sN, 1))
    customEng.init_search(initial_state, sokoban_goal_state, heur_fn)
    best_result = customEng.search(timebound=until_end)
    until_end -= (os.times()[0] - start)

    if best_result[0] == False:
        return best_result

    #start iterating
    while until_end > 0:
        start = os.times()[0]
        customEng.init_search(initial_state, sokoban_goal_state, heur_fn)
        result = customEng.search(timebound=until_end)
        until_end -= (os.times()[0] - start)
        if(result[0] != False and result[0].gval < best_result[0].gval):
            best_result = result

    return best_result



