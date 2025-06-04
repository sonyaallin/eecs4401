#   Look for #IMPLEMENT tags in this file. These tags indicate what has
#   to be implemented to complete the warehouse domain.

#   You may add only standard python imports
#   You may not remove any imports.
#   You may not import or otherwise source any of your own files

import os  # for time functions
import math  # for infinity
from search import *  # for search engines
from sokoban import sokoban_goal_state, SokobanState, Direction, PROBLEMS, UP, RIGHT, DOWN, LEFT  # for Sokoban specific classes and problems
import numpy as np

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

    # IMPROVEMENTS:
    # 1. Remove assumption that multiple boxes can be stored at one location
    # 2. Detect/skip states that are certain to never lead to the goal state (dead states):
    #        i.      box is on a wall with no storage points along that wall 
    #        ii.     box is in a corner (wall or obstacle), includes case when two consecutive obstacles along wall
    # 3. Include manhattan distance of robots to boxes as well 

    # IDEAS THAT WERE ATTEMPTED/DIDN'T WORK:
    # 1. When detecting dead states, tried do all checking before any manhattan distance computation/result began (i.e. going through all box-storage-obstacle
    #    combinations before any computation, and then doing another for-loop of the same structure after to actually calculate the manhattan distance).
    #    However, if it was the case that it was a valid state, all of this computation time would be wasted without accumulating any results. Thus, it was
    #    better to check for dead state while the computation was happening. 
    # 2. When checking for any stores on same wall that box is on, if there WERE stores on that wall, tried to check if any obstacles were in between the
    #    box and those stores. However, it did not make much of a difference, and on a larger scale it would become too computation heavy in filtering all
    #    obstacles and stores on each wall. Thus, the simple version to 'not care' and assume: if there IS storage on the same wall, it is not blocked
    #    saved some time.
    # 3. Tried using different weights for manhattan distance of robots to boxes (e.g. heur_alternate = 1*manhattan_box_to_storage + 1.5*manhattan_robot_to_box)
    #    in an attempt to favour the distance of robots to boxes more than boxes to storage, since robots need to be adjacent to boxes if the boxes are to move.
    #    However, equal weights seemed to be the best.

    # initialize manhattan sums for boxes->storage and robots->boxes 
    sum_man_s = 0
    sum_man_r = 0

    # lists of stores on each wall
    wtop=[s for s in state.storage if s[1]==state.height-1]
    wbottom=[s for s in state.storage if s[1]==0]
    wleft=[s for s in state.storage if s[0]==0]
    wright=[s for s in state.storage if s[0]==state.width-1]
    wall_storages=[wtop, wbottom, wleft, wright]
    
    # filter out boxes already in stores, skip those stores
    boxes_left = [b for b in state.boxes if not b in state.storage]
    storage_available = [s for s in state.storage if not s in boxes_left]

    for b in boxes_left:#state.boxes:
        # initialize min_distance from this box to both storage and robots
        min_distance_s = float('inf')
        min_distance_r = float('inf')

        # flag states that are certain to never reach the goal
        if dead_state(b, state.obstacles, wall_storages, state.width, state.height):
            return float('inf')

        # search for nearest AVAILABLE storage point from this box
        for s in storage_available:
            manhattan_dist = abs(b[0]-s[0]) + abs(b[1]-s[1])
            min_distance_s = min(min_distance_s,manhattan_dist)

        # factor in distance of robots from boxes: want robot closer to the box
        for r in state.robots:
            manhattan_dist = abs(b[0]-r[0]) + abs(b[1]-r[1])
            min_distance_r = min(min_distance_r,manhattan_dist)

        # add to result
        sum_man_s+=min_distance_s
        sum_man_r+=min_distance_r
    return sum_man_s+sum_man_r

# Detect/skip states that are certain to never lead to the goal state (dead states):
#        1.     box is on a wall with no storage points along that wall 
#        2.     box is in a corner (wall or obstacle), includes case when two consecutive obstacles along wall
def dead_state(box, obstacles, wall_storages, width, height):
    # 1. check if box on wall has any reachable stores (i.e. on the same wall)
    
    # top/bottom
    if (box[1]==height-1 and not wall_storages[0]) or (box[1]==0 and not wall_storages[1]):
        return True

    # left/right
    if (box[0]==0 and not wall_storages[2]) or (box[0]==width-1 and not wall_storages[3]):
        return True
    
    # 2. check box is cornered by walls/obstacles
    # points adjacent to box
    up=UP.move(box)
    down=DOWN.move(box)
    right=RIGHT.move(box)
    left=LEFT.move(box)

    # flags for obstacles/walls adjacent to box
    obst_above = box[1]==height-1 or up in obstacles
    obst_below = box[1]==0 or down in obstacles
    obst_right = box[0]==width-1 or right in obstacles
    obst_left = box[0]==0 or left in obstacles

    return True if ((obst_above) and (obst_right or obst_left)) or ((obst_below) and (obst_right or obst_left)) else False

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

    sum_man = 0
    for bx,by in state.boxes:
        # initialize min_distance for this box
        min_distance = float('inf')

        # search for nearest storage point from this box (assumption: many boxes can be stored at one location)
        for sx,sy in state.storage:
            # calculate manhattan to box, update minumum
            manhattan_dist = abs(bx-sx) + abs(by-sy)
            min_distance = min(min_distance,manhattan_dist)

        # add to result
        sum_man+=min_distance
    return sum_man

def fval_function(sN, weight):
    # IMPLEMENT
    """
    Provide a custom formula for f-value computation for Anytime Weighted A star.
    Returns the fval of the state contained in the sNode.

    @param sNode sN: A search node (containing a SokobanState)
    @param float weight: Weight given by Anytime Weighted A star
    @rtype: float
    """
    return sN.gval + weight*sN.hval

# SEARCH ALGORITHMS
def weighted_astar(initial_state, heur_fn, weight, timebound):
    # IMPLEMENT    
    '''Provides an implementation of weighted a-star, as described in the HW1 handout'''
    '''INPUT: a sokoban state that represents the start state and a timebound (number of seconds)'''
    '''OUTPUT: A goal state (if a goal is found), else False as well as a SearchStats object'''
    '''implementation of weighted astar algorithm'''

    # setup custom a-star search engine for sokoban
    searchEngine = SearchEngine('astar')
    wrapper_fval_function = (lambda sN : fval_function(sN,weight)) 
    searchEngine.init_search(initial_state, goal_fn=sokoban_goal_state, heur_fn=heur_fn, fval_function=wrapper_fval_function)
    
    # return if goal found, stats 
    return searchEngine.search(timebound=timebound)

def iterative_astar(initial_state, heur_fn, weight=1, timebound=5):  # uses f(n), see how autograder initializes a search line 88
    # IMPLEMENT
    '''Provides an implementation of realtime a-star, as described in the HW1 handout'''
    '''INPUT: a sokoban state that represents the start state and a timebound (number of seconds)'''
    '''OUTPUT: A goal state (if a goal is found), else False as well as a SearchStats object'''
    '''implementation of iterative astar algorithm'''

    # initialize costbound - the triple: (gval, hval, gval+hval) represents type of evaluation
    costbound = (float('inf'),float('inf'),float('inf'))
    
    # initialize bookkeeping and return variables
    timeleft = timebound
    best_state = False
    best_cost = float('inf')
    result = None, None

    # setup custom a-star search engine for sokoban
    searchEngine = SearchEngine('custom', 'full')
    curr_weight=min(5,(initial_state.width+initial_state.height)/2)
    step=max(2,(curr_weight/2))

    while timeleft > 0:
        # perform search, update timeleft as well as searchEngine with updated weights
        wrapper_fval_function = (lambda sN : fval_function(sN,curr_weight)) 
        searchEngine.init_search(initial_state, goal_fn=sokoban_goal_state, heur_fn=heur_fn, fval_function=wrapper_fval_function)
        curr, stats = searchEngine.search(timebound=timeleft, costbound=costbound)
        timeleft -= stats.total_time

        # found better solution, update best state/costbound
        if curr!=False:

            # every new solution found is the new best since it beats the updated costbound from the previous solution
            best_state = curr 
            best_cost = best_state.gval
            result = best_state, stats
            
        # update weights and costbound
        costbound = (float('inf'), float('inf'), best_cost)
        curr_weight = max(1,curr_weight/step)

    return result

def iterative_gbfs(initial_state, heur_fn, timebound=5):  # only use h(n)
    # IMPLEMENT
    '''Provides an implementation of anytime greedy best-first search, as described in the HW1 handout'''
    '''INPUT: a sokoban state that represents the start state and a timebound (number of seconds)'''
    '''OUTPUT: A goal state (if a goal is found), else False'''
    '''implementation of iterative gbfs algorithm'''

    # initialize costbound
    costbound = (float('inf'), float('inf'), float('inf'))

    # initialize bookkeeping and return variables
    timeleft = timebound
    best_state = False
    best_cost = float('inf')
    result = None, None

    # setup custom bfs engine with default fval_function (only uses hval) for sokoban
    searchEngine = SearchEngine('best_first', 'full')
    searchEngine.init_search(initial_state, goal_fn=sokoban_goal_state, heur_fn=heur_fn)

    while timeleft > 0:
        # perform search, update timeleft
        curr, stats = searchEngine.search(timebound=timeleft, costbound=costbound)
        timeleft -= stats.total_time

        # found better solution, update best state/costbound
        if curr!=False:

            # every new solution found is the new best since it beats the updated costbound from the previous solution
            best_state = curr 
            best_cost = best_state.gval
            result = best_state, stats
            
        # update costbound: prune nodes that have gval greater than gval of best path
        costbound = (best_cost, float('inf'), float('inf'))

    return result



