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
# This heuristic checks for all deadlocks including if a box is cornered between a wall/obstacle,
# if a box is along the wall with another box beside it and if a box is along the wall with no storage 
# locations along it, in which case all these cases will return infinity meaning its unsolveable.
# Or else the distance will be:
# for all boxes that are not in a storage location,
# shortest distance between the box and a robot along with the obstacles around that box 
#     + 
# shortest distance between the box and a storage location that is available along with the obstacles and walls around that box.

def heur_alternate(state):
    # IMPLEMENT
    '''a better heuristic'''
    '''INPUT: a sokoban state'''
    '''OUTPUT: a numeric value that serves as an estimate of the distance of the state to the goal.'''
    # heur_manhattan_distance has flaws.
    # Write a heuristic function that improves upon heur_manhattan_distance to estimate distance between the current state and the goal.
    # Your function should return a numeric value for the estimate of the distance to the goal.
    # EXPLAIN YOUR HEURISTIC IN THE COMMENTS. Please leave this function (and your explanation) at the top of your solution file, to facilitate marking.
    sum_of_distances = 0

    for box in state.boxes:
        
        if (box in state.storage):
            continue
        else:
            move_left = (box[0] -1, box[1]) in state.boxes
            move_right = (box[0] + 1, box[1]) in state.boxes
            move_down = (box[0], box[1] - 1) in state.boxes
            move_up = (box[0], box[1] + 1) in state.boxes

            against_left_wall = box[0] - 1 == -1
            against_right_wall = box[0] + 1 == state.width
            against_bottom_wall = box[1] - 1 == -1
            against_top_wall = box[1] + 1 == state.height
            
            free_storage = state.storage.difference(state.boxes)

            # no obstacles
            if (len(state.obstacles) == 0):
                # check if box is cornered between walls
                if ((against_left_wall) and (against_bottom_wall)):
                    return float('inf')
                elif ((against_right_wall) and (against_top_wall)):
                    return float('inf')
                elif ((against_left_wall) and (against_top_wall)):
                    return float('inf')
                elif ((against_right_wall) and (against_bottom_wall)):
                    return float('inf')

                # check if a box is along the wall with another box beside it
                elif (against_left_wall and (move_up or move_down)):
                    return float('inf')
                elif ((against_right_wall) and (move_up or move_down)):
                    return float('inf')
                elif ((against_top_wall) and (move_right or move_left)):
                    return float('inf')
                elif ((against_bottom_wall) and ((move_right or move_left))):
                    return float('inf')

                shortest_distance = None
                
                storage_wall_left = False
                storage_wall_right = False
                storage_wall_top = False
                storage_wall_bottom = False

                obstacles_around_box =  against_bottom_wall + against_right_wall + against_top_wall + against_left_wall
                
                for stor in free_storage:
                    distance = (abs(box[0] - stor[0]) + abs(box[1] - stor[1]))
                    distance = distance + obstacles_around_box
                   
                    if shortest_distance is None:
                        shortest_distance = distance
                    elif distance < shortest_distance:
                        shortest_distance = distance
                    # check if a box is along a wall but no storages around that wall
                    if (against_left_wall and stor[0] -1 == -1):
                        storage_wall_left = True    
                    elif (against_right_wall and stor[0] + 1 == state.width):
                        storage_wall_right = True
                    if (against_bottom_wall and stor[1] - 1 == -1):
                        storage_wall_bottom = True  
                    elif (against_top_wall and stor[1] + 1 == state.height):
                        storage_wall_top = True
                            

                if ((against_left_wall and not storage_wall_left) or (against_right_wall and not storage_wall_right) or
                (against_top_wall and not storage_wall_top) or (against_bottom_wall and not storage_wall_bottom)):
                    return float('inf')

                sum_of_distances = sum_of_distances + shortest_distance

                shortest_distance = None
                for robot in state.robots:
                    distance = (abs(box[0] - robot[0]) + abs(box[1] - robot[1]))
                    if shortest_distance is None:
                        shortest_distance = distance                
                    elif distance < shortest_distance:
                        shortest_distance = distance

                sum_of_distances = sum_of_distances + shortest_distance
   
            else: 
                move_left_obstacle = (box[0] -1, box[1]) in state.obstacles
                move_right_obstacle = (box[0] + 1, box[1]) in state.obstacles
                move_down_obstacle = (box[0], box[1] - 1) in state.obstacles
                move_up_obstacle = (box[0], box[1] + 1) in state.obstacles

                # check if box is cornered between a wall/obstacle
                if ((move_left_obstacle) or (against_left_wall)) and (move_down_obstacle or (against_bottom_wall)):
                    return float('inf')
                elif ((move_right_obstacle or (against_right_wall)) and (move_up_obstacle or (against_top_wall))):
                    return float('inf')
                elif (((move_left_obstacle) or (against_left_wall)) and ((move_up_obstacle) or (against_top_wall))):
                    return float('inf')
                elif (((move_right_obstacle) or (against_right_wall)) and ((move_down_obstacle)) or (against_bottom_wall)):
                    return float('inf')

                # check if a box is along the wall with another box beside it
                elif (against_left_wall and ((move_up) or (move_down))):
                    return float('inf')
                elif ((against_right_wall) and ((move_up) or (move_down ))):
                    return float('inf')
                elif ((against_top_wall) and ((move_right) or (move_left))):
                    return float('inf')
                elif ((against_bottom_wall) and ((move_right) or (move_left))):
                    return float('inf')


                shortest_distance = None
                storage_wall_left = False
                storage_wall_right = False
                storage_wall_top = False
                storage_wall_bottom = False
                
                obstacles_around_box = ((move_left_obstacle) + (move_right_obstacle) + (move_down_obstacle) + (move_up_obstacle)) \
                                                  +  against_bottom_wall + against_right_wall + against_top_wall + against_left_wall

                for stor in free_storage:
                    distance = (abs(box[0] - stor[0]) + abs(box[1] - stor[1]))
                    distance = distance + obstacles_around_box
                   
                    if shortest_distance is None:
                        shortest_distance = distance
                        #continue
                    elif distance < shortest_distance:
                        shortest_distance = distance
                    # check if a box is along a wall but no storages around that wall
                    if (against_left_wall and stor[0] -1 == -1):
                        storage_wall_left = True   
                    elif (against_right_wall and stor[0] + 1 == state.width):
                        storage_wall_right = True    
                    if (against_bottom_wall and stor[1] - 1 == -1):
                        storage_wall_bottom = True
                    elif (against_top_wall and stor[1] + 1 == state.height):
                        storage_wall_top = True
                            
                if ((against_left_wall and not storage_wall_left) or (against_right_wall and not storage_wall_right) or
                (against_top_wall and not storage_wall_top) or (against_bottom_wall and not storage_wall_bottom)):
                    return float('inf')

                sum_of_distances = sum_of_distances + shortest_distance


                shortest_distance = None
                for robot in state.robots:
                    distance = (abs(box[0] - robot[0]) + abs(box[1] - robot[1]))
                   
                    distance = distance + move_down_obstacle + move_up_obstacle + move_right_obstacle + move_left_obstacle

                    if shortest_distance is None:
                        shortest_distance = distance
                        
                    elif distance < shortest_distance:
                        shortest_distance = distance
                sum_of_distances = sum_of_distances + shortest_distance
                


    return sum_of_distances  # CHANGE THIS

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

    sum_of_distances = 0

    for box in state.boxes:
        shortest_distance = None
        for stor in state.storage:
            distance = (abs(box[0] - stor[0]) + abs(box[1] - stor[1]))
            if shortest_distance is None:
                shortest_distance = distance
                continue
            if distance < shortest_distance:
                shortest_distance = distance
        sum_of_distances = sum_of_distances + shortest_distance

    return sum_of_distances  # CHANGE THIS

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
    se = SearchEngine('custom')


    wrapped_fval_function = (lambda sN : fval_function(sN,weight)) 
    se.init_search(initial_state, sokoban_goal_state, heur_fn, wrapped_fval_function)
    goal, stats = se.search(timebound)
     #  wrapped_fval_function = (lambda N : fval_function(sN,weight)) 
    #wrapped_fval_function = (lambda N : fval_function(sN,weight)) 

    return goal, stats  # CHANGE THIS

