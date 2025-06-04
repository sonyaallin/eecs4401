#   Look for #IMPLEMENT tags in this file. These tags indicate what has
#   to be implemented to complete the Rush Hour domain.

#   You may add only standard python imports (numpy, itertools are both ok).
#   You may not remove any imports.
#   You may not import or otherwise source any of your own files.

import os  # you will likely want this for timing functions
import math # for infinity
from search import *  # for search engines
from rushhour import *

def get_vertical_cars(state, red_car, exit_direction):
    '''
    This function is used to find the number of vertical cars that are blocking the red car from exiting the board.
    If the car is vertical, then we need to check the column.
    '''
    count = 0;
    board = get_board(state.get_vehicle_statuses(), state.board_properties)
    for i in range(0, state.board_properties[0][1] - 1):
        if exit_direction == 'N' or exit_direction == 'S':
            if board[red_car[1][0]][i] == '.':
                count += 1
    return count

def get_horizontal_cars(state, red_car, exit_direction): 
    '''
    This function is used to find the number of horizontal cars that are blocking the red car from exiting the board.
    If the car is horizontal, then we need to check the row.
    '''
    count = 0;
    board = get_board(state.get_vehicle_statuses(), state.board_properties)
    for i in range(0, state.board_properties[0][0] - 1):
        if exit_direction == 'W' or exit_direction == 'E':
            if board[i][red_car[1][1]] == '.':
                count += 1
    return 0

def get_red_cars(state):
    '''
    This function is used to find the all red cars in the board.
    '''
    red_cars = []
    for car in state.get_vehicle_statuses():
        if car[4]:
            red_cars.append(car)
    return red_cars

def get_car_lst(car, board_size):
    '''
    This function is used to find the all part of the car in the board.
    '''
    (m, n) = board_size
    red_car_lst = []
    red_car_lst.append(car[1])
    for i in range(1, car[2]):
        if car[3]:
            # This car is horizontal
            red_car_lst.append(((car[1][0] + i) % n, car[1][1]))
        else:
            # This car is vertical
            red_car_lst.append((car[1][0], (car[1][1] + i) % m))
    return red_car_lst
            

