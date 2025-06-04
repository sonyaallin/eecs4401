#   Look for #IMPLEMENT tags in this file. These tags indicate what has
#   to be implemented to complete the warehouse domain.

#   You may add only standard python imports
#   You may not remove any imports.
#   You may not import or otherwise source any of your own files

import os  # for time functions
import math  # for infinity
from search import *  # for search engines
from sokoban import sokoban_goal_state, SokobanState, Direction, \
    PROBLEMS  # for Sokoban specific classes and problems


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
    #the heuristic iterates through all the boxes that are not in "storage", and checks whether there is a possible solutions, if not then the
    # function realizes that and returns inifinty. the heuristic checks for different kinds of blockades. It also takes into consideration
    # the small distance from the nearest robot to the box and the extra steps the robot might need to move due to obstacles.
    t_dist = 0
    corners = frozenset(((0, 0), (state.height - 1, state.width - 1),
                         (0, state.height - 1), (state.width - 1, 0)))
    #iterate through the boxes
    for box in state.boxes:
        #box is not in storage so moves can be made
        if box not in state.storage:
            min_d = float("inf")
            obstacles = state.obstacles
            #area around the box
            up = (box[0], box[1] - 1)
            down = (box[0], box[1] + 1)
            left = (box[0] - 1, box[1])
            right = (box[0] + 1, box[1])
            adjacent = [up, down, left, right]

            #blocks from different directions
            upblock = box[1] == state.height - 1 or up in obstacles
            downblock = box[1] == 0 or down in obstacles
            leftblock = box[0] == 0 or left in obstacles
            rightblock = box[0] == state.width - 1 or right in obstacles

            # check if at board corner but not at storage - not solvable
            if box in corners:
                return float("inf")

            # check if stuck in a corner inside the board -unsolvable
            if (upblock or downblock) and (leftblock or rightblock):
                return float('inf')
            #blocked from all directions and cant be moved -unsolvable
            if upblock and downblock and leftblock and rightblock:
                return float('inf')

            #whether there is a storage space available along each wall
            stor_at_rWall = False
            stor_at_lWall = False
            stor_at_uWall = False
            stor_at_dWall = False

            #get the min manhattan distance from the box to storage
            for s in state.storage:
                if s[0] == 0:
                    stor_at_lWall = True
                if s[0] == state.width - 1:
                    stor_at_rWall = True
                if s[1] == 0:
                    stor_at_dWall = True
                if s[1] == state.height - 1:
                    stor_at_uWall = True
                dist = abs(box[0] - s[0]) + abs(box[1] - s[1]) #manhattan distance
                if dist < min_d:
                    min_d = dist
            #add the min distance from box to storage
            t_dist += min_d

            #box at wall but no storage space -unsolvable
            if box[0] == 0 and not stor_at_lWall:
                return float("inf")
            if box[0] == state.width - 1 and not stor_at_rWall:
                return float("inf")
            if box[1] == state.height - 1 and not stor_at_uWall:
                return float("inf")
            if box[1] == 0 and not stor_at_dWall:
                return float("inf")
            #2 boxes next to each other -unsolvable
            if box[0] == 0 and (up in state.boxes or down in state.boxes):
                return float("inf")
            if box[0] == state.width - 1 and (up in state.boxes or down in state.boxes):
                return float("inf")
            if box[1] == state.height - 1 and (left in state.boxes or right in state.boxes):
                return float("inf")
            if box[1] == 0 and (left in state.boxes or right in state.boxes):
                return float("inf")

            #add extra moves for the different obstacles
            for x in adjacent:
                if x in obstacles:
                    t_dist += 1
                # walls as an obstacle
                if x[0] - 1 == -1:
                    t_dist += 1
                if x[0] + 1 == state.width:
                    t_dist += 1
                if x[1] + 1 == state.height:
                    t_dist += 1
                if x[1] - 1 == -1:
                    t_dist += 1

        min_d = float("inf")
        #get the manhatta distance from a robot to box
        for robot in state.robots:
            up = (robot[0], robot[1] - 1)
            down = (robot[0], robot[1] + 1)
            left = (robot[0] - 1, robot[1])
            right = (robot[0] + 1, robot[1])
            #check if a robot is blocked in all directions
            if up in state.obstacles and down in state.obstacles and left in state.obstacles and right in state.obstacles:
                continue
            dist = abs(robot[0] - box[0]) + abs(robot[1] - box[1])
            if dist < min_d:
                min_d = dist
        t_dist += min_d
    return t_dist  # CHANGE THIS


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

    t_distance = 0

    for box in state.boxes:
        min_d = float("inf")
        for storage in state.storage:
            dist = abs(box[0] - storage[0]) + abs(box[1] - storage[1])
            if dist < min_d:
                min_d = dist
        t_distance += min_d

    return t_distance  # CHANGE THIS


