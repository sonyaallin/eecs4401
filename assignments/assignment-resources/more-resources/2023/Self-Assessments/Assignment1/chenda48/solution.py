#   Look for #IMPLEMENT tags in this file. These tags indicate what has
#   to be implemented to complete the warehouse domain.

#   You may add only standard python imports
#   You may not remove any imports.
#   You may not import or otherwise source any of your own files

from calendar import c
import os  # for time functions
import math  # for infinity
from search import *  # for search engines
from sokoban import sokoban_goal_state, SokobanState, Direction, PROBLEMS  # for Sokoban specific classes and problems

global is_n
is_n = False

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

    # Explanation:
    # My heuristic looks at storage spaces and matches them to a box until each box is matched to a storage space.
    # The storages are matched in order of distance from a corner, since corner storages are difficult
    # to fill if the surrounding spaces have boxes or obstacles. Additionally, the heuristic checks if the current
    # state is solvable by seeing if any boxes are stuck or cannot get to a storage and if the state is unsolvable
    # then the state gets pushed to the end of the search queue so it does not use up any time.
    # Some additional heuristics I tried to incorporate include:
    # - Removing boxes that are already in a storage from the matching
    # - Matching robots to unstored boxes
    # - Prioritizing robots to be further away from each other
    distance = 0
    if not is_not_stuck(state):
        return math.inf

    mdist, bts = matching(state)
    if mdist == math.inf:
        return math.inf

    distance += mdist

    return distance
    
def is_not_stuck(state):
    for box in state.boxes:
        x = box[0]
        y = box[1]
        if box not in state.storage:
            if x == state.width and y == 0: # top-right
                return False
            elif x == state.width and y == state.height: # bottom-right
                return False
            elif x == 0 and y == 0: # top-left
                return False
            elif x == 0 and y == state.height: # bottom-left
                return False
            elif y == state.height and ((x+1,y) in state.boxes or (x+1,y) in state.obstacles):
                return False
            elif y == 0 and ((x+1,y) in state.boxes or (x+1,y) in state.obstacles):
                return False
            elif y == state.height and ((x-1,y) in state.boxes or (x-1,y) in state.obstacles):
                return False
            elif y == 0 and ((x-1,y) in state.boxes or (x-1,y) in state.obstacles):
                return False
            elif x == 0 and ((x,y+1) in state.boxes or (x,y+1) in state.obstacles):
                return False
            elif x == state.width and ((x,y+1) in state.boxes or (x,y+1) in state.obstacles):
                return False
            elif x == 0 and ((x,y-1) in state.boxes or (x,y-1) in state.obstacles):
                return False
            elif x == state.width and ((x,y-1) in state.boxes or (x,y-1) in state.obstacles):
                return False
            elif ((x-1, y) in state.boxes or (x-1, y) in state.obstacles) and ((x,y+1) in state.boxes or (x,y+1) in state.obstacles) and ((x-1,y+1) in state.boxes or (x-1,y+1) in state.obstacles): 
                return False
            ### $X
            ### $$
            elif ((x+1, y) in state.boxes or (x+1, y) in state.obstacles) and ((x,y+1) in state.boxes or (x,y+1) in state.obstacles) and ((x+1,y+1) in state.boxes or (x+1,y+1) in state.obstacles):
                return False
            ### X$
            ### $$
            elif ((x+1, y) in state.boxes or (x+1, y) in state.obstacles) and ((x,y-1) in state.boxes or (x,y-1) in state.obstacles) and ((x+1,y-1) in state.boxes or (x+1,y-1) in state.obstacles):
                return False
            ### $$
            ### X$
            elif ((x-1, y) in state.boxes or (x-1, y) in state.obstacles) and ((x,y-1) in state.boxes or (x,y-1) in state.obstacles) and ((x-1,y-1) in state.boxes or (x-1,y-1) in state.obstacles):
                return False   
            ### $$
            ### $X 
            else:
                continue

    return True

# def is_adjacent(box, robot):
#     bx = box[0]
#     by = box[1]
#     rx = robot[0]
#     ry = robot[1]

#     if bx == rx and (by == ry - 1 or by == ry + 1):
#         return True
#     elif by == ry and (bx == rx - 1 or bx == rx + 1):
#         return True
#     elif (bx == rx + 1 and by == ry + 1) or (bx == rx + 1 and by == ry - 1) or (bx == rx - 1 and by == ry - 1) or (bx == rx - 1 and by == ry + 1):
#         return True
#     ### r r
#     ###  X 
#     ### r r
#     else:
#         return False

def matching(state):
    distance = 0
    boxes = [b for b in state.boxes]
    storages = [s for s in state.storage]
    bts = {}

    c_s = []
    for storage in storages:
        sx = storage[0]
        sy = storage[1]
        h = state.height
        w = state.width
        c_dist = min(abs(sx - w) + abs(sy - h), abs(sx - 0) + abs(sy-h), abs(sx - 0) + abs(sy-0), abs(sx - w) + abs(sy-0))
        c_s.append((c_dist, storage))
    
    c_s.sort()
    i = 0
    while boxes:
        closest = math.inf
        
        storage = c_s[i]
        sx = storage[1][0]
        sy = storage[1][1]
        matched = False
        for box in boxes:
            bx = box[0]
            by = box[1]

            if bx < sx and bx == 0:
                continue
            elif bx > sx and bx == state.width:
                continue
            elif by < sy and by == 0:
                continue
            elif by > sy and by == state.height:
                continue
            else:
                matched = True
                dist = abs(sx - bx) + abs(sy - by)
                if dist < closest:
                    closest = dist
                    cpair = [storage[1], box]
        
        if not matched:
            return math.inf, {}
        distance += closest
        boxes.remove(cpair[1])
        bts[cpair[1]] = cpair[0]
        i += 1
        
    return distance, bts

