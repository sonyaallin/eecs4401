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
    
    # This improved version of heur_manhattan_distance first check all the boxes that yet to be stored, 
    # whether or not they are stuck (cannot move forever). For example, box lies in the corner or box 
    # has obstacles arnound it... In this case, we need to return infinity. Otherwise, we implement the 
    # minimum sum of manhattan distances between pairs and return it.
    
    distance = 0    # It stores the total heuristic value.
    corners = frozenset(((0, 0), (state.width-1, 0), (0, state.height-1), (state.width-1, state.height-1)))    # It stores corner locations of the board.
    obstacles = state.obstacles.union(state.boxes)      # Obstacles union boxes.
    for box in state.boxes:
        if box not in state.storage:    
            if box in corners:      # A box lies in corner, which means stuck
                return math.inf
            if box[0] == 0:     # Box that lies on the left edge (not include corners).
                if (0, box[1]-1) in obstacles or (0, box[1]+1) in obstacles:    
                    return math.inf                                           
                
            if box[0] == state.width-1:    # Box that lies on the right edge (not include corners).
                if (state.width-1, box[1]-1) in obstacles or (state.width-1, box[1]+1) in obstacles:    
                    return math.inf                                          
            if box[1] == 0:    # Box that lies on the bottom edge (not include corners).
                if (box[0]-1, 0) in obstacles or (box[0]+1, 0) in obstacles:    
                    return math.inf                                             
            if box[1] == state.height-1:        # Box that lies on the top edge (not include corners).
                if (box[0]-1, state.height-1) in obstacles or (box[0]+1, state.height-1) in obstacles:
                    return math.inf                                           
              
            # Box that has obstacles around it.
            if (((box[0]-1, box[1]) in state.obstacles) and ((box[0], box[1]+1) in state.obstacles)) or \
                (((box[0]-1, box[1]) in state.obstacles) and ((box[0], box[1]-1) in state.obstacles)) or \
                (((box[0]+1, box[1]) in state.obstacles) and ((box[0], box[1]+1) in state.obstacles)) or \
                (((box[0]+1, box[1]) in state.obstacles) and ((box[0], box[1]-1) in state.obstacles)):
                    return math.inf
            if (((box[0]-1, box[1]) in obstacles) and ((box[0]-1, box[1]+1) in obstacles) and ((box[0], box[1]+1) in obstacles)) or \
                (((box[0]-1, box[1]) in obstacles) and ((box[0]-1, box[1]-1) in obstacles) and ((box[0], box[1]-1) in obstacles)) or \
                (((box[0]+1, box[1]) in obstacles) and ((box[0]+1, box[1]+1) in obstacles) and ((box[0], box[1]+1) in obstacles)) or \
                (((box[0]+1, box[1]) in obstacles) and ((box[0]+1, box[1]-1) in obstacles) and ((box[0], box[1]-1) in obstacles)):
                    return math.inf
                
            # Find the minimum sum of manhattan distance between pairs.
            # For each box, first find the closet storage point near it, and calcualte manhatten distance.
            # Amont those distances, find the maximum and corresponding pair, add that value to the result, 
            # and remove that pair from the pair list. After that, repeat process above until there is 
            # no pairs left in the pair.
            distance_table = []
            i = 0
            for box in state.boxes:
                distance_table.append([])
                for storage in state.storage:
                    distance_table[i].append(abs(storage[0]-box[0])+abs(storage[1]-box[1]))         
                i += 1
            while len(distance_table) > 0:     
                min_lst = []
                min_idx = []
                for i in range(len(distance_table)):
                    min_value = min(distance_table[i])
                    min_lst.append(min_value)
                    min_idx.append((i, distance_table[i].index(min_value)))
                max_value = max(min_lst)
                distance += max_value
                idx = min_lst.index(max_value)
                distance_table.pop(min_idx[idx][0])
                for item in distance_table:
                    item.pop(min_idx[idx][1])               
    return distance

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
    distance = 0
    for box in state.boxes:
        if box not in state.storage:
            sub_distance = math.inf
            for location in state.storage:
                if (abs(location[0]-box[0])+abs(location[1]-box[1])) < sub_distance:
                    sub_distance = abs(location[0]-box[0])+abs(location[1]-box[1])
            distance += sub_distance
    return distance

def fval_function(sN, weight):
    # IMPLEMENT
    """
    Provide a custom formula for f-value computation for Anytime Weighted A star.
    Returns the fval of the state contained in the sNode.

    @param sNode sN: A search node (containing a SokobanState)
    @param float weight: Weight given by Anytime Weighted A star
    @rtype: float
    """
    return sN.gval + sN.hval*weight

# SEARCH ALGORITHMS
def weighted_astar(initial_state, heur_fn, weight, timebound):
    # IMPLEMENT    
    '''Provides an implementation of weighted a-star, as described in the HW1 handout'''
    '''INPUT: a sokoban state that represents the start state and a timebound (number of seconds)'''
    '''OUTPUT: A goal state (if a goal is found), else False as well as a SearchStats object'''
    '''implementation of weighted astar algorithm'''
    wrapped_fval_function = (lambda sN : fval_function(sN,weight))
    search_engine = SearchEngine(strategy='custom')
    search_engine.init_search(initial_state, sokoban_goal_state, heur_fn, wrapped_fval_function)
    return search_engine.search(timebound)

def iterative_astar(initial_state, heur_fn, weight=1, timebound=5):  # uses f(n), see how autograder initializes a search line 88
    # IMPLEMENT
    '''Provides an implementation of realtime a-star, as described in the HW1 handout'''
    '''INPUT: a sokoban state that represents the start state and a timebound (number of seconds)'''
    '''OUTPUT: A goal state (if a goal is found), else False as well as a SearchStats object'''
    '''implementation of iterative astar algorithm'''
    wrapped_fval_function = (lambda sN : fval_function(sN,weight))
    search_engine = SearchEngine(strategy='custom')
    search_engine.init_search(initial_state, sokoban_goal_state, heur_fn, wrapped_fval_function)
    costbound = (math.inf, math.inf, math.inf)
    result = False
    time = os.times()[0]
    time_limit = time + timebound
    while time < time_limit:
        goal = search_engine.search(time_limit-time, costbound)
        if goal[0] != False:
            result = goal        
        else:
            if result == False:
                return goal
            else:
                return result
        if weight > 1:
            weight -= 0.1
        costbound = (math.inf, math.inf, goal[0].gval)
        time = os.times()[0]
    return result

def iterative_gbfs(initial_state, heur_fn, timebound=5):  # only use h(n)
    # IMPLEMENT
    '''Provides an implementation of anytime greedy best-first search, as described in the HW1 handout'''
    '''INPUT: a sokoban state that represents the start state and a timebound (number of seconds)'''
    '''OUTPUT: A goal state (if a goal is found), else False'''
    '''implementation of iterative gbfs algorithm'''
    search_engine = SearchEngine(strategy='best_first')
    search_engine.init_search(initial_state, sokoban_goal_state, heur_fn)
    costbound = (math.inf, math.inf, math.inf)
    result = False
    time = os.times()[0]
    time_limit = time + timebound
    while time < time_limit:
        goal = search_engine.search(time_limit-time, costbound)
        if goal[0] != False:
            result = goal        
        else:
            if result == False:
                return goal
            else:
                return result
        
        costbound = (goal[0].gval, math.inf, math.inf)
        time = os.times()[0]
    return result



