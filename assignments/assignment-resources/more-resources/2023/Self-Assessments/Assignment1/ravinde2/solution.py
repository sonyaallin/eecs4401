#   Look for #IMPLEMENT tags in this file. These tags indicate what has
#   to be implemented to complete the warehouse domain.

#   You may add only standard python imports
#   You may not remove any imports.
#   You may not import or otherwise source any of your own files
'''
For the heuristic I decided to make it so that only one box can be put in one
storage. So we take the first box and see what storage it is closest to
calculate the manhattan distance. The the storage is dropped from the
list of storages we check. I also decided in multiply the heuristic added by 2
in experiementation this seemed to yeild the best results for computations.
The heuristic also makes sure we never push the box into a corner since
that would result in a game over instantly

In addition to this I tried a few other heuristcs ideas namely factoring in
the manhattan distance from the robot to the box and the distance from the closest
obstacles but this seemed to hurt the results so they were dropped.
'''
import os  # for time functions
import math  # for infinity
from search import *  # for search engines
from sokoban import sokoban_goal_state, SokobanState, Direction, PROBLEMS  # for Sokoban specific classes and problems

def in_corner(state, box):
  ''' Checks if box is in corner '''

  up_block = (box[1] == 0) or ((box[0], box[1] + 1) in state.obstacles) 
  down_block = (box[1] == state.height - 1) or ((box[0], box[1] - 1) in state.obstacles) 

  left_block = (box[0] == 0) or ((box[0] - 1, box[1]) in state.obstacles)
  right_block = (box[0] == state.width - 1) or ((box[0] + 1, box[1]) in state.obstacles)

  return (up_block or down_block) and (left_block or right_block) 


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


    unused_storage = set(state.storage) # for removing storages once we find a box that its close to 
    total_value = 0 #the heuristic number we will return
    for box in state.boxes:
        min_dist_stor = 3000 #tracker for the smallest dist to a storage spot
        for stor in unused_storage:
            temp_dist = abs(box[0] - stor[0]) + abs(box[1] - stor[1]) # calculate the manhattan distance from box to storage
            if temp_dist < min_dist_stor:
                min_dist_stor = temp_dist
                close_storage = stor
        if close_storage: 
            unused_storage.remove(close_storage) # remove the the storage that was closest to the smallest box
        if min_dist_stor == 0: # if the dist is 0 we know the box is on a storage point so we don't waste time calculating anything else
            continue
        elif in_corner(state, box): # if the box is in a corner we are completly stuck so we want to always avoid this
            return 3000
        total_value += 2*min_dist_stor # we add our smallest distance to the heuristic tracker

    return total_value

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
    valid_box = []
    total_dist = 0
    for box in state.boxes:
        min_dist = 3000
        for storage in state.storage:
            temp_dist = abs(box[0] - storage[0]) + abs(box[1] - storage[1])
            min_dist = min(temp_dist, min_dist)
        total_dist += min_dist
    return total_dist  # CHANGE THIS


def fval_function(sN, weight):
    # IMPLEMENT
    """
    Provide a custom formula for f-value computation for Anytime Weighted A star.
    Returns the fval of the state contained in the sNode.

    @param sNode sN: A search node (containing a SokobanState)
    @param float weight: Weight given by Anytime Weighted A star
    @rtype: float
    """
    return sN.gval + weight * sN.hval #CHANGE THIS

# SEARCH ALGORITHMS
def weighted_astar(initial_state, heur_fn, weight, timebound):
    # IMPLEMENT    
    '''Provides an implementation of weighted a-star, as described in the HW1 handout'''
    '''INPUT: a sokoban state that represents the start state and a timebound (number of seconds)'''
    '''OUTPUT: A goal state (if a goal is found), else False as well as a SearchStats object'''
    '''implementation of weighted astar algorithm'''
    wrapped_fval_function = (lambda sN : fval_function(sN,weight)) 

    search_engine = SearchEngine(strategy = "custom", cc_level = "default")
    search_engine.init_search(initial_state, sokoban_goal_state, heur_fn, wrapped_fval_function)
    search = search_engine.search(timebound)

    return search

def iterative_astar(initial_state, heur_fn, weight=1, timebound=5):  # uses f(n), see how autograder initializes a search line 88
    # IMPLEMENT
    '''Provides an implementation of realtime a-star, as described in the HW1 handout'''
    '''INPUT: a sokoban state that represents the start state and a timebound (number of seconds)'''
    '''OUTPUT: A goal state (if a goal is found), else False as well as a SearchStats object'''
    '''implementation of iterative astar algorithm'''
    current_time = os.times()[0]
    time_left = timebound
    end_time = current_time + timebound

    wrapped_fval_function = (lambda sN : fval_function(sN,weight)) 

    search_engine = SearchEngine(strategy = "custom", cc_level = "default")
    search_engine.init_search(initial_state, sokoban_goal_state, heur_fn, wrapped_fval_function)
    search_sol = search_engine.search(timebound)

    final_result = False
    final_stats = search_sol[1]
    costbound = (math.inf, math.inf, math.inf)

    while current_time < end_time:
        if search_sol[0] == False:
            return final_result, final_stats
        if (search_sol[0].gval <= costbound[0]):
            final_result = search_sol[0]
            final_stats = search_sol[1]
            costbound = (search_sol[0].gval, search_sol[0].gval, search_sol[0].gval)

        wrapped_fval_function = (lambda sN : fval_function(sN,weight * 0.95)) 
        
        time_difference = os.times()[0] - current_time 
        time_left = time_left - time_difference

        search_engine.init_search(initial_state, sokoban_goal_state, heur_fn, wrapped_fval_function)
        search_sol = search_engine.search(time_left, costbound)

        current_time = os.times()[0]
    return final_result, final_stats

def iterative_gbfs(initial_state, heur_fn, timebound=5):  # only use h(n)
    # IMPLEMENT
    '''Provides an implementation of anytime greedy best-first search, as described in the HW1 handout'''
    '''INPUT: a sokoban state that represents the start state and a timebound (number of seconds)'''
    '''OUTPUT: A goal state (if a goal is found), else False'''
    '''implementation of iterative gbfs algorithm'''
    current_time = os.times()[0]
    time_left = timebound
    end_time = current_time + timebound
    
    search_engine = SearchEngine(strategy = "best_first", cc_level = "default")
    search_engine.init_search(initial_state, sokoban_goal_state, heur_fn)
    search_sol = search_engine.search(time_left)

    final_result = search_sol[0]
    final_stats = search_sol[1]
    costbound = (math.inf, math.inf, math.inf)

    while current_time < end_time:
        if search_sol[0] == False:
            return final_result, final_stats
        if (search_sol[0].gval <= costbound[0]):
            final_result = search_sol[0]
            final_stats = search_sol[1]
            costbound = (search_sol[0].gval, search_sol[0].gval, search_sol[0].gval)

        time_difference = os.times()[0] - current_time 
        time_left = time_left - time_difference

        search_sol = search_engine.search(time_left, costbound)
        current_time = os.times()[0]

    return final_result, final_stats


