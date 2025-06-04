#   Look for #IMPLEMENT tags in this file. These tags indicate what has
#   to be implemented to complete the warehouse domain.

#   You may add only standard python imports
#   You may not remove any imports.
#   You may not import or otherwise source any of your own files

import os  # for timer functions
import math  # for infinity
from search import *  # for search engines
from sokoban import sokoban_goal_state, SokobanState, Direction, PROBLEMS  # for Sokoban specific classes and problems

# globals for alternate heur
visited_states = {} # visited states
saved_state = None 
saved_state_heur = None 

# SOKOBAN HEURISTICS
def heur_alternate(state):
    # IMPLEMENT
    '''a better heuristic'''
    '''INPUT: a sokoban state'''
    '''OUTPUT: a numeric value that serves as an estimate of the distance of the state to the goal.'''
    # heur_manhattan_distance has flaws.
    # Write a heuristic function that improves upon heur_manhattan_distance to estimate distance between the current state and the goal.
    # Your function should return a numeric value for the estimate of the distance to the goal.
    # EXPLAIN YOUR HEURISTIC IN THE COMMENTS. Please leave this function (and your explanation) at the top of your choice file, to facilitate marking.
    
    # store visited states to prevent unnecessary work
    global visited_states
    global saved_state
    global saved_state_heur
    
    # state encountered same as previous, check
    if saved_state == state:
        return saved_state_heur
    
    # store the hash in a variable,
    key = state.hashable_state()
    
    # visited state, check
    if key in visited_states:
        return visited_states[key]
    
    # boxes already in storage, check
    leftover_storages = []
    for s in state.storage:
        if s not in state.boxes:
            leftover_storages.append(s)
    
    movable_boxes = []
    for b in state.boxes:
        if b not in state.storage:
            movable_boxes.append(b)
    
    # stuck check
    for b in movable_boxes:
        # boundary check for corner b
        up = (b[1] <= 0) or ((b[0], b[1] + 1) in state.obstacles) 
        down = (b[1] >= state.height - 1) or ((b[0], b[1] - 1) in state.obstacles)
        left = (b[0] <= 0) or ((b[0] - 1, b[1]) in state.obstacles)
        right = (b[0] >= state.width - 1) or ((b[0] + 1, b[1]) in state.obstacles)
        
        if (up and left) or (up and right) or (down and right) or (down and left):
            saved_state = state
            saved_state_heur = math.inf
            visited_states[key] = saved_state_heur
            return saved_state_heur
        
        # axis align check
        for s in state.storage:
            if (b[0] == (state.width - 1) and b[0] != s[0]) or (b[0] == 0 and b[0] != s[0]) or \
                    (b[1] == (state.height - 1) and b[1] != s[1]) or (b[1] == 0 and b[1] != s[1]):
                        saved_state = state
                        saved_state_heur = math.inf
                        visited_states[key] = saved_state_heur
                        return saved_state_heur
    
    count = 0
    for b in movable_boxes:
        min_r_count = min_s_count = math.inf
        for r in state.robots:
            min_r_count = min(abs(b[0] - r[0]) + abs(b[1] - r[1]), min_r_count)
        for s in leftover_storages:
            min_s_count = min(abs(b[0] - s[0]) + abs(b[1] - s[1]), min_s_count)

        blocked_edges = ((b[0], b[1] + 1) in state.obstacles) + ((b[0] + 1, b[1]) in state.obstacles) \
            + ((b[0] - 1, b[1]) in state.obstacles) + ((b[0], b[1] - 1) in state.obstacles)
        count += blocked_edges + min_r_count + min_s_count

    saved_state = state
    saved_state_heur = count
    visited_states[key] = saved_state_heur
    return saved_state_heur

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
    
    count = 0
    for box in state.boxes:
        dist = state.height+state.width
        for storage in state.storage:
            dist = min(abs(box[0] - storage[0]) + abs(box[1] - storage[1]), dist)
        count += dist
    return count  # CHANGE THIS

