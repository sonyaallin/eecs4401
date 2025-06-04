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
    
    '''
    WHAT WAS TRIED:
    The initial attempt was to create a search tree with individual SokobanStates as nodes, and each node would have the movement of a single box.
    Every move would be checked that it was not being pushed into an obstacle or another box as well as checking that there was space for a robot
    to be able to push the box in a given direction (the robot positions were to be ignored otherwise). From here, I would run a breadth first search
    on the tree to try to get the least costly answer to get every box in individual storage spaces. To try to cut down on run time, I tried to prevent
    cycling already seen states, using the StateSpace's cycle check function as well as keeping checking the currnetly queued states to make sure that
    no duplicates existed in there as well to try to lower run time.
    
    However, I greatly misjudged how many children there would be anyways as well as how long it would run. So in the end, this plan was abandoned.
    
    Then, I have switched to using grids to keep track of possible movements for each individual box. Keeping the ideas of moving one step at a time
    for each box, making sure that moves being made were at least theoretically possible (i.e. that the space a box was being pushed to and the space a
    robot would push the box from were not in obstacles or out of bounds) and ignoring robot and other box positions otherwise, and search for the
    closest destination. As a result, each grid is like trying to solve the game assuming there is only one box and robots in the perfect locations to not
    interfer and be able to push the box to the closest storage location. Then adding all of these answers up to a total.
    
    While better then the last attempt, this one was also running for too long for many of the test runs.
    
    WHAT I ENDED WITH:
    
    The third attempt is largely the same as the second, having each block with a grid mapping out it's possible movements in a breath first search manner,
    keeping track of obstacles positions (still ignoring robot positions and other boxes) and only allowing moves that are at least theoretically possible
    (i.e. the space before where the robot should stand to push it and the location the box should be pushed to are both in bound and don't have an obstacle
    in them). However, this time, I have the grid mapping premptively stop itself and return the distance travelled once a path to any storage space is found
    to prevent unecessary running time and remove the need to cycle through to find the path to each individual storage space. In additon, I also calculate
    the distance each robot is to the nearest box (in a similar fashion to the simplest heuristic function) and added that to the returned distance to try to
    keep the search algorithms using this from calculating robot moves that have them running around like headless chickens and not pushing boxes.
    '''
    #Our returned value
    total_dist = 0
    
    #Calculating the distance to each box to the nearest theoretically reachable storage space
    for box in state.boxes:
        #If the box is already in a storage space, no need to find a path for it
        if box in state.storage:
            continue
        
        #2D array to keep track of all pathing, obstacles, and storage locations
        grid = []
        
        #Initially fill the whole grid with math.inf, this value representing a location yet to be considered
        for i in range(0, state.height):
            grid.append([math.inf] * state.width)
        
        #Place all the obstacles on the grid as -1
        for obs in state.obstacles:
            grid[obs[1]][obs[0]] = -1
        
        #Place all storage locations as -2
        for store in state.storage:
            grid[store[1]][store[0]] = -2

        #Looks backwards I know, but in order for the grid to not be rotated 90 degrees when printed out, I need it this way
        grid[box[1]][box[0]] = 0
        
        #Contains all the locations to be checked next
        frontier = [(box[0], box[1])]
        
        #If this value remains true when the frontier is empty, then we know a box has no feasible path to a storage space
        continue_loop = True
        
        while frontier != [] and continue_loop:
            curr = frontier.pop(0)
            curr_value = grid[curr[1]][curr[0]]
            
            check_left = math.inf
            check_right = math.inf
            check_up = math.inf
            check_down = math.inf
            
            #Checking horizontal pathing
            #Checking that neither the locations being pushed to or from are out of bounds
            if curr[0] > 0 and curr[0] < state.width - 1:
                check_left = grid[curr[1]][curr[0] - 1]
                check_right = grid[curr[1]][curr[0] + 1]
                
                #Checking if a storage space is horizontally adjacent and feasible to reach
                #If so, can mark down the distance travelled and move onto the next box
                if ((check_left == -2) and (check_right != -1)) or ((check_left != -1) and (check_right == -2)):
                    total_dist += (curr_value + 1)
                    continue_loop = False
                    break
                
                #Checking if moving left or right is feasible
                if (check_left > -1) and (check_right > -1):
                    #Checking if the location to the left hasn't been explored yet
                    if curr_value + 1 < check_left:
                        grid[curr[1]][curr[0] - 1] = curr_value + 1
                        frontier.append((curr[0] - 1, curr[1]))
            
                    #Checking if the location to the right hasn't been explored yet
                    if curr_value + 1 < check_right:
                        grid[curr[1]][curr[0] + 1] = curr_value + 1
                        frontier.append((curr[0] + 1, curr[1]))
            
            #Checking vertical pathing
            #Checking that neither the locations being pushed to or from are out of bounds
            if curr[1] > 0 and curr[1] < state.height - 1:
                check_up = grid[curr[1] - 1][curr[0]]
                check_down = grid[curr[1] + 1][curr[0]]
                
                #Checking if a storage space is vertically adjacent and feasible to reach
                #If so, can mark down the distance travelled and move onto the next box                
                if ((check_up == -2) and (check_down != -1)) or ((check_up != -1) and (check_down == -2)):                 
                    total_dist += (curr_value + 1)
                    continue_loop = False
                    break
                
                #Checking if moving up or down is feasible
                if (check_up > -1) and (check_down > -1):
                    #Checking if the location above hasn't been explored yet
                    if curr_value < check_up:
                        grid[curr[1] - 1][curr[0]] = curr_value + 1
                        frontier.append((curr[0], curr[1] - 1))
                    
                    #Checking if the location below hasn't been explored yet
                    if curr_value < check_down:
                        grid[curr[1] + 1][curr[0]] = curr_value + 1
                        frontier.append((curr[0], curr[1] + 1))
        
        #If this is still true and the frontier is out of locations to search, we know there is no
        #storage space reachable for this box and we can just return math.inf to denote it's impossible
        #to complete the puzzle for this state
        if continue_loop:
            return math.inf
    
    #Get the distance each robot is to the closest box and add said distance to the final value to promote keeping the robots close to the boxes
    for robot in state.robots:
        closest_dist = math.inf
        for box in state.boxes:
            #The - 1 is to refer to any position next to the box since a box and a robot cannot share the same space
            dist_from_box = abs(robot[0] - box[0]) + abs(robot[1] - box[1]) - 1
            if closest_dist > dist_from_box:
                closest_dist = dist_from_box
        total_dist += closest_dist
        
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
    
    total_dist = 0
    
    for box in state.boxes:
        current_dist = math.inf
        for store in state.storage:
            temp_dist = abs(box[0] - store[0]) + abs(box[1] - store[1])
            if temp_dist < current_dist:
                current_dist = temp_dist
        total_dist += current_dist
    
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
    SE = SearchEngine('custom', "full")
    wrapped_fval_function = (lambda sN : fval_function(sN,weight))
    SE.init_search(initial_state, sokoban_goal_state, heur_fn, wrapped_fval_function)
    
    return SE.search(timebound, (math.inf, math.inf, math.inf))

