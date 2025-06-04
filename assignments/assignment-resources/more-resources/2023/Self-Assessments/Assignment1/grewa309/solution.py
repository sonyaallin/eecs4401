#   Look for #IMPLEMENT tags in this file. These tags indicate what has
#   to be implemented to complete the warehouse domain.

#   You may add only standard python imports
#   You may not remove any imports.
#   You may not import or otherwise source any of your own files

import os  # for time functions
import math
from re import search # for infinity

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

    # There are couple of issues with the heur_manhattan_distance.
    #   1. We are not considering the manhattan distance of the nearest robot to the box
    #   2. We are not checking for deadlocks where the box cannot be moved from current location
    #   3. (OUT OF SCOPE OF ASSIGNMENT) We are not considering that manhattan distance allows multiple boxes to go 
    #   to the same storage box and multiple robotos to go to same box
  
    # Solution: 
    # - The easiest thing we can do is solve problem (1) by also summing manhattan distance of the nearest robot to a particular box
    # To get a even tighter lower bound for our heuristic. We still ignore obstacles like in the original heuristic function to ensure 
    # that this heuristic function is still admissible 
    #
    # - Also checking deadlock is quite easy and can save us lot of time. Deadlocks include scenrious like when the box is 
    # in a corner or is is along the top or bottom edge but there is not storage in the top or bottom edge

    heur_total = 0 
    available_boxes = state.boxes.difference(state.storage)
    available_storage = state.storage.difference(state.boxes)


    # apply manhatten heuristic on robots AND boxes
    for curr_box in available_boxes:
        closest_storage_loc = min(available_storage, key=lambda s: get_manhatten_distance(state, curr_box, s))
        heur_total += get_manhatten_distance(state, curr_box, closest_storage_loc)
       
        closest_robot = min(state.robots, key=lambda s: abs(curr_box[0] -s[0]) + abs(curr_box[1] - s[1]))
        heur_total += abs(curr_box[0] - closest_robot[0]) + abs(curr_box[1] - closest_robot[1])
                
        if (heur_total == math.inf):
            return heur_total
    
    return heur_total


# did not help solution
# def get_robot_manhatten_distance(state, curr_box, robot):
#     tile_neighbours_top= frozenset(((robot[0] - 1, robot[1])))
#     tile_neightbours_bottom = frozenset(((robot[0] + 1, robot[1])))
#     tile_neightbours_left = frozenset(((robot[0], robot[1] - 1)))
#     tile_neighbours_right = frozenset(((robot[0], robot[1] + 1)))

#     obstacles = (state.obstacles | frozenset(state.robots))

#     if(tile_neighbours_top & obstacles and tile_neightbours_bottom & obstacles and tile_neightbours_left & obstacles
#     and tile_neighbours_right & obstacles):
#         return math.inf

#     # # Check if box is edge locked
#     # elif ((box[0] == 0 or box[0] == state.height - 1) and (box[1] == 0 or box[1] == state.width - 1)):
#     #     return True
#     # elif((box[0] == 0 and storage[0] != 0) or (box[0] == state.height - 1 and storage[0] != state.height - 1)):
#     #     return True
#     # elif ((box[1] == 0 and storage[1] != 0) or (box[1] == state.width - 1 and storage[1] != state.width - 1)):
#     #     return True
    
#     # return False

#     return abs(curr_box[0] -robot[0]) + abs(curr_box[1] - robot[1])


"""
Check if box is in deadlock where it cannot be moved to the specific storage location
"""
def check_deadlock(state, box, storage):
    tile_neighbours_vertical= set(((box[0] - 1, box[1]), (box[0] + 1, box[1])))
    tile_neighbours_horizontal = set(((box[0], box[1] - 1), (box[0], box[1] + 1)))

    if(tile_neighbours_vertical & (state.obstacles | state.boxes) and tile_neighbours_horizontal & (state.obstacles | state.boxes)):
        return True

    # Check if box is edge locked
    elif ((box[0] == 0 or box[0] == state.height - 1) and (box[1] == 0 or box[1] == state.width - 1)):
        return True
    elif((box[0] == 0 and storage[0] != 0) or (box[0] == state.height - 1 and storage[0] != state.height - 1)):
        return True
    elif ((box[1] == 0 and storage[1] != 0) or (box[1] == state.width - 1 and storage[1] != state.width - 1)):
        return True
    
    return False

