#   Look for #IMPLEMENT tags in this file. These tags indicate what has
#   to be implemented to complete the warehouse domain.

#   You may add only standard python imports
#   You may not remove any imports.
#   You may not import or otherwise source any of your own files

import os  # for time functions
import math # for infinity
from search import *  # for search engines
from sokoban import sokoban_goal_state, SokobanState, Direction, PROBLEMS  # for Sokoban specific classes and problems

UP = Direction("up", (0, -1))
RIGHT = Direction("right", (1, 0))
DOWN = Direction("down", (0, 1))
LEFT = Direction("left", (-1, 0))
UPLEFT = Direction('upLeft', (-1, -1))
UPRIGHT = Direction('upRight', (-1, 1))
DOWNLEFT = Direction('downLeft', (1, -1))
DOWNRIGHT = Direction('downRight', (1, 1))


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
        To improve on heur_manhattan_distance, I
        1. Sorted my storage points by distance from the walls (corners would be at the front of the list whilst the middle square of the board would be near the end)
        The reason for sorting it was is because I map one box to one storage point, so I mapped the ones closest to the wall especically the ones in corners first because
        otherwise the storage points in the corner could be blocked by the boxes.
        2. As stated above I mapped one storage point to one box, this is to prune some states where multiple boxes are moving towards one storage point.
        3. I pruned any states where the box end up in a corner against the walls or is cornered using obstacles
        4. I pruned any states where the box and storage were on the same axis but it was not possible for the robot to push the box towards the storage point
        Using these 4 techniques I was able to prune a lot of states and optimize which storages I mapped to which boxes to first.
    '''

    total_distance = 0
    boxes = set(state.boxes)

    for storage in sorted(state.storage, key=(lambda x: distance_from_wall(x, state.width, state.height))):
        if storage in boxes:
            boxes.remove(storage)
            continue
        
        min_distance_box = math.inf
        closest_box = None
        
        for box in boxes:
            # Stuck in a corner or stuck along the edges
            if is_cornor_obstruction(box, state.obstacles, state.width, state.height) or \
               is_edge_obstruction(box, state.boxes, storage, state.obstacles, state.width, state.height):
                return math.inf
            
            distance = get_manhattan_distance(box[0], box[1], storage[0], storage[1])

            if distance < min_distance_box:
                min_distance_box = distance
                closest_box = box
        
        if closest_box:
            total_distance += min_distance_box
            boxes.remove(closest_box)

    return total_distance

def distance_from_wall(coord, width, height):
    return min(coord[0], width - coord[0] - 1) + min(coord[1], height - coord[1] - 1)

def is_edge_obstruction(box, boxes, storage, obstacles, width, height):
    # Stuck along the left or right edge and no storage on our axis
    if (box[0] == 0 and storage[0] != 0) or (box[0] == width - 1 and storage != width - 1):
        return True

    # Stuck along the top or bottom edge and no storage on our axis
    if (box[1] == 0 and storage[1] != 0) or (box[1] == height - 1 and storage != height - 1):
        return True
    
    # Stuck but there is a storage on our axis
    if (box[0] == storage[0]):
        if (box[1] > storage[1]):
            # Make sure we can get below the box to push it up
            return (DOWN.move(box) in obstacles) or (box[1] == height - 1) or (DOWN.move(box) in boxes)
        else:
            return (UP.move(box) in obstacles) or (box[1] == 0) or (UP.move(box) in boxes)
    elif (box[1] == storage[1]):
        if (box[0] > storage[0]):
            return (RIGHT.move(box) in obstacles) or (box[0] == width - 1) or (RIGHT.move(box) in boxes)
        else:
            return (LEFT.move(box) in obstacles) or (box[0] == 0) or (LEFT.move(box) in boxes)
    return False

# We need to check above, below and left, and right of the box
# to check which sides it is obstructed on. It can either be obstructed by a
# wall or an obstacle.
def is_cornor_obstruction(box, obstacles, width, height):
    up_obstruction = (UP.move(box) in obstacles) or (box[1] == 0)
    down_obstruction = (DOWN.move(box) in obstacles) or (box[1] == height - 1)
    left_obstruction = (LEFT.move(box) in obstacles) or (box[0] == 0)
    right_obstruction = (RIGHT.move(box) in obstacles) or (box[0] == width - 1)

    return (up_obstruction or down_obstruction) and \
           (left_obstruction or right_obstruction)

def heur_zero(state):
    '''Zero Heuristic can be used to make A* search perform uniform cost search'''
    return 0

# Calculating manhattan distance
def get_manhattan_distance(x0, y0, x1, y1):
    return abs(x0 - x1) + abs(y0 - y1)

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
    for box in state.boxes:
        min_distance = math.inf
        box_stored = False
        for storage in state.storage:
            if box == storage:
                box_stored = True
                break
            min_distance = min(get_manhattan_distance(box[0], box[1], storage[0], storage[1]), min_distance)
        if not box_stored:
            total_distance += min_distance
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
    return sN.gval + sN.hval*weight

# SEARCH ALGORITHMS
def weighted_astar(initial_state, heur_fn, weight, timebound):
    # IMPLEMENT
    '''Provides an implementation of weighted a-star, as described in the HW1 handout'''
    '''INPUT: a sokoban state that represents the start state and a timebound (number of seconds)'''
    '''OUTPUT: A goal state (if a goal is found), else False as well as a SearchStats object'''
    '''implementation of weighted astar algorithm'''
    se = SearchEngine('custom', 'full')
    _func = lambda sN: fval_function(sN, weight)
    se.init_search(initial_state, goal_fn=sokoban_goal_state, heur_fn=heur_fn, fval_function=_func)
    final, stats = se.search(timebound)
    return final, stats  # CHANGE THIS

def iterative_astar(initial_state, heur_fn, weight=1, timebound=5):  # uses f(n), see how autograder initializes a search line 88
    # IMPLEMENT
    '''Provides an implementation of realtime a-star, as described in the HW1 handout'''
    '''INPUT: a sokoban state that represents the start state and a timebound (number of seconds)'''
    '''OUTPUT: A goal state (if a goal is found), else False as well as a SearchStats object'''
    '''implementation of iterative astar algorithm'''

    se = SearchEngine('custom', 'full')
    final, stats = None, None
    costbound = None
    while timebound > 0:
        _func = lambda sN: fval_function(sN, weight)
        se.init_search(initial_state, goal_fn=sokoban_goal_state, heur_fn=heur_fn, fval_function=_func)
        res_final, res_stats = se.search(timebound, costbound=costbound)
        
        if not res_final: 
            break

        weight = math.log2(weight)
        final, stats = res_final, res_stats
        gval, hval = final.gval, heur_fn(final)
        fval = gval + hval*weight
        costbound = [gval, hval, fval]
        timebound -= stats.total_time
        
    return final, stats

def iterative_gbfs(initial_state, heur_fn, timebound=5):  # only use h(n)
    # IMPLEMENT
    '''Provides an implementation of anytime greedy best-first search, as described in the HW1 handout'''
    '''INPUT: a sokoban state that represents the start state and a timebound (number of seconds)'''
    '''OUTPUT: A goal state (if a goal is found), else False'''
    '''implementation of iterative gbfs algorithm'''

    se = SearchEngine('best_first', 'full')
    final, stats = None, None
    costbound = None
    while timebound > 0:
        se.init_search(initial_state, goal_fn=sokoban_goal_state, heur_fn=heur_fn)
        res_final, res_stats = se.search(timebound, costbound=costbound)
        
        if not res_final: 
            break

        final, stats = res_final, res_stats
        gval, hval = final.gval, heur_fn(final)
        fval = gval + hval
        costbound = [gval, hval, fval]
        timebound -= stats.total_time
        
    return final, stats



