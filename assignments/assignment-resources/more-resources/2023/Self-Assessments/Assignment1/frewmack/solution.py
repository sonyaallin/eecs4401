#   Look for #IMPLEMENT tags in this file. These tags indicate what has
#   to be implemented to complete the warehouse domain.

#   You may add only standard python imports
#   You may not remove any imports.
#   You may not import or otherwise source any of your own files

import os  # for time functions
import math  # for infinity
from search import *  # for search engines
from sokoban import sokoban_goal_state, SokobanState, Direction, PROBLEMS, UP, DOWN, LEFT, RIGHT  # for Sokoban specific classes and problems

directions = [UP, LEFT, DOWN, RIGHT]

"""
***Better heuristic explanation***

1. We incur a hefty cost (1.0 ^ 10^32) for states where the box is in a corner that is not a goal state
   and where it cannot be moved. This represents a fail state and should be avoided.
2. We calculate the manhattan distance from all "free" boxes (not in storage) to the closest "free" storage space
   (storage spaces not occupied by boxes). This is more accurate since we cannot move multiple boxes to the same 
   space.
3. We calculate the distance of each robot to its closest box. This includes all boxes, not just "free" ones.
   This encourages robots to stay close to boxes.
4. The "stay out of my way!" heuristic: robots should not occupy opposite sides of a box, this incurs a +1 added cost.
5. We calculate the box between each free box and its closest free goal. Every obstacle, robot, or other box in the way
   incurs a +1 cost. This is a crude attempt to represent the additional cost of moving boxes around obstacles.
"""


# HELPERS
def mh_distance(a, b):
    """Manhattan distance between 2 points of equal dimension."""
    return sum([abs(a[i] - b[i]) for i in range(len(a))])

def decrease_weight(weight):
    """
    Reduces the weight during iterative A*
    """
    return max(1.0, (weight - 1.0) / 2.0 + 1.0)

def out_of_bounds(coords, state: SokobanState):
    """
    Return whether the given coordinates are out of bounds or includes an obstacle.
    (Basically anywhere that the robots or boxes cannot go)
    """
    return coords[0] >= state.width or coords[1] >= state.width or coords[0] < 0 or coords[1] < 0 or coords in state.obstacles

def box_in_corner(box, state):
    """
    Return whether the box is in a corner or not. Accounts for boundaries and obstacles.
    """
    places = [out_of_bounds(x.move(box), state) for x in directions]

    return sum(places) > 2 or (
        any([places[i] and places[(i+1)%4] and not places[(i+2)%4] and not places[(i+3)%4] for i in range(4)])
    )

def zone_area(a, b):
    """Calculate a list of coordinates for each tile between two corner points a, b."""
    l0, l1 = min(a[0], b[0]), min(a[1], b[1])
    h0, h1 = max(a[0], b[0]), max(a[1], b[1])

    return [(x, y) for x in range(l0, h0 + 1) for y in range(l1, h1 + 1)]

# SOKOBAN HEURISTICS
def heur_alternate(state):
    '''a better heuristic'''
    '''INPUT: a sokoban state'''
    '''OUTPUT: a numeric value that serves as an estimate of the distance of the state to the goal.'''
    # heur_manhattan_distance has flaws.
    # Write a heuristic function that improves upon heur_manhattan_distance to estimate distance between the current state and the goal.
    # Your function should return a numeric value for the estimate of the distance to the goal.
    # EXPLAIN YOUR HEURISTIC IN THE COMMENTS. Please leave this function (and your explanation) at the top of your solution file, to facilitate marking.
    
    # Ideas: - the closest storage space from a box cannot be a space that is already occupied by a box
    #        - boxes that are already in a storage space still count as 0
    #        - boxes in corners are really bad, and cost an infinitely high amount
    #        - robots should not get in each other's way around boxes
    
    distances = 0

    free_storage = set(state.storage)
    free_boxes = set(state.boxes)
    for box in state.boxes:
        if box in free_storage:
            free_boxes.discard(box)  # Don't look at boxes that are already in storage
            free_storage.discard(box)  # Don't try to put boxes in storage that's been taken
        if box_in_corner(box, state) and box not in state.storage:
            return 1e32  # GG, puzzle failed

    # Distances from free boxes to free storage spaces
    for box in free_boxes:
        closest_distance = math.inf
        closest_goal = None
        for goal in free_storage:
            dist = mh_distance(box, goal)
            if dist < closest_distance:
                closest_distance = dist
                closest_goal = goal

        if not math.isinf(closest_distance):
            distances += closest_distance
            for coord in zone_area(box, closest_goal):
                if coord in state.obstacles or coord in state.robots or coord in state.boxes:
                    distances += 1

    # distances from robots to boxes
    for robot in state.robots:
        closest_distance = math.inf
        for box in state.boxes:
            dist = mh_distance(robot, box)
            if dist < closest_distance:
                closest_distance = dist

        if not math.isinf(closest_distance):
            distances += closest_distance - 1  # robots can't occupy the same space as a box

    # the "stay out of my way!" heuristic
    for box in free_boxes:
        surroundings = [x.move(box) for x in directions]
        if any([surroundings[i] in state.robots and surroundings[(i+2)%4] in state.robots for i in range(4)]):
            distances += 1
    
    return distances

def heur_zero(state):
    '''Zero Heuristic can be used to make A* search perform uniform cost search'''
    return 0

def heur_manhattan_distance(state):
    '''admissible sokoban puzzle heuristic: manhattan distance'''
    '''INPUT: a sokoban state'''
    '''OUTPUT: a numeric value that serves as an estimate of the distance of the state to the goal.'''
    # We want an admissible heuristic, which is an optimistic heuristic.
    # It must never overestimate the cost to get from the current state to the goal.
    # The sum of the Manhattan distances between each box that has yet to be stored and the storage point nearest to it is such a heuristic.
    # When calculating distances, assume there are no obstacles on the grid.
    # You should implement this heuristic function exactly, even if it is tempting to improve it.
    # Your function should return a numeric value; this is the estimate of the distance to the goal.
    
    distances = []
    for box in state.boxes:
        closest_distance = math.inf
        for goal in state.storage:
            dist = abs(box[0] - goal[0]) + abs(box[1] - goal[1])
            if dist < closest_distance:
                closest_distance = dist
        distances.append(closest_distance)
    
    return sum(distances)

def fval_function(sN, weight):
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
    '''Provides an implementation of weighted a-star, as described in the HW1 handout'''
    '''INPUT: a sokoban state that represents the start state and a timebound (number of seconds)'''
    '''OUTPUT: A goal state (if a goal is found), else False as well as a SearchStats object'''
    '''implementation of weighted astar algorithm'''

    wrapped_fval_func = (lambda sN : fval_function(sN, weight))
    engine = SearchEngine(strategy='custom')
    engine.init_search(
        initState=initial_state, 
        goal_fn=sokoban_goal_state, 
        heur_fn=heur_fn, 
        fval_function=wrapped_fval_func
    )
    final, stats = engine.search(timebound)

    return final, stats  # CHANGE THIS

def iterative_astar(initial_state, heur_fn, weight=1, timebound=5):  # uses f(n), see how autograder initializes a search line 88
    '''Provides an implementation of realtime a-star, as described in the HW1 handout'''
    '''INPUT: a sokoban state that represents the start state and a timebound (number of seconds)'''
    '''OUTPUT: A goal state (if a goal is found), else False as well as a SearchStats object'''
    '''implementation of iterative astar algorithm'''

    time_used = 0.0
    costbound = (math.inf, math.inf, math.inf)
    engine = SearchEngine(strategy='custom')
    final, stats = False, None

    # do-while 
    while True:
        # We can't depend on engine.search to get elapsed time, so we measure ourselves
        wrapped_fval_func = (lambda sN: fval_function(sN, weight))

        start = os.times()[0]

        engine.init_search(
            initState=initial_state, 
            goal_fn=sokoban_goal_state, 
            heur_fn=heur_fn, 
            fval_function=wrapped_fval_func
        )
        temp_final, temp_stats = engine.search(timebound - time_used, costbound)

        diff = os.times()[0] - start

        time_used += diff

        if temp_final:
            final, stats = temp_final, temp_stats
            costbound = (math.inf, math.inf, final.gval)

        weight = decrease_weight(weight)

        # do-while condition
        if time_used >= timebound:
            break

    return final, stats

def iterative_gbfs(initial_state, heur_fn, timebound=5):  # only use h(n)
    # IMPLEMENT
    '''Provides an implementation of anytime greedy best-first search, as described in the HW1 handout'''
    '''INPUT: a sokoban state that represents the start state and a timebound (number of seconds)'''
    '''OUTPUT: A goal state (if a goal is found), else False'''
    '''implementation of iterative gbfs algorithm'''

    time_used = 0.0
    costbound = (math.inf, math.inf, math.inf)
    engine = SearchEngine(strategy="best_first")
    final, stats = False, None

    # do-while
    while True:
        start = os.times()[0]

        engine.init_search(
            initState=initial_state, 
            goal_fn=sokoban_goal_state, 
            heur_fn=heur_fn, 
        )
        temp_final, temp_stats = engine.search(timebound - time_used, costbound)

        diff = os.times()[0] - start

        time_used += diff

        if temp_final:
            final, stats = temp_final, temp_stats
            costbound = (final.gval, math.inf, math.inf)

        if time_used >= timebound:
            break

    return final, stats



