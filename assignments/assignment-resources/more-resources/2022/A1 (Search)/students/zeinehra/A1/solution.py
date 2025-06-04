#   Look for #IMPLEMENT tags in this file. These tags indicate what has
#   to be implemented to complete the warehouse domain.

#   You may add only standard python imports
#   You may not remove any imports.
#   You may not import or otherwise source any of your own files

from cgitb import small
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
    '''
    Initially, I attempted to create a manhattan heuristic while taking into account obstacles by
    counting the obstacles
    as twice the length of regular path length. This did not result in
    promising results. Afterwards, I calculated manhattan distances but discarded corner boxes
    that were not on storage points. This is due to not being able to move them whatsoever. This
    did not show significant improvement so then I also added edge of map detection as well as tunnel
    detection. For edge of map detection, I would scan the row/column to see if there were more boxes
    than storages indicating that the goal is unreachable. For tunnel dection, if two boxes are in a tunnel
    stuck together, then it is impossible to move either. I then combined all the improvements with
    checking robot distances as well as discouraging them from standing on storage tiles (as they
    need to move for the goal state) showing a significant improvement. I also added square checking
    but that had a marginal effect.
    '''
    total_dist = 0

    for box in state.boxes:
        smallest_dist_b2s = state.width + state.height  # Smallest distance from a box to a storage
        if box not in state.storage and deadlocked(state, box):
            return 2**31
        for storage in state.storage:
            if storage in state.boxes and storage != box:
                continue
            dist_b2s = abs(box[0] - storage[0]) + abs(box[1] - storage[1])
            if smallest_dist_b2s > dist_b2s:
                smallest_dist_b2s = dist_b2s

        total_dist += smallest_dist_b2s

    # If at wall, check left/right or up/down storage points to encourage moving to the furthest storage to allow more boxes
    

    # Calculating manhattan distance from closest robot to a box
    for robot in state.robots:
        smallest_dist_r2b = state.width + state.height  # Smallest distance from a robot to a box
        for box in state.boxes:
            dist_r2b = abs(box[0] - robot[0]) + abs(box[1] - robot[1])
            if smallest_dist_r2b > dist_r2b:
                smallest_dist_r2b = dist_r2b

        total_dist += smallest_dist_r2b - 1 # Robots can't be at the same place as a box so 1 block away is the closest
        if robot in state.storage:  # Discourage robots from standing in storage points
            total_dist += 1

    return total_dist

def deadlocked(state, box):
    '''Returns if the tuple box is on a corner or wall without a storage'''
    # Corner checking
    if (box[0] - 1, box[1]) in state.obstacles or (box[0] - 1) < 0 or \
        (box[0] + 1, box[1]) in state.obstacles or (box[0] + 1) >= state.width:   # left/right edge/obstacle
        if (box[0], box[1] - 1) in state.obstacles or (box[1] - 1) < 0:   # bottom left/right corner/obstacle
            return True
        elif (box[0], box[1] + 1) in state.obstacles or (box[1] + 1) >= state.height: # top left/right corner/obstacle
            return True

    # Check edges of map
    if box[0] == 0 or box[0] == state.width - 1:
        edge_storages = 0
        edge_boxes = 0

        for storage in state.storage:
            if storage[0] == box[0]:  
                edge_storages += 1  # Count number of storages at the edge

        for other_box in state.boxes:
            if box[0] == other_box[0]:
                edge_boxes += 1     # Count number of boxes along the same edge

        if edge_boxes > edge_storages:
            return True

        # Check adjacent tiles at edges as that would also deadlock
        if (box[0], box[1] + 1) in state.boxes or (box[0], box[1] + 1) in state.obstacles:
            return True
        elif (box[0], box[1] - 1) in state.boxes or (box[0], box[1] - 1) in state.obstacles:
            return True

    if box[1] == 0 or box[1] == state.height - 1:
        edge_storages = 0
        edge_boxes = 0

        for storage in state.storage:
            if storage[1] == box[1]:  
                edge_storages += 1  # Count number of storages at the edge

        for other_box in state.boxes:
            if box[1] == other_box[1]:
                edge_boxes += 1     # Count number of boxes along the same edge

        if edge_boxes > edge_storages:
            return True

        # Check adjacent tiles at edges as that would also deadlock
        if (box[0] + 1, box[1]) in state.boxes or (box[0] + 1, box[1]) in state.obstacles:
            return True
        elif (box[0] - 1, box[1]) in state.boxes or (box[0] - 1, box[1]) in state.obstacles:
            return True

    # Tunnel checking (cannot be cornered at this point)
    if ((box[0] - 1, box[1]) in state.obstacles or (box[0] - 1) < 0) and \
        ((box[0] + 1, box[1]) in state.obstacles or (box[0] + 1) >= state.width):   # Vertical tunnel
        if ((box[0], box[1] + 1) in state.boxes) and \
            ((box[0] - 1, box[1] + 1) in state.obstacles or (box[0] - 1) < 0) and \
            ((box[0] + 1, box[1] + 1) in state.obstacles or (box[0] + 1) >= state.width):   # box above in tunnel (trapped)
            return True
        elif ((box[0], box[1] - 1) in state.boxes) and \
            ((box[0] - 1, box[1] - 1) in state.obstacles or (box[0] - 1) < 0) and \
            ((box[0] + 1, box[1] - 1) in state.obstacles or (box[0] + 1) >= state.width):   # box below in tunnel (trapped)
            return True
    elif ((box[0], box[1] - 1) in state.obstacles or (box[1] - 1) < 0) and \
        ((box[0], box[1] + 1) in state.obstacles or (box[1] + 1) >= state.height):   # Horizontal tunnel
        if ((box[0] + 1, box[1]) in state.boxes) and \
            ((box[0] + 1, box[1] - 1) in state.obstacles or (box[1] - 1) < 0) and \
            ((box[0] + 1, box[1] + 1) in state.obstacles or (box[1] + 1) >= state.height):   # box to the right in tunnel (trapped)
            return True
        elif ((box[0] - 1, box[1]) in state.boxes) and \
            ((box[0] - 1, box[1] - 1) in state.obstacles or (box[1] - 1) < 0) and \
            ((box[0] - 1, box[1] + 1) in state.obstacles or (box[1] + 1) >= state.height):   # box to the left in tunnel (trapped)
            return True

    # square checking (or larger)
    blockers = state.boxes.union(state.obstacles)
    if (box[0], box[1] + 1) in blockers:
        if (box[0] + 1, box[1] + 1) in blockers and (box[0] + 1, box[1]) in blockers:
            return True
        elif (box[0] - 1, box[1] + 1) in blockers and (box[0] - 1, box[1]) in blockers:
            return True
    elif (box[0], box[1] - 1) in blockers:
        if (box[0] + 1, box[1] - 1) in blockers and (box[0] + 1, box[1]) in blockers:
            return True
        elif (box[0] - 1, box[1] - 1) in blockers and (box[0] - 1, box[1]) in blockers:
            return True

    return False

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
    total_dist = 0

    for boxX, boxY in state.boxes:
        smallest_dist = state.width + state.height  # The max distance is the manhattan distance of the entire board
        for storageX, storageY in state.storage:
            dist = abs(boxX - storageX) + abs(boxY - storageY)
            if smallest_dist > dist:
                smallest_dist = dist

        total_dist += smallest_dist

    return total_dist

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
    wrapped_fval_function = (lambda sN : fval_function(sN,weight))

    search_engine = SearchEngine('custom')
    search_engine.init_search(initial_state, sokoban_goal_state, heur_fn, wrapped_fval_function)
    
    return search_engine.search(timebound)

