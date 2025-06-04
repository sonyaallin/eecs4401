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

    # This heuristic calculates the distance from robots to unique boxes,
    # distance from boxes to unique storage, and checks for invalid states.
    # If a state is invalid (like a box is trapped or can't reach a storage)
    # then inf is returned.

    acc = 0
    # CHECK FOR INVALID POSITIONS
    collision = set(state.obstacles)
    for x, y in state.boxes:
        if (x, y) not in state.storage:
            acc += check_wall(x, y, state, collision)

    if acc == float('inf'):
        return acc

    for x, y in state.boxes:
        if (x, y) not in state.storage:
            acc += check_wall2(x, y, state)

    if acc == float('inf'):
        return acc

    for x, y in state.boxes:
        if (x, y) not in state.storage:
            acc += check_wall3(x, y, state, collision)

    if acc == float('inf'):
        return acc

    # FIND MANHATTAN DISTANCE FROM EACH BOX TO CLOSEST UNIQUE STORAGE
    openn = set(state.storage)
    for b in state.boxes:
        curr_mn = float('inf')
        to_del = -1, -1
        for x, y in openn:
            curr = abs(x-b[0]) + abs(y-b[1])
            if curr <= curr_mn:
                to_del = x, y
                curr_mn = curr
        openn.remove(to_del)
        acc += curr_mn

    # FIND MANHATTAN DISTANCE FROM EACH ROBOT TO CLOSEST UNIQUE BOX
    openn = set(state.boxes)
    for r in state.robots:
        curr_mn = float('inf')
        to_del = -1, -1
        for x, y in openn:
            curr = abs(x-r[0]) + abs(y-r[1])
            if curr <= curr_mn:
                to_del = x, y
                curr_mn = curr
        if curr_mn != float('inf'):
            openn.remove(to_del)
            acc += curr_mn

    return acc

def check_wall3(x, y, state, collision):

    # if a square is formed with obstalces/other boxes then invalid state

    if ((x, y+1) in state.boxes or (x, y+1) in collision) and \
            ((x+1, y) in state.boxes or (x+1, y) in collision) \
            and ((x+1, y+1) in state.boxes or (x+1, y+1) in collision):
        return float('inf')

    if ((x, y+1) in state.boxes or (x, y+1) in collision) and \
            ((x-1, y) in state.boxes or (x-1, y) in collision) \
            and ((x-1, y+1) in state.boxes or (x-1, y+1) in collision):
        return float('inf')

    if ((x, y-1) in state.boxes or (x, y-1) in collision) and \
            ((x-1, y) in state.boxes or (x-1, y) in collision) \
            and ((x-1, y-1) in state.boxes or (x-1, y-1) in collision):
        return float('inf')

    if ((x, y-1) in state.boxes or (x, y-1) in collision) and \
            ((x+1, y) in state.boxes or (x+1, y) in collision) \
            and ((x+1, y-1) in state.boxes or (x+1, y-1) in collision):
        return float('inf')

    return 0

def check_wall(x, y, state, collision):

    # CHECK IF BOX IS TRAPPED IN A CORNER BETWEEN WALLS/OBSTACLES
    next = [[(0, 1), (-1, 0)], [(-1, 0), (0, -1)], [(0, -1), (1, 0)], [(1, 0), (0, 1)]]

    # POSSIBLE ADJACENT WALL PIECES
    collision.add((x, -1))
    collision.add((x, state.height))
    collision.add((-1, y))
    collision.add((state.width, y))

    for a, b in next:
        if (x+a[0], y+a[1]) in collision and (x+b[0], y+b[1]) in collision:
            collision.add((x, y))
            return float('inf')
    return 0

def check_wall2(x, y, state):
    # if box is against a top/bot wall
    if (x, 0) == (x, y) or (x, state.height-1) == (x, y):
        # if two boxes are adjacently against a wall
        if (x+1, y) in state.boxes or (x-1, y) in state.boxes:
            return float('inf')

        for s in state.storage:
            # if box is against wall, and theres a non blocked storage
            if s[1] == y and obst_between(x,y,s,state):
                return 0
        return float('inf') # if box against wall and no storage against wall

    # if box is against a left/right wall
    elif (0, y) == (x, y) or (state.width-1, y) == (x, y):
        # if two boxes are adjacently against a wall
        if (x, y+1) in state.boxes or (x, y-1) in state.boxes:
            return float('inf')

        for s in state.storage:
            # if box is against wall, and theres a non blocked storage
            if s[0] == x and s not in state.boxes and obst_between(x,y,s,state):
                return 0
        return float('inf') # if box against wall and no storage against wall

    return 0