def iterative_astar(initial_state, heur_fn, weight=1, timebound=5):  # uses f(n), see how autograder initializes a search line 88
    # IMPLEMENT
    '''Provides an implementation of realtime a-star, as described in the HW1 handout'''
    '''INPUT: a sokoban state that represents the start state and a timebound (number of seconds)'''
    '''OUTPUT: A goal state (if a goal is found), else False as well as a SearchStats object'''
    '''implementation of iterative astar algorithm'''
    
    start_time = os.times()[0]
    curr_time = os.times()[0]
    best_final = None
    best_stats = None
    best_gval = math.inf
    best_fval = math.inf
    curr_weight = weight
    hval = heur_fn(initial_state)
    
    #How long it took to compute a single round
    #To be used to determine if we have time to run another round or not
    real_timebound = timebound - 0.1
    if real_timebound < 0:
        real_timebound = timebound
        
    #How long it took to compute a single round
    #To be used to determine if we have time to run another round or not
    loop_time = 0
    prev_time = 0    
        
    while (curr_time - start_time) + loop_time < real_timebound and curr_weight > 0:
        SE = SearchEngine('custom', "full")
        wrapped_fval_function = (lambda sN : fval_function(sN,weight))
        SE.init_search(initial_state, sokoban_goal_state, heur_fn, wrapped_fval_function)
        temp_final, temp_stats = SE.search(real_timebound, (best_gval, math.inf, best_fval))
        
        curr_weight -= 0.1
        curr_time = os.times()[0]
        
        #Check the time taken again to see if this calculation was made in time or not
        #And the last attempt didn't end as false        
        if(curr_time - start_time) < real_timebound and temp_final != False:
            if (best_gval) > (temp_final.gval):
                best_gval = temp_final.gval
                best_fval = fval_function(sNode(temp_final, hval, wrapped_fval_function), weight)
                best_final = temp_final
                best_stats = temp_stats
        else:
            return best_final, best_stats
        
        time_taken = (curr_time - start_time) - prev_time
        if time_taken < 0:
            time_taken = 0
        prev_time = time_taken        
                
    return best_final, best_stats

def iterative_gbfs(initial_state, heur_fn, timebound=5):  # only use h(n)
    # IMPLEMENT
    '''Provides an implementation of anytime greedy best-first search, as described in the HW1 handout'''
    '''INPUT: a sokoban state that represents the start state and a timebound (number of seconds)'''
    '''OUTPUT: A goal state (if a goal is found), else False'''
    '''implementation of iterative gbfs algorithm'''
    
    start_time = os.times()[0]
    curr_time = os.times()[0]
    best_final = None
    best_stats = None
    best_gval = math.inf
    
    #A little more buffer so the end calculations time don't go too overboard
    real_timebound = timebound - 0.1
    if real_timebound < 0:
        real_timebound = timebound
        
    #How long it took to compute a single round
    #To be used to determine if we have time to run another round or not
    loop_time = 0
    prev_time = 0
    
    while (curr_time - start_time) + loop_time < real_timebound:
        SE = SearchEngine('best_first', "full")
        wrapped_fval_function = (lambda sN : fval_function(sN,weight))
        SE.init_search(initial_state, sokoban_goal_state, heur_fn, wrapped_fval_function)
        temp_final, temp_stats = SE.search(real_timebound, (best_gval, math.inf, math.inf))
        
        curr_time = os.times()[0]
        
        #Check the time taken again to see if this calculation was made in time or not
        #And the last attempt didn't end as false
        if(curr_time - start_time) < real_timebound and temp_final != False:
            if (best_gval) > (temp_final.gval):
                best_gval = temp_final.gval
                best_final = temp_final
                best_stats = temp_stats
        else:
            return best_final, best_stats
        
        time_taken = (curr_time - start_time) - prev_time
        if time_taken < 0:
            time_taken = 0
        prev_time = time_taken
                
    return best_final, best_stats



