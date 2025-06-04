#   Look for #IMPLEMENT tags in this file. These tags indicate what has
#   to be implemented to complete the warehouse domain.

#   You may add only standard python imports---i.e., ones that are automatically
#   available on TEACH.CS
#   You may not remove any imports.
#   You may not import or otherwise source any of your own files

import os #for time functions
from search import * #for search engines
from rushhour import * #for Rush Hour specific classes and problems

#Rush hour GOAL TEST
def rushhour_goal_fn(state): #IMPLEMENT
    '''Have we reached a goal state?'''
    if state.board_properties[2] == 'N':
        for vehicle in state.vehicle_list:
            if (vehicle.is_goal and not vehicle.is_horizontal
                and vehicle.loc[0] == state.board_properties[1][0]
                and vehicle.loc[1] == state.board_properties[1][1]):
                return True
        return False
    elif state.board_properties[2] == 'S':
        for vehicle in state.vehicle_list:
            if (vehicle.is_goal and not vehicle.is_horizontal
                and vehicle.loc[0] == state.board_properties[1][0]
                and (vehicle.loc[1] + vehicle.length - 1) % state.board_properties[0][0] == state.board_properties[1][1]):
                return True
        return False
    elif state.board_properties[2] == 'W':
        for vehicle in state.vehicle_list:
            if (vehicle.is_goal and vehicle.is_horizontal
                and vehicle.loc[0] == state.board_properties[1][0]
                and vehicle.loc[1] == state.board_properties[1][1]):
                return True
        return False
    elif state.board_properties[2] == 'E':
        for vehicle in state.vehicle_list:
            if (vehicle.is_goal and vehicle.is_horizontal
                and (vehicle.loc[0] + vehicle.length - 1) % state.board_properties[0][1] == state.board_properties[1][0]
                and vehicle.loc[1] == state.board_properties[1][1]):
                return True
        return False
    else:
        raise Exception('invalid goal orientation')

#RUSH HOUR HEURISTICS
def heur_zero(state):
    '''Zero Heuristic can be used to make A* search perform uniform cost search'''
    return 0

def heur_min_moves(state):
#IMPLEMENT
    '''rushhour heuristic'''
    #We want an admissible heuristic. Getting to the goal requires
    #one move for each tile of distance.
    #Since the board wraps around, there are two different
    #directions that lead to the goal.
    #NOTE that we want an estimate of the number of ADDITIONAL
    #     moves required from our current state
    #1. Proceeding in the first direction, let MOVES1 =
    #   number of moves required to get to the goal if it were unobstructed
    #2. Proceeding in the second direction, let MOVES2 =
    #   number of moves required to get to the goal if it were unobstructed
    #
    #Our heuristic value is the minimum of MOVES1 and MOVES2 over all goal vehicles.
    #You should implement this heuristic function exactly, even if it is
    #tempting to improve it.
    distances = list()
    (board_size, goal_entrance, goal_direction) = state.board_properties
    for vehicle in state.vehicle_list:
        if vehicle.is_goal:
            # check if can reach goal
            if (vehicle.is_horizontal and
               (goal_direction == 'W' or
                goal_direction == 'E') and
                vehicle.loc[1] == goal_entrance[1]):
                if goal_direction == 'W':
                    # positive direction
                    distances.append((goal_entrance[0] - vehicle.loc[0]) % board_size[1])
                    # negative direction
                    distances.append((vehicle.loc[0] - goal_entrance[0]) % board_size[1])
                elif goal_direction == 'E':
                    # positive direction
                    distances.append((goal_entrance[0] - (vehicle.loc[0] + vehicle.length - 1)) % board_size[1])
                    # negative direction
                    distances.append(((vehicle.loc[0] + vehicle.length - 1) - goal_entrance[0]) % board_size[1])
                assert distances
            elif (not vehicle.is_horizontal and
               (goal_direction == 'N' or
                goal_direction == 'S') and
                vehicle.loc[0] == goal_entrance[0]):
                if goal_direction == 'N':
                    # positive direction
                    distances.append((goal_entrance[1] - vehicle.loc[1]) % board_size[0])
                    # negative direction
                    distances.append((vehicle.loc[1] - goal_entrance[1]) % board_size[0])
                elif goal_direction == 'S':
                    # positive direction
                    distances.append((goal_entrance[1] - (vehicle.loc[1] + vehicle.length - 1)) % board_size[0])
                    # negative direction
                    distances.append(((vehicle.loc[1] + vehicle.length - 1) - goal_entrance[1]) % board_size[0])
                assert distances
    return min(distances)

