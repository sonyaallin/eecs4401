#   Look for #IMPLEMENT tags in this file. These tags indicate what has
#   to be implemented to complete the warehouse domain.

#   You may add only standard python imports
#   You may not remove any imports.
#   You may not import or otherwise source any of your own files

from dis import dis
from email.errors import FirstHeaderLineIsContinuationDefect
import os  # for time functions
import math
from unittest import result  # for math.infinity
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

    global result

    if sokoban_goal_state(state):  # check if it is already solved
        return 0

    if state.parent and state.parent.boxes == state.boxes: # there exists a previous solution
                                                            # for which the result would be the same
        return result
        
    distance = 0

    boxes = []
    for box in state.boxes:
        if blocked(state, box): #check to see if the boxes cant be moved
            result = math.inf
            return math.inf
        boxes.append(box)

    storages = []
    for sto in state.storage: #create a seperate list of storages that can be mutated
        storages.append(sto)

    for box in boxes: 
        minimum = math.inf
        keep = None

        if box[0] == 0 or box[0] == state.width-1: # if the box is on an edge it can only be solved by
                                                    # placing it on a storage on the same ledge
            for storage in storages:
                if storage[0] != box[0]:
                    continue
                curr = abs(box[1] - storage[1])
                if curr < minimum:
                    minimum = curr
                    keep = storage # keep track of the minimum length and the storage space
                if minimum == 0:
                    break  #if its 0, we know its the minimum already and we can stop searching 

        elif box[1] == 0 or box[1] == state.height-1: # if the box is on an edge it can only be solved by
                                                    # placing it on a storage on the same ledge
            for storage in storages:
                if storage[1] != box[1]:
                    continue
                curr = abs(box[0] - storage[0]) 
                if curr < minimum:
                    minimum = curr
                    keep = storage
                if minimum == 0:
                    break

        else:
            for storage in storages:
                curr = (abs(box[0] - storage[0]) + abs(box[1] - storage[1]))
                if curr < minimum:
                    minimum = curr
                    keep = storage
                if minimum == 0:
                    break

        if minimum == math.inf: # if there is no solution for a box, we can exit with no solution
            result = math.inf
            return minimum

        distance += minimum
        storages.remove(keep) # remove the minimum distance storage because it is "taken"

    result = distance # set our result to the current result so it can be accessed later
    return distance

def blocked(state, box):
    row = False
    col = False
    for obstacle in state.obstacles:
        if obstacle == (box[0]+1, box[1]) or obstacle == (box[0]-1, box[1]) or box[0] == 0 or box[0] == state.width-1:
            row = True
        elif obstacle == (box[0], box[1]+1) or obstacle == (box[0], box[1]-1) or box[1] == 0 or box[1] == state.height-1:
            col = True
        if row and col:
            break
    return row and col


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
    distance = 0
    for box in state.boxes:
        minimum = math.inf
        for storage in state.storage:
            curr = (abs(box[0] - storage[0]) + abs(box[1] - storage[1]))
            minimum = min(curr, minimum)
        distance += minimum
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
    return sN.gval + (weight*sN.hval)

# SEARCH ALGORITHMS
def weighted_astar(initial_state, heur_fn, weight, timebound):
    # IMPLEMENT    
    '''Provides an implementation of weighted a-star, as described in the HW1 handout'''
    '''INPUT: a sokoban state that represents the start state and a timebound (number of seconds)'''
    '''OUTPUT: A goal state (if a goal is found), else False as well as a SearchStats object'''
    '''implementation of weighted astar algorithm'''
    deadline = os.times()[0] + timebound

    wrapped_fval_function = ( lambda sN : fval_function(sN, weight) ) 
    search = SearchEngine("custom", "default")

    while os.times()[0] < deadline:
        search.init_search(initial_state, sokoban_goal_state, heur_fn, wrapped_fval_function)
        path, stat = search.search(deadline-os.times()[0])
        break
    
    goalpath = path
    goalstat = stat
    cost = math.inf

    while os.times()[0] < deadline and path :
        if path.gval <= cost:
            cost = path.gval
            goalpath = path
            goalstat = stat
            path, stat = search.search(deadline-os.times()[0], [cost, cost, cost])
        else:
            break

    return goalpath, goalstat  # CHANGE THIS

def iterative_astar(initial_state, heur_fn, weight=1, timebound=5):  # uses f(n), see how autograder initializes a search line 88
    # IMPLEMENT
    '''Provides an implementation of realtime a-star, as described in the HW1 handout'''
    '''INPUT: a sokoban state that represents the start state and a timebound (number of seconds)'''
    '''OUTPUT: A goal state (if a goal is found), else False as well as a SearchStats object'''
    '''implementation of iterative astar algorithm'''
    deadline = os.times()[0] + timebound
    goalpath = False
    goalstat = None

    while os.times()[0] < deadline:
        path, stat = weighted_astar(initial_state, heur_fn, weight, deadline-os.times()[0])
        goalpath = path
        goalstat = stat
        break

    while os.times()[0] < deadline and path:
        goalpath = path
        goalstat = stat
        weight = weight - 0.05
        path, stat = weighted_astar(initial_state, heur_fn, weight, deadline-os.times()[0])

    return goalpath, goalstat 

def iterative_gbfs(initial_state, heur_fn, timebound=5):  # only use h(n)
    # IMPLEMENT
    '''Provides an implementation of anytime greedy best-first search, as described in the HW1 handout'''
    '''INPUT: a sokoban state that represents the start state and a timebound (number of seconds)'''
    '''OUTPUT: A goal state (if a goal is found), else False'''
    '''implementation of iterative gbfs algorithm'''
    deadline = os.times()[0] + timebound

    search = SearchEngine("best_first", "default")

    while os.times()[0] < deadline:
        search.init_search(initial_state, sokoban_goal_state, heur_fn)
        path, stat = search.search(deadline-os.times()[0])
        break
    
    goalpath = path
    goalstat = stat
    cost = math.inf

    while os.times()[0] < deadline and path :
        if path.gval <= cost:
            cost = path.gval
            goalpath = path
            goalstat = stat
            path, stat = search.search(deadline-os.times()[0], [cost, cost, cost])
        else:
            break

    return goalpath, goalstat  # CHANGE THIS



