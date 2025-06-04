import os  # for time functions
import math  # for infinity
from search import *  # for search engines
from sokoban import sokoban_goal_state, SokobanState, Direction, PROBLEMS  # for Sokoban specific classes and problems

from itertools import permutations 

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
    
    # The alternate heuristic tries to improve on the manhattan distance heuristic, by removing the assumption that 
    # more than one box can go into the same drop off point. I tried to implement more features, like taking
    # into account the distance of the robots to the boxes, or to make the paths more costly if they
    # went trhough an obstacle, but none of these things made a difference, or if they did, it was for the worse.
    
    boxes = state.boxes
    storage_points = list(state.storage)
    robots = list(state.robots)
    
    storage_permutations = permutations(storage_points, len(storage_points))
    
    permutations_and_costs = list()

    for i in list(storage_permutations):
        total_cost = 0
        j=0
        for box in iter(boxes):
            box_to_pass = frozenset((box,))                   
            new_state = SokobanState("START", 0, None, state.width, state.height, state.robots,
                                     box_to_pass,frozenset(((i[j][0],i[j][1]),)), 
                                     state.obstacles)
            total_cost += heur_manhattan_distance(new_state)
            j += 1
        permutations_and_costs.append((i,total_cost))
    
    min_cost = float('inf')
    
    visited_boxes = dict()
    for robot in iter(robots):
        minimum_distance = float('inf')
        minumum_box = None
        for box in iter(boxes):
            distance = abs(box[0]-robot[0])+abs(box[1]-robot[1])-1
            if distance < minimum_distance:
                minimum_distance = distance
                minimum_box = box
        if minimum_box not in visited_boxes.keys() or visited_boxes[minimum_box] > minimum_distance:
            visited_boxes[minimum_box] = minimum_distance

    for perm in permutations_and_costs:
        if perm[1] < min_cost:
            min_cost = perm[1]
    
    return min_cost  # CHANGE THIS

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
    
    total_distance = 0
    
    boxes = list(state.boxes)
    storage_points = list(state.storage)

    for box in boxes:
        closest_point = storage_points[0]
        min_manhatan = abs(box[0]-closest_point[0])+abs(box[1]-closest_point[1])
        for storage_point in storage_points:
            local_manhatan = abs(box[0]-storage_point[0])+abs(box[1]-storage_point[1])
            if local_manhatan < min_manhatan:
                min_manhatan = local_manhatan
        total_distance += min_manhatan
                
    return total_distance

def fval_function(sN, weight):
    # IMPLEMENT
    """
    Provide a custom formula for f-value computation for Anytime Weighted A star.
    Returns the fval of the state contained in the sNode.

    @param sNode sN: A search node (containing a SokobanState)
    @param float weight: Weight given by Anytime Weighted A star
    @rtype: float
    """
    return sN.gval + weight*sN.hval #CHANGE THIS

# SEARCH ALGORITHMS
def weighted_astar(initial_state, heur_fn, weight, timebound):
    # IMPLEMENT    
    '''Provides an implementation of weighted a-star, as described in the HW1 handout'''
    '''INPUT: a sokoban state that represents the start state and a timebound (number of seconds)'''
    '''OUTPUT: A goal state (if a goal is found), else False as well as a SearchStats object'''
    '''implementation of weighted astar algorithm'''
    
    wrapped_fval_function = (lambda sN : fval_function(sN, weight)) 
    
    search_engine = SearchEngine(strategy='custom')
    
    search_engine.init_search(initial_state, sokoban_goal_state, heur_fn, wrapped_fval_function)
    
    complete_path, stats = search_engine.search(timebound)
    
    return complete_path, stats  # CHANGE THIS

def iterative_astar(initial_state, heur_fn, weight=1, timebound=5):  # uses f(n), see how autograder initializes a search line 88
    # IMPLEMENT
    '''Provides an implementation of realtime a-star, as described in the HW1 handout'''
    '''INPUT: a sokoban state that represents the start state and a timebound (number of seconds)'''
    '''OUTPUT: A goal state (if a goal is found), else False as well as a SearchStats object'''
    '''implementation of iterative astar algorithm'''
    
    time_left = timebound
    current_costbound = [float('inf'), float('inf'), float('inf')]
    result_path = None
    result_stats = None
    
    while(weight >= 1 and time_left > 0.0):
        wrapped_fval_function = (lambda sN : fval_function(sN, weight)) 
        search_engine = SearchEngine(strategy='custom')
        search_engine.init_search(initial_state, sokoban_goal_state, heur_fn, wrapped_fval_function)
        complete_path, stats = search_engine.search(timebound=time_left, costbound=current_costbound)
        time_left -= stats.total_time
        if complete_path is not False:
            current_costbound[2] = complete_path.gval
            result_path = complete_path
        if result_stats is None:
            result_stats = stats
        else:
            result_stats.states_expanded += stats.states_expanded
            result_stats.states_generated += stats.states_expanded
            result_stats.states_pruned_cycles += stats.states_pruned_cycles
            result_stats.states_pruned_cost += stats.states_pruned_cost
            result_stats.total_time += stats.total_time
        weight -= 1
    
    return result_path, result_stats #CHANGE THIS

def iterative_gbfs(initial_state, heur_fn, timebound=5):  # only use h(n)
    # IMPLEMENT
    '''Provides an implementation of anytime greedy best-first search, as described in the HW1 handout'''
    '''INPUT: a sokoban state that represents the start state and a timebound (number of seconds)'''
    '''OUTPUT: A goal state (if a goal is found), else False'''
    '''implementation of iterative gbfs algorithm'''
    
    
    time_left = timebound
    current_costbound = [float('inf'), float('inf'), float('inf')]
    result_path = None
    result_stats = None
    
    while time_left >= 0:
        
        search_engine = SearchEngine(strategy='best_first')
        search_engine.init_search(initial_state, sokoban_goal_state, heur_fn)
        complete_path, stats = search_engine.search(timebound=time_left, costbound=current_costbound)
        time_left -= stats.total_time
        if complete_path is not False:
            if complete_path.gval < current_costbound[0]:
                current_costbound[0] = complete_path.gval -1
            result_path = complete_path
        if result_stats is None:
            result_stats = stats
        else:
            result_stats.states_expanded += stats.states_expanded
            result_stats.states_generated += stats.states_expanded
            result_stats.states_pruned_cycles += stats.states_pruned_cycles
            result_stats.states_pruned_cost += stats.states_pruned_cost
            result_stats.total_time += stats.total_time
    
    return result_path, result_stats #CHANGE THIS