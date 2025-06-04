#   Look for #IMPLEMENT tags in this file. These tags indicate what has
#   to be implemented to complete the warehouse domain.

#   You may add only standard python imports
#   You may not remove any imports.
#   You may not import or otherwise source any of your own files

import os  # for time functions
import math
from queue import Empty  # for infinity
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
    total_alt_distance = 0 #return value
    max_dist = state.width + state.height
    final_dist = max_dist
    curr_dist = 0
    curr_storage = ()
    occupied_storage = []  #Storage spots that have already been accounted for, either because a box is already on them, or because they were the closest storage to an unstored box
    #blocked_storage = []  This was being used to look for storage that got blocked off by boxes. Didn't end up working out
    #unstored_boxes = []   This was being used to ensure each box was assigned to a unique storage so that the cost would be the lowest possible. Took too long

    for curr_box in state.boxes:
        if is_stuck(state, curr_box): #Checks that the box is not stuck, i.e. cannot be pushed anywhere. If stuck, we return a very large value to discourage this path
            return (state.width * state.height)*2
        elif curr_box in state.storage: #If any boxes are already in a storage, then we don't need to calculate any distances for them, so we just append to occupied_storage
            occupied_storage.append(curr_box)

        else:
            
            for storage in state.storage: #loop through storage spots
                
                if storage not in occupied_storage: #if a storage has not been accounted for, find the manhattan distance, plus a cost for if there are obstacles in the way
                    curr_dist = (abs(curr_box[0] - storage[0])) + (abs(curr_box[1] - storage[1])) + get_obstacle_cost(state, curr_box, storage)  #+ is_storage_stuck(state, storage, occupied_storage)
                    if curr_dist < final_dist:                                                                                                   #This was used to account for storage spots that got blocked off.
                        final_dist = curr_dist                                                                                                   #It was only faster for iterative weighted a star
                        curr_storage = storage
                        #if a smaller distance was found, update final_dist, which represents smallest distance found so far. update curr_storage so it can be appended to occupied_storage
            total_alt_distance += final_dist
            occupied_storage.append(curr_storage)
            final_dist = max_dist

    return total_alt_distance 

def is_stuck(state, curr_box):
   
    if curr_box in state.storage: #if box already on a storage, it cannot be stuck
        return False
    
    if curr_box[0] == 0: #if box is on left edge of board
        if curr_box[1] - 1 >= 0 and (curr_box[0], curr_box[1] - 1) in state.obstacles:
            return True
        if curr_box[1] + 1 <= state.height-1 and (curr_box[0], curr_box[1] + 1) in state.obstacles:
            return True
        if curr_box[1] == 0 or curr_box[1] == state.height-1:
            return True
    if curr_box[0] == state.width-1: #if box is on right edge of board
        if curr_box[1] - 1 >= 0 and (curr_box[0], curr_box[1] - 1) in state.obstacles:
            return True
        if curr_box[1] + 1 <= state.height-1 and (curr_box[0], curr_box[1] + 1) in state.obstacles:
            return True
        if curr_box[1] == 0 or curr_box[1] == state.height-1:
            return True
    if curr_box[1] == 0: #if box is on top edge of board
        if curr_box[0] - 1 >= 0 and (curr_box[0] - 1, curr_box[1]) in state.obstacles:
            return True
        if curr_box[0] + 1 <= state.width-1 and (curr_box[0] + 1, curr_box[1]) in state.obstacles:
            return True
        if curr_box[0] == 0 or curr_box[0] == state.width-1:
            return True
    if curr_box[1] == state.height - 1: #if box is on bottom edge of board
        if curr_box[0] - 1 >= 0 and (curr_box[0] - 1, curr_box[1]) in state.obstacles:
            return True
        if curr_box[0] + 1 <= state.width-1 and (curr_box[0] + 1, curr_box[1]) in state.obstacles:
            return True
        if curr_box[0] == 0 or curr_box[0] == state.width-1:
            return True
    #if box is not on an edge, so cannot be blocked by a wall, only obstacles
    if (curr_box[0]-1, curr_box[1]) in state.obstacles: 
        if (curr_box[0], curr_box[1] - 1) in state.obstacles or (curr_box[0], curr_box[1] + 1) in state.obstacles:
            return True
    if (curr_box[0]+1, curr_box[1]) in state.obstacles:
        if (curr_box[0], curr_box[1] - 1) in state.obstacles or (curr_box[0], curr_box[1] + 1) in state.obstacles:
            return True

    return False

