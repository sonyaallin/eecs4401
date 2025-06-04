#   Look for #IMPLEMENT tags in this file. These tags indicate what has
#   to be implemented to complete the warehouse domain.

#   You may add only standard python imports
#   You may not remove any imports.
#   You may not import or otherwise source any of your own files

import os  # for time functions
import math
from turtle import width  # for infinity
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

    # Implementing ideas from Piazza @63
    ans = 0

    # Right now I'm getting 16/20, after seeing the cases I did not pass. I realise that it is due to a same issue:
    # let X represent walls, 7 represent closed_storages, and O represent an open storage
    # XXXXX....
    # XO7......
    # x7.......
    # X........
    # X........
    # as can be seen, the storage on the top left is unaccessible.
    # i'm trying to adjust my code to allow it but i'm failing.

    # Step 1:
    # Find out which boxes and storages are solved and which ones are open
    open_boxes = []
    closed_storages = []
    open_edges = [0,0,0,0] #if edge of wall have n open storages, n, else 0. each index represent left edge, top, right, bottom

    for box in state.boxes:
        found_storage = False
        for store in state.storage:
            if box == store:
                closed_storages.append(store)
                found_storage = True
                break
        if not found_storage:
            open_boxes.append(box)

    
    for store in state.storage:
        if store not in closed_storages:
            if store[0] == 0:
                open_edges[0] += 1
            if store[0] == state.width-1:
                open_edges[2] += 1
            if store[1] == 0:
                open_edges[1] += 1
            if store[1] == state.height-1:
                open_edges[3] += 1    


    # Step 2:
    # Check if state can no longer produce a solution, meaning state is stuck.
    # A state can be stuck if it is in a corner of {(x,x) where x in walls+obstacles+closed_storages}
    # or if it is at the edge of the board and no open storage is in that edge
    # If state is stuck, return inf
    for box in open_boxes:
        # four corners of map
        if box == (0,0) or box == (state.width-1, 0) or box == (0, state.height-1) \
        or box == (state.width-1, state.height-1):
            return float('inf')

        # checks if there is an obstacle/wall/used-storage-space on box's left,right,up,down
        left = (box[0]-1, box[1])
        right = (box[0]+1, box[1])
        down = (box[0], box[1]+1)
        up = (box[0], box[1]-1)
        left_check = (box[0]-1 == -1) or (left in closed_storages) or (left in state.obstacles)
        right_check = (box[0]+1 == state.width) or (right in closed_storages) or (right in state.obstacles)
        down_check = (box[1]+1 == state.height) or (down in closed_storages) or (down in state.obstacles)
        up_check = (box[1]-1 == -1) or (up in closed_storages) or (up in state.obstacles)
        
        # to be stuck, there should be at least one obstacle/wall/used-storage in each axis
        if (left_check or right_check) and (down_check or up_check):
            return float('inf')

        # at edge of board and no open storages at that edge
        if box[0]==0:
            if open_edges[0]==0:
                return float('inf')
            open_edges[0] = open_edges[0] - 1
        if box[0]==state.width-1:
            if open_edges[2]==0:
                return float('inf')
            open_edges[2] = open_edges[2] - 1
        if box[1]==0:
            if open_edges[1]==0:
                return float('inf')
            open_edges[1] = open_edges[1] - 1
        if box[1]==state.height-1:
            if open_edges[3]==0:
                return float('inf')
            open_edges[3] = open_edges[3] - 1


    # Step 3:
    # assign each open box to closest robot
        robot_dist = float('inf')
        for robot in state.robots:
            robot_x = robot[0]
            robot_y = robot[1]
            dist = abs(box[0] - robot_x) + abs(box[1] - robot_y)
            robot_dist = min(robot_dist, dist)
        ans += robot_dist
    
    # Step 4:
    # assign each open box to closest open storage
        storage_dist = float('inf')
        box_storage = -1
        for storage in state.storage:
            if storage not in closed_storages:
                storage_x = storage[0]
                storage_y = storage[1]
                dist = abs(box[0] - storage_x) + abs(box[1] - storage_y)
                #Step 5: calculate amount of obstacles between box and storage
                obs_ans = 0
                for obs in state.obstacles:
                    if min(storage[0], box[0]) < obs[0] < max(storage[0], box[0])\
                    and min(storage[1], box[1]) < obs[1] < max(storage[1], box[1]):
                        obs_ans += 1
                dist += obs_ans * 2
                if dist < storage_dist:
                    storage_dist = dist
                    box_storage = storage

        ans += storage_dist

        #Step 5: calculate amount of obstacles between box and closest storage
        # if (box_storage != -1):
        #     obs_ans = 0
        #     for obs in state.obstacles:
        #         if min(box_storage[0], box[0]) < obs[0] < max(box_storage[0], box[0])\
        #         and min(box_storage[1], box[1]) < obs[1] < max(box_storage[1], box[1]):
        #             obs_ans += 1
        #     ans += obs_ans*2
        
    # Last but not least, return h(n)
    return ans 


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
    ans = 0
    for box in state.boxes:
        box_x = box[0]
        box_y = box[1]
        box_ans = float('inf')
        for storage in state.storage:
            storage_x = storage[0]
            storage_y = storage[1]
            dist = abs(box_x - storage_x) + abs(box_y - storage_y)
            box_ans = min(box_ans, dist)
        ans += box_ans

    return ans  # CHANGE THIS

