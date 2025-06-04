#   Look for #IMPLEMENT tags in this file. These tags indicate what has
#   to be implemented to complete the warehouse domain.

#   You may add only standard python imports
#   You may not remove any imports.
#   You may not import or otherwise source any of your own files

import os  # for time functions
import math
from turtle import st

from soupsieve import closest  # for infinity
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

    #convert to set to be able to remove used storage spots
    storage = set(state.storage)

    sum = 0
    for b in state.boxes:
        x,y = b
        if((y==0 and x >= 0 and x < state.width) and ((x-1,y) in state.boxes or (x+1,y) in state.boxes) and b not in storage ):
                return math.inf
        # closest_dist = abs(x-state.storage[0][0]) + math.abs(y-state.storage[0][1])
        closest_dist = math.inf
        for st in storage:
        
            dist = abs(x-st[0]) + abs(y-st[1])
            if dist < closest_dist:
                closest_dist = dist
                stor_used = st
            
        sum += closest_dist
        # storage_used.append(stor_used)
        storage.remove(stor_used)

    return sum



def heur_zero(state):
    '''Zero Heuristic can be used to make A* search perform uniform cost search'''
    return 0

def heur_manhattan_distance(state):
    # IMPLEMENT - DONE
    '''admissible sokoban puzzle heuristic: manhattan distance'''
    '''INPUT: a sokoban state'''
    '''OUTPUT: a numeric value that serves as an estimate of the distance of the state to the goal.'''
    # We want an admissible heuristic, which is an optimistic heuristic.
    # It must never overestimate the cost to get from the current state to the goal.
    # The sum of the Manhattan distances between each box that has yet to be stored and the storage point nearest to it is such a heuristic.
    # When calculating distances, assume there are no obstacles on the grid.
    # You should implement this heuristic function exactly, even if it is tempting to improve it.
    # Your function should return a numeric value; this is the estimate of the distance to the goal.
    sum = 0
    for b in state.boxes:
        x,y = b
        closest_dist = math.inf
        for st in state.storage:
            dist = abs(x-st[0]) + abs(y-st[1])
            if dist < closest_dist:
                closest_dist = dist
        sum += closest_dist

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
    return sN.gval + (weight*sN.hval)

# SEARCH ALGORITHMS
def weighted_astar(initial_state, heur_fn, weight, timebound):
    # IMPLEMENT    
    '''Provides an implementation of weighted a-star, as described in the HW1 handout'''
    '''INPUT: a sokoban state that represents the start state and a timebound (number of seconds)'''
    '''OUTPUT: A goal state (if a goal is found), else False as well as a SearchStats object'''
    '''implementation of weighted astar algorithm'''

    cus = SearchEngine(strategy='custom')
    wrapped_fval_function = (lambda sN : fval_function(sN,weight))
    cus.init_search(initial_state,sokoban_goal_state,heur_fn,wrapped_fval_function)
    ret = cus.search(timebound)
    return ret
    # return None, None  # CHANGE THIS


def iterative_astar(initial_state, heur_fn, weight=1, timebound=5):  # uses f(n), see how autograder initializes a search line 88
    # IMPLEMENT
    '''Provides an implementation of realtime a-star, as described in the HW1 handout'''
    '''INPUT: a sokoban state that represents the start state and a timebound (number of seconds)'''
    '''OUTPUT: A goal state (if a goal is found), else False as well as a SearchStats object'''
    '''implementation of iterative astar algorithm'''
    cus = SearchEngine(strategy='custom')
    wrapped_fval_function = (lambda sN : fval_function(sN,weight))
    cus.init_search(initial_state,sokoban_goal_state,heur_fn,wrapped_fval_function)
    cost = (math.inf, math.inf,math.inf)
    
    best = None
    while(timebound > 0):
        wrapped_fval_function = (lambda sN : fval_function(sN,weight))
        # cus.init_search(initial_state,sokoban_goal_state,heur_fn,wrapped_fval_function)
        ret = cus.search(timebound,cost)
        if ret[0] != False:
            fval = heur_fn(ret[0])+ ret[0].gval
            cost = (math.inf,math.inf,fval)
            best = ret
            timebound-=ret[1].total_time
        else:
            if best is not None:
                return best
            else:
                return ret
        weight -= 0.01
    return best
        
        # cus.init_search(initial_state,sokoban_goal_state,heur_fn,wrapped_fval_function)
        # if sol is not None:
        #     ret = cus.search(timebound, (n.gval,n.hval, fval_function(n, weight)))
        #     if ret[0]:
        #         sol = ret[1]
        #         timebound-=ret[1].total_time

        
    return None, None #CHANGE THIS

def iterative_gbfs(initial_state, heur_fn, timebound=5):  # only use h(n)
    # IMPLEMENT
    '''Provides an implementation of anytime greedy best-first search, as described in the HW1 handout'''
    '''INPUT: a sokoban state that represents the start state and a timebound (number of seconds)'''
    '''OUTPUT: A goal state (if a goal is found), else False'''
    '''implementation of iterative gbfs algorithm'''
    gr = SearchEngine(strategy="best_first") #full
    gr.init_search(initial_state,sokoban_goal_state,heur_fn)
    best = None
    cost = (math.inf,math.inf,math.inf)
    while(timebound > 0):
        before = os.times()[0]
        ret = gr.search(timebound,cost)
        after = os.times()[0]
        if ret[0] != False:
            timebound-=(after - before)
            cost = (ret[0].gval,math.inf,math.inf)
            best = ret
        else:
            if best is not None:
                return best
            else:
                return ret

    return best