def is_storage_stuck(state, storage, occupied_storage):
    left = 0
    right = 0
    above = 0
    below = 0
    
    #This was for checking if a storage space got blocked off

    if storage == (0,0):
        if storage[0] + 1 < state.width and (storage[0] + 1, storage[1]) in occupied_storage:
            right = 1
        if storage[1] + 1 < state.width and (storage[0], storage[1] + 1) in occupied_storage:
            below = 1
    if storage == (state.width - 1, 0):
        if storage[0] - 1 > -1 and (storage[0] - 1, storage[1]) in occupied_storage:
            left = 1
        if storage[1] + 1 < state.width and (storage[0], storage[1] + 1) in occupied_storage:
            below = 1
    if storage == (0, state.height -1):
        if storage[0] + 1 < state.width and (storage[0] + 1, storage[1]) in occupied_storage:
            right = 1
        if storage[1] - 1 > -1 and (storage[0], storage[1] - 1) in occupied_storage:
            above = 1
    if storage == (state.width - 1, state.height -1):
        if storage[0] - 1 > -1 and (storage[0] - 1, storage[1]) in occupied_storage:
            left = 1
        if storage[1] - 1 > -1 and (storage[0], storage[1] - 1) in occupied_storage:
            above = 1
    
    
    if (left + right + above + below) > 1:
        return 2
    else:
        return 0
    


def get_obstacle_cost(state, curr_box, storage):
    #Finds a cost for obstacles to add to the heuristic
    x_offset = curr_box[0] - storage[0] #how many units the box will have to move in the x axis, the sign tells the direction
    y_offset = curr_box[1] - storage[1] #how many units the box will have to move in the y axis, the sign tells the direction
    x_obstacle = 0 #is there an obstacle on x-axis, sign tells direction
    y_obstacle = 0 #is there an obstacle on y-axis, sign tells direction
    diagonal_obstacle = 0 #is there a diagonal obstacle

    if x_offset > 0 and curr_box[0] - 1 >= 0:
        if (curr_box[0] - 1, curr_box[1]) in state.obstacles or ((curr_box[0] - 1, curr_box[1]) in state.boxes):
            x_obstacle = -1
    if x_offset < 0 and curr_box[0] + 1 <= (state.width - 1):
        if (curr_box[0] + 1, curr_box[1]) in state.obstacles or ((curr_box[0] + 1, curr_box[1]) in state.boxes):
            x_obstacle = 1
    if y_offset > 0 and curr_box[1] - 1 >= 0:
        if (curr_box[0], curr_box[1] - 1) in state.obstacles or ((curr_box[0], curr_box[1] - 1) in state.boxes):
            y_obstacle = -1
    if y_offset < 0 and curr_box[1] + 1 <= (state.height - 1):
        if (curr_box[0], curr_box[1] + 1) in state.obstacles or ((curr_box[0], curr_box[1] + 1) in state.boxes):
            y_obstacle = 1

    if x_offset != 0 and y_offset != 0:
        if (curr_box[0] + x_obstacle >= 0 and curr_box[0] + x_obstacle <= state.width - 1) and (curr_box[1] + y_obstacle >= 0 and curr_box[1] + y_obstacle <= state.height-1):
            if (curr_box[0] + x_obstacle, curr_box[1] + y_obstacle) in state.obstacles or ((curr_box[0] + x_obstacle, curr_box[1] + y_obstacle) in state.boxes):
                diagonal_obstacle = 1

    return abs(x_obstacle) + abs(y_obstacle) + diagonal_obstacle
    

def test():
    state = SokobanState("START", 0, None, 6, 4,  # dimensions
                 ((2, 1), (2, 2)),  # robots
                 frozenset(((1, 1), (1, 2), (4, 1), (4, 2))),  # boxes
                 frozenset(((2, 1), (2, 2), (3, 1), (3, 2))),  # storage
                 frozenset()  # obstacles
                 )
    rt_val = heur_alternate(state)
    print(rt_val)
    return rt_val

