#   Look for #IMPLEMENT tags in this file. These tags indicate what has
#   to be implemented to complete the Rush Hour domain.

#   You may add only standard python imports (numpy, itertools are both ok).
#   You may not remove any imports.
#   You may not import or otherwise source any of your own files.

import os  # you will likely want this for timing functions
import math # for infinity
from search import *  # for search engines
from rushhour import *

# The alternative heuristic function loops through all vehicles until it reaches a vehicle marked as a goal vehicle (is_goal=true).
# Like heur_min_dist, it considers two directions but this time it will consider the orientation of the goal on the board.
# If the goal is N or W then get the distance from the front to the goal and for S/E get the distance from the back to the goal.
# Orientations are split into cases and further divided into two cases which are whether the vehicle is ahead or behind the goal on the board.
# Once the front/back has been decided, calculate the number of moves going directly to the goal without wrapping (moves1) and also the number
# of moves with wrapping (moves2). Take the minimum of moves1 and moves2 at the end of the iteration and update the overall minimum if
# needed. Finally, return the minimum number of moves a goal vehicle can make towards a goal on the board.

# I attempted to make the heuristic better by taking into account vehicles that would be blocking the path to a goal by either incrementing
# 1 to the movement count per vehicle on the path or by the number of moves for a blocking vehicle to get out of the way. The results
# in the test cases didn't change and this could have had some performance impacts so I did not keep it in. I just wanted to mention
# what I had considered and tried.

# RUSH HOUR GOAL TEST
def rushhour_goal_fn(state): 
    # IMPLEMENT
    '''a Rush Hour Goal Test'''
    '''INPUT: a parking state'''
    '''OUTPUT: True, if satisfies the goal, else false.'''
    # Get the useful info from the state
    vehicles_list = state.get_vehicle_statuses()
    board_props = state.get_board_properties()
    rows, cols = board_props[0]
    gx, gy = board_props[1]
    g_dir = board_props[2]

    for vehicle in vehicles_list:
        if vehicle[4]: # if the vehicle is_goal=true
            # Check if the vehicle is in the goal
            x, y = vehicle[1]
            vlength = vehicle[2]
            is_horiz = vehicle[3]

            # vertical goals
            if not is_horiz:
                if g_dir == 'N' and gx == x and gy == y: # If front touches the goal
                    return True
                elif g_dir == 'S' and gx == x: # Same column but need to check if back touches the goal
                    # Back of the vehicle needs to touch the goal for S
                    exp_y = (gy - (vlength - 1)) % rows # Where the front of the vehicle should be compared to the goal/back. Mod used for wrapping
                    if exp_y == y:
                        return True
            elif is_horiz: # horizontal goals
                if g_dir == 'W' and gx == x and gy == y: # If front touches the goal
                    return True
                elif g_dir == 'E' and gy == y: # Chec if same row and back touches the goal
                    exp_x = (gx - (vlength - 1)) % cols
                    if exp_x == x:
                        return True
    return False

