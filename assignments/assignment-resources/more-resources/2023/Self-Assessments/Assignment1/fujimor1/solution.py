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

    """Explanation of the alternative heuristic function

    I take the following things into considerations:
    
    1) Set to infinity (or 1e8) heuristic when the game is unsolvable given the current state
        (e.g., four corners, a box surrounded by two obstacles, etc.)
        Implemented in the helper function: isGameover()
    
    2) Improvement of Manhattan distance (i.e., only one box can be matched with each storage)

    3) Add additional costs if an obstacle exists in nearby 8 cells of each box/robot
        Implemented in the helper function: obstacle_nearby_count()

    4) Find the minimum distance between each box and robot
    """
    
    # check whether the game is unsolvable with the current state
    if isGameover(state):
        return 1e8
    
    # only one box can be in each storage
    storages = list(state.storage)
    total = 0
    for box in state.boxes:
        # the box is already on the storage
        if box in storages:
            storages.remove(box)
            continue
        # find the minimum distance between the box and storages
        mindist = 1e8
        closest_storage = None
        for storage in storages:
            dist = abs(box[0] - storage[0]) + abs(box[1] - storage[1])
            if dist < mindist:
                mindist = dist
                closest_storage = storage
        total += mindist
        storages.remove(closest_storage)

        # add cost for obstacles (nearby box)
        total += obstacle_nearby_count(box, state.obstacles)

        # find the minimum distance between the box and robots
        mindist = 1e8
        for robot in state.robots:
            dist = abs(box[0] - robot[0]) + abs(box[1] - robot[1])
            if dist < mindist:
                mindist = dist
        total += mindist

    # add cost for obstacles (nearby each robot)
    for robot in state.robots:
        total += obstacle_nearby_count(robot, state.obstacles)

    return total

def obstacle_nearby_count(box, obstacles):
    ''' Helper function for heur_alternate()
    Count a number of nearby obstacles.

    INPUT: a target box (or robot), obstacles
    OUTPUT: int, number of obstacles
    '''
    nearby = ((box[0]+1, box[1]), (box[0]+1, box[1]+1), (box[0]-1, box[1]+1), (box[0]+1, box[1]-1), 
    (box[0]-1, box[1]-1),(box[0]-1, box[1]), (box[0], box[1]-1), (box[0], box[1]+1))

    return len(set(obstacles) & set(nearby))

def isGameover(state):
    ''' Helper function for heur_alternate()
    Check whether the game is unsolvable with the current state.
    INPUT: a sokoban state
    OUTPUT: boolean value
    '''
    # remove boxes that are already in one of the storage 
    orig_boxes = list(state.boxes)
    boxes = orig_boxes.copy()
    storages = list(state.storage)
    for box in orig_boxes:
        if box in storages:
            boxes.remove(box)
            storages.remove(box)

    # check for various deadlocks
    for box in boxes:
        # four corners
        if (box[0] == 0 and (box[1] == 0 or box[1] == state.height-1)) or \
            (box[0] == state.width-1 and (box[1] == 0 or box[1] == state.height-1)):
            return True

        # box in far-left/right column
        # deadlock situations:
        # 1) two boxes next to each other
        # 2) cannot reach a storage or no storage in the same column
        # 3) More boxes than storages in the same column
        elif box[0] == 0 or box[0] == state.width-1:
            # 1) two boxes next to each other
            if (box[0], box[1]-1) in state.boxes or (box[0], box[1]+1) in state.boxes:
                return True

            # 2) cannot reach a storage or no storage in the same column
            upper_storages = [s[1] for s in storages if (s[0] == box[0] and s[1] < box[1])]
            lower_storages = [s[1] for s in storages if (s[0] == box[0] and s[1] > box[1])]
            # check for upper side
            upper_dead = False
            if upper_storages:
                for i in range(max(upper_storages)+1, box[1]):
                    if (box[0], i) in state.obstacles:
                        upper_dead = True
            else:
                upper_dead = True
            # check for loweer side
            lower_dead = False
            if lower_storages:
                for i in range(box[1]+1, min(lower_storages)):
                    if (box[0], i) in state.obstacles:
                        lower_dead = True
            else:
                lower_dead = True
            # if both upper and lower sides are dead, then return True
            if upper_dead and lower_dead:
                return True

            # 3) More boxes than storages in the same column
            nbox = sum(i[0] == box[0] for i in boxes)
            if nbox > len(upper_storages) + len(lower_storages):
                return True

        # box in top/bottom row
        # deadlock situations:
        # 1) two boxes next to each other
        # 2) cannot reach a storage or no storage in the same row
        # 3) More boxes than storages in the same row
        elif box[1] == 0 or box[1] == state.height-1:
            # 1) two boxes next to each other
            if (box[0]-1, box[1]) in state.boxes or (box[0]+1, box[1]) in state.boxes:
                return True

            # 2) cannot reach a storage or no storage in the same row
            right_storages = [s[0] for s in storages if (s[1] == box[1] and s[0] > box[0])]
            left_storages = [s[0] for s in storages if (s[1] == box[1] and s[0] < box[0])]
            # check for RHS
            right_dead = False
            if right_storages:
                for i in range(box[0]+1, min(right_storages)):
                    if (i, box[1]) in state.obstacles:
                        right_dead = True
            else:
                right_dead = True
            # check for LHS
            left_dead = False
            if left_storages:
                for i in range(max(left_storages)+1, box[0]):
                    if (i, box[1]) in state.obstacles:
                        left_dead = True
            else:
                left_dead = True
            # if both RHS and LHS are dead, then return True
            if right_dead and left_dead:
                return True

            # 3) More boxes than storages in the same column
            nbox = sum(i[1] == box[1] for i in boxes)
            if nbox > len(right_storages) + len(left_storages):
                return True

        # two obstacles in one above and right of the box
        elif (box[0], box[1]-1) in state.obstacles and (box[0]+1, box[1]) in state.obstacles:
            return True
        # two obstacles in one above and left of the box
        elif (box[0], box[1]-1) in state.obstacles and (box[0]-1, box[1]) in state.obstacles:
            return True
        # two obstacles in one below and right of the box
        elif (box[0], box[1]+1) in state.obstacles and (box[0]+1, box[1]) in state.obstacles:
            return True
        # two obstacles in one below and left of the box
        elif (box[0], box[1]+1) in state.obstacles and (box[0]-1, box[1]) in state.obstacles:
            return True
        else:
            continue
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
    total = 0
    for box in state.boxes:
        mindist = 1e8
        if box in state.storage:
            continue
        for storage in state.storage:
            dist = abs(box[0] - storage[0]) + abs(box[1] - storage[1])
            if dist < mindist:
                mindist = dist
        total += mindist
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
    # initialize search engine
    engine = SearchEngine(strategy="custom")
    engine.init_search(initial_state, sokoban_goal_state, heur_fn, fval_function=(lambda sN: fval_function(sN, weight)))

    # search
    goal_state, stats = engine.search(timebound)
    return goal_state, stats