"""
Return the distance from one box to another but now we catch deadlocks. If the box cannot be moved to the 
storage location than we return math.inf.
"""
def get_manhatten_distance(state, box, storage):
    if check_deadlock(state, box, storage):
        return math.inf
    return abs(box[0] - storage[0]) + abs(box[1] - storage[1])


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

    distance_to_goal = 0

    for curr_box in state.boxes:
        if curr_box not in state.storage:
            # this box has not found it's way to a storage location
            closest_storage_loc = min(state.storage, key=lambda s: abs(curr_box[0] -s[0]) + abs(curr_box[1] - s[1]))
            distance_to_goal += abs(curr_box[0] - closest_storage_loc[0]) + abs(curr_box[1] - closest_storage_loc[1])
        
    return distance_to_goal

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

    # intialize the search engine
    wrapped_fval_function = (lambda sN : fval_function(sN,weight)) 
    search_engine = SearchEngine('custom', 'default')
    search_engine.init_search(initial_state, sokoban_goal_state, heur_fn, wrapped_fval_function)

    # Run the search engine
    goal_path, search_stats = search_engine.search(timebound, None)

    return goal_path, search_stats
        
def iterative_astar(initial_state, heur_fn, weight=1, timebound=5):  # Uses f(n), see how autograder initializes a search line 88
    # IMPLEMENT
    '''Provides an implementation of realtime a-star, as described in the HW1 handout'''
    '''INPUT: a sokoban state that represents the start state and a timebound (number of seconds)'''
    '''OUTPUT: A goal state (if a goal is found), else False as well as a SearchStats object'''
    '''implementation of iterative astar algorithm'''

    curr_weight = weight
    cost_bound = None
    goal_path, search_stats = False, None
    best_goal_path, best_goal_path_stats = False, None

    # intialize the search engine
    wrapped_fval_function = (lambda sN : fval_function(sN,weight)) 
    search_engine = SearchEngine('custom', 'default')
    search_engine.init_search(initial_state, sokoban_goal_state, heur_fn, wrapped_fval_function)

    iter_search_curr_time = os.times()[0]
    iter_search_end_time = iter_search_curr_time + timebound 

    while(iter_search_curr_time < iter_search_end_time and curr_weight >= 1):
        # run the search algo
        goal_path, search_stats = search_engine.search(iter_search_end_time - iter_search_curr_time, cost_bound)

        if(not goal_path or iter_search_curr_time + search_stats.total_time >= iter_search_end_time):
            break # no more iterations is possible that will lead to better solution that we have
            
        # update variables
        best_goal_path = goal_path  
        best_goal_path_stats = search_stats
        cost_bound = (math.inf, math.inf, best_goal_path.gval)
        iter_search_curr_time += search_stats.total_time
        curr_weight -= 0.2

    
    if(not goal_path):
        best_goal_path_stats = search_stats

    return best_goal_path, best_goal_path_stats

def iterative_gbfs(initial_state, heur_fn, timebound=5):  # only use h(n)
    # IMPLEMENT
    '''Provides an implementation of anytime greedy best-first search, as described in the HW1 handout'''
    '''INPUT: a sokoban state that represents the start state and a timebound (number of seconds)'''
    '''OUTPUT: A goal state (if a goal is found), else False'''
    '''implementation of iterative gbfs algorithm'''

    cost_bound = None
    goal_path, search_stats = False, None
    best_goal_path, best_goal_path_stats = False, None

    # intialize the search engine
    search_engine = SearchEngine('best_first')
    search_engine.init_search(initial_state, sokoban_goal_state, heur_fn)

    iter_search_curr_time = os.times()[0]
    iter_search_end_time = iter_search_curr_time + timebound

    while(iter_search_curr_time < iter_search_end_time):
        # run the search algo
        goal_path, search_stats = search_engine.search(iter_search_end_time - iter_search_curr_time, cost_bound)

        if(not goal_path or iter_search_curr_time + search_stats.total_time >= iter_search_end_time):
            break # No more iterations is possible that will lead to better solution that we have
            
        # update variables
        best_goal_path = goal_path  
        best_goal_path_stats = search_stats
        cost_bound = (best_goal_path.gval, math.inf,  math.inf)
        iter_search_curr_time += search_stats.total_time

    
    if(not goal_path):
        best_goal_path_stats = search_stats

    return best_goal_path, best_goal_path_stats