# RUSH HOUR HEURISTICS
def heur_alternate(state):
    # IMPLEMENT
    '''a better heuristic'''
    '''INPUT: a tokyo parking state'''
    '''OUTPUT: a numeric value that serves as an estimate of the distance of the state to the goal.'''
    # heur_min_moves has obvious flaws.
    # Write a heuristic function that improves upon heur_min_moves to estimate distance between the current state and the goal.
    # Your function should return a numeric value for the estimate of the distance to the goal.
    # EXPLAIN YOUR HEURISTIC IN THE COMMENTS. Please leave this function (and your explanation) at the top of your solution file, to facilitate marking.

    # This heuristic function loops through all vehicles until it reaches a vehicle marked as a goal vehicle (is_goal=true).
    # Like heur_min_dist, it considers two directions but this time it will consider the orientation of the goal on the board.
    # If the goal is N or W then get the distance from the front to the goal and for S/E get the distance from the back to the goal.
    # Orientations are split into cases and further divided into two cases which are whether the vehicle is ahead or behind the goal on the board.
    # Once the front/back has been decided, calculate the number of moves going directly to the goal without wrapping (moves1) and also the number
    # of moves with wrapping (moves2). Take the minimum of moves1 and moves2 at the end of the iteration and update the overall minimum if
    # needed. Finally, return the minimum number of moves a goal vehicle can make towards a goal on the board.

    # I attempted to make the heuristic better by taking into account vehicles that would be blocking the path to a goal by either incrementing
    # 1 to the movement count per vehicle on the path or by the number of moves for a blocking vehicle to get out of the way. The results
    # in the test cases didn't change and this could have had some performance impacts so I did not keep it in. I just wanted to mention
    # what I had considered and tried.

    min_moves = -1

    # Get useful info about the board/vehicles
    vehicles_list = state.get_vehicle_statuses()
    board_props = state.get_board_properties()
    rows, cols = board_props[0]
    gx, gy = board_props[1]
    g_dir = board_props[2]

    for vehicle in vehicles_list:
        if vehicle[4]: # if the vehicle is_goal=true
            x, y = vehicle[1]
            vlength = vehicle[2]
            is_horiz = vehicle[3]

            # An initial value for moves that is higher than the most moves possible before hitting the goal
            moves1 = rows + cols # moves1 will be direct distance without any board wrapping
            moves2 = rows + cols # moves2 will be distance that involved board wrapping

            # Vertical movement - on the same column as the goal
            if not is_horiz and gx == x:
                if g_dir == 'N': # front of vehicle must touch goal
                    if gy <= y: # goal at or above front of vehicle
                        moves1 = y - gy
                        moves2 = (rows - y) + gy # like all moves2, sum of distances to edges from front/back and goal
                    elif gy > y: # goal below front of vehicle
                        moves1 = gy - y
                        moves2 = y + (rows - gy)
                elif g_dir == 'S': # back of vehicle must touch goal
                    back = (y + (vlength - 1)) % rows # Find the back of the vehicle and account for wrapping
                    if gy <= back: # goal at or above back of vehicle
                        moves1 = back - gy
                        moves2 = (rows - back) + gy
                    elif gy > back: # goal below back of vehicle
                        moves1 = gy - back
                        moves2 = back + (rows - gy)
            elif is_horiz and gy == y: # Horizontal movement - on same row as the goal
                if g_dir == 'W': # front of vehicle must touch goal
                    if gx <= x: # goal at or to the left of the front of the vehicle
                        moves1 = x - gx
                        moves2 = (cols - x) + gx
                    elif gx > x: # goal to the right of the front of the vehicle
                        moves1 = gx - x
                        moves2 = x + (cols - gx)
                elif g_dir == 'E': # back of vehicle must touch goal
                    back = (x + (vlength - 1)) % cols # Find the back of the vehicle
                    if gx <= back: # goal at or the right of the back of the vehicle
                        moves1 = back - gx
                        moves2 = (cols - back) + gx
                    elif gx > back: # goal to the left of the back of the vehicle
                        moves1 = gx - back
                        moves2 = back + (cols - gx)

            # Early return as 0 is minimum amount of possible moves you could make
            if moves1 == 0 or moves2 == 0:
                return 0

            # Find min between movement in opposite directions
            rel_min_moves = min(moves1, moves2)
            # Update overall minimum
            if rel_min_moves < min_moves or min_moves == -1:
                min_moves = rel_min_moves

    return min_moves