def test2():
    print((1 // 3))

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
    total_manhattan_distance = 0
    max_dist = state.width + state.height
    final_dist = max_dist
    curr_dist = 0

    for curr_box in state.boxes:
        for storage in state.storage:
            curr_dist = (abs(curr_box[0] - storage[0])) + (abs(curr_box[1] - storage[1]))
            if curr_dist < final_dist:
                final_dist = curr_dist
        total_manhattan_distance += final_dist
        final_dist = max_dist

    return total_manhattan_distance  # CHANGE THIS

def fval_function(sN, weight):
    # IMPLEMENT
    """
    Provide a custom formula for f-value computation for Anytime Weighted A star.
    Returns the fval of the state contained in the sNode.

    @param sNode sN: A search node (containing a SokobanState)
    @param float weight: Weight given by Anytime Weighted A star
    @rtype: float
    """
    return sN.gval + (weight*(sN.hval)) #CHANGE THIS

# SEARCH ALGORITHMS
def weighted_astar(initial_state, heur_fn, weight, timebound):
    # IMPLEMENT    
    '''Provides an implementation of weighted a-star, as described in the HW1 handout'''
    '''INPUT: a sokoban state that represents the start state and a timebound (number of seconds)'''
    '''OUTPUT: A goal state (if a goal is found), else False as well as a SearchStats object'''
    '''implementation of weighted astar algorithm'''
    se = SearchEngine('custom', 'full')
    wrapped_fval_function = (lambda sN : fval_function(sN,weight)) 
    se.init_search(initial_state, sokoban_goal_state, heur_fn, wrapped_fval_function)
    final, stats = se.search(timebound)
    
    return final, stats  # CHANGE THIS

def iterative_astar(initial_state, heur_fn, weight=1, timebound=5):  # uses f(n), see how autograder initializes a search line 88
    # IMPLEMENT
    '''Provides an implementation of realtime a-star, as described in the HW1 handout'''
    '''INPUT: a sokoban state that represents the start state and a timebound (number of seconds)'''
    '''OUTPUT: A goal state (if a goal is found), else False as well as a SearchStats object'''
    '''implementation of iterative astar algorithm'''
    start_time = os.times()[0]
    i = 0
    #weights = [10, 5, 2, 1]
    best, best_stats = weighted_astar(initial_state, heur_fn, weight, timebound - (os.times()[0] - start_time))
    se = SearchEngine('custom', 'full')
    while os.times()[0] - start_time < timebound and weight != 0:
        if best:
            #best_cost = best.gval
            costbound = [best.gval, best.gval, best.gval]
            weight = weight // 2
            
            wrapped_fval_function = (lambda sN : fval_function(sN,weight)) 
            se.init_search(initial_state, sokoban_goal_state, heur_fn, wrapped_fval_function)
            final, stats = se.search(timebound - (os.times()[0] - start_time), costbound)    
            if final:
                
                best = final
                best_stats = stats
            else:
                return best, best_stats
    return best, best_stats
    
    
    

def iterative_gbfs(initial_state, heur_fn, timebound=5):  # only use h(n)
    # IMPLEMENT
    '''Provides an implementation of anytime greedy best-first search, as described in the HW1 handout'''
    '''INPUT: a sokoban state that represents the start state and a timebound (number of seconds)'''
    '''OUTPUT: A goal state (if a goal is found), else False'''
    '''implementation of iterative gbfs algorithm'''
    start_time = os.times()[0]
    se = SearchEngine('best_first', 'full')
    se.init_search(initial_state, goal_fn=sokoban_goal_state, heur_fn=heur_alternate)
    best, best_stats = se.search(timebound - (os.times()[0] - start_time))
    while (os.times()[0] - start_time)<timebound:
        if best:
            costbound = [best.gval, best.gval, best.gval]
            se.init_search(initial_state, goal_fn=sokoban_goal_state, heur_fn=heur_alternate)
            final, stats = se.search(timebound - (os.times()[0] - start_time), costbound)
            if final:
                best = final
                best_stats = stats
            else:
                return best, best_stats
    return best, best_stats

    
if __name__=='__main__':
    test2()



