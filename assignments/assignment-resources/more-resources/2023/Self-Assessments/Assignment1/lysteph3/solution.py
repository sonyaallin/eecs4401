#   Look for #IMPLEMENT tags in this file. These tags indicate what has
#   to be implemented to complete the warehouse domain.

#   You may add only standard python imports
#   You may not remove any imports.
#   You may not import or otherwise source any of your own files

import os  # for time functions
import math  # for infinity
from search import *  # for search engines
from sokoban import sokoban_goal_state, SokobanState, Direction, PROBLEMS  # for Sokoban specific classes and problems
    
# Attempts to skip hashing to retreive previous state
previous_state = None 
previous_heuristic = None 

hashed_states = {} # Previous states that have been precalculated, used for the heur-alternative

# DEADLOCK DETECTION
def deadlock(state, boxes):
    '''Detects if the state is deadlocked by a wall'''
    '''INPUT: a sokoban state'''
    '''OUTPUT: True or False'''

    for b in boxes:

        #Checks for obstacles in the given positions        
        up = (b[1] == 0) or (b[0], b[1] + 1) in state.obstacles 
        right = (b[0] == state.width - 1) or (b[0] + 1, b[1]) in state.obstacles 
        left = (b[0] == 0) or (b[0] - 1, b[1]) in state.obstacles 
        down = (b[1] == state.height - 1) or (b[0], b[1] - 1) in state.obstacles

        if (up or down) and (left or right):
            return True

        for s in state.storage:
            if (b[0] == (state.width - 1) != s[0]) or (b[0] == 0 != s[0]):
                return True
            if (b[1] == (state.height - 1) != s[1]) or (b[1] == 0 != s[1]):
                return True
                
    return False

# SOKOBAN HEURISTICS
def heur_alternate(state):
    '''a better heuristic'''
    '''INPUT: a sokoban state'''
    '''OUTPUT: a numeric value that serves as an estimate of the distance of the state to the goal.'''
    # heur_manhattan_distance has flaws.
    # Write a heuristic function that improves upon heur_manhattan_distance to estimate distance between the current state and the goal.
    # Your function should return a numeric value for the estimate of the distance to the goal.
    # EXPLAIN YOUR HEURISTIC IN THE COMMENTS. Please leave this function (and your explanation) at the top of your solution file, to facilitate marking.

    #My Heuristic Function attempts to improve on just the taxi distance of the boxes and the storages by implementing measures to detect whether there
    #are deadlocks (states that the game cannot move any further from), obstacles nearby, and the distance between robots and each box to try to guess whether
    #There is a more optimal solution given a closer robot to a given box. In addition, previous states are hashed using the built-in hash function from the
    #starter code, and placed in a dictionary. Though this is very memory inefficient, we see a large increase in overall-solving speed.

    #Variables for caching previous states
    global hashed_states
    global previous_state
    global previous_heuristic
   
    #Attempts to reduce the amount of hashing required... if cached, skip everything.
    if state == previous_state:
        return previous_heuristic
    
    #Attempt to reduce the number of caluclates needed in nested loops by checking which boxes reached goal state
    remaining = [x for x in state.boxes if x not in state.storage]
    remaining_storage = [x for x in state.storage if x not in state.boxes]
    
    #Check if the state is hashed, then return the corresponding heuristic
    if state.hashable_state() in hashed_states:
        return hashed_states[state.hashable_state()]
    else: #Checks for deadlock
        if deadlock(state, remaining):
            hashed_states.update({state.hashable_state(): math.inf})
            previous_heuristic = math.inf
            previous_state = state
            return math.inf
        else: #Calculate distances between robots, boxes, and storage, adds costs for nearby obstacles
            total = 0
            
            for b in remaining:
                
                minimum = math.inf
                
                for s in remaining_storage:
                    minimum = min(abs(b[0] - s[0]) + abs(b[1] - s[1]), minimum)
                
                total += minimum + ((b[0], b[1] + 1) in state.obstacles) + ((b[0] + 1, b[1]) in state.obstacles) + \
                    ((b[0] - 1, b[1]) in state.obstacles) +  ((b[0], b[1] - 1) in state.obstacles)
                
                minimum = math.inf
                
                for r in state.robots:
                    minimum = min(abs(b[0] - r[0]) + abs(b[1] - r[1]), minimum)
                
                total += minimum
            
            #Hashing and Caching    
            hashed_states.update({state.hashable_state(): total})
            previous_heuristic = total
            previous_state = state
            
            return total