def heur_min_dist(state):
    #IMPLEMENT
    '''admissible tokyo parking puzzle heuristic'''
    '''INPUT: a tokyo parking state'''
    '''OUTPUT: a numeric value that serves as an estimate of the distance of the state to the goal.'''
    # We want an admissible heuristic, which is an optimistic heuristic.
    # It must never overestimate the cost to get from the current state to the goal.
    # Getting to the goal requires one move for each tile of distance.
    # Since the board wraps around, there will be two different directions that lead to a goal.
    # NOTE that we want an estimate of the number of moves required from our current state
    # 1. Proceeding in the first direction, let MOVES1 =
    #    number of moves required to get to the goal if it were unobstructed and if we ignore the orientation of the goal
    # 2. Proceeding in the second direction, let MOVES2 =
    #    number of moves required to get to the goal if it were unobstructed and if we ignore the orientation of the goal
    #
    # Our heuristic value is the minimum of MOVES1 and MOVES2 over all goal vehicles.
    # You should implement this heuristic function exactly, and you can improve upon it in your heur_alternate
    min_moves = -1

    # Get useful info about board and vehicles
    vehicles_list = state.get_vehicle_statuses()
    board_props = state.get_board_properties()
    rows, cols = board_props[0]
    gx, gy = board_props[1]
    g_dir = board_props[2]

    for vehicle in vehicles_list:
        if vehicle[4]: # is_goal
            x, y = vehicle[1]
            vlength = vehicle[2]
            is_horiz = vehicle[3]

            # Initial more than max moves possible
            moves1 = rows + cols
            moves2 = rows + cols

            # vertical
            if (g_dir == 'N' or g_dir == 'S') and not is_horiz:
                front = y
                back = (y + (vlength-1)) % rows # Find back. Back could wrap to other side of the board
                if gy <= front: # goal above the top of the vehicle
                    moves1 = front - gy # up
                    if back <= gy: # if bottom has been wrapped around
                        moves2 = gy - back
                    else:
                        moves2 = gy + (rows - back)
                else: # goal below the bottom of the vehicle
                    moves1 = front + (rows - gy)
                    moves2 = gy - back

            # horizontal
            if (g_dir == 'W' or g_dir == 'E') and is_horiz:
                left = x
                right = (x + (vlength - 1)) % cols
                if gx <= left:
                    moves1 = left - gx
                    if right <= gx: # if bottom has been wrapped around
                        moves2 = gx - right
                    else:
                        moves2 = gx + (cols - right)
                else:
                    moves1 = left + (cols - gx)
                    moves2 = gx - right

            # Get minimum and update overall minimum if this vehicle has a lower minimum
            rel_min_moves = min(moves1, moves2)
            if rel_min_moves < min_moves or min_moves == -1:
                min_moves = rel_min_moves

    return min_moves

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
    return sN.gval + (weight * sN.hval) # f(node) = g(node) + weight*h(node)

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
    g = sN.gval
    h = sN.hval
    f = (1/(2*weight)) * (g + h + math.sqrt(math.pow(g+h, 2) + 4*weight*(weight-1)*math.pow(h,2)))
    return f

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
    g = sN.gval
    h = sN.hval
    f = (1/(2*weight)) * (g + (2*weight - 1) * h + math.sqrt(math.pow(g-h, 2) + 4*weight*g*h))
    return f

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
    # Set up seach engine and run search with the fval_function
    search_engine = SearchEngine('custom')
    wrapped_fval_function = (lambda sN : fval_function(sN, weight))
    search_engine.init_search(initial_state, rushhour_goal_fn, heur_fn, wrapped_fval_function)
    goal, search_stats = search_engine.search(timebound, costbound)

    return goal, search_stats

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

    goal = False
    search_stats = None
    costbound = None

    # Loop while there is time remaining until time can no longer be bounded
    while timebound >= 0:
        time = os.times()[0]
        new_goal, search_stats = weighted_astar(initial_state, heur_fn, weight, timebound, costbound)
        time = os.times()[0] - time
        timebound = timebound - time

        # Make the weight smaller each iteration
        weight = weight / 2

        # Update the goal if the goal from the search had a better gval
        if new_goal:
            if (not goal) or (goal and goal.gval > new_goal.gval):
                goal = new_goal

        # Update costbound so g+h is bounded by the best gval so far
        if goal:
            costbound = (float(math.inf), float(math.inf), goal.gval)

    return goal, search_stats

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
    goal = False
    search_stats = None
    costbound = None

    # Based on best first search so the best_first option should be used for hval comparisons
    search_engine = SearchEngine('best_first')

    # Loop while time remains
    while timebound > 0:
        search_engine.init_search(initial_state, rushhour_goal_fn, heur_fn)
        time = os.times()[0]
        new_goal, search_stats = search_engine.search(timebound, costbound) # Leave out fval_function since best first compares hval
        time = os.times()[0] - time
        timebound = timebound - time

        # Update the goal if gval returned from search is smaller
        if new_goal:
            if (not goal) or (goal and goal.gval > new_goal.gval):
                goal = new_goal

        # Update costbound to lower gval. First index of triple is for gval
        if goal:
            costbound = (goal.gval, float(math.inf), float(math.inf))

    return goal, search_stats

