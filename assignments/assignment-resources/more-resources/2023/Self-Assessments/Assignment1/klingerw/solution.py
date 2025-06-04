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
    # For heuristic attempts, first I tried to add robot distance to a given box in addition to the goal distance. This is because each robot must push the 
    # box into place at the goal position. This produced better results, but was still underperforming. I then added corner checks with boundaries and the walls
    # of the board, which improved my solution some more. If a state had a box in a corner, and couldn't be moved, then there could be no solution and so a 
    # heuristic value of "inf" is achieved. I also added a check to see if a storage is already occupied by a box, and so we don't use that storage for heuristic 
    # calculations regarding distance (since we won't use that stoage unit). I also added checks to see if a box was stuck in a row (attached to a wall) which didn't have a 
    # goal. If this were the case, they would not be able to get unstuck from this wall, and would therefore result in no solution. I set this to "inf" as well, but this resulted 
    # in even worse performance for my alt heur, so was removed. I also attempted to add in "box collision", where if a box were blocking the way of another box, and it was stuck to a wall border
    # then heuristic value would be "inf". Once again, this made performance worse, so was removed. I also added that if a box is on the same level as the goal, and a robot is aligned
    # such that it can push a box to that goal directly, then we incentivize this path since it leads to a guaranteed goal rather quickly. This final check improved my performance to the point
    # where I achieved the improved benchmark solution count, and so I am now satisfied with my heuristic.

    curr_dist = 0
    smallest_dist = 0
    total_dist = 0
    
    for box in state.boxes:
        found = False
        smallest_dist = float('inf')
        
        # find unfinished robots
        for storage in state.storage:

            # box already in storage, cant use this box
            if box in state.storage:
                found = True
                break
            
            # cant use this storage, already has box in it
            if storage in state.boxes:
                continue

            # if box is stuck in a corner, then we can't find a solution ever in this state
            if ((((box[0] - 1, box[1]) in state.obstacles or box[0] - 1 < 0) and ((box[0], box[1] - 1) in state.obstacles or box[1] - 1 < 0)) or 
            (((box[0] + 1, box[1]) in state.obstacles or box[0] + 1 == state.width) and ((box[0], box[1] - 1) in state.obstacles or box[1] - 1 < 0)) or 
            (((box[0] - 1, box[1]) in state.obstacles or box[0] - 1 < 0) and ((box[0], box[1] + 1) in state.obstacles or box[1] + 1 == state.height)) or 
            (((box[0] + 1, box[1]) in state.obstacles or box[0] + 1 == state.width) and ((box[0], box[1] + 1) in state.obstacles or box[1] + 1 == state.height))):
                return float('inf')

            # must compare robot distance to box as well
            for robot in state.robots:
                # Make heuristic value equal to distance from robot to box to goal
                curr_dist = abs(box[0] - storage[0]) + abs(box[1] - storage[1]) + abs(box[0] - robot[0]) + abs(box[1] - robot[1])
                
                # if a box is on the same level as the goal, and a robot is aligned such that it can push a box to that goal,
                # incentivize this path since it leads to guaranteed goal quickly and efficiently.
                if ((box[0] - 1 == robot[0] and box[1] == robot[1]) and (box[0] < storage[0] and box[1] == storage[1]) or 
                (box[0] + 1 == robot[0] and box[1] == robot[1]) and (box[0] > storage[0] and box[1] == storage[1]) or 
                (box[0] == robot[0] and box[1] - 1 == robot[1]) and (box[0] == storage[0] and box[1] < storage[1]) or 
                (box[0] == robot[0] and box[1] + 1 == robot[1]) and (box[0] == storage[0] and box[1] > storage[1])):
                    curr_dist /= 2

                # Update heuristic if we have found a smaller distance from a box to a goal
                if curr_dist < smallest_dist:
                    smallest_dist = curr_dist

        # Skip heuristic value since the box is already in goal
        if found == False:
            total_dist += smallest_dist
    
    return total_dist


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
    curr_dist = 0
    smallest_dist = 0
    total_dist = 0

    for box in state.boxes:
        found = False
        smallest_dist = float('inf')

        # find unfinished robots
        for storage in state.storage:
        
            curr_dist = abs(box[0] - storage[0]) + abs(box[1] - storage[1])

            # This box is already in a storage, so we don't need to move it
            if curr_dist == 0:
                found = True
                break
            
            # Current storage is closer to this box than previous
            if curr_dist < smallest_dist:
                smallest_dist = curr_dist

        if found == False:
            total_dist += smallest_dist
    
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
    return sN.gval + weight * sN.hval

# SEARCH ALGORITHMS
def weighted_astar(initial_state, heur_fn, weight, timebound):
    # IMPLEMENT    
    '''Provides an implementation of weighted a-star, as described in the HW1 handout'''
    '''INPUT: a sokoban state that represents the start state and a timebound (number of seconds)'''
    '''OUTPUT: A goal state (if a goal is found), else False as well as a SearchStats object'''
    '''implementation of weighted astar algorithm'''

    search = SearchEngine(strategy='custom')

    wrapped_fval_function = (lambda sN : fval_function(sN, weight))

    search.init_search(initial_state, sokoban_goal_state, heur_fn, wrapped_fval_function)

    return search.search(timebound)

def iterative_astar(initial_state, heur_fn, weight=1, timebound=5):  # uses f(n), see how autograder initializes a search line 88
    # IMPLEMENT
    '''Provides an implementation of realtime a-star, as described in the HW1 handout'''
    '''INPUT: a sokoban state that represents the start state and a timebound (number of seconds)'''
    '''OUTPUT: A goal state (if a goal is found), else False as well as a SearchStats object'''
    '''implementation of iterative astar algorithm'''
    time_left = timebound
    costbound = None
    path = None
    stat = None
    
    while(time_left > 0):
        
        wrapped_fval_function = (lambda sN : fval_function(sN, weight))

        start_time = os.times()[0]
        search = SearchEngine(strategy='custom')
        search.init_search(initial_state, sokoban_goal_state, heur_fn, wrapped_fval_function)
        temp_path, temp_stat = search.search(timebound, costbound)
        time_left -= os.times()[0] - start_time

        # Not guaranteed that path isn't found, so must check before modifications
        if temp_path != False:
            path = temp_path
            stat = temp_stat

            # only concerned with f val bound
            costbound = (float('inf'), float('inf'), path.gval)
            weight -= 0.25
            
    return path, stat


def iterative_gbfs(initial_state, heur_fn, timebound=5):  # only use h(n)
    # IMPLEMENT
    '''Provides an implementation of anytime greedy best-first search, as described in the HW1 handout'''
    '''INPUT: a sokoban state that represents the start state and a timebound (number of seconds)'''
    '''OUTPUT: A goal state (if a goal is found), else False'''
    '''implementation of iterative gbfs algorithm'''
    time_left = timebound
    costbound = None
    path = None
    stat = None

    while(time_left > 0):
        
        start_time = os.times()[0]
        search = SearchEngine(strategy='best_first')
        search.init_search(initial_state, sokoban_goal_state, heur_fn)
        temp_path, temp_stat = search.search(timebound, costbound)
        time_left -= os.times()[0] - start_time
        
        if temp_path != False:
            path = temp_path
            stat = temp_stat

            # only concerned with g val bound
            costbound = (path.gval, float('inf'), float('inf'))
    
    return path, stat



