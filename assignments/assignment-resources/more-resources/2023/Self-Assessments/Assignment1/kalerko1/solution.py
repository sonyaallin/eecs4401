#   Look for #IMPLEMENT tags in this file. These tags indicate what has
#   to be implemented to complete the warehouse domain.

#   You may add only standard python imports
#   You may not remove any imports.
#   You may not import or otherwise source any of your own files

from mimetypes import init
import os  # for time functions
import math
from sre_parse import State  # for infinity
from search import *  # for search engines
from sokoban import sokoban_goal_state, SokobanState, Direction, PROBLEMS  # for Sokoban specific classes and problems

# SOKOBAN HEURISTICS
def heur_alternate(state):
    '''a better heuristic'''
    '''INPUT: a sokoban state'''
    '''OUTPUT: a numeric value that serves as an estimate of the distance of the state to the goal.'''

    # heur_manhattan_distance has flaws.
    # Write a heuristic function that improves upon heur_manhattan_distance to estimate distance between the current state and the goal.
    # Your function should return a numeric value for the estimate of the distance to the goal.
    # EXPLAIN YOUR HEURISTIC IN THE COMMENTS. Please leave this function (and your explanation) at the top of your solution file, to facilitate marking.
    #first we check if box is in corners
    #then we check if box is on a vertical/horizontal edge and check if theres storage spot in the same row/column
    #check if theres an obstacle inbetween the storage and box
    #finally check which robot is closest to the box
    #remove storage spot from list
    #loop through all boxes
    
    robots = state.robots
    boxes = state.boxes
    storages = state.storage
    obstacles = state.obstacles
    temp_dist = 0
    min_dist = math.inf
    total_dist = 0
    used_storage_spaces = []
    storage_list= []
    obstacle_list= []

    for storage in storages:
        storage_list.append(storage)
    for obstacle in obstacles:
        obstacle_list.append(obstacle)

    for box in boxes:
        #if box in storage, then skip to next box in list
        if check_box_in_storage(box,storages):
            continue
        # if box in top left corner, then impossible to move
        if box[0] == box[1] == 0:
            return math.inf
        # if box in bottom left corner, then impossible to move
        if box[0] == 0 and box[1] == (state.height - 1):
            return math.inf
        # if box in top right corner, then impossible to move
        if box[0] == (state.width - 1) and box[1] == 0:
            return math.inf
        # if box in bottom right corner, then impossible to moves
        if box[0] == (state.width - 1) and (box[1] == (state.height - 1)):
            return math.inf

        # for storage in free_storages:
        for i in range(len(storages)):
            #if storage is used_storage_spaces, skip to next storage spot
            if i in used_storage_spaces:
                continue

            storage = storage_list[i]    
            #if box is in top row and storage isn't, then move to next storage spot
            if box[0] == 0 and storage[0] != 0:
                continue
            #if box is in first column and storage isn't, then move to next storage spot
            if box[1] == 0 and storage[1] != 0:
                continue            
            #if box is in last row and storage isn't, then move to next storage spot
            if box[0] == (state.width - 1) and storage[0] != (state.width - 1):
                continue
            #if box is in last column and storage isn't, then move to next storage spot
            if box[1] == (state.height - 1) and storage[1] != (state.height - 1):
                continue
            
            #calculate distance between box and storage
            box_storage_dist = manhattan_dist(box, storage) 

            #if in the same row, check for obstacles in that row
            if box[0] == storage[0]:
                box_storage_dist += check_obstacle_in_path(box, obstacle_list, storage, 0, state)

 
            if box[1] == storage[1]:
                box_storage_dist += check_obstacle_in_path(box, obstacle_list, storage, 1, state)

 
            #check where the robots are and choose the closest robot to do the job
            for robot in robots:
                temp_dist = manhattan_dist(robot, box) + box_storage_dist
                if temp_dist < min_dist:
                    min_dist = temp_dist
                    #append the storage list to the used_storage_spaces storage spaces
                    used_storage_spaces.append(i)
        total_dist += min_dist
        min_dist = math.inf

    # print (total_dist)
    return total_dist 
    
