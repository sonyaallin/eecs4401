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
    # 
    # First Attempt: Distances as sum of manhattandistance(boxes, storages) + manhattandistance(boxes, robots)
    # instead of just manhattandistance(boxes, storages) since a box may be close to a goal but there may
    # not be any robots near the box, but it is too time consuming.
    # 
    # Second Attempt: We check if the state is on the right track by checking its validity before doing the regular manhattan distance,
    # i.e. if all boxes can reach the storages since boxes may be stuck on a tile / unreachable, but it is still too time consuming.
    #
    # Third Attempt: Scrap the manhattan distance part from heur_manhattan_distance and replace it with a modified first attempt,
    # where boxes and storages calculations are separate from boxes and robots calculations.
    # 
    # Fourth Attempt: Combine all loops together to minimize repeated calculations and variables and move checking to possible_storages().
    # 
    # Fifth Attempt: Consider nearly objects blocking the path in a weighted A star manner with a calibrated weight constant 2.
    #
    # Sixth Attempt: Consider unreachable storages blocked by other storages but implementation not ideal so commented out.
    total = 0
    for robot in state.robots:
        minimum = []
        for box in state.boxes:

            storages = possible_storages(state, box)
            if box not in storages:
                if not storages:
                    return math.inf # When there are no storages that the box can go to the state is dead

                total += min((manhattan(box, storage) + obstacles(state, box, storage, 2) for storage in storages), default=0)
                minimum.append((manhattan(robot, box) + obstacles(state, robot, box, 2)))
            else:
                if immovable(state, *box):    # Remove box and storage from sets when immovable filled storage
                    state.storage = state.storage.difference(box)
                    state.boxes = state.boxes.difference(box)
                # else:
                #     total += 1    # Incentivize pushing boxes to corners to avoid unreachable storages
        total += min(minimum, default=0)

    return total    # Heuristic is the sum of minimum (distance + obstacle values) for boxes to storages and robots to boxes

def immovable(state, X, Y):
    '''
    Return True iff coordinate object is immovable.
    '''
    B = state.height - 1
    R = state.width - 1
    T = L = 0

    # Check if object is cornered on the map corners
    if (X == L and (Y == T or Y == B) or    # left corners
        X == R and (Y == T or Y == B)):     # right corners
        return True

    # Define Directional Coordinates
    LMOVE = X - 1, Y
    RMOVE = X + 1, Y
    UMOVE = X, Y - 1
    DMOVE = X, Y + 1

    # Check if object is cornered by two obstacles
    OBSTACLES = state.obstacles
    if (UMOVE in OBSTACLES and (LMOVE in OBSTACLES or RMOVE in OBSTACLES) or    # top corner
        DMOVE in OBSTACLES and (LMOVE in OBSTACLES or RMOVE in OBSTACLES)):     # bottom corner
        return True
    
    # Check if object is cornered by a wall and an obstacle / box
    BLOCK = OBSTACLES.union(state.boxes)
    if (X == L and (UMOVE in BLOCK or DMOVE in BLOCK) or    # left wall
        X == R and (UMOVE in BLOCK or DMOVE in BLOCK) or    # right wall
        Y == T and (LMOVE in BLOCK or RMOVE in BLOCK) or    # top wall
        Y == B and (LMOVE in BLOCK or RMOVE in BLOCK)):     # bottom wall
        return True
    
    return False

