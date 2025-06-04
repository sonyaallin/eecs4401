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
  '''Have we reached a goal state?'''

  for car in state.vehicle_list:
    if car.is_goal:
      gv = car
  properties = state.get_board_properties()

  c = properties[0][1]
  r = properties[0][0]

  head = gv.loc
  if car.is_horizontal:
    if head[0] + gv.length - 1 >= c:
      tail = (head[0] + gv.length - 1 - c, head[1])
    else:
      tail = (head[0] + gv.length - 1, head[1])
  else:
    if head[1] + gv.length - 1 >= r:
      tail = (head[0], head[1] + gv.length - 1 - r)
    else:
      tail = (head[0], head[1] + gv.length - 1)

  if properties[2] == 'W' or properties[2] == 'N':
    if head == properties[1]:
      return True
  else:
    if tail == properties[1]:
      return True

  return False


#RUSH HOUR HEURISTICS
def heur_zero(state):
#IMPLEMENT  
  '''Zero Heuristic can be used to make A* search perform uniform cost search'''
  return 0 #replace this

def heur_min_moves(state):
  #IMPLEMENT
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

  goalv = []
  move1 = []
  move2 = []
  properties = state.get_board_properties()
  goal = properties[1]
  c = properties[0][1]
  r = properties[0][0]
  for car in state.vehicle_list:
    if car.is_goal:
      goalv.append(car)

  for gv in goalv:
    if gv.loc[0] != goal[0] and gv.loc[1] != goal[1]:
      return None

    head = gv.loc
    if gv.is_horizontal:
      if head[0] + gv.length - 1 >= c:
        tail = (head[0] + gv.length - 1 - c, head[1])
      else:
        tail = (head[0] + gv.length - 1, head[1])
    else:
      if head[1] + gv.length - 1 >= r:
        tail = (head[0], head[1] + gv.length - 1 - r)
      else:
        tail = (head[0], head[1] + gv.length - 1)
    if properties[2] == 'W' and gv.is_horizontal:
      if head == goal:
        return 0
      if head[0] >= goal[0]:
        move1.append(head[0] - goal[0])
        move2.append(c - head[0] + goal[0])
      else:
        move1.append(goal[0] - head[0])
        move2.append(head[0] + c - goal[0])
    elif properties[2] == 'E' and gv.is_horizontal:
      if tail == goal:
        return 0
      if tail[0] <= goal[0]:
        move1.append(goal[0] - tail[0])
        move2.append(tail[0] + c - goal[0])
      else:
        move1.append(tail[0] - goal[0])
        move2.append(c - tail[0] + goal[0])
    elif properties[2] == 'N' and not gv.is_horizontal:
      if head == goal:
        return 0
      if head[1] >= goal[1]:
        move1.append(head[1] - goal[1])
        move2.append(r - head[1] + goal[1])
      else:
        move1.append(goal[1] - head[1])
        move2.append(head[1] + r - goal[1])
    elif properties[2] == 'S' and not gv.is_horizontal:
      if tail == goal:
        return 0
      if tail[1] >= goal[1]:
        move1.append(tail[1] - goal[1])
        move2.append(r - tail[1] + goal[1])
      else:
        move1.append(goal[1] - tail[1])
        move2.append(tail[1] + r - goal[1])

  return min(min(move1), min(move2))

def check_if_block(state, posi):
  properties = state.get_board_properties()
  c = properties[0][1]
  r = properties[0][0]

  for car in state.vehicle_list:
    if not car.is_goal and car.is_horizontal:
      if car.loc[1] == posi[1]:
        for i in range(car.loc[0], car.loc[0] + car.length):
          if i >= c:
            if i - c == posi[0]:
              return True
          if i == posi[0]:
            return True
    elif not car.is_goal:
      if car.loc[0] == posi[0]:
        for i in range(car.loc[1], car.loc[1] + car.length):
          if i >= r:
            if i - r == posi[1]:
              return True
          if i == posi[1]:
            return True
  return False