def check_obstacle_in_path(box, obstacles, storage, direction, state):
    #if box is in ilegal coordinates 
    if box[0] >= state.width or box[1] >= state.height or box[0] < 0 or box[1] < 0:
        return math.inf

    for obstacle in obstacles:
        #check if obstacle is inbetween box and storage
        if obstacle[direction] == box[direction]:
            if (box[direction] <= obstacle[direction] <= storage[direction]) or (box[direction] >= obstacle[direction] >= storage[direction]):
                #moves box vertically or horizontally depending on direction value
                if not direction:
                    box_up = (box[0], box[1] + 1)            
                    box_down = (box[0], box[1] - 1)
                else:
                    box_up = (box[0] + 1, box[1])            
                    box_down = (box[0] - 1, box[1]) 
                #checks if theres an obstacle in new location
                obstacles.remove(obstacle)
                step_up = check_obstacle_in_path(box_up, obstacles, storage, direction, state)
                step_down = check_obstacle_in_path(box_down, obstacles, storage, direction, state)
                #goes with the path with least steps + avoiding the initial obstacle
                if step_up > step_down:
                    return step_down + 2
                return step_up + 2
    return 0



def check_box_in_storage(box,storages):
    if box in storages:
        return True
    return False
    
def heur_zero(state):
    '''Zero Heuristic can be used_storage_spaces to make A* search perform uniform cost search'''
    return 0

def heur_manhattan_distance(state):
    '''admissible sokoban puzzle heuristic: manhattan distance'''
    '''INPUT: a sokoban state'''
    '''OUTPUT: a numeric value that serves as an estimate of the distance of the state to the goal.'''
    # We want an admissible heuristic, which is an optimistic heuristic.
    # It must never overestimate the cost to get from the current state to the goal.
    # The sum of the Manhattan distances between each box that has yet to be stored and the storage point nearest to it is such a heuristic.
    # When calculating distances, assume there are no obstacles on the grid.
    # You should implement this heuristic function exactly, even if it is tempting to improve it.
    # Your function should return a numeric value; this is the estimate of the distance to the goal.

    boxes = state.boxes
    storages = state.storage
    temp_dist = 0
    min_dist = math.inf
    total_dist = 0

    for box in boxes:
        for storage in storages:
            temp_dist = manhattan_dist(box, storage)
            if temp_dist < min_dist:
                min_dist = temp_dist
        total_dist += min_dist
        min_dist = math.inf

    return total_dist 

def manhattan_dist(box,storage):
    dist = abs(box[0] - storage[0]) + abs(box[1] - storage[1]) 
    return dist


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

    wrapped_fval_function = (lambda sN : fval_function(sN,weight))
    #initialize search 
    search_engine = SearchEngine('custom', 'default')
    search_engine.init_search(initial_state, sokoban_goal_state, heur_fn, wrapped_fval_function) 
    return search_engine.search(timebound) 

def iterative_astar(initial_state, heur_fn, weight=1, timebound=5):  # uses f(n), see how autograder initializes a search line 88
    '''Provides an implementation of realtime a-star, as described in the HW1 handout'''
    '''INPUT: a sokoban state that represents the start state and a timebound (number of seconds)'''
    '''OUTPUT: A goal state (if a goal is found), else False as well as a SearchStats object'''
    '''implementation of iterative astar algorithm'''
    weight = 1
    initial_time = os.times()[0]
    wrapped_fval_function = (lambda sN : fval_function(sN,weight))
    cost = math.inf
    #initialize search 
    search_engine = SearchEngine('custom','default')
    search_engine.init_search(initial_state, sokoban_goal_state, heur_fn, wrapped_fval_function)    
    # seperate search results
    (goal_node, search_stats) = search_engine.search(initial_time + timebound - os.times()[0]) 
    return (goal_node, search_stats) 

def iterative_gbfs(initial_state, heur_fn, timebound=5):  # only use h(n)
    '''Provides an implementation of anytime greedy best-first search, as described in the HW1 handout'''
    '''INPUT: a sokoban state that represents the start state and a timebound (number of seconds)'''
    '''OUTPUT: A goal state (if a goal is found), else False'''
    '''implementation of iterative gbfs algorithm'''
    
    initial_time = os.times()[0]
    #initialize search 
    search_engine = SearchEngine('best_first', 'default')
    search_engine.init_search(initial_state, sokoban_goal_state, heur_fn)
    # seperate search results
    (goal_node, search_stats) = search_engine.search(timebound)
    return (goal_node, search_stats) 



