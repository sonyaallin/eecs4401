#   Look for #IMPLEMENT tags in this file. These tags indicate what has
#   to be implemented to complete the Rush Hour domain.

#   You may add only standard python imports (numpy, itertools are both ok).
#   You may not remove any imports.
#   You may not import or otherwise source any of your own files.

import math # for infinity
from search import *  # for search engines
from rushhour import *

# RUSH HOUR GOAL TEST
def rushhour_goal_fn(state): 
    '''a Rush Hour Goal Test'''
    '''INPUT: a parking state'''
    '''OUTPUT: True, if satisfies the goal, else false.'''
    
    (rows, cols), goal_entrance, goal_direction = state.get_board_properties()
    
    # iterate through the vehicle list to find goal vehicle(s)
    goal_vs = [(status[1], status[2], status[3]) for status in state.get_vehicle_statuses() \
               if status[4] == True]
    
    for loc, length, is_horizontal in goal_vs:
        if (goal_direction == 'N' and loc == goal_entrance) or \
            (goal_direction == 'W' and loc == goal_entrance):
            return True            
        if goal_direction == 'E' and loc == ((goal_entrance[0] - length + 1) % cols,
                                                goal_entrance[1]):
            return True
        if goal_direction == 'S' and loc == (goal_entrance[0], 
                                                (goal_entrance[1] - length + 1) % rows):
            return True

    return False



# ### Helper functions for computing moves
moves_1 = lambda a, b, c: a - b if b < a else c - b + a
moves_2 = lambda a, b, c: c - a + b if b < a else b - a

def moves_left(loc, target, length, board_dims):
    """Return the number of moves required to place the front of the car on target
       by moving left.
       Precondition: Car satisfies is_horziontal
    """
    rows, cols = board_dims
    return moves_1(loc[0], target[0], cols)


def moves_right(loc, target, length, board_dims):
    """Return the number of moves required to place the back of the car on target
       by moving right.
       Precondition: Car is horizontal
    """
    rows, cols = board_dims
    return moves_2((loc[0] + length - 1) % cols, target[0], cols)


def moves_up(loc, target, length, board_dims):
    """Return the number of moves required to place the front of the car on target
       by moving up.
    """
    rows, cols = board_dims
    return moves_1(loc[1], target[1], rows)


def moves_down(loc, target, length, board_dims):
    """Return the number of moves require to place the back of the car on target by moving down.
    """
    rows, cols = board_dims
    return moves_2((loc[1] + length - 1) % rows, target[1], rows)

BLOCKING = []

# RUSH HOUR HEURISTICS
def heur_alternate(state):
    """
    A better admissible heuristic

    INPUT: a tokyo parking state
    OUTPUT: a numeric value that serves as an estimate of the distance of the state to the goal.

    Explanation: This heuristic computes two values:
    (1) The minimum number of moves for a goal vehicle to reach the goal, respecting goal orientation and assuming 
        unobstructed paths to the goal.
    (2) The minimum number of moves required to remove any single vehicle blocking a path to the goal.
    
    If the next cell in the goal vehicle's path to the goal is blocked, the heuristic returns the sum of (1) and (2), 
    otherwise it returns (1) and does not compute (2)
    """

    (rows, cols), goal_entrance, goal_direction = state.get_board_properties()

    goal_vs = [(status[1], status[2], status[3]) for status in state.get_vehicle_statuses() \
               if status[4] == True]

    min_blocking = 0
    if state.action == "START":
        global BLOCKING
        BLOCKING = get_blocking_vs(state)
        
    elif not state.action[13].isalpha():
        min_blocking = math.inf
        board_dims = (rows, cols)
        for bv in BLOCKING:
            if goal_entrance in ["N", "S"]:
                r_target = ((goal_entrance[0] + bv.length), goal_entrance[1])
                l_target = ((goal_entrance[0] - bv.length), goal_entrance[1])

                blocking = min(moves_left(bv.loc, l_target, bv.length, board_dims),
                                moves_right(((bv.loc[0] + bv.length - 1) % cols, bv.loc[1]), r_target, bv.length, board_dims))
            else:

                u_target = (goal_entrance[0], (goal_entrance[1] + bv.length) % rows)
                d_target = (goal_entrance[0], (goal_entrance[1] - bv.length) % rows)

                blocking = min(moves_up(bv.loc, u_target, bv.length, board_dims),
                               moves_down((bv.loc[0], (bv.loc[1] + bv.length - 1) % rows), d_target, bv.length, board_dims))
            min_blocking = min(min_blocking, blocking)
        
        
    min_dist = math.inf
    for loc, length, is_horizontal in goal_vs:
        if is_horizontal:
    
            end_x = (loc[0] + length  - 1) % cols

            # distance from front to goal
            moves1 = min(abs(loc[0] - goal_entrance[0]),
                        cols - abs(loc[0] - goal_entrance[0]))

            # distance from back to goal
            moves2 = min(abs(end_x - goal_entrance[0]),
                        cols - abs(end_x - goal_entrance[0]))

            if goal_direction == 'W':
                moves2 += (length - 1)
            else:
                moves1 += (length - 1)

        else:

            end_y = (loc[1] + length - 1) % rows
            
            moves1 = min(abs(loc[1] - goal_entrance[1]),
                        rows - abs(loc[1] - goal_entrance[1]))
            moves2 = min(abs(end_y - goal_entrance[1]),
                        rows - abs(end_y - goal_entrance[1]))

            if goal_direction == 'N':
                moves2 += (length - 1)
            else:
                moves1 += (length - 1)

    min_dist = min(min_dist, moves1, moves2)
    
    return min_dist + min_blocking
    