def heur_alternate(state):
#IMPLEMENT
  '''a better heuristic'''
  '''INPUT: a rush hour state'''
  '''OUTPUT: a numeric value that serves as an estimate of the distance of the state to the goal.'''
  #heur_min_moves has an obvious flaw.
  #Write a heuristic function that improves a little upon heur_min_moves to estimate distance between the current state and the goal.
  #Your function should return a numeric value for the estimate of the distance to the goal.
  goalv = []
  move1 = []
  move2 = []
  properties = state.get_board_properties()
  goal = properties[1]
  c = properties[0][1]
  r = properties[0][0]
  for car in state.vehicle_list:
    if car.is_goal:
      goalv.append(car)
  for gv in goalv:
    if gv.loc[0] != goal[0] and gv.loc[1] != goal[1]:
      return None

    head = gv.loc
    if gv.is_horizontal:
      if head[0] + gv.length - 1 >= c:
        tail = (head[0] + gv.length - 1 - c, head[1])
      else:
        tail = (head[0] + gv.length - 1, head[1])
    else:
      if head[1] + gv.length - 1 >= r:
        tail = (head[0], head[1] + gv.length - 1 - r)
      else:
        tail = (head[0], head[1] + gv.length - 1)

    if properties[2] == 'W' and gv.is_horizontal:

      if head == goal:
        return 0

      block1 = 0
      block2 = 0

      if check_if_block(state, (goal[0], goal[1])):
        block2 += 1
        block1 += 1

      for i in range(min(head[0], goal[0]) + 1, max(head[0], goal[0])):
        if check_if_block(state, (i, goal[1])):
          block1 += 1
      for i in range(min(head[0], goal[0])):
        if check_if_block(state, (i, goal[1])):
          block2 += 1
      if max(head[0], goal[0]) != c - 1:
        for i in range(max(head[0], goal[0]) + 1, c):
          if check_if_block(state, (i, goal[1])):
            block2 += 1

      block = [block1, block2]


      if head[0] >= goal[0]:
        move1.append(head[0] - goal[0] + block[0])
        move2.append(c - head[0] + goal[0] + block[1])
      else:
        move1.append(goal[0] - head[0] + block[0])
        move2.append(head[0] + c - goal[0] + block[1])

    elif properties[2] == 'E' and gv.is_horizontal:
      if tail == goal:
        return 0

      block1 = 0
      block2 = 0

      if check_if_block(state, (goal[0], goal[1])):
        block2 += 1
        block1 += 1

      for i in range(min(tail[0], goal[0]) + 1, max(tail[0], goal[0])):
        if check_if_block(state, (i, goal[1])):
          block1 += 1
      for i in range(min(tail[0], goal[0])):
        if check_if_block(state, (i, goal[1])):
          block2 += 1
      if max(tail[0], goal[0]) != c - 1:
        for i in range(max(tail[0], goal[0]) + 1, c):
          if check_if_block(state, (i, goal[1])):
            block2 += 1

      block = [block1, block2]

      if tail[0] <= goal[0]:
        move1.append(goal[0] - tail[0] + block[0])
        move2.append(tail[0] + c - goal[0] + block[1])
      else:
        move1.append(tail[0] - goal[0] + block[0])
        move2.append(c - tail[0] + goal[0] + block[1])


    elif properties[2] == 'N' and not gv.is_horizontal:
      if head == goal:
        return 0

      block1 = 0
      block2 = 0

      if check_if_block(state, (goal[0], goal[1])):
        block2 += 1
        block1 += 1
      for i in range(min(head[1], goal[1]) + 1, max(head[1], goal[1])):
        if check_if_block(state, (goal[0], i)):
          block1 += 1
      for i in range(min(head[1], goal[1])):
        if check_if_block(state, (goal[0], i)):
          block2 += 1
      if max(head[1], goal[1]) != r - 1:
        for i in range(max(head[1], goal[1]) + 1, r):
          if check_if_block(state, (goal[0], i)):
            block2 += 1

      block = [block1, block2]

      if head[1] >= goal[1]:
        move1.append(head[1] - goal[1] + block[0])
        move2.append(r - head[1] + goal[1] + block[1])
      else:
        move1.append(goal[1] - head[1] + block[0])
        move2.append(head[1] + r - goal[1] + block[1])

    elif properties[2] == 'S' and not gv.is_horizontal:
      if tail == goal:
        return 0

      block1 = 0
      block2 = 0

      if check_if_block(state, (goal[0], goal[1])):
        block2 += 1
        block1 += 1

      for i in range(min(tail[1], goal[1]) + 1, max(tail[1], goal[1])):
        if check_if_block(state, (goal[0], i)):
          block1 += 1
      for i in range(min(tail[1], tail[1])):
        if check_if_block(state, (goal[0], i)):
          block2 += 1
      if max(tail[1], goal[1]) != r - 1:
        for i in range(max(tail[1], goal[1]) + 1, r):
          if check_if_block(state, (goal[0], i)):
            block2 += 1

      block = [block1, block2]

      if tail[1] >= goal[1]:
        move1.append(tail[1] - goal[1] + block[0])
        move2.append(r - tail[1] + goal[1] + block[1])
      else:
        move1.append(goal[1] - tail[1] + block[0])
        move2.append(tail[1] + r - goal[1] + block[1])

  return min(min(move1), min(move2))