def heur_zero(state):
    '''Zero Heuristic can be used to make A* search perform uniform cost search'''
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
    
    total = 0
    for b in state.boxes:
        minimum = math.inf
        for s in state.storage:
            current = abs(b[0] - s[0]) + abs(b[1] - s[1])
            if minimum > current:
                minimum = current
        total += minimum
                    
    return total

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
    '''Provides an implementation of weighted a-star, as described in the HW1 handout'''
    '''INPUT: a sokoban state that represents the start state and a timebound (number of seconds)'''
    '''OUTPUT: A goal state (if a goal is found), else False as well as a SearchStats object'''
    '''implementation of weighted astar algorithm'''
    
    wrapped_fval_function = (lambda sN : fval_function(sN,weight)) 
    weight_search = SearchEngine('custom')
    weight_search.init_search(initial_state, sokoban_goal_state, heur_fn, wrapped_fval_function)

    result = weight_search.search(timebound)
    return result 

def iterative_astar(initial_state, heur_fn, weight=1, timebound=5):  # uses f(n), see how autograder initializes a search line 88
    '''Provides an implementation of realtime a-star, as described in the HW1 handout'''
    '''INPUT: a sokoban state that represents the start state and a timebound (number of seconds)'''
    '''OUTPUT: A goal state (if a goal is found), else False as well as a SearchStats object'''
    '''implementation of iterative astar algorithm'''
    
    optimal_solution = False
    
    #Guarantees that it always fit within time
    timebound -= 0.15
    
    time = os.times()[0]
    costbound = (math.inf, math.inf, math.inf)
    
    wrapped_fval_function = (lambda sN : fval_function(sN,weight)) 
    weight_search = SearchEngine('custom')
    weight_search.init_search(initial_state, sokoban_goal_state, heur_fn, wrapped_fval_function)
    solution = weight_search.search(timebound, costbound)
    
    time_taken = os.times()[0] - time
    timebound -= time_taken
    time = os.times()[0]
    
    if (solution[0] == False):
        return solution
 
    optimal_solution = solution

    #Otherwise there is remaining time to do iterative search   
    while (0 < timebound):
        if solution[0] != False:
            if solution[0].gval < costbound[0]: #Compare the costbound with the current solution cost
                optimal_solution = solution
                costbound = (solution[0].gval, solution[0].gval, solution[0].gval)
        
        weight /= 5
        weight_search.init_search(initial_state, sokoban_goal_state, heur_fn, wrapped_fval_function)
        solution = weight_search.search(timebound, costbound)
        
        #Update time bound
        time_taken = os.times()[0] - time
        timebound -= time_taken
        time = os.times()[0]

    return optimal_solution

def iterative_gbfs(initial_state, heur_fn, timebound=5):  # only use h(n)
    '''Provides an implementation of anytime greedy best-first search, as described in the HW1 handout'''
    '''INPUT: a sokoban state that represents the start state and a timebound (number of seconds)'''
    '''OUTPUT: A goal state (if a goal is found), else False'''
    '''implementation of iterative gbfs algorithm'''
    
    optimal_solution = False
    
    #Guarantees that it always fit within time
    timebound -= 0.1
    
    time = os.times()[0]
    costbound = (math.inf, math.inf, math.inf)
    weight_search = SearchEngine('best_first')
    weight_search.init_search(initial_state, sokoban_goal_state, heur_fn)
    solution = weight_search.search(timebound, costbound)

    if (solution[0] == False):
        return solution

    time_taken = os.times()[0] - time
    timebound -= time_taken
    time = os.times()[0]

    optimal_solution = solution
    
    while (0 < timebound):
        
        if solution[0] != False:
            if solution[0].gval < costbound[0]: 
                optimal_solution = solution
                costbound = (solution[0].gval, solution[0].gval, solution[0].gval)

        solution = weight_search.search(timebound, costbound)

        #Update time bound    
        time_taken = os.times()[0] - time
        timebound -= time_taken
        time = os.times()[0]
        
    return optimal_solution