def obst_between(x, y, s, state):
    # check if obstacle between storage and box
    if y == s[1]:
        for o in state.obstacles:
            if o[1] == y and s[0] < o[0] < x:
                return False
    elif x == s[0]:
        for o in state.obstacles:
            if o[0] == x and s[1] < o[1] < y:
                return False

    return True

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

    acc = 0
    for box in state.boxes:
        curr_mn = float('inf')
        for storage in state.storage:
            dist = abs(storage[0] - box[0]) + abs(storage[1] - box[1])
            curr_mn = min(dist, curr_mn)
        acc += curr_mn

    return acc

def fval_function(sN, weight):
    # IMPLEMENT
    """
    Provide a custom formula for f-value computation for Anytime Weighted A star.
    Returns the fval of the state contained in the sNode.

    @param sNode sN: A search node (containing a SokobanState)
    @param float weight: Weight given by Anytime Weighted A star
    @rtype: float
    """
    return sN.gval + (weight*sN.hval)

# SEARCH ALGORITHMS
def weighted_astar(initial_state, heur_fn, weight, timebound):
    # IMPLEMENT
    '''Provides an implementation of weighted a-star, as described in the HW1 handout'''
    '''INPUT: a sokoban state that represents the start state and a timebound (number of seconds)'''
    '''OUTPUT: A goal state (if a goal is found), else False as well as a SearchStats object'''
    '''implementation of weighted astar algorithm'''
    e = SearchEngine('custom')
    wrapped_fval_function = (lambda sN : fval_function(sN, weight))
    e.init_search(initial_state, sokoban_goal_state, heur_fn, wrapped_fval_function)

    return e.search(timebound)

def iterative_astar(initial_state, heur_fn, weight=1, timebound=5):  # uses f(n), see how autograder initializes a search line 88
    # IMPLEMENT
    '''Provides an implementation of realtime a-star, as described in the HW1 handout'''
    '''INPUT: a sokoban state that represents the start state and a timebound (number of seconds)'''
    '''OUTPUT: A goal state (if a goal is found), else False as well as a SearchStats object'''
    '''implementation of iterative astar algorithm'''
    weight = 100
    e = SearchEngine('custom', 'full')
    wrapped_fval_function = (lambda sN : fval_function(sN, weight))
    e.init_search(initial_state, sokoban_goal_state, heur_fn, wrapped_fval_function)
    costbound = (float('inf'), float('inf'), float('inf'))
    prev_found, prev_stats = False, SearchStats(0, 0, 0, 0, 0)
    cur_time = timebound
    while cur_time > 0:
        found, stats = e.search(cur_time, costbound)
        if not found:
            if prev_found:
                return prev_found, prev_stats
            else:
                return found, stats
        weight = max(1, weight//40)
        prev_found, prev_stats = found, prev_stats
        wrapped_fval_function = (lambda sN : fval_function(sN, weight))
        e.init_search(initial_state, sokoban_goal_state, heur_fn, wrapped_fval_function)
        hval = heur_fn(found)
        costbound = (float('inf'), float('inf'), hval + found.gval)
        cur_time -= stats.total_time

    return prev_found, prev_stats


def iterative_gbfs(initial_state, heur_fn, timebound=5):  # only use h(n)
    # IMPLEMENT
    '''Provides an implementation of anytime greedy best-first search, as described in the HW1 handout'''
    '''INPUT: a sokoban state that represents the start state and a timebound (number of seconds)'''
    '''OUTPUT: A goal state (if a goal is found), else False'''
    '''implementation of iterative gbfs algorithm'''
    e = SearchEngine('best_first', 'full')
    e.init_search(initial_state, sokoban_goal_state, heur_fn)
    cur_time = timebound
    costbound = (float('inf'), float('inf'), float('inf'))
    prev_found, prev_stats = False, SearchStats(0, 0, 0, 0, 0)
    while cur_time > 0:
        found, stats = e.search(cur_time, costbound)
        if not found:
            if prev_found:
                return prev_found, prev_stats
            else:
                return found, stats

        prev_found, prev_stats = found, prev_stats
        costbound = (found.gval, float('inf'), float('inf'))
        cur_time -= stats.total_time

    return prev_found, prev_stats





