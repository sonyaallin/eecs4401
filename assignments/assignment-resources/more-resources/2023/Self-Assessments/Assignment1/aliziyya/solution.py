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
    curr_sum = 0            # holds the total distance 
    nonavail_storage = []   # contains the already used storages
    
    for box in state.boxes: 
        if stuck(state, box):           # if the box is stuck, return infinity as there is no point
            return math.inf
        best_storage = None             # holds the coordinates for the best storage for this particular box
        best_storage_dist = math.inf    # set to infinity because we want to get something smaller
        for storage in state.storage:
            if storage not in nonavail_storage:     # makes sure the storage isnt already one that we've used
                dist = abs(box[0] - storage[0]) + abs(box[1] - storage[1])  # calculate the manhatten distance
                calateral_dist = find_calateral(state, box, storage)        # find the added cost to this storage given there is an obstacle in our path
                dist += calateral_dist
                if dist < best_storage_dist:    # if distance is better than distance to another storage...
                    best_storage_dist = dist    # set this as best distance
                    best_storage = storage      # save best storage
        nonavail_storage.append(best_storage)   # after looking at available storages, save the best for this box to the non available list
        curr_sum += best_storage_dist           # add to the total distance
    
    return curr_sum

def stuck(state, box):
    ''' Returns True if a box is stuck and cannot be moved by a robot'''
    # if box is already on goal state return False
    if box in state.storage:
        return False
    
    # check if box on the corners and edges of the board
    # top side
    if box[1] == 0:
        if ((box[0] == 0 or box[0] == state.width-1) or         # top left and top right corners
            ((box[0]-1, box[1]) in state.obstacles) or          # obstacle is left of box
            ((box[0]+1, box[1]) in state.obstacles)):           # obstacle is right of box
            return True
    # bottom side
    if box[1] == state.height-1:
        if ((box[0] == 0 or box[0] == state.width-1) or         # bottom left and bottom right corners
            ((box[0]-1, box[1]) in state.obstacles) or          # obstacle is left of box
            ((box[0]+1, box[1]) in state.obstacles)):           # obstacle is right of box
            return True
    # left side 
    if box[0] == 0:
        if ((box[1] == 0 or box[1] == state.height-1) or        # top left and bottom left corners
            ((box[0], box[1]-1) in state.obstacles) or          # obstacle is above of box
            ((box[0], box[1]+1) in state.obstacles)):           # obstacle is below of box
            return True
    # right side 
    if box[0] == state.width-1:
        if ((box[1] == 0 or box[1] == state.height-1) or        # top left and bottom left corners
            ((box[0], box[1]-1) in state.obstacles) or          # obstacle is above of box
            ((box[0], box[1]+1) in state.obstacles)):           # obstacle is below of box
            return True
    
    # check if box within the board (not on edges or corners) is surrounded by obstacles 
    # barrier is on top of box, check if barrier also exists on right or left side
    if ((box[0], box[1]-1) in state.obstacles and          # obstacle on top 
        (((box[0]-1, box[1]) in state.obstacles) or ((box[0]+1, box[1]) in state.obstacles))): # obstacle on right or left
        return True
    # barrier is below box, check if barrier also exists on right or left side
    if ((box[0], box[1]+1) in state.obstacles and          # obstacle on bottom 
        (((box[0]-1, box[1]) in state.obstacles) or ((box[0]+1, box[1]) in state.obstacles))): # obstacle on right or left
        return True
    return False

