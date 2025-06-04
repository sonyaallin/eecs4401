#   Look for #IMPLEMENT tags in this file. These tags indicate what has
#   to be implemented to complete the Rush Hour domain.

#   You may add only standard python imports (numpy, itertools are both ok).
#   You may not remove any imports.
#   You may not import or otherwise source any of your own files.

import os  # you will likely want this for timing functions
import math # for infinity
from search import *  # for search engines
from rushhour import *

# RUSH HOUR GOAL TEST
def rushhour_goal_fn(state): 
    # IMPLEMENT
    '''a Rush Hour Goal Test'''
    '''INPUT: a parking state'''
    '''OUTPUT: True, if satisfies the goal, else false.'''
    x = state.get_board_properties()[0][1]
    y = state.get_board_properties()[0][0]   
    goal_loc = state.get_board_properties()[1]
    goal_dir = state.get_board_properties()[2]

    for vehicle in state.get_vehicle_statuses():
        if not possible_ori(goal_dir, vehicle[3], vehicle[4]):
            continue
        head_loc = vehicle[1]
        tail_loc = find_tail(vehicle, x, y)
        if goal_dir == 'W' and head_loc == goal_loc:
            return True
        if goal_dir == 'E' and tail_loc == goal_loc:
            return True
        if goal_dir == 'N' and head_loc == goal_loc:
            return True
        if goal_dir == 'S' and tail_loc == goal_loc:
            return True
    return False

# Helper functions
def find_tail(vehicle, x, y):
    head_loc = vehicle[1]         
    if vehicle[3]:
        if head_loc[0] + vehicle[2] - 1 >= x:
            return (head_loc[0] + vehicle[2] - 1 - x, head_loc[1])
        else:
            return (head_loc[0] + vehicle[2] - 1, head_loc[1])
    else:
        if head_loc[1] + vehicle[2] - 1 >= y:
            return (head_loc[0], head_loc[1] + vehicle[2] - 1 - y)
        else:
            return (head_loc[0], head_loc[1] + vehicle[2] - 1)

def possible_ori(d, is_hori, is_goal):
    if is_goal and is_hori and (d == 'W' or d == 'E'):
        return True
    if is_goal and not is_hori and (d == 'N' or d == 'S'):
        return True
    return False