def iterative_astar(initial_state, heur_fn, weight=1, timebound=5):  # uses f(n), see how autograder initializes a search line 88
    # IMPLEMENT
    '''Provides an implementation of realtime a-star, as described in the HW1 handout'''
    '''INPUT: a sokoban state that represents the start state and a timebound (number of seconds)'''
    '''OUTPUT: A goal state (if a goal is found), else False as well as a SearchStats object'''
    '''implementation of iterative astar algorithm'''
    # 0.02s buffer
    timebound -= 0.02
    
    # start time
    start_time = os.times()[0]

    # initialize search engine
    engine = SearchEngine(strategy="custom")

    # override weight
    weight = [10, 5, 3, 2, 1.5, 1]

    best_gval = 1e8
    costbound = 1e8
    best_goal_state = None
    best_stats = None
    for w in weight:
        # initialize search
        engine.init_search(initial_state, sokoban_goal_state, heur_fn, fval_function=(lambda sN: fval_function(sN, w)))

        # update remaining time
        end_time = os.times()[0]
        timebound = timebound - (end_time - start_time)
        start_time = end_time
        if timebound < 0:
            break

        # search
        goal_state, stats = engine.search(timebound, costbound=(1e8, 1e8, costbound))

        if not goal_state:
            break
        elif goal_state.gval < best_gval:
            best_goal_state = goal_state
            best_stats = stats
            best_gval = goal_state.gval
            costbound = best_gval
    
    # return best goal_state and stats
    if best_stats is None:
        return False, stats
    else:
        return best_goal_state, best_stats

def iterative_gbfs(initial_state, heur_fn, timebound=5):  # only use h(n)
    # IMPLEMENT
    '''Provides an implementation of anytime greedy best-first search, as described in the HW1 handout'''
    '''INPUT: a sokoban state that represents the start state and a timebound (number of seconds)'''
    '''OUTPUT: A goal state (if a goal is found), else False'''
    '''implementation of iterative gbfs algorithm'''
    # 0.02s buffer
    timebound -= 0.02
    
    # start time
    start_time = os.times()[0]

    # initialize search engine
    engine = SearchEngine(strategy="best_first")

    best_gval = 1e8
    costbound = 1e8
    best_goal_state = None
    best_stats = None
    while True:
        # initialize search
        engine.init_search(initial_state, sokoban_goal_state, heur_fn)

        # update remaining time
        end_time = os.times()[0]
        timebound -= (end_time - start_time)
        start_time = end_time
        if timebound < 0:
            break

        # search
        goal_state, stats = engine.search(timebound, costbound=(costbound, 1e8, 1e8))

        if not goal_state:
            break
        elif goal_state.gval < best_gval:
            best_goal_state = goal_state
            best_stats = stats
            best_gval = goal_state.gval
            costbound = best_gval
    
    # return best goal_state and stats
    if best_stats is None:
        return False, stats
    else:
        return best_goal_state, best_stats

