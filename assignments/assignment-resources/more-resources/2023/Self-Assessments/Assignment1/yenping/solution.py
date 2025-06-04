#   Look for #IMPLEMENT tags in this file. These tags indicate what has
#   to be implemented to complete the warehouse domain.

#   You may add only standard python imports
#   You may not remove any imports.
#   You may not import or otherwise source any of your own files

import os  # for time functions
import math

from numpy import empty  # for infinity
from search import *  # for search engines
from sokoban import UP, sokoban_goal_state, SokobanState, Direction, PROBLEMS  # for Sokoban specific classes and problems

# Alternate Heuristic Helper Functions
def manhattan(coor1, coor2):
    """
    Return the mahattan distance between the input coordinates
    """
    return abs(coor1[0] - coor2[0]) + abs(coor1[1] - coor2[1])

def num_obstacle(start, goal, state):
    """
    Return the number of obstacles between start and goal
    """
    # Find the bounds of possible obstacle positions
    top = min(start[1], goal[1])
    bottom = max(start[1], goal[1])
    left = min(start[0], goal[0])
    right = max(start[0], goal[0])
        
    count = 0
    for obstacle in state.obstacles:
        if (left < obstacle[0] < right) and (top < obstacle[1] < bottom):
            count += 1
    
    # Robots are also treated as obstacles when moving
    for robot in state.robots:
        if (left < robot[0] < right) and (top < robot[1] <  bottom):
            count += 1
    return count

def edge_no_storage(state):
    """
    Check if a box locate along an edge with no available storage.
    Return True if there exists such box. Otherwise, False
    """
    # Find available storages
    available_x = []
    available_y = []
    for storage in state.storage:
        occupied = False
        for box in state.boxes:
            if box[0] == storage[0] and box[1] == storage[1]:
                occupied = True
                break
        if not occupied:
            available_x.append(storage[0])
            available_y.append(storage[1])
        
    for box in state.boxes:
        if box not in state.storage:
            if (box[0] == 0) and (0 not in available_x):
                return True
            if (box[0] == state.width-1) and (state.width-1 not in available_x):
                return True
            if (box[1] == 0) and (0 not in available_y):
                return True
            if (box[1] == state.height-1) and (state.height-1 not in available_y):
                return True
    return False