def fval_function(sN, weight):
    # IMPLEMENT
    """
    Provide a custom formula for f-value computation for Anytime Weighted A star.
    Returns the fval of the state contained in the sNode.

    @param sNode sN: A search node (containing a SokobanState)
    @param float weight: Weight given by Anytime Weighted A star
    @rtype: float
    """
    return sN.gval + (weight * sN.hval)


# SEARCH ALGORITHMS
def weighted_astar(initial_state, heur_fn, weight, timebound):
    # IMPLEMENT
    '''Provides an implementation of weighted a-star, as described in the HW1 handout'''
    '''INPUT: a sokoban state that represents the start state and a timebound (number of seconds)'''
    '''OUTPUT: A goal state (if a goal is found), else False as well as a SearchStats object'''
    '''implementation of weighted astar algorithm'''

    # wrap function
    wrapped_fval_function = (lambda sN: fval_function(sN, weight))
    # create engine
    search_eng = SearchEngine(strategy='custom')
    search_eng.init_search(initial_state, sokoban_goal_state, heur_fn,
                           wrapped_fval_function)
    # get solution
    sol = search_eng.search(timebound)

    return sol


def iterative_astar(initial_state, heur_fn, weight=1,
                    timebound=5):  # uses f(n), see how autograder initializes a search line 88
    # IMPLEMENT
    '''Provides an implementation of realtime a-star, as described in the HW1 handout'''
    '''INPUT: a sokoban state that represents the start state and a timebound (number of seconds)'''
    '''OUTPUT: A goal state (if a goal is found), else False as well as a SearchStats object'''
    '''implementation of iterative astar algorithm'''

    # create search engine
    wrapped_fval_function = (lambda sN: fval_function(sN, weight))
    search_eng = SearchEngine('custom')
    search_eng.init_search(initial_state, sokoban_goal_state, heur_fn,
                           wrapped_fval_function)

    # set up time and cost
    start_time = os.times()[0]
    end_time = start_time + timebound
    cost = [float("inf"), float("inf"), float("inf")]

    init_sol = search_eng.search(timebound)
    sol = init_sol

    # run until time is up
    while start_time < end_time:
        start_time = os.times()[0]
        time_left = end_time - start_time
        if init_sol[0] != False and init_sol[0].gval + heur_fn(sol[0]) <= cost[
            2]:
            cost = [init_sol[0].gval, heur_fn(sol[0]),
                    init_sol[0].gval + heur_fn(sol[0])]
            sol = init_sol
            # update cost and time for the new search
            init_sol = search_eng.search(time_left, cost)


    return sol


def iterative_gbfs(initial_state, heur_fn, timebound=5):  # only use h(n)
    # IMPLEMENT
    '''Provides an implementation of anytime greedy best-first search, as described in the HW1 handout'''
    '''INPUT: a sokoban state that represents the start state and a timebound (number of seconds)'''
    '''OUTPUT: A goal state (if a goal is found), else False'''
    '''implementation of iterative gbfs algorithm'''

    # create search engine
    search_eng = SearchEngine('best_first')
    search_eng.init_search(initial_state, sokoban_goal_state, heur_fn)

    # set up time and cost
    start_time = os.times()[0]
    end_time = start_time + timebound
    cost = [float("inf"), float("inf"), float("inf")]

    init_sol = search_eng.search(timebound)
    sol = init_sol

    while start_time < end_time:
        start_time = os.times()[0]
        time_left = end_time - start_time
        if init_sol[0] != False and init_sol[0].gval <= cost[0]:
            cost = [init_sol[0].gval, heur_fn(sol[0]),
                    init_sol[0].gval + heur_fn(sol[0])]
            sol = init_sol
            # update cost and time for the new search
            init_sol = search_eng.search(time_left, cost)

    return sol