def fval_function(sN, weight):
#IMPLEMENT  
  """
  Provide a custom formula for f-value computation for Anytime Weighted A star.
  Returns the fval of the state contained in the sNode.

  @param sNode sN: A search node (containing a rush hour state)
  @param float weight: Weight given by Anytime Weighted A star
  @rtype: float
  """
  return sN.gval + weight * sN.hval

  
  #Many searches will explore nodes (or states) that are ordered by their f-value.
  #For UCS, the fvalue is the same as the gval of the state. For best-first search, the fvalue is the hval of the state.
  #You can use this function to create an alternate f-value for states; this must be a function of the state and the weight.
  #The function must return a numeric f-value.
  #The value will determine your state's position on the Frontier list during a 'custom' search.
  #You must initialize your search engine object as a 'custom' search engine if you supply a custom fval function.

def anytime_weighted_astar(initial_state, heur_fn, weight=1., timebound = 10):
#IMPLEMENT
  '''Provides an implementation of anytime weighted a-star, as described in the HW1 handout'''
  '''INPUT: a rush hour state that represents the start state and a timebound (number of seconds)'''
  '''OUTPUT: A goal state (if a goal is found), else False'''
  '''implementation of weighted astar algorithm'''

  def fval_wrapped(sN):
    return fval_function(sN, weight)
  result = True
  se = SearchEngine('custom', 'full')
  se.init_search(initial_state, rushhour_goal_fn, heur_fn, fval_wrapped)
  starttime = os.times()[0]
  final = se.search(timebound=timebound)
  remaintime = timebound - (os.times()[0] - starttime)
  if final == False:
     return False
  while result:
     starttime = os.times()[0]
     result = se.search(costbound=(final.gval, final.gval, final.gval), timebound=remaintime)
     remaintime -= os.times()[0] - starttime
     if result != False:
        if result.gval < final.gval:
           final = result

  return final


def anytime_gbfs(initial_state, heur_fn, timebound = 10):
#IMPLEMENT  
  '''Provides an implementation of anytime greedy best-first search, as described in the HW1 handout'''
  '''INPUT: a rush hour state that represents the start state and a timebound (number of seconds)'''
  '''OUTPUT: A goal state (if a goal is found), else False'''
  '''implementation of anytime greedybfs algorithm'''

  result = True
  se = SearchEngine('best_first', 'full')
  se.init_search(initial_state, rushhour_goal_fn, heur_fn)
  starttime = os.times()[0]
  final = se.search(timebound=timebound)
  remaintime = timebound - (os.times()[0] - starttime)
  if final == False:
    return False
  while result:
    starttime = os.times()[0]
    result = se.search(costbound=(final.gval, final.gval, 2 * final.gval), timebound=remaintime)
    remaintime -= os.times()[0] - starttime
    if result != False:
      if result.gval < final.gval:
        final = result

  return final