def heur_min_dist(state):
    """
    admissible tokyo parking puzzle heuristic
    INPUT: a tokyo parking state
    OUTPUT: a numeric value that serves as an estimate of the distance of the state to the goal.
    We want an admissible heuristic, which is an optimistic heuristic.
    It must never overestimate the cost to get from the current state to the goal.
    Getting to the goal requires one move for each tile of distance.
    Since the board wraps around, there will be two different directions that lead to a goal.
    NOTE that we want an estimate of the number of moves required from our current state
    1. Proceeding in the first direction, let MOVES1 =
       number of moves required to get to the goal if it were unobstructed and if we ignore the orientation of the goal
    2. Proceeding in the second direction, let MOVES2 =
       number of moves required to get to the goal if it were unobstructed and if we ignore the orientation of the goal

    Our heuristic value is the minimum of MOVES1 and MOVES2 over all goal vehicles.
    You should implement this heuristic function exactly, and you can improve upon it in your heur_alternate
    """

    (rows, cols), goal_entrance = state.get_board_properties()[:2]

    goal_vs = [(status[1], status[2], status[3]) for status in state.get_vehicle_statuses() \
               if status[4] == True]

    min_dist = math.inf
    for loc, length, is_horizontal in goal_vs:

        if is_horizontal:
            end_x = (loc[0] + length  - 1) % cols
            moves1 = min(abs(loc[0] - goal_entrance[0]),
                        cols - abs(loc[0] - goal_entrance[0]))
            moves2 = min(abs(end_x - goal_entrance[0]),
                        cols - abs(end_x - goal_entrance[0]))
        else:

            end_y = (loc[1] + length - 1) % rows
            
            moves1 = min(abs(loc[1] - goal_entrance[1]),
                        rows - abs(loc[1] - goal_entrance[1]))
            moves2 = min(abs(end_y - goal_entrance[1]),
                        rows - abs(end_y - goal_entrance[1]))
        min_dist = min(min_dist, moves1, moves2)

    return min_dist

def heur_zero(state):
    '''Zero Heuristic can be used to make A* search perform uniform cost search'''
    return 0

def fval_function(sN, weight):
    # IMPLEMENT
    """
    Provide a custom formula for f-value computation for Weighted A star.
    Returns the fval of the state contained in the sNode.

    @param sNode sN: A search node (containing a SokobanState)
    @param float weight: Weight given by Weighted A star
    @rtype: float
    """
    return sN.gval +  weight * sN.hval


def fval_function_XUP(sN, weight):
    #IMPLEMENT
    """
    Another custom formula for f-value computation for Weighted A star.
    Returns the fval of the state contained in the sNode.
    XUP causes the best-first search to explore near-optimal paths near the end of a path.

    @param sNode sN: A search node (containing a RushHour State)
    @param float weight: Weight given by Weighted A star
    @rtype: float
    """
    fval_xup = (1 / (2 * weight)) * (sN.gval + sN.hval + math.sqrt(math.pow(sN.gval + sN.hval, 2) + 4 * weight * (weight - 1) * math.pow(sN.hval, 2)))
    return fval_xup

def fval_function_XDP(sN, weight):
    #IMPLEMENT
    """
    A third custom formula for f-value computation for Weighted A star.
    Returns the fval of the state contained in the sNode.
    XDP causes the best-first search to explore near-optimal paths near the start of a path. 

    @param sNode sN: A search node (containing a RushHour State)
    @param float weight: Weight given by Weighted A star
    @rtype: float
    """
    fval_xdp = (1 / (2 * weight)) * (sN.gval + (2 * weight - 1)*sN.hval + math.sqrt(math.pow(sN.gval - sN.hval, 2) + 4 * weight * sN.gval * sN.hval))
    return fval_xdp

