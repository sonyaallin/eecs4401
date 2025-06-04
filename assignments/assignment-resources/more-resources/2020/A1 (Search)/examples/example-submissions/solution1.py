#   Look for #IMPLEMENT tags in this file. These tags indicate what has
#   to be implemented to complete the warehouse domain.

#   You may add only standard python imports---i.e., ones that are automatically
#   available on TEACH.CS
#   You may not remove any imports.
#   You may not import or otherwise source any of your own files

import os #for time functions
from search import * #for search engines
from rushhour import * #for Rush Hour specific classes and problems

#RUSH HOUR GOAL TEST
def rushhour_goal_fn(state): 
#IMPLEMENT
  '''Have we reached a goal state?'''

  # have to get vehicle
  # have to get the board
  board = state.get_board_properties()
  #print(board)
  #print(M)
  #M = state.board_size[1]
  (M,N) = board[0]
  goal_entrance = board[1] # (x, y) location
  goal_direction = board[2] #N/E/S/W indicating orientation
 
 
  for vehicle in state.get_vehicle_statuses():
    if vehicle[4]:
      (pos_x, pos_y) = vehicle[1] #location of the vehicle
      (goal_x, goal_y) = goal_entrance #location of the goal

      if (vehicle[3] == True): 
        #what do we do if its horizontal
        # means its either East or West
        # so now we have to look at the orientation of the goal.
        if goal_direction == 'W':
          if pos_x == goal_x:
            return True
          elif pos_x != goal_x:
            return False
        elif goal_direction == 'E':
          #tbh idk what would happen here
          if goal_x == 0:
            #vehicle[2] is the length of the vehicle bc that affects how much it moves
            if pos_x == M - 1 - (vehicle[2] - 2):
              return True
            else:
              return False
          else:
            if goal_x == pos_x + vehicle[2] - 1:
              return True
            else:
              return False
      else:
        #what do we do if its vertical
        if goal_direction == 'N':
          if pos_y == goal_y:
            return True
          elif pos_y != goal_y:
            return False
        elif goal_direction == 'S':
          #tbh idk what would happen here either
          if pos_y == 0:
            if pos_y == N - 1 - (vehicle[2] - 2):
              return True
            else:
              return False
          else: 
            if goal_y == pos_y + vehicle[2] - 1:
              return True
            else:
              return False      
  return False # last case, if we haven't reached anything

#RUSH HOUR HEURISTICS
def heur_zero(state):
#IMPLEMENT  - COMPLETE - literally just need to return 0 i guess
  '''Zero Heuristic can be used to make A* search perform uniform cost search'''
  return 0 

def heur_min_moves(state):
#IMPLEMENT - In Progress - GAH
  '''basic rushhour heuristic'''
  #An admissible heuristic is nice to have. Getting to the goal may require
  #many moves and each moves the goal vehicle one tile of distance.
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
  
  # base case: we are at the goal
  if (rushhour_goal_fn(state)):
    return 0

  # have to actually calculate move_1 and move_2
  moves_1 = 0 
  moves_2 = 0
  # intializing the board
  board = state.get_board_properties()
  (M,N) = board[0] # M rows, N cols, for personal reference
  goal_entrance = board[1]
  goal_dir = board[2]
  
  for vehicle in state.get_vehicle_statuses():
    (pos_x, pos_y) = vehicle[1]
    (goal_x, goal_y) = goal_entrance
    if vehicle[4]: #is goal
      v_h = ""
      if (vehicle[3] == True):
        v_h = "HORIZONTAL"
      else:
        v_h =  "VERTICAL"

      if (v_h == "HORIZONTAL"): 
        if (goal_dir == 'W'):
          if pos_x >= goal_x:
            moves_1 = pos_x - goal_x
            moves_2 = N - pos_x + goal_x
            return min(moves_1, moves_2)
          else:
            moves_1 = goal_x - pos_x
            moves_2 = N - goal_x + pos_x
            return min(moves_1, moves_2)
        elif (goal_dir == 'E'):
          end = pos_x + vehicle[2] - 1
          moves_1 = abs(goal_x - end)
          moves_2 = abs(N- abs(goal_x - end))
          return min(moves_1, moves_2)
      elif(v_h == "VERTICAL"):
        if (goal_dir == 'N'):
          if pos_y >= goal_y:
            moves_1 = pos_y - goal_y
            moves_2 = M - pos_y + goal_y
            return min(moves_1, moves_2)
          else:
            moves_1 = goal_y - pos_y
            moves_2 = M - goal_y + pos_y
            return min(moves_1, moves_2)
        elif (goal_dir == 'S'):
          end = pos_y + vehicle[2] - 1
          moves_1 = abs(goal_y - end)
          moves_2 = abs(M - abs(goal_y - end))
          return min(moves_1, moves_2)
  # ultimate goal: returning the minimum of moves one and two
  return min(moves_1, moves_2)