def iterative_astar(initial_state, heur_fn, weight=1, timebound=5):  # uses f(n), see how autograder initializes a search line 88
    # IMPLEMENT
    '''Provides an implementation of realtime a-star, as described in the HW1 handout'''
    '''INPUT: a sokoban state that represents the start state and a timebound (number of seconds)'''
    '''OUTPUT: A goal state (if a goal is found), else False as well as a SearchStats object'''
    '''implementation of iterative astar algorithm'''

    se = SearchEngine('custom')
    wrapped_fval_function = (lambda sN : fval_function(sN,weight)) 
    se.init_search(initial_state, sokoban_goal_state, heur_fn, wrapped_fval_function)
    best_goal, best_stats = se.search(timebound)

    if best_goal is False:
            return best_goal, best_stats

    costbound = [best_goal.gval, heur_fn(best_goal), best_goal.gval + heur_fn(best_goal)]
    timebound = timebound - best_stats.total_time

    while (timebound > 0):
        weight = weight / 2
        goal, stats = se.search(timebound, costbound)
        if goal is False:
            return best_goal, best_stats
        costbound_goal = goal.gval + heur_fn(goal)
        if (costbound_goal < costbound[2]):
            costbound = [goal.gval, heur_fn(goal), goal.gval + heur_fn(goal)]
            best_goal = goal
            best_stats = stats
        timebound = timebound - stats.total_time
    return best_goal, best_stats #CHANGE THIS

def iterative_gbfs(initial_state, heur_fn, timebound=5):  # only use h(n)
    # IMPLEMENT
    '''Provides an implementation of anytime greedy best-first search, as described in the HW1 handout'''
    '''INPUT: a sokoban state that represents the start state and a timebound (number of seconds)'''
    '''OUTPUT: A goal state (if a goal is found), else False'''
    '''implementation of iterative gbfs algorithm'''
    se = SearchEngine('best_first')
    wrapped_fval_function = (lambda sN : fval_function(sN,1)) 
    se.init_search(initial_state, sokoban_goal_state, heur_fn, wrapped_fval_function)
    best_goal, best_stats = se.search(timebound)

    if best_goal is False:
            return best_goal, best_stats

    costbound = [best_goal.gval, heur_fn(best_goal), best_goal.gval + heur_fn(best_goal)]
    timebound = timebound - best_stats.total_time
    best_gval = best_goal.gval

    while (timebound > 0):
        goal, stats = se.search(timebound, costbound)
        if goal is False:
            return best_goal, best_stats
        if (goal.gval < best_gval):
            best_gval = goal.gval
            costbound = [goal.gval, heur_fn(goal), goal.gval + heur_fn(goal)]
            best_goal = goal
            best_stats = stats
        timebound = timebound - stats.total_time
    return best_goal, best_stats #CHANGE THIS
   # return None, None #CHANGE THIS