def fval_function(sN, weight):
    # IMPLEMENT
    """
    Provide a custom formula for f-value computation for Anytime Weighted A star.
    Returns the fval of the state contained in the sNode.

    @param sNode sN: A search node (containing a SokobanState)
    @param float weight: Weight given by Anytime Weighted A star
    @rtype: float
    """
    return weight * sN.hval + sN.gval

# SEARCH ALGORITHMS
def weighted_astar(initial_state, heur_fn, weight, timebound):
    # IMPLEMENT    
    '''Provides an implementation of weighted a-star, as described in the HW1 handout'''
    '''INPUT: a sokoban state that represents the start state and a timeleft (number of seconds)'''
    '''OUTPUT: A goal state (if a goal is found), else False as well as a SearchStats object'''
    '''implementation of weighted astar algorithm'''

    wrapped_fval_function = (lambda sN : fval_function(sN,weight)) 
    weighted_search = SearchEngine("custom")
    weighted_search.init_search(initial_state, sokoban_goal_state, heur_fn, wrapped_fval_function)
    ret = weighted_search.search(timebound)
    return ret 

def iterative_astar(initial_state, heur_fn, weight=1, timebound=5):  # uses f(n), see how autograder initializes a search line 88
    # IMPLEMENT
    '''Provides an implementation of realtime a-star, as described in the HW1 handout'''
    '''INPUT: a sokoban state that represents the start state and a timeleft (number of seconds)'''
    '''OUTPUT: A goal state (if a goal is found), else False as well as a SearchStats object'''
    '''implementation of iterative astar algorithm'''
    
    timeleft = timebound
    timer = os.times()[0]

    wrapped_fval_function = (lambda sN : fval_function(sN,weight)) 
    
    weighted_search = SearchEngine('custom')
    weighted_search.init_search(initial_state, sokoban_goal_state, heur_fn, wrapped_fval_function)

    costbound = (math.inf, math.inf, math.inf)
    choice = weighted_search.search(timeleft, costbound)

    timeleft -= os.times()[0] - timer
    timer = os.times()[0]

    # first time false check
    if choice[0] is False:
        return choice

    opt_choice = choice
    # timeleft check
    while timeleft > 0.2:
        if (choice[0] is not False) and (choice[0].gval < costbound[0]):
            # update costbound for improved pruning
            opt_choice = choice
            costbound = (choice[0].gval, choice[0].gval, choice[0].gval)
        
        choice = weighted_search.search(timeleft, costbound)
        weight /= 4 # reduce weight
        weighted_search.init_search(initial_state, sokoban_goal_state, heur_fn, wrapped_fval_function)

        # update timeleft for loop
        timeleft -= os.times()[0] - timer
        timer = os.times()[0]
    return opt_choice

def iterative_gbfs(initial_state, heur_fn, timebound=5):  # only use h(n)
    # IMPLEMENT
    '''Provides an implementation of anytime greedy best-first search, as described in the HW1 handout'''
    '''INPUT: a sokoban state that represents the start state and a timeleft (number of seconds)'''
    '''OUTPUT: A goal state (if a goal is found), else False'''
    '''implementation of iterative gbfs algorithm'''
    
    timeleft = timebound
    timer = os.times()[0]
    
    weighted_search = SearchEngine('best_first')
    weighted_search.init_search(initial_state, sokoban_goal_state, heur_fn)

    costbound = (math.inf, math.inf, math.inf)
    choice = weighted_search.search(timeleft, costbound)

    timeleft -= os.times()[0] - timer
    timer = os.times()[0]

    # first time false check
    if choice[0] is False:
        return choice

    opt_choice = choice
    # timeleft check
    while timeleft > 0.2:
        if (choice[0] is not False) and (choice[0].gval < costbound[0]):
            # update costbound for improved pruning
            opt_choice = choice
            costbound = (choice[0].gval, choice[0].gval, choice[0].gval)
        
        choice = weighted_search.search(timeleft, costbound)

        # update timeleft for loop
        timeleft -= os.times()[0] - timer
        timer = os.times()[0]
    return opt_choice