def possible_storages(state, box):
    '''
    Return list of itself if box is already in a storage otherwise all unfilled storages that are reacheable by the box.
    '''
    if box in state.storage:
        return [box]

    # Define X Y and Top Bottom Left Right Coordinates
    X, Y = box
    B = state.height - 1
    R = state.width - 1
    T = L = 0

    storages = state.storage.difference(state.boxes)    # Empty Storages

    # Check if box is stuck outside a storage
    if immovable(state, X, Y):
        return []

    # Check if box is cornered by a side with no empty storages
    X_COORDS, Y_COORDS = zip(*storages)
    if (X == L and L not in X_COORDS or     # left side
        X == R and R not in X_COORDS or     # right side
        Y == T and T not in Y_COORDS or     # top side
        Y == B and B not in Y_COORDS):      # bottom side
        return []

    if X == L:
        return [storage for storage in storages if storage[0] == L]    # Only Left Side Storages
    if X == R:
        return [storage for storage in storages if storage[0] == R]    # Only Right Side Storages
    if Y == T:
        return [storage for storage in storages if storage[1] == T]    # Only Top Side Storages
    if Y == B:
        return [storage for storage in storages if storage[1] == B]    # Only Bottom Side Storages
    
    return storages

def obstacles(state, a, b, weight):
    '''
    Return number of objects in range of rectangle made by a to b coordinates * weight.
    '''
    OBSTACLES = state.obstacles.union(frozenset(state.robots))

    L = min(a[0], b[0])     # Leftmost Coordinate
    R = max(a[0], b[0])     # Rightmost Coordinate
    T = min(a[1], b[1])     # Topmost Coordinate
    B = max(a[1], b[1])     # Bottommost Coordinate

    return sum(obstacle[0] in range(L + 1, R) and obstacle[1] in range(T + 1, B) for obstacle in OBSTACLES) * weight

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
    return sum(min((manhattan(box, storage) for storage in state.storage), default=0) for box in state.boxes)

def manhattan(a, b):
    '''
    Return manhattan distance between two objects a and b.
    '''
    return abs(a[0] - b[0]) + abs(a[1] - b[1])

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
    engine = SearchEngine('custom', 'full')
    engine.init_search(initial_state, sokoban_goal_state, heur_fn, (lambda sN : fval_function(sN, weight)))
    return engine.search(timebound=timebound)

def iterative_astar(initial_state, heur_fn, weight=1, timebound=5):  # uses f(n), see how autograder initializes a search line 88
    # IMPLEMENT
    '''Provides an implementation of realtime a-star, as described in the HW1 handout'''
    '''INPUT: a sokoban state that represents the start state and a timebound (number of seconds)'''
    '''OUTPUT: A goal state (if a goal is found), else False as well as a SearchStats object'''
    '''implementation of iterative astar algorithm'''
    end_time = os.times()[0] + timebound
    goal, stats = False, None

    engine = SearchEngine('custom', 'full')
    
    costbound = math.inf
    timebound = end_time - os.times()[0]
    while timebound > 0:    # Try to find more optimal state within timebound with a decaying weight and cost bound
        
        engine.init_search(initial_state, sokoban_goal_state, heur_fn, (lambda sN : fval_function(sN, weight)))
        state, searchstats = engine.search(timebound, (math.inf, math.inf, costbound))
        timebound -= searchstats.total_time
        
        if state:    # Update variables with new optimal path
            costbound = state.gval + weight * heur_fn(state)
            goal = state
            stats = searchstats
            weight /= 2
        else:
            break

    return goal, stats

def iterative_gbfs(initial_state, heur_fn, timebound=5):  # only use h(n)
    # IMPLEMENT
    '''Provides an implementation of anytime greedy best-first search, as described in the HW1 handout'''
    '''INPUT: a sokoban state that represents the start state and a timebound (number of seconds)'''
    '''OUTPUT: A goal state (if a goal is found), else False'''
    '''implementation of iterative gbfs algorithm'''
    end_time = os.times()[0] + timebound
    goal, stats = False, None

    engine = SearchEngine('best_first')
    engine.init_search(initial_state, sokoban_goal_state, heur_fn)
    
    costbound = math.inf
    timebound = end_time - os.times()[0]
    while timebound > 0:    # Try to find more optimal state within timebound based on the g(node) value
        
        state, searchstats = engine.search(timebound, (costbound, math.inf, math.inf))
        timebound -= searchstats.total_time
        
        if state:    # Update variables with new optimal path
            costbound = state.gval - 1
            goal = state
            stats = searchstats
        else:
            break

    return goal, stats