def heur_alternate(state):
#IMPLEMENT
  '''a better heuristic'''
  '''INPUT: a rush hour state'''
  '''OUTPUT: a numeric value that serves as an estimate of the distance of the state to the goal.'''
  #heur_min_moves has an obvious flaw.
  #Write a heuristic function that improves a little upon heur_min_moves to estimate distance between the current state and the goal.
  #Your function should return a numeric value for the estimate of the distance to the goal.
  # yeet = 0
  # return yeet

  board = state.get_board_properties()
  (M,N) = board[0] # M rows, N cols, for personal reference
  goal_entrance = board[1]
  goal_dir = board[2]
  manhattan_distance = 0 # set it to inifinity to start
  running_total = 0

  for vehicle in state.get_vehicle_statuses():
    (pos_x, pos_y) = vehicle[1]
    (goal_x, goal_y) = goal_entrance
    # check orientation of vehicle and check orientation of goal
        # if they are the same then check the axis
            # if goal axis and vehicle axis are the same add the vehicle length to running total
    if (vehicle[3] and (goal_dir == 'E' or goal_dir == 'W')): #aka horizontal
      if pos_x == goal_x:
        running_total += vehicle[2] # add the vehicle length
      # ok so now what if its not oriented in the same direction...
      # check its length against the y position (bc thats the only way it could intersect)
    elif (vehicle[3] and (goal_dir == 'N' or goal_dir == 'S')):
      tail_of_vehicle = pos_x + vehicle[2] - 1
      head_of_vehicle = pos_x
      for i in range(head_of_vehicle, tail_of_vehicle):
        placeholder = i
        if (placeholder == goal_y):
          running_total += 1
    # rinse and repeat for verical
    elif (not vehicle[3] and (goal_dir == 'N' or goal_dir == 'S')):
      if pos_y == goal_y:
        running_total += vehicle[2]
    elif (not vehicle[3] and (goal_dir == 'E' or goal_dir == 'W')):
      tail_of_vehicle = pos_y + vehicle[2] - 1
      head_of_vehicle = pos_y
      for i in range(head_of_vehicle, tail_of_vehicle):
        placeholder = i
        if (placeholder == goal_x):
          running_total += 1

    if vehicle[4]:
      manhattan_distance = abs(pos_x - goal_x) + abs(pos_y - goal_y)

  return manhattan_distance #+ running_total
  



def fval_function(sN, weight):
#IMPLEMENT  
  """
  Provide a custom formula for f-value computation for Anytime Weighted A star.
  Returns the fval of the state contained in the sNode.

  @param sNode sN: A search node (containing a rush hour state)
  @param float weight: Weight given by Anytime Weighted A star
  @rtype: float
  """
  
  #Many searches will explore nodes (or states) that are ordered by their f-value.
  #For UCS, the fvalue is the same as the gval of the state. For best-first search, the fvalue is the hval of the state.
  #You can use this function to create an alternate f-value for states; this must be a function of the state and the weight.
  #The function must return a numeric f-value.
  #The value will determine your state's position on the Frontier list during a 'custom' search.
  #You must initialize your search engine object as a 'custom' search engine if you supply a custom fval function.
  
  #f(node) = g(node)+w×h(node)
  #basic, formula given in the pdf
  return sN.gval + sN.hval*weight
  
  #return 0 #replace this

def anytime_weighted_astar(initial_state, heur_fn, weight=1., timebound = 10):
#IMPLEMENT  
  '''Provides an implementation of anytime weighted a-star, as described in the HW1 handout'''
  '''INPUT: a rush hour state that represents the start state and a timebound (number of seconds)'''
  '''OUTPUT: A goal state (if a goal is found), else False'''
  '''implementation of weighted astar algorithm'''

  search_engine = SearchEngine('custom', 'full')
  wrappedFn = (lambda sN: fval_function(sN,weight))
  search_engine.init_search(initial_state, rushhour_goal_fn, heur_fn, wrappedFn)

  soln = None
  f_val = None

  search_start = os.times()[0]
  search_end = search_start + timebound

  current = search_engine.search(timebound=timebound)

  if current: # not empty state

    f_val = current.gval + heur_fn(current)

    #updating the time left
    time_difference = search_end - os.times()[0]
    #setting up the soln
    soln = current

    while time_difference >= 0:

      new_time = os.times()[0]

      #updating the fval because thats what we care about
      new_soln = search_engine.search(time_difference,(float("inf"), float("inf"), f_val))

      time_difference = time_difference - (os.times()[0] - new_time)

      if new_soln:
        # calculate new fval
        f_val = new_soln.gval + heur_fn(new_soln)
        # set new soln
        soln = new_soln

    # once time is up return
    return soln
  else:
    # return false or none
    return False

  # while current time is less than the stop time
  # while os.times()[0] <= search_end:
  #   current = search_engine.search(search_end - os.times()[0], cost_bound)      

  #   if current:
  #     soln = current
  #     cost_bound = soln.fval + heur_fn(soln)
    
  #   if 
  
  # return 0 #replace this

def anytime_gbfs(initial_state, heur_fn, timebound = 10):
#IMPLEMENT  
  '''Provides an implementation of anytime greedy best-first search, as described in the HW1 handout'''
  '''INPUT: a rush hour state that represents the start state and a timebound (number of seconds)'''
  '''OUTPUT: A goal state (if a goal is found), else False'''
  '''implementation of anytime greedybfs algorithm'''
  # states
  soln = None
  current_state = None
  # initializations
  best_gval = 0
  first_time = True 
  # search engine
  seach_engine = SearchEngine('best_first', 'full')
  seach_engine.init_search(initial_state, rushhour_goal_fn, heur_fn)
  node = float("inf") 
  # we start with a time bound on the clock
  while timebound >= 0:

      if (first_time):

            #just search, we also don't have a costbound yet
            current_state = seach_engine.search(timebound) 
            soln = current_state
            if current_state: 
                best_gval = current_state.gval
            first_time = False

      elif (not first_time):
            # the path we are on is NOT optimal
            if (current_state): #and the current state is NOT empty
              current_gval = current_state.gval

              if current_gval < best_gval:
                  soln = current_state
                  best_gval = current_gval
                  #cost bound -> gval, hval, fval. but since this is BFS we only care about gval
                  current_state = seach_engine.search(timebound, (node, float("inf"), float("inf")))
              
              elif current_gval >= best_gval:
                  node = current_gval
                  current_state = seach_engine.search(timebound, (node, float("inf"), float("inf")))

      #must update the time left
      timebound = timebound - os.times()[0] + seach_engine.search_start_time

  return soln