# SEARCH ALGORITHMS
def weighted_astar(initial_state, heur_fn, weight, timebound, costbound = (float(math.inf), float(math.inf), float(math.inf))):
    # IMPLEMENT    
    """
    Provides an implementation of weighted a-star, as described in the HW1 handout'''
    INPUT: a rushhour state that represents the start state and a timebound (number of seconds)
    OUTPUT: A goal state (if a goal is found), else False as well as a SearchStats object
    implementation of weighted astar algorithm

    @param initial_state: A RushHour State
    @param heur_fn: The heuristic to use
    @param weight: The weight to use
    @param timebound: The timebound to enforce
    @param costbound: The costbound to enforce, if any
    @rtype: (Rushour State, SearchStats) if solution is found, else (False, SearchStats)
    """

    se = SearchEngine('custom', 'full')
    wrapped_fval_func = lambda sN: fval_function(sN, weight)
    se.init_search(initial_state, rushhour_goal_fn, heur_fn, wrapped_fval_func)
    return se.search(timebound=timebound, costbound=costbound)
    

def iterative_astar(initial_state, heur_fn, weight=1, timebound=5):  # uses f(n), see how autograder initializes a search
    # IMPLEMENT
    """
    Provides an implementation of iterative a-star, as described in the HW1 handout
    INPUT: a rushhour state that represents the start state and a timebound (number of seconds)
    OUTPUT: A goal state (if a goal is found), else False as well as a SearchStats object
    implementation of weighted astar algorithm
    
    @param initial_state: A RushHour State
    @param heur_fn: The heuristic to use
    @param weight: The weight to begin with during the first iteration (this should change)
    @param timebound: The timebound to enforce
    @rtype: (Rushour State, SearchStats) if solution is found, else (False, SearchStats)
    """

    final, stats = False, None
    se = SearchEngine('custom', 'full')
    wrapped_fval_func = lambda sN: fval_function(sN, weight)
    se.init_search(initial_state, rushhour_goal_fn, heur_fn, wrapped_fval_func)
    best_fval = float(math.inf)
    time_remaining = timebound
    while time_remaining > 0:
        solution, ss = se.search(timebound=time_remaining, 
        costbound=(float(math.inf), float(math.inf), best_fval))
        time_remaining -= ss.total_time
        weight = max(1, weight / 2)

        if solution:
            final, stats = solution, ss
            best_fval = final.gval + heur_fn(final)
        else:
            break
    return final, stats

def iterative_gbfs(initial_state, heur_fn, timebound=5):  # only use h(n)
    # IMPLEMENT
    """
    Provides an implementation of anytime greedy best-first search, as described in the HW1 handout
    INPUT: a rush hour state that represents the start state and a timebound (number of seconds)
    OUTPUT: A goal state (if a goal is found), else False

    @param initial_state: A RushHour State
    @param heur_fn: The heuristic to use
    @param timebound: The timebound to enforce
    @rtype: (Rushour State, SearchStats) if solution is found, else (False, SearchStats)
    """
    final, stats = False, None
    se = SearchEngine('best_first', 'full')
    se.init_search(initial_state, rushhour_goal_fn, heur_fn)
    best_gval = float(math.inf)
    time_remaining = timebound
    while time_remaining > 0:
        solution, ss = se.search(timebound=time_remaining, 
        costbound=(best_gval, float(math.inf), float(math.inf)))
        time_remaining -= ss.total_time
        if solution:
            final, stats = solution, ss
            best_gval = final.gval
        else:
            break
    return final, stats

#### HELPER FUNCTIONS ####
def get_blocking_vs(state):
    """Return a list of vehicles which are blocking a path to the goal entrance.
    """
    status_lst = state.get_vehicle_statuses()
    (rows, cols), goal_entrance, goal_direction = state.get_board_properties()

    res = []
    same_row = False
    if goal_direction in ['E', 'W']:
        overlap_coord = goal_entrance[1]
        same_row = True
    else:
        overlap_coord = goal_entrance[0]
        # Check if vehicles in the same column.

    for v in state.vehicle_list:
        loc, length, is_horizontal, is_goal = v.loc, v.length, v.is_horizontal, v.is_goal

        if is_goal:
            continue

        if same_row:
            if is_horizontal and loc[1] == overlap_coord:
                res.append(v)
            if not is_horizontal and overlap_coord in set(map(lambda i: (loc[1] + i) % rows, range(0, length))):
                res.append(v)
        else:
            if is_horizontal and overlap_coord in set(map(lambda i: (loc[0] + i) % cols, range(0, length))):
                res.append(v)
            if not is_horizontal and loc[0] == overlap_coord:
                res.append(v)

    return res
