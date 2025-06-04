#   Look for #IMPLEMENT tags in this file. These tags indicate what has
#   to be implemented to complete the warehouse domain.

#   You may add only standard python imports
#   You may not remove any imports.
#   You may not import or otherwise source any of your own files

import os  # for time functions
import math # for infinity
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
    # Method1: This heuristic pairs each box to the closest storage, such that it minimizes the total distance that has to be transvered. Number of cases passed with 2 seconds: 6
    # Method2: This heuristics pairs each box to the closest robot, updates the robot positions, then pairs the robots to the closest storage positions while checking for corners + edges
    # 9 solved from current version

    boxes = list(state.boxes)
    stores = list(state.storage)
    robots = list(state.robots)
    tot_dis = 0
    chosen_store = []


    if sokoban_goal_state(state): # if boxes are already in goal state, heuristic is 0
        return 0

    for box in boxes:   
        if checkcorner(box[0], box[1], state) and box not in stores:
            return math.inf # cannot be solved
        elif box in stores:
            boxes.remove(box) #remove box from boxes
            stores.remove(box) #remove store from storages
        if checkobstacles(box, state.obstacles):
            tot_dis += 2 

    for box in boxes:
        min_dis, min_dis_r, chosen_store, chosen_robot = math.inf, math.inf, None, None
        if atedge(box, state): # not movable
            if not checkstoreatedge(box, state, stores):
                return math.inf

        for robot in robots:
            if  manhattan_dis(box[0], box[1], robot[0], robot[1]) < min_dis_r:
                min_dis_r = manhattan_dis(box[0], box[1], robot[0], robot[1])
                chosen_robot = robot
        tot_dis += min_dis_r

        for store in stores:
            if  manhattan_dis(box[0], box[1], store[0], store[1]) < min_dis:
                min_dis = manhattan_dis(box[0], box[1], store[0], store[1])
                chosen_store = store

        stores.remove(chosen_store)        
        tot_dis += min_dis 

    return tot_dis





def manhattan_dis(x, y, a, b):
    # calculates the manhattan distance for object at position (x,y) and object at position (a,b)
    return abs(x - a) + abs(y - b)

def checkstoreatedge(box, state, stores):
    for store in stores:
        if (box[0] == 0 and store[0] == 0) or ((box[1] == 0 and store[1] == 0)) or (box[0] == state.width - 1 and store[0] == state.width - 1) or (box[1] == state.height - 1 and store[1] == state.height - 1):
            return True
    return False

def checkobstacles(positions, obstacle):
    if ((positions[0] + 1, positions[1]) in obstacle) or ((positions[0] - 1, positions[1]) in obstacle) or ((positions[0], positions[1] - 1) in obstacle) or ((positions[0], positions[1] + 1) in obstacle):
        return True # if obstacles are below, above, left or right to a box at location positions

def atedge(box, state):
    return box[0] == 0 or (box[0] == state.width - 1) or box[1] == 0 or (box[1]== state.height)

def checkcorner(x, y, state):
    # checks if a box is in corner at an obstacle or at the board, a box in a corner cannot be moved
    # Parameters: x and y are the positions of a box, state denotes the sokuban state
    obs_and_board_corner_x = (x == 0 and (0, y - 1) in state.obstacles) or (x == 0 and (x, y + 1) in state.obstacles) or (x + 1 == state.width and (x, y - 1) in state.obstacles) or  (x+1 == state.width and (x, y + 1) in state.obstacles)
    obstacle_corner = ((x-1, y) in state.obstacles and (x, y - 1) in state.obstacles) or ((x+1, y) in state.obstacles and (x, y - 1) in state.obstacles) or ((x, y + 1) in state.obstacles and (x + 1, y) in state.obstacles) or ((x - 1, y) in state.obstacles and (x, y + 1) in state.obstacles)
    board_corner = (x == 0 and y == 0) or (x == 0 and y == state.height - 1) or (x == state.width - 1 and y == 0) or (x == state.width -1 and y == state.height - 1)
    return obstacle_corner or board_corner or obs_and_board_corner_x    


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
    boxes = state.boxes
    storage = state.storage
    tot_dis = 0
    for box in boxes:
        min_dis = math.inf
        for store in storage:
            min_dis = min(min_dis, manhattan_dis(box[0], box[1], store[0], store[1]))
        tot_dis += min_dis
    return tot_dis  

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

    a_search = SearchEngine("custom")
    wrapped_fval_function = (lambda sN : fval_function(sN, weight)) 
    a_search.init_search(initial_state, sokoban_goal_state, heur_fn, wrapped_fval_function)
    return a_search.search(timebound)


def iterative_astar(initial_state, heur_fn, weight=1, timebound=5):  # uses f(n), see how autograder initializes a search line 88
    # IMPLEMENT
    '''Provides an implementation of realtime a-star, as described in the HW1 handout'''
    '''INPUT: a sokoban state that represents the start state and a timebound (number of seconds)'''
    '''OUTPUT: A goal state (if a goal is found), else False as well as a SearchStats object'''
    '''implementation of iterative astar algorithm'''

    def weighted_astar_cost(initial_state, heur_fn, weight=1, timebound=5, costbound=None):
            # weighted astar that accounts for cost as well
            a_search = SearchEngine("custom")
            wrapped_fval_function = (lambda sN : fval_function(sN, weight)) 
            a_search.init_search(initial_state, sokoban_goal_state, heur_fn, wrapped_fval_function)
            return a_search.search(timebound, costbound)

    best_state, best_stat = (initial_state, SearchEngine('custom').initStats())
    costbound = None

    while timebound > 0:

        goal_state, stat = weighted_astar_cost(initial_state, heur_fn, weight, timebound, costbound)
        if costbound is None:
            costbound = (math.inf, math.inf, math.inf)
        if goal_state == False:
            break
        gval, hval = goal_state.gval, heur_fn(goal_state)
        if (gval + hval) < costbound[2]:
            best_state, best_stat = goal_state, stat
            costbound = (math.inf, math.inf, gval + hval)
        weight -= 1
        timebound -= stat.total_time 

    return best_state, best_stat


def iterative_gbfs(initial_state, heur_fn, timebound=5):  # only use h(n)
    # IMPLEMENT
    '''Provides an implementation of anytime greedy best-first search, as described in the HW1 handout'''
    '''INPUT: a sokoban state that represents the start state and a timebound (number of seconds)'''
    '''OUTPUT: A goal state (if a goal is found), else False'''
    '''implementation of iterative gbfs algorithm'''

    def gbfs(initial_state, heur_fn, timebound=5, costbound=None):
        a_search = SearchEngine("best_first")
        a_search.init_search(initial_state, sokoban_goal_state, heur_fn)
        return a_search.search(timebound, costbound)

    best_state, best_stat = (initial_state, SearchEngine('best_first').initStats())
    costbound = None

    while timebound > 0:
        goal_state, stat = gbfs(initial_state, heur_fn, timebound, costbound)
        if costbound is None:
            costbound = (math.inf, math.inf, math.inf)
        if goal_state == False:
            break
        if (goal_state.gval) < costbound[0]:
            best_state, best_stat = goal_state, stat
            costbound = (goal_state.gval, math.inf, math.inf)

        timebound -= stat.total_time 

    return best_state, best_stat