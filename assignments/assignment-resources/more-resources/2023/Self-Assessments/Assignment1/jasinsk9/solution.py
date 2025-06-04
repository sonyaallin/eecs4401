#   Look for #IMPLEMENT tags in this file. These tags indicate what has
#   to be implemented to complete the warehouse domain.

#   You may add only standard python imports
#   You may not remove any imports.
#   You may not import or otherwise source any of your own files

import os  # for time functions
import math  # for infinity
import numpy as np
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
    ------------ HEURISTIC EXPLANATION BELOW ------------
    '''
    total = [[0 for x in range(len(state.storage))] for y in range(len(state.boxes))]
    total = np.array(total)
    blocked_boxes = {}
    bot_dist = 0
    gone_to = []
    i = 0
    unsorted = 0
    best = 0
    for box in state.boxes:
        j = 0
        # collect this to penalize boxes not being in a goal
        if box not in state.storage:
            unsorted += 1
        # find manhattan distance between each box for optimal storage
        for goal in state.storage:
            total[i][j] = abs(box[0] - goal[0]) + abs(box[1] - goal[1])
            j += 1
        # consider directions of box for boxes getting stuck
        for dir in (UP, RIGHT, DOWN, LEFT):
            newloc = dir.move(box)
            if (newloc in state.boxes or newloc in state.obstacles or
                newloc[0] < 0 or newloc[1] < 0 or
                newloc[0] >= state.width or newloc[1] >= state.height):
                if box not in blocked_boxes:
                    blocked_boxes[box] = [(newloc, dir)]
                else:
                    blocked_boxes[box].append((newloc, dir))
        i += 1
    # coerce robots to be close to boxes
    for robots in state.robots:
        closest_box = float("inf")
        for box in state.boxes:
            if box not in state.storage and box not in gone_to:
                temp = abs(box[0] - robots[0]) + abs(box[1] - robots[1])
                if closest_box > temp:
                    closest_box = temp
        if closest_box <= 2:
            bot_dist += 1
        else:
            bot_dist += closest_box
    # check if there is a box stuck
    for block in blocked_boxes:
        if len(blocked_boxes[block]) == 2:
            counter = 0
            if (not (((blocked_boxes[block][0][1] == UP and blocked_boxes[block][1][1] == DOWN) or
                    (blocked_boxes[block][0][1] == RIGHT and blocked_boxes[block][1][1] == LEFT))) and
                    block not in state.storage):
                for blocking in blocked_boxes[block]:
                    if ((blocking[0] in blocked_boxes and len(blocked_boxes[blocking[0]]) > 1)
                            or blocking[0] in state.obstacles or
                            blocking[0][0] < 0 or blocking[0][1] < 0 or
                            blocking[0][0] >= state.width or blocking[0][1] >= state.height):
                        counter += 1
                if counter >= 2:
                    best += 1000
    # sort the distances to boxes and pick a unique best goal for each box
    sorted = np.sort(total, axis=None, kind='heapsort')
    c = 0
    rows = []
    cols = []
    while c < len(sorted) and len(rows) != len(state.boxes):
        a = np.where(total == sorted[c])
        for i in range(len(a[0])):
            if a[0][i] not in rows and a[1][i] not in cols:
                rows.append(a[0][i])
                cols.append(a[1][i])
                best += 2 * sorted[c]
        c += 1
    # if we are close to finishing we can just explore states
    if best >= 10:
        best += bot_dist
    # i don't really like this one because it makes it not admissible at all, but everything breaks if i remove it
    # heavily penalize boxes not in storage
    best += 100 * unsorted
    return best

    """
    ------------ Explanation at bottom of attempts ------------
    Attempt 1:
    Average manhattan distance * number of boxes incorrect
    identical to manhattan distance
    
    Attempt 2:
    manhattan distance - robot manhattan from box
    only solved 4
    
    Attempt 3:  
    smallest manhattan distance to unique goal squares
    solved 11, failed on 11, 14, 16 and 19 compared to better solution
    and solved 0 over better sltn.
    
    Attempt 4:
    smallest manhattan distance to unique goal squares dynamically updated
    solved 11 failed on same 11, 14, 17, 19 compared to better solution
    noticed in 11 and 14 that boxes were getting stuck together at top of room
    
    Attempt 5:
    smallest manhattan distance to unique goal squares  + highly discourage having two obstacles touching box
    solved 14 in time, equal to better solution except it 19 and mine solves 0
    why is it failing 5 and 6? -> considers pushing the box through the middle worse
    why is it failing 9? -> puts box thats closer to goal into that goal when another box has to use it
    why is it failing 17, 18, 19? -> takes too long
    easiest to fix probably 17, 18, 19 try making the robots stay near boxes that are not in the goal.\
    
    Attempt 6:
    attempt 5 and encourage robots to be near boxes
    solved 15 in time! solves 6 now and still misses 5, 9, 17, 18 and 19
    literally gets 2 moves away from 19 being solved :(
    probably add edge checking
    
    Attempt 7:
    attempt 6 with movable box obstacle discouragement
    solved 16 in time! solved 5 now and misses 9, 17, 18, 19
    both 17, 18 and 19 i assume to be a time problem
    9 is resolved with reserve squares.
    
    Attempt 8 Final Version:
    attempt 7 with bot dist removed from equation at low heuristic levels and more weight on manhattan dist
    solved 17, 18 in time and 19 sometimes, missed 5, 6 and 9
    yay!
    
    EXPLANATION
    This heuristic is far from perfect, in fact I think it kind of sucks and it's not even admissible but no time 
    left so whatever. 
    Things this heuristic does:
    1) Find the manhattan distance from each box to each goal and then determine a the best combination of unique
    goals for each box. We flatten the distance array and sort then pick out the smallest distances until we 
    have a unique goal square for every box that is minimal
    2) Look at the position of each box, and whether it is surrounded by a wall, other box or obstacle.
    If we are surrounded on two adjacent sides by any of these and none of the surrounding objects are movable
    themselves, then we have gotten a box stuck. Heavily penalize this because the goal is now unreachable.
    3) Evaluate the distance from each robot to each box and add the distance from the robot to its closest
    box that is not in a goal square. We do not distinguish whether a robot is 1 or 2 away from a box to allow the robot
    to circle a box without lowering the heuristic if it must push it from the other side.
    4) Penalize boxes being out of the goal by counting the unsorted boxes and adding 100 times that to the heuristic.
    I really hate doing this, because it makes the heuristic not admissible but otherwise the robots don't want to push
    the boxes into goal squares because their closest unsorted box is now far away and the heuristic increases.
    
    Overall the heuristic equation is:
    2 * distance from each box to a unique goal square + 100 * number of unsorted boxes + distance of robots from closest
    boxes.
    
    Potential Improvements that I didn't want to rewrite the function for/ran out of time:
    Picking a unique goal square for each box (would solve problem 5, 6, 9)
    Checking if a robot gets stuck (messes up some cases sometimes)
    Checking for obstacles (i'm kind of proud I got this far without considering obstacles)
    Check if a box is against a wall and is limited to a certain number of squares. (similar to the first one)
    Encourage robots to be on the opposite side of boxes from a goal to push optimally.
    Assign a box for each robot to push.
    """


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
    # SokobanState.print_state(state)
    total = 0
    for box in state.boxes:
        shortest_man = float("inf")
        for goal in state.storage:
            manhattan = abs(box[0] - goal[0]) + abs(box[1] - goal[1])
            if manhattan < shortest_man:
                shortest_man = manhattan
        total += shortest_man
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
    fval = sN.gval + (weight * sN.hval)
    return fval


# SEARCH ALGORITHMS
def weighted_astar(initial_state, heur_fn, weight, timebound):
    # IMPLEMENT    
    '''Provides an implementation of weighted a-star, as described in the HW1 handout'''
    '''INPUT: a sokoban state that represents the start state and a timebound (number of seconds)'''
    '''OUTPUT: A goal state (if a goal is found), else False as well as a SearchStats object'''
    '''implementation of weighted astar algorithm'''
    se = SearchEngine('custom', 'full')
    wrapped_fval_function = (lambda sN : fval_function(sN, weight))
    se.init_search(initial_state, goal_fn=sokoban_goal_state, heur_fn=heur_fn, fval_function=wrapped_fval_function)
    if isinstance(timebound, int):
        final, stats = se.search(timebound)
    if isinstance(timebound, tuple):
        final, stats = se.search(timebound[0], timebound[1])
    return final, stats


def iterative_astar(initial_state, heur_fn, weight=1,
                    timebound=5):  # uses f(n), see how autograder initializes a search line 88
    # IMPLEMENT
    '''Provides an implementation of realtime a-star, as described in the HW1 handout'''
    '''INPUT: a sokoban state that represents the start state and a timebound (number of seconds)'''
    '''OUTPUT: A goal state (if a goal is found), else False as well as a SearchStats object'''
    '''implementation of iterative astar algorithm'''
    time = 0
    weight = 100
    final_temp = 0
    final, stats = weighted_astar(initial_state, heur_fn, weight, timebound)
    time += stats.total_time
    weight = weight / 2
    while timebound > time + 0.5 and final_temp is not False:
        final_temp, temp_stats = weighted_astar\
            (initial_state, heur_fn, weight,
             (timebound - time - 0.1, [float("inf"), float("inf"), final.gval + heur_fn(initial_state)]))
        if final_temp is not False and final_temp.gval < final.gval:
            final = final_temp
            stats = temp_stats
        time += stats.total_time
        weight = weight / 2
    return final, stats  # CHANGE THIS

def iterative_gbfs(initial_state, heur_fn, timebound=5):  # only use h(n)
    # IMPLEMENT
    '''Provides an implementation of anytime greedy best-first search, as described in the HW1 handout'''
    '''INPUT: a sokoban state that represents the start state and a timebound (number of seconds)'''
    '''OUTPUT: A goal state (if a goal is found), else False'''
    '''implementation of iterative gbfs algorithm'''
    time = 0
    se = SearchEngine('best_first', 'full')
    se.init_search(initial_state, goal_fn=sokoban_goal_state, heur_fn=heur_fn)
    final, stats = se.search(timebound)
    time += stats.total_time
    while timebound > time + 0.5:
        se.init_search(initial_state, goal_fn=sokoban_goal_state, heur_fn=heur_fn)
        final_temp, temp_stats = se.search((timebound - time - 0.1), costbound=[final.gval, float("inf"), float("inf")])
        if final_temp is not False:
            final = final_temp
            stats = temp_stats
        time += stats.total_time
    return final, stats  # CHANGE THIS


UP = Direction("up", (0, -1))
RIGHT = Direction("right", (1, 0))
DOWN = Direction("down", (0, 1))
LEFT = Direction("left", (-1, 0))