def at_corner(state):
    """
    Check whether there exists a box located in a corner
    Corner can be formed by:
    1. Map corners
    2. Map edge and obstacle
    3. Two Obstacles
    4. One obstacle and one box
    Return True if there exists such box. Otherwise, False
    """
    for box in state.boxes:
        if box not in state.storage:
            above = (box[0], box[1]-1)
            below = (box[0], box[1]+1)
            left = (box[0]-1, box[1])
            right = (box[0]+1, box[1])
            # Box locate at map corners
            if box[0] == 0 and box[1] == 0:
                return True
            if box[0] == 0 and box[1] == state.height-1:
                return True
            if box[0] == state.width-1 and box[1] == 0:
                return True
            if box[0] == state.width-1 and box[1] == state.height-1:
                return True
            # Box locate at corners form by edge and obstacle
            if (box[0] == 0) or (box[0] == state.width-1):
                if (above in state.obstacles) or (below in state.obstacles) or (above in state.boxes) or (below in state.boxes):
                    return True
            if (box[1] == 0) or (box[1] == state.height-1):
                if (left in state.obstacles) or (right in state.obstacles) or (left in state.boxes) or (right in state.boxes):
                    return True
            # Box locate at corners form by obstacles
            if (above in state.obstacles) or (below in state.obstacles) or (above in state.boxes) or (below in state.boxes):
                if (left in state.obstacles) or (right in state.obstacles) or (left in state.boxes) or (right in state.boxes):
                    return True
    return False

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

    # Observation
    # 1. Obstacles must be considered in heuristics to best represent the real world.
    # 2. It requires time for robots to move toward boxes.
    # 3. Robot action limitations must be considered. 

    # Improvement I - Incorporate the number of obstacles in the path
    #   Mahattan distance is the optimal distance between start and goal on a grid system. In other words, when obstacles are considered, 
    #   path that is the closest to any of the possible Mahattan paths is the optimal path. To get over an obstacle, one should make 
    #   one move to move away, and another one move to mave back, in order to stick to the ideal path. Therefore, to obtain an optimal
    #   path obstacles considered, we should consider the number of obstacles one might encounter. 
    # 
    # Improvement II - Compute heuristic values for robot-box and box-storage
    #   Robots are the ones moving the boxes, and it also requires time for robots to reach boxes. Therefore, the final heuristic
    #   values should involve both box-to-storage and robot-to-box heuristic values.
    # 
    # Improvement III - Consider Robot action availability
    #   As mentioned in the handout, robots are only able to push a box. Therefore, if any of the following scenarios occurs, it is impossible
    #   to obtain a solution. Hence, the heuristic value for such scenario should be set to infinity
    #   (1) A box is located along an edge of the map, and there is storage point along that edge. 
    #   (2) A box is located at a corner formed by obstacles, walls, edges, another box, or any two.
    #   (3) A box is located at the corner of the map.
    #   The only action to solve the above scenarios is the pull the box, but robots are unable to perform that, and thus such scenarios
    #   are unsolvable, and the heuristic values are set to infinity.

    # Heuristic Computation
    #   1. Check whether the state is solvable or not. If unsolvable, return infinity. If solvable, perform the following steps.
    #   2. For every robot, compute the mahattan distance (M) to the closest box. Then compute the number of obstacles (N) between the robot and the box.
    #      Lastly, compute the heuristic value: H = M + 2*N
    #   3. Apply the above computation to all robots and boxes, and sum all heuristic values up to obtain the final heuristic value.
    
    if at_corner(state) or edge_no_storage(state):
        return math.inf

    result = 0;
    
    # Robot-box heuristic
    for robot in state.robots:
        shortest = math.inf
        for box in state.boxes:
            hval = manhattan(robot, box) + 2 * num_obstacle(robot, box, state)
            if hval < shortest:
                shortest = hval
        result += shortest

    # Find available storages
    available = []
    for storage in state.storage:
        occupied = False
        for box in state.boxes:
            if box[0] == storage[0] and box[1] == storage[1]:
                occupied = True
                break
        if not occupied:
            available.append(storage)

    # Box-Storage heuristic
    for box in state.boxes:
        if box not in state.storage:
            shortest = math.inf
            for storage in available:
                hval = manhattan(box, storage) + 2 * num_obstacle(box, storage, state)
                if hval < shortest:
                    shortest = hval
            result += shortest
    return result

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
    total = 0
    for box in state.boxes:
        if box not in state.storage:
            min = math.inf
            for storage in state.storage:
                curr = abs(box[0] - storage[0]) + abs(box[1] - storage[1])
                if curr < min:
                    min = curr
            total = total + min
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
    # IMPLEMENT    
    '''Provides an implementation of weighted a-star, as described in the HW1 handout'''
    '''INPUT: a sokoban state that represents the start state and a timebound (number of seconds)'''
    '''OUTPUT: A goal state (if a goal is found), else False as well as a SearchStats object'''
    '''implementation of weighted astar algorithm'''    
    # Wrap f-value function and goal function
    fval_func = (lambda sN: fval_function(sN, weight))
    goal_func = (lambda state: sokoban_goal_state(state))

    # Initiate custom SearchEngine 
    engine = SearchEngine(strategy='custom', cc_level='full')
    engine.init_search(initial_state, goal_func, heur_fn, fval_func)
    return engine.search(timebound=timebound)

def iterative_astar(initial_state, heur_fn, weight=1, timebound=5):  # uses f(n), see how autograder initializes a search line 88
    # IMPLEMENT
    '''Provides an implementation of realtime a-star, as described in the HW1 handout'''
    '''INPUT: a sokoban state that represents the start state and a timebound (number of seconds)'''
    '''OUTPUT: A goal state (if a goal is found), else False as well as a SearchStats object'''
    '''implementation of iterative astar algorithm'''
    # Wrap f-value function and goal function
    fval_func = (lambda sN: fval_function(sN, weight))
    goal_func = (lambda state: sokoban_goal_state(state))

    # Initiate custom SearchEngine 
    engine = SearchEngine(strategy='custom', cc_level='full')
    engine.init_search(initial_state, goal_func, heur_fn, fval_func)

    result_state, resultStat = False, None
    optimal_f = math.inf
    remaining = timebound
    while remaining > 0:
        goal, stat = engine.search(remaining, (math.inf, math.inf, optimal_f))
        remaining -= stat.total_time
        if goal:
            result_state = goal
            resultStat = stat
            optimal_f = goal.gval + weight * heur_fn(goal)
            weight *= 0.8
        else:
            break
    return result_state, resultStat

        

def iterative_gbfs(initial_state, heur_fn, timebound=5):  # only use h(n)
    # IMPLEMENT
    '''Provides an implementation of anytime greedy best-first search, as described in the HW1 handout'''
    '''INPUT: a sokoban state that represents the start state and a timebound (number of seconds)'''
    '''OUTPUT: A goal state (if a goal is found), else False'''
    '''implementation of iterative gbfs algorithm'''
    goal_func = (lambda state: sokoban_goal_state(state))

    engine = SearchEngine(strategy='best_first', cc_level='full')
    engine.init_search(initial_state, goal_func, heur_fn)

    result_state, resultStat = False, None
    optimal_g = math.inf
    remaining = timebound
    while remaining > 0:
        goal, stat = engine.search(remaining, (optimal_g, math.inf, math.inf))
        remaining -= stat.total_time
        if goal:
            result_state = goal
            resultStat = stat
            optimal_g = goal.gval
        else:
            break
    return result_state, resultStat