def fval_function(sN, weight):
    # IMPLEMENT
    """
    Provide a custom formula for f-value computation for Anytime Weighted A star.
    Returns the fval of the state contained in the sNode.

    @param sNode sN: A search node (containing a SokobanState)
    @param float weight: Weight given by Anytime Weighted A star
    @rtype: float
    """
    fval = sN.gval + (weight * sN.hval)
    return fval

# SEARCH ALGORITHMS
def weighted_astar(initial_state, heur_fn, weight, timebound):
    # IMPLEMENT    
    '''Provides an implementation of weighted a-star, as described in the HW1 handout'''
    '''INPUT: a sokoban state that represents the start state and a timebound (number of seconds)'''
    '''OUTPUT: A goal state (if a goal is found), else False as well as a SearchStats object'''
    '''implementation of weighted astar algorithm'''
    engine = SearchEngine('custom', 'full')
    wrapped_fval_function = (lambda sN : fval_function(sN,weight)) 
    engine.init_search(initial_state, sokoban_goal_state, heur_fn, wrapped_fval_function)
    return engine.search(timebound=timebound)


def iterative_astar(initial_state, heur_fn, weight=1, timebound=5):  # uses f(n), see how autograder initializes a search line 88
    # IMPLEMENT
    '''Provides an implementation of realtime a-star, as described in the HW1 handout'''
    '''INPUT: a sokoban state that represents the start state and a timebound (number of seconds)'''
    '''OUTPUT: A goal state (if a goal is found), else False as well as a SearchStats object'''
    '''implementation of iterative astar algorithm'''
    engine = SearchEngine('custom', 'full')
    wrapped_fval_function = (lambda sN : fval_function(sN,weight)) 
    time_before = os.times()[0]
    engine.init_search(initial_state, sokoban_goal_state, heur_fn, wrapped_fval_function)
    time_after = os.times()[0]
    time_left = timebound - (time_after - time_before)
    keep_going = True
    ans1, ans2 = False, None
    cost = float('inf')
    while keep_going:
        time_before = os.times()[0]
        state, stats = engine.search(time_left, (float('inf'), float('inf'), cost))
        time_after = os.times()[0]
        if state:
            cost = min(cost, state.gval + weight*heur_fn(state))
            ans1 = state
            ans2 = stats
            weight = weight * 0.5

        time_left = time_left - (time_after - time_before)
        if time_left <= 0:
            keep_going = False
            break # just to make sure it breaks

    return ans1, ans2

def iterative_gbfs(initial_state, heur_fn, timebound=5):  # only use h(n)
    # IMPLEMENT
    '''Provides an implementation of anytime greedy best-first search, as described in the HW1 handout'''
    '''INPUT: a sokoban state that represents the start state and a timebound (number of seconds)'''
    '''OUTPUT: A goal state (if a goal is found), else False'''
    '''implementation of iterative gbfs algorithm'''
    engine = SearchEngine('custom', 'full')
    time_before = os.times()[0]
    engine.init_search(initial_state, sokoban_goal_state, heur_fn)
    time_after = os.times()[0]
    time_left = timebound - (time_after - time_before)
    keep_going = True
    ans1, ans2 = False, None
    cost = float('inf')
    while keep_going:
        time_before = os.times()[0]
        state, stats = engine.search(time_left, (cost, float('inf'), float('inf')))
        time_after = os.times()[0]
        if state:
            cost = state.gval-1
            ans1 = state
            ans2 = stats

        time_left = time_left - (time_after - time_before)
        if time_left <= 0:
            keep_going = False
            break # just to make sure it breaks

    return ans1, ans2