def heur_alternate(state):
#IMPLEMENT
    '''a better heuristic'''
    '''INPUT: a rush hour state'''
    '''OUTPUT: a numeric value that serves as an estimate of the distance of the state to the goal.'''
    #heur_manhattan_distance has flaws.
    #Write a heuristic function that improves upon heur_manhattan_distance to estimate distance between the current state and the goal.
    #Your function should return a numeric value for the estimate of the distance to the goal.
    return 0

def fval_function(sN, weight):
  """
  Provide a custom formula for f-value computation for Anytime Weighted A star.
  Returns the fval of the state contained in the sNode.

  @param sNode sN: A search node (containing a SokobanState)
  @param float weight: Weight given by Anytime Weighted A star
  @rtype: float
  """
  
  #Many searches will explore nodes (or states) that are ordered by their f-value.
  #For UCS, the fvalue is the same as the gval of the state. For best-first search, the fvalue is the hval of the state.
  #You can use this function to create an alternate f-value for states; this must be a function of the state and the weight.
  #The function must return a numeric f-value.
  #The value will determine your state's position on the Frontier list during a 'custom' search.
  #You must initialize your search engine object as a 'custom' search engine if you supply a custom fval function.
  return sN.gval + weight*sN.hval

def anytime_weighted_astar(initial_state, heur_fn, weight=1., timebound = 10):
  '''Provides an implementation of anytime weighted a-star, as described in the HW1 handout'''
  '''INPUT: a sokoban state that represents the start state and a timebound (number of seconds)'''
  '''OUTPUT: A goal state (if a goal is found), else False'''
  '''implementation of weighted astar algorithm'''
  start_time = os.times()[0]
  time_remaining = timebound
  goal_reached = False
  lowset_cost = float("inf")
  wrapped_fval_function = (lambda sN: fval_function(sN, weight))

  se = SearchEngine('custom', 'full')
  se.init_search(initial_state, rushhour_goal_fn, heur_fn, wrapped_fval_function)
  
  while time_remaining > 0:
    if goal_reached == False:
        solution = se.search(time_remaining)
        time_remaining -= (os.times()[0] - start_time)
        if solution:
            goal_reached = True

    if goal_reached:
        if solution.gval + heur_fn(solution) < lowset_cost:
          lowset_cost = solution.gval + heur_fn(solution)
        new_sol = se.search(time_remaining, (float("inf"), float("inf"), lowset_cost))
        time_remaining = timebound - (os.times()[0] - start_time)
        if new_sol and new_sol.gval + heur_fn(new_sol) < lowset_cost:
          lowset_cost = new_sol.gval
          solution = new_sol

  return solution

def anytime_gbfs(initial_state, heur_fn, timebound = 10):
  '''Provides an implementation of anytime greedy best-first search, as described in the HW1 handout'''
  '''INPUT: a sokoban state that represents the start state and a timebound (number of seconds)'''
  '''OUTPUT: A goal state (if a goal is found), else False'''
  '''implementation of anytime greedybfs algorithm'''

  start_time = os.times()[0]
  time_remaining = timebound
  goal_reached = False
  lowset_cost = float("inf")

  se = SearchEngine('best_first', 'full')
  se.init_search(initial_state, rushhour_goal_fn, heur_fn)

  time_remaining -= (os.times()[0] - start_time)
  
  while time_remaining > 0:
    if goal_reached == False:
        solution = se.search(time_remaining)
        time_remaining -= (os.times()[0] - start_time)
        if solution:
            goal_reached = True

    if goal_reached:
        #print("solution found at time {}".format((os.times()[0] - start_time)))
        if solution.gval < lowset_cost:
            lowset_cost = solution.gval
        new_sol = se.search(time_remaining, (lowset_cost, float("inf"), float("inf")))
        time_remaining = timebound - (os.times()[0] - start_time)
        if new_sol and new_sol.gval < lowset_cost:
            lowset_cost = new_sol.gval
            solution = new_sol

  return solution