# RUSH HOUR GOAL TEST
def rushhour_goal_fn(state): 
    # IMPLEMENT
    '''a Rush Hour Goal Test'''
    '''INPUT: a parking state'''
    '''OUTPUT: True, if satisfies the goal, else false.'''
    board_size = state.board_properties[0]
    red_cars = get_red_cars(state)
    for red_car in red_cars:
        red_car_lst = get_car_lst(red_car, board_size)
        exit_entrance = state.board_properties[1]
        exit_direction = state.board_properties[2]
        if exit_direction == 'N':
            if not red_car[3]:
                if red_car[1] == exit_entrance:
                    return True
        elif exit_direction == 'S':
            if not red_car[3]:
                if red_car_lst[-1] == exit_entrance:
                    return True
        elif exit_direction == 'W':
            if red_car[3]:
                if red_car[1] == exit_entrance:
                    return True
        elif exit_direction == 'E':
            if red_car[3]:
                if red_car_lst[-1] == exit_entrance:
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

    # The basic idea is to find the number of cars that are blocking the red car from exiting the board. Each blocked car will cost at least 1 move.
    # Additionally, if the goal direction is N OR E, then it should be closer to the head of car, the tail direction move should add the cost of the len of the car.
    # If the goal direction is S OR W, then it should be closer to the tail of car, the head direction move should add the cost of the len of the car.
    # Furthormore, if the red car is on the exit entrance, then determing if head is closer or the tail is closer, append the small one into the list.
    board_size = state.board_properties[0]
    red_cars = get_red_cars(state)
    lsit_of_min = []
    for red_car in red_cars:
        red_car_lst = get_car_lst(red_car, board_size)
        exit_entrance = state.board_properties[1]
        exit_direction = state.board_properties[2]
        red_car_head = red_car[1]
        red_car_tail = red_car_lst[-1]
        MOVES1 = math.inf
        MOVES2 = math.inf
        if exit_direction == 'N':
            block_car = get_vertical_cars(state, red_car, state.board_properties[2])
            if not red_car[3]:
                MOVES1 = (board_size[0] + red_car_head[1] - exit_entrance[1]) % board_size[0]
                MOVES2 = (board_size[0] + red_car_tail[1] - exit_entrance[1]) % board_size[0]
                MOVES2 += red_car[2] - 1 + block_car
            lsit_of_min.append(min(MOVES1, MOVES2))
        elif exit_direction == 'S':
            block_car = get_vertical_cars(state, red_car, state.board_properties[2])
            if not red_car[3]:
                MOVES1 = (board_size[0] + red_car_head[1] - exit_entrance[1]) % board_size[0]
                MOVES2 = (board_size[0] + red_car_tail[1] - exit_entrance[1]) % board_size[0]
                MOVES1 += red_car[2] - 1 + block_car
            lsit_of_min.append(min(MOVES1, MOVES2))
        elif exit_direction == 'W':
            block_car = get_horizontal_cars(state, red_car, state.board_properties[2])
            if red_car[3]:
                MOVES1 = (board_size[1] + red_car_head[0] - exit_entrance[0]) % board_size[1]
                MOVES2 = (board_size[1] + red_car_tail[0] - exit_entrance[0]) % board_size[1]
                MOVES2 += red_car[2] - 1 + block_car
            lsit_of_min.append(min(MOVES1, MOVES2))
        elif exit_direction == 'E':
            block_car = get_horizontal_cars(state, red_car, state.board_properties[2])
            if red_car[3]:
                MOVES1 = (board_size[1] + red_car_head[0] - exit_entrance[0]) % board_size[1]
                MOVES2 = (board_size[1] + red_car_tail[0] - exit_entrance[0]) % board_size[1]
                MOVES1 += red_car[2] - 1 + block_car
            lsit_of_min.append(min(MOVES1, MOVES2))
        for i in range(0, len(red_car_lst)):
            car_part = red_car_lst[i]
            if car_part == exit_entrance:
                half = len(red_car_lst) // 2
                if i <= half:
                    lsit_of_min.append(i)
                else:
                    lsit_of_min.append(len(red_car_lst) - i)
    return min(lsit_of_min)

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

    board_size = state.board_properties[0]
    red_cars = get_red_cars(state)
    lsit_of_min = []
    for red_car in red_cars:
        red_car_lst = get_car_lst(red_car, board_size)
        exit_entrance = state.board_properties[1]
        exit_direction = state.board_properties[2]
        red_car_head = red_car[1]
        red_car_tail = red_car_lst[-1]
        MOVES1 = math.inf
        MOVES2 = math.inf
        if exit_direction == 'N':
            if not red_car[3]:
                MOVES1 = (board_size[0] + red_car_head[1] - exit_entrance[1]) % board_size[0]
                MOVES2 = (board_size[0] + red_car_tail[1] - exit_entrance[1]) % board_size[0]
            lsit_of_min.append(min(MOVES1, MOVES2))
        elif exit_direction == 'S':
            if not red_car[3]:
                MOVES1 = (board_size[0] + red_car_head[1] - exit_entrance[1]) % board_size[0]
                MOVES2 = (board_size[0] + red_car_tail[1] - exit_entrance[1]) % board_size[0]
            lsit_of_min.append(min(MOVES1, MOVES2))
        elif exit_direction == 'W':
            if red_car[3]:
                MOVES1 = (board_size[1] + red_car_head[0] - exit_entrance[0]) % board_size[1]
                MOVES2 = (board_size[1] + red_car_tail[0] - exit_entrance[0]) % board_size[1]
            lsit_of_min.append(min(MOVES1, MOVES2))
        elif exit_direction == 'E':
            if red_car[3]:
                MOVES1 = (board_size[1] + red_car_head[0] - exit_entrance[0]) % board_size[1]
                MOVES2 = (board_size[1] + red_car_tail[0] - exit_entrance[0]) % board_size[1]
            lsit_of_min.append(min(MOVES1, MOVES2))
        for car_part in red_car_lst:
            if car_part == exit_entrance:
                lsit_of_min.append(0)
    return min(lsit_of_min)


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
    return sN.gval + weight * sN.hval
    


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
    return (1/(2*weight))*(sN.gval+sN.hval+math.sqrt((sN.gval+sN.hval)**2+4*weight*(weight-1)*sN.hval**2))

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
    return (1/(2*weight))*(sN.gval+(2*weight-1)*sN.hval+math.sqrt((sN.gval-sN.hval)**2+4*weight*sN.gval*sN.hval))

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
    # se.trace_on(2)
    se.init_search(initial_state, rushhour_goal_fn, heur_fn, lambda sN: fval_function(sN, weight))
    return se.search(timebound, costbound)
    

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
    time = os.times()[0]
    given_time = timebound + time
    se = SearchEngine('custom', 'full')
    se.init_search(initial_state, rushhour_goal_fn, heur_fn, lambda sN: fval_function(sN, weight))
    result = se.search(timebound)
    cost = (float("inf"), float("inf"), float("inf"))
    time = os.times()[0]
    while time < given_time:
        while result[0]:
            start = os.times()[0]
            weight -= 0.01
            se.init_search(initial_state, rushhour_goal_fn, heur_fn, lambda sN: fval_function(sN, weight))
            bound_gval = result[0].gval
            cost = (float("inf"), float("inf"), bound_gval)
            se.init_search(initial_state, rushhour_goal_fn, heur_fn, lambda sN: fval_function(sN, weight))
            result = se.search(timebound, cost)
            end = os.times()[0]
            time += end - start
            if time >= given_time:
                break
    return result

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
    time = os.times()[0]
    given_time = timebound + time
    se = SearchEngine('custom', 'full')
    se.init_search(initial_state, rushhour_goal_fn, heur_fn)
    result = se.search(timebound)
    cost = (float("inf"), float("inf"), float("inf"))
    time = os.times()[0]
    while time < given_time:
        while result[0]:
            start = os.times()[0]
            se.init_search(initial_state, rushhour_goal_fn, heur_fn)
            bound_val = result[0].gval
            # cost = (bound_gval, float("inf"), float("inf"))
            cost = (float("inf"), bound_val, float("inf"))
            se.init_search(initial_state, rushhour_goal_fn, heur_fn)
            result = se.search(timebound, cost)
            end = os.times()[0]
            time += end - start
            if time >= given_time:
                break
    return result