def find_calateral(state, box, storage):
    ''' Determines the additive cost if the box is not stuck but a block is in its manhatten 
    path. Only checks around the start and around the goal.'''
    # determine directions box would need to travel
    x_dist = box[0] - storage[0]
    y_dist = box[1] - storage[1]
    calateral = 0
    # box only needs to travel up or down
    if (x_dist == 0):
        if (((y_dist > 0) and (box[0], box[1]-1) in state.obstacles) or # storage is above box and there is obstacle right above box
            ((y_dist < 0) and (box[0], box[1]+1) in state.obstacles)):  # storage is below box and there is obstacle right below box
            calateral += 2
        elif (((y_dist > 0) and (storage[0], storage[1]+1) in state.obstacles) or # storage is above box and there is obstacle right below storage
              ((y_dist < 0) and (storage[0], storage[1]-1) in state.obstacles)):    # storage is below box and there is obstacle right above storage
            calateral += 2
    #box only needs to travel right or left
    elif (y_dist == 0):
        if (((x_dist > 0) and (box[0]-1, box[1]) in state.obstacles) or # storage is left of box and there is obstacle left above box
            ((x_dist < 0) and (box[0]+1, box[1]) in state.obstacles)):  # storage is right box and there is obstacle right below box
            calateral += 2
        elif (((x_dist > 0) and (storage[0]+1, storage[1]) in state.obstacles) or # storage is left of box and there is obstacle right of storage
              ((x_dist < 0) and (storage[0]-1, storage[1]) in state.obstacles)):    # storage is right of box and there is obstacle left of storage
            calateral += 2
    return calateral
        

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
    
    curr_sum = 0
    for box in state.boxes:
        closest_dist = math.inf
        for storage in state.storage:
            dist = abs(box[0] - storage[0]) + abs(box[1] - storage[1])
            if dist < closest_dist:
                closest_dist = dist
        curr_sum += closest_dist
    return curr_sum  

def fval_function(sN, weight):
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
    '''Provides an implementation of weighted a-star, as described in the HW1 handout'''
    '''INPUT: a sokoban state that represents the start state and a timebound (number of seconds)'''
    '''OUTPUT: A goal state (if a goal is found), else False as well as a SearchStats object'''
    '''implementation of weighted astar algorithm'''
    se = SearchEngine('custom', 'full')
    fvfun = (lambda sN: fval_function(sN, weight))
    se.init_search(initial_state, sokoban_goal_state, heur_fn, fvfun)
    goal, stats = se.search(timebound)
    return goal, stats  

def iterative_astar(initial_state, heur_fn, weight=1, timebound=5):  # uses f(n), see how autograder initializes a search line 88
    '''Provides an implementation of realtime a-star, as described in the HW1 handout'''
    '''INPUT: a sokoban state that represents the start state and a timebound (number of seconds)'''
    '''OUTPUT: A goal state (if a goal is found), else False as well as a SearchStats object'''
    '''implementation of iterative astar algorithm'''
    start = os.times()[0]
    goal, stats = weighted_astar(initial_state, heur_fn, weight, timebound - (os.times()[0] - start))
    if goal == False:
        return False, stats
    costbound = [goal.gval, goal.gval, goal.gval]
    while (os.times()[0] - start) < timebound:
        se = SearchEngine('custom')
        mweight = weight//2
        se.init_search(initial_state, sokoban_goal_state, heur_fn, (lambda sN: fval_function(sN, mweight)))
        ngoal, nstats = se.search(timebound - (os.times()[0] - start), costbound)
        if (ngoal == False) or (ngoal.gval == goal.gval):
            return goal, stats
        goal, stats = ngoal, nstats
        costbound = [goal.gval, goal.gval, goal.gval]
    return goal, stats 

def iterative_gbfs(initial_state, heur_fn, timebound=5):  # only use h(n)
    '''Provides an implementation of anytime greedy best-first search, as described in the HW1 handout'''
    '''INPUT: a sokoban state that represents the start state and a timebound (number of seconds)'''
    '''OUTPUT: A goal state (if a goal is found), else False'''
    '''implementation of iterative gbfs algorithm'''
    start = os.times()[0]
    se = SearchEngine('best_first', 'full')
    se.init_search(initial_state, sokoban_goal_state, heur_fn)
    goal, stats = se.search(timebound - (os.times()[0] - start))
    if goal == False:
        return False, stats
    costbound = [goal.gval, goal.gval, goal.gval]
    while (os.times()[0] - start) < timebound:
        se.init_search(initial_state, sokoban_goal_state, heur_fn)
        ngoal, nstats = se.search(timebound - (os.times()[0] - start), costbound)
        if (ngoal == False) or (ngoal.gval == goal.gval):
            return goal, stats
        goal, stats = ngoal, nstats
        costbound = [goal.gval, goal.gval, goal.gval]
    return goal, stats 