def blocking_car(vehicle, goal_loc, goal_dir, head_loc, tail_loc, x, y):
    if goal_dir == 'W' and goal_dir == 'E':
        if not vehicle[3]:
            if head_loc[1] <= tail_loc[1]:
                if head_loc[1] <= goal_loc[1] <= tail_loc[1]:
                    return [head_loc[0]]
                else:
                    return False
            else:
                if goal_loc[1] <= tail_loc[1] or goal_loc[1] >= head_loc[1]:
                    return [head_loc[0]]
                else:
                    return False
        else:
            if head_loc[1] == goal_loc[1]:
                result = []
                for i in range(vehicle[2]):
                    if i + head_loc[0] >= x:
                        result.append(i + head_loc[0] - x)
                    else:
                        result.append(i + head_loc[0])
                return result
            else:
                return False
    else:
        if vehicle[3]:
            if head_loc[0] <= tail_loc[0]:
                if head_loc[0] <= goal_loc[0] <= tail_loc[0]:
                    return [head_loc[1]]
                else:
                    return False
            else:
                if goal_loc[0] <= tail_loc[0] or goal_loc[0] >= head_loc[0]:
                    return [head_loc[1]]
                else:
                    return False
        else:
            if head_loc[0] == goal_loc[0]:
                result = []
                for i in range(vehicle[2]):
                    if i + head_loc[1] >= y:
                        result.append(i + head_loc[1] - y)
                    else:
                        result.append(i + head_loc[1])
                return result
            else:
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
    x = state.get_board_properties()[0][1]
    y = state.get_board_properties()[0][0]
    goal_loc = state.get_board_properties()[1]
    goal_dir = state.get_board_properties()[2]

    # The basic idea is orientation + # of blocked car:
    #   Orientation: if E or S, the tail of goal car should be on the goal location.
    #                Otherwise, the head of goal car should be on the goal location.
    #   #(number) of blocked car: We want to check if a car blocked the road between the goal car and goal.
    #                             This is because some direction with smaller distance but with much more blocking
    #                             cars. This direction will have more moves than other directions. 
    min_dist = []
    b_car = []
    for vehicle in state.get_vehicle_statuses():
        head_loc = vehicle[1]
        tail_loc = find_tail(vehicle, x, y)
        # Check if the car is goal or not, check the exit is on one line with the goal car.
        if not possible_ori(goal_dir, vehicle[3], vehicle[4]):
            # If it is not goal car, check if one part of the car is blocked on the road.
            # More specifically, the helper functions have four cases:
            #       E or W:
            #               **bbb**c***W*****de**
            #               In this case, there are 4 cars blocked the roads. Car b is horizontal
            #               , I count the length as blocking numbers.
            #       N or S:
            #               vertical version of above case.
            #And, I record each blocking index for comparing the blocking numbers on each direction.
            #For example:
            #           **W*b
            #This case will return a list [4] which means index 4 has 1 blocked car.
            temp = blocking_car(vehicle, goal_loc, goal_dir, head_loc, tail_loc, x, y)
            if temp:
                b_car.extend(temp)
            continue
        
        if vehicle[3] and goal_loc[1] == head_loc[1]:
            # The tail of car
            if goal_dir == 'E':
                # The goal is at the left side of the goal car
                if goal_loc[0] <= tail_loc[0]:
                    # Calculate the the number of blocked cars on two sides of the tail 
                    # of the goal car.
                    # For example:
                    #      **a***E***bc**d*gg*
                    # left = 3(b, c, d), right = 1(a)
                    left = 0
                    right = 0
                    for i in b_car:
                        if i <= tail_loc[0] and i >= goal_loc[0]:
                            left += 1
                        if i > tail_loc[0] or i < goal_loc[0]:
                            right += 1
                    min_dist.append(tail_loc[0] - goal_loc[0] + left)
                    min_dist.append(x - tail_loc[0] + goal_loc[0] + right)
                # The goal is at the right side of the goal car
                else:
                    # Calculate the the number of blocked cars on two sides of the tail 
                    # of the goal car.
                    # For example:
                    #      **a***E***bc**d*gg*
                    # left = 3(b, c, d), right = 1(a)
                    left = 0
                    right = 0
                    for i in b_car:
                        if i <= goal_loc[0] and i >= tail_loc[0]:
                            right += 1
                        if i > goal_loc[0] or i < tail_loc[0]:
                            left += 1
                    min_dist.append(goal_loc[0] - tail_loc[0] + right)
                    min_dist.append(x - goal_loc[0] + tail_loc[0] + left)
            # West: the head of the car
            else:
                # The goal is at the left side of the goal car
                if goal_loc[0] <= head_loc[0]:
                    # Calculate the the number of blocked cars on two sides of the tail 
                    # of the goal car.
                    # For example:
                    #      **a***W***bc**d*gg*
                    # left = 3(b, c, d), right = 1(a)
                    left = 0
                    right = 0
                    for i in b_car:
                        if i <= head_loc[0] and i >= goal_loc[0]:
                            left += 1
                        if i > head_loc[0] or i < goal_loc[0]:
                            right += 1
                    min_dist.append(head_loc[0] - goal_loc[0] + left)
                    min_dist.append(x - head_loc[0] + goal_loc[0] + right)
                # The goal is at the right side of the goal car
                else:
                    # Calculate the the number of blocked cars on two sides of the tail 
                    # of the goal car.
                    # For example:
                    #      **a***W***bc**d*gg*
                    # left = 3(b, c, d), right = 1(a)
                    left = 0
                    right = 0
                    for i in b_car:
                        if i <= goal_loc[0] and i >= head_loc[0]:
                            right += 1
                        if i > goal_loc[0] or i < head_loc[0]:
                            left += 1
                    min_dist.append(goal_loc[0] - head_loc[0] + right)
                    min_dist.append(x - goal_loc[0] + head_loc[0] + left)
        if not vehicle[3] and goal_loc[0] == head_loc[0]:
            # The head of the goal car
            if goal_dir == 'N':
                # The goal is at the up side of the goal car
                if goal_loc[1] <= head_loc[1]:
                    # Calculate the the number of blocked cars on two sides of the tail 
                    # of the goal car.
                    # For example:
                    #      **a***N***bc**d*gg*
                    # up = 3(b, c, d), down = 1(a)
                    up = 0
                    down = 0
                    for i in b_car:
                        if goal_loc[1] <= i <= head_loc[1]:
                            up += 1
                        if i < goal_loc[1] or i > head_loc[1]:
                            down += 1
                    min_dist.append(head_loc[1] - goal_loc[1] + up)
                    min_dist.append(y - head_loc[1] + goal_loc[1] + down)
                # The goal is at the down side of the goal car
                else:
                    # Calculate the the number of blocked cars on two sides of the tail 
                    # of the goal car.
                    # For example:
                    #      **a***N***bc**d*gg*
                    # up = 3(b, c, d), down = 1(a)
                    up = 0
                    down = 0
                    for i in b_car:
                        if head_loc[1] <= i <= goal_loc[1]:
                            down += 1
                        if i < head_loc[1] or i > goal_loc[1]:
                            up += 1
                    min_dist.append(goal_loc[1] - head_loc[1] + down)
                    min_dist.append(y - goal_loc[1] + head_loc[1] + up)
            #South: The tail of the goal car
            else:
                # The goal is at the up side of the goal car
                if goal_loc[1] <= tail_loc[1]:
                    # Calculate the the number of blocked cars on two sides of the tail 
                    # of the goal car.
                    # For example:
                    #      **a***W***bc**d*gg*
                    # up = 3(b, c, d), down = 1(a)
                    up = 0
                    down = 0
                    for i in b_car:
                        if goal_loc[1] <= i <= tail_loc[1]:
                            up += 1
                        if i < goal_loc[1] or i > tail_loc[1]:
                            down += 1
                    min_dist.append(tail_loc[1] - goal_loc[1] + up)
                    min_dist.append(y - tail_loc[1] + goal_loc[1] + down)
                # The goal is at the down side of the goal car
                else:
                    # Calculate the the number of blocked cars on two sides of the tail 
                    # of the goal car.
                    # For example:
                    #      **a***W***bc**d*gg*
                    # up = 3(b, c, d), down = 1(a)
                    up = 0
                    down = 0
                    for i in b_car:
                        if tail_loc[1] <= i <= goal_loc[1]:
                            down += 1
                        if i < tail_loc[1] or i > goal_loc[1]:
                            up += 1
                    min_dist.append(goal_loc[1] - tail_loc[1] + down)
                    min_dist.append(y - goal_loc[1] + tail_loc[1] + up)
    return min(min_dist)
        
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
    x = state.get_board_properties()[0][1]
    y = state.get_board_properties()[0][0]
    goal_loc = state.get_board_properties()[1]
    goal_dir = state.get_board_properties()[2]

    min_dist = []
    for vehicle in state.get_vehicle_statuses():
        if not possible_ori(goal_dir, vehicle[3], vehicle[4]):
            continue
        head_loc = vehicle[1]
        tail_loc = find_tail(vehicle, x, y)
        if vehicle[3] and goal_loc[1] == head_loc[1]:
            if goal_loc[0] <= head_loc[0]:
                min_dist.append(head_loc[0] - goal_loc[0])
                min_dist.append(x - head_loc[0] + goal_loc[0])
            else:
                min_dist.append(goal_loc[0] - head_loc[0])
                min_dist.append(x - goal_loc[0] + head_loc[0])
            if goal_loc[0] <= tail_loc[0]:
                min_dist.append(tail_loc[0] - goal_loc[0])
                min_dist.append(x - tail_loc[0] + goal_loc[0])
            else:
                min_dist.append(goal_loc[0] - tail_loc[0])
                min_dist.append(x - goal_loc[0] + tail_loc[0])
        if not vehicle[3] and goal_loc[0] == head_loc[0]:
            if goal_loc[1] <= head_loc[1]:
                min_dist.append(head_loc[1] - goal_loc[1])
                min_dist.append(y - head_loc[1] + goal_loc[1])
            else:
                min_dist.append(goal_loc[1] - head_loc[1])
                min_dist.append(y - goal_loc[1] + head_loc[1])
            if goal_loc[1] <= tail_loc[1]:
                min_dist.append(tail_loc[1] - goal_loc[1])
                min_dist.append(y - tail_loc[1] + goal_loc[1])
            else:
                min_dist.append(goal_loc[1] - tail_loc[1])
                min_dist.append(y - goal_loc[1] + tail_loc[1])
    return min(min_dist)

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
    return (1 / (2 * weight)) * (sN.gval + sN.hval + math.sqrt(math.pow((sN.gval + sN.hval), 2) + 4 * weight * (weight - 1) * math.pow(sN.hval, 2)))

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
    return (1 / (2 * weight)) * (sN.gval + (2 * weight - 1) * sN.hval + math.sqrt(math.pow((sN.gval - sN.hval), 2) + 4 * weight * sN.gval * sN.hval))

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
    cus_search = SearchEngine('custom')
    cus_search.init_search(initial_state, rushhour_goal_fn, heur_fn, (lambda sN : fval_function(sN,weight)))
    return cus_search.search(timebound, costbound)
    

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
    curr_weight = weight
    curr_timebound = timebound
    curr_costbound = (float(math.inf), float(math.inf), float(math.inf))

    state, stats = False, None
    it_search = SearchEngine('custom')
    it_search.init_search(initial_state, rushhour_goal_fn, heur_fn, (lambda sN : fval_function(sN,curr_weight)))

    start = os.times()[0]
    state, stats = it_search.search(curr_timebound, curr_costbound)
    end = os.times()[0]

    curr_timebound -= (end - start)

    if state:
        # curr_weight = curr_weight * (1/2) 16/20
        # curr_weight = curr_weight * (1/3) 16/20
        # curr_weight = curr_weight * (1/4) 16/20
        curr_weight = curr_weight * (1/5)
        # curr_weight = curr_weight * (1/6) 16/20
        # curr_weight = curr_weight * (1/7) 16/20
        # curr_weight = curr_weight * (1/8) 16/20
        # curr_weight = curr_weight * (1/9) 16/20
        # curr_weight = curr_weight * (1/10) 16/20
        curr_costbound = (curr_costbound[0], curr_costbound[1], state.gval + heur_fn(state))

    temp_state, temp_stats = False, None
    while curr_timebound >= 0 and curr_weight > 0:
        # it_search.init_search(initial_state, rushhour_goal_fn, heur_fn, (lambda sN : fval_function(sN, curr_weight))) 16/20
        # it_search.init_search(initial_state, rushhour_goal_fn, heur_fn, (lambda sN : fval_function_XDP(sN, curr_weight))) 16/20
        # it_search.init_search(initial_state, rushhour_goal_fn, heur_fn, (lambda sN : fval_function_XUP(sN, curr_weight))) 16/20
        it_search.init_search(initial_state, rushhour_goal_fn, heur_fn, (lambda sN : fval_function(sN, curr_weight)))
        start = os.times()[0]
        temp_state, temp_stats = it_search.search(curr_timebound, curr_costbound)
        end = os.times()[0]
        curr_timebound -= (end - start)

        
        if temp_state:
            if temp_state.gval + heur_fn(temp_state) < curr_costbound[2]:
                state, stats = temp_state, temp_stats
                curr_costbound = (curr_costbound[0], curr_costbound[1], temp_state.gval + heur_fn(temp_state))
        # curr_weight = curr_weight * (1/2) 16/20
        # curr_weight = curr_weight * (1/3) 16/20
        # curr_weight = curr_weight * (1/4) 16/20
        curr_weight = curr_weight * (1/5)
         # curr_weight = curr_weight * (1/6) 16/20
        # curr_weight = curr_weight * (1/7) 16/20
        # curr_weight = curr_weight * (1/8) 16/20
        # curr_weight = curr_weight * (1/9) 16/20
        # curr_weight = curr_weight * (1/10) 16/20
    return state, stats

#curr_costbound = (state.gval, heur_fn(state), float(math.inf))
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
    curr_timebound = timebound
    curr_costbound = (float(math.inf), float(math.inf), float(math.inf))

    state, stats = False, None
    it_search = SearchEngine('best_first')
    it_search.init_search(initial_state, rushhour_goal_fn, heur_fn)

    start = os.times()[0]
    state, stats = it_search.search(curr_timebound, curr_costbound)
    end = os.times()[0]

    curr_timebound -= (end - start)

    if state:
        curr_costbound = (state.gval, float(math.inf), float(math.inf))

    temp_state, temp_stats = False, None
    while curr_timebound >= 0:
        it_search.init_search(initial_state, rushhour_goal_fn, heur_fn)
        start = os.times()[0]
        temp_state, temp_stats = it_search.search(curr_timebound, curr_costbound)
        end = os.times()[0]
        curr_timebound -= (end - start)

        if temp_state:
            if temp_state.gval < curr_costbound[0]:
                curr_costbound = (temp_state.gval, curr_costbound[1], curr_costbound[2])
                state, stats = temp_state, temp_stats
    
    return state, stats