def straight_line_dist(box, robot, storage):
    bx = box[0]
    by = box[1]
    rx = robot[0]
    ry = robot[1]
    sx = storage[0]
    sy = storage[1]

    if (sy == by == ry and ((sx < bx and bx < rx) or (rx < bx and bx < sx))):
        return True, abs(rx - bx) + abs(bx - sx)
    elif (sx == bx == rx and ((sy < by and by < ry) or (ry < by and by < sy))):
        return True, abs(ry - by) + abs(by - sy)
    else:
        return False, abs(rx - bx) + abs(ry - by) + abs(bx - sx) + abs(by - sy)

def is_between(box, robot, storage):
    bx = box[0]
    by = box[1]
    rx = robot[0]
    ry = robot[1]
    sx = storage[0]
    sy = storage[1]

    b, straight_dist = straight_line_dist(box, robot, storage)
    if b:
        return straight_dist

    if (sy == by) and ((sx < bx and bx < rx) or (rx < bx and bx < sx)):
        return straight_dist
    ## G B
    ##     X
    elif (sy == by) and ((sx < bx and rx <= bx) or (bx <= rx and bx < sx)):
        return straight_dist + 1 + abs(by - ry)
    ## G B
    ##   X
    elif (sx == bx) and ((sy < by and by < ry) or (ry < by and by < sy)):
        return straight_dist
    ## G
    ## B
    ##   X
    elif (sx == bx and ((sy < by and ry <= by) or (by <= ry and by < sy))):
        return straight_dist + 1 + abs(bx - rx)
    # ## G
    # ## B X
    else:
        return straight_dist

def one_left(state):
    l = []
    for box in state.boxes:
        if box not in state.storage:
            l.append(box)
    
    if len(l) == 1:
        return l[0]
    else:
        return False

def remaining(box, storage, robot):
    bx = box[0]
    by = box[1]
    rx = robot[0]
    ry = robot[1]
    sx = storage[0]
    sy = storage[1]

    b, d = straight_line_dist(box, storage, robot)
    if b:
        return 0
    else:
        turns = 0
        if (sx < bx and rx < bx) or (bx < rx and bx < sx):
            turns += 1
        if (sy < by and ry < by) or (by < ry and by < sy):
            turns += 1
        return 2 * turns

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
        closest = math.inf
        for storage in state.storage:
            bx = box[0]
            by = box[1]
            sx = storage[0]
            sy = storage[1]
            mh_dist = abs(bx-sx) + abs(by-sy)
            if mh_dist < closest:
                closest = mh_dist
        distance += closest
    
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
    gval = sN.gval
    hval = sN.hval
    return gval + weight * hval

# SEARCH ALGORITHMS
def weighted_astar(initial_state, heur_fn, weight, timebound):
    # IMPLEMENT    
    '''Provides an implementation of weighted a-star, as described in the HW1 handout'''
    '''INPUT: a sokoban state that represents the start state and a timebound (number of seconds)'''
    '''OUTPUT: A goal state (if a goal is found), else False as well as a SearchStats object'''
    '''implementation of weighted astar algorithm'''
    astar_e = SearchEngine(strategy='custom')
    wrapped_fval_function = (lambda sN : fval_function(sN,weight))
    astar_e.init_search(initial_state, sokoban_goal_state, heur_fn, wrapped_fval_function)
    return astar_e.search(timebound)

def iterative_astar(initial_state, heur_fn, weight=1, timebound=5):  # uses f(n), see how autograder initializes a search line 88
    # IMPLEMENT
    '''Provides an implementation of realtime a-star, as described in the HW1 handout'''
    '''INPUT: a sokoban state that represents the start state and a timebound (number of seconds)'''
    '''OUTPUT: A goal state (if a goal is found), else False as well as a SearchStats object'''
    '''implementation of iterative astar algorithm'''
    time_left = timebound
    cur_weight = weight/2
    cur_bound = None
    astar_e = SearchEngine(strategy='custom')
    while time_left > 0:
        wrapped_fval_function = (lambda sN : fval_function(sN,cur_weight))
        astar_e.init_search(initial_state, sokoban_goal_state, heur_fn, wrapped_fval_function)
        sol, stats = astar_e.search(timebound, costbound = cur_bound)
        if sol != False:
            cur_weight = cur_weight/2
            cur_bound = (sol.gval, 0, 0)
        time_left -= os.times()[0]
    return sol, stats


def iterative_gbfs(initial_state, heur_fn, timebound=5):  # only use g(n)
    # IMPLEMENT
    '''Provides an implementation of anytime greedy best-first search, as described in the HW1 handout'''
    '''INPUT: a sokoban state that represents the start state and a timebound (number of seconds)'''
    '''OUTPUT: A goal state (if a goal is found), else False'''
    '''implementation of iterative gbfs algorithm'''
    time_left = timebound
    solved = False
    gbfs_e = SearchEngine(strategy='best_first')
    gbfs_e.init_search(initial_state, sokoban_goal_state, heur_fn)
    while time_left > 0:
        if solved:
            cur_gval = (solState.gval, 0, 0)
            solState, stats = gbfs_e.search(timebound=time_left, costbound=cur_gval)
        else:
            solState, stats = gbfs_e.search(timebound=time_left)
        if solState != False:
            solved = True
        time_left -= os.times()[0]
    return solState, stats