def iterative_astar(initial_state, heur_fn, weight=1, timebound=5):  # uses f(n), see how autograder initializes a search line 88
    # IMPLEMENT
    '''Provides an implementation of realtime a-star, as described in the HW1 handout'''
    '''INPUT: a sokoban state that represents the start state and a timebound (number of seconds)'''
    '''OUTPUT: A goal state (if a goal is found), else False as well as a SearchStats object'''
    '''implementation of iterative astar algorithm'''
    wrapped_fval_function = (lambda sN : fval_function(sN,weight))
    end_time = os.times()[0] + timebound

    search_engine = SearchEngine('custom')
    search_engine.init_search(initial_state, sokoban_goal_state, heur_fn, wrapped_fval_function)

    goal_state, stats = search_engine.search(timebound)

    if goal_state == False:
        return False, stats

    while weight > 1 and os.times()[0] < end_time:
        weight //= 2
        wrapped_fval_function = (lambda sN : fval_function(sN,weight))

        search_engine.init_search(initial_state, sokoban_goal_state, heur_fn, wrapped_fval_function)

        potential_goal_state, potential_stats = search_engine.search((end_time - os.times()[0]), (goal_state.gval, float('inf'), float('inf')))

        # Check if a better solution in case an inadmissible heuristic is used
        if potential_goal_state != False and potential_goal_state.gval < goal_state.gval:
            goal_state, stats = potential_goal_state, potential_stats
    
    return goal_state, stats

def iterative_gbfs(initial_state, heur_fn, timebound=5):  # only use h(n)
    # IMPLEMENT
    '''Provides an implementation of anytime greedy best-first search, as described in the HW1 handout'''
    '''INPUT: a sokoban state that represents the start state and a timebound (number of seconds)'''
    '''OUTPUT: A goal state (if a goal is found), else False'''
    '''implementation of iterative gbfs algorithm'''
    end_time = os.times()[0] + timebound

    search_engine = SearchEngine('best_first')
    search_engine.init_search(initial_state, sokoban_goal_state, heur_fn)

    goal_state, stats = search_engine.search(timebound)

    if goal_state == False:
        return False, stats

    while os.times()[0] < end_time:

        search_engine.init_search(initial_state, sokoban_goal_state, heur_fn)
        
        potential_goal_state, potential_stats = search_engine.search((end_time - os.times()[0]), (goal_state.gval, float('inf'), float('inf')))

        # Check if a better solution in case an inadmissible heuristic is used
        if potential_goal_state != False and potential_goal_state.gval < goal_state.gval:
            goal_state, stats = potential_goal_state, potential_stats
    
    return goal_state, stats



