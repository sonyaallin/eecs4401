#   Look for #IMPLEMENT tags in this file. These tags indicate what has
#   to be implemented to complete the warehouse domain.

#   You may add only standard python imports---i.e., ones that are automatically
#   available on TEACH.CS
#   You may not remove any imports.
#   You may not import or otherwise source any of your own files

import os #for time functions
from search import StateSpace,sNode, Open,SearchEngine #for search engines
from rushhour import * #for Rush Hour specific classes and problems

#RUSH HOUR GOAL TEST
def rushhour_goal_fn(state): 
#IMPLEMENT
  '''Have we reached a goal state?'''
  #get_vehicle_statuses() ==> [vehicle.name, vehicle.loc, vehicle.length, vehicle.is_horizontal, vehicle.is_goal]'''
  #get_board_properties() ==> (board_size, goal_entrance, goal_direction)'''
  
  (board_size, goal_loc, direction)  = Rushhour.get_board_properties(state) #get board and goal info 
  V_front, V_tail = find_vehicle_head_and_tail(find_goal_vehicle(state),board_size)  #Helper function for vehicle head and tail 
  
  result = None
  if direction in ("N" ,"W"):
      result =  V_front == goal_loc
  else: #elif direction == "S" or "E":
      result  = V_tail == goal_loc


  return result #replace this

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
  
  
  goal_vehicle = find_goal_vehicle(state) #Helper function for find goal

  (board_size, goal_loc, direction)  = Rushhour.get_board_properties(state) #get board and goal info
  
  V_front, V_tail = find_vehicle_head_and_tail(goal_vehicle,board_size) #Helper function for vehicle head and tail 


  if direction in [ "N" , "W"]:
      if direction  == "N":
          result = min((abs(V_front[1]-goal_loc[1])),(board_size[0]-abs(V_front[1]-goal_loc[1])))
      else:
          result = min((abs(V_front[0]-goal_loc[0])),(board_size[1]-abs(V_front[0]-goal_loc[0])))


  else: 
      if direction == "S":
          result = min((abs(V_tail[1]-goal_loc[1])),(board_size[0]-abs(V_tail[1]-goal_loc[1])))

      else:
          result = min((abs(V_tail[0]-goal_loc[0])),(board_size[1]-abs(V_tail[0]-goal_loc[0])))

                
  
  
  
  return result #replace this



def heur_alternate(state):
    
#IMPLEMENT
  '''a better heuristic'''
  '''INPUT: a rush hour state'''
  '''OUTPUT: a numeric value that serves as an estimate of the distance of the state to the goal.'''
  #heur_min_moves has an obvious flaw.
  #Write a heuristic function that improves a little upon heur_min_moves to estimate distance between the current state and the goal.
  #Your function should return a numeric value for the estimate of the distance to the goal.
  
  #get_vehicle_statuses() ==> [vehicle.name, vehicle.loc, vehicle.length, vehicle.is_horizontal, vehicle.is_goal]'''
  #get_board_properties() ==> (board_size, goal_entrance, goal_direction)'''
  #vehicle,board_size, goal_loc, direction,path1,path2,goal_vehicle
  
  vs = Rushhour.get_vehicle_statuses(state)
  (board_size, goal_loc, direction)  = Rushhour.get_board_properties(state)
  path1,path2 = heur_min_moves_2(state)
  goal_vehicle = find_goal_vehicle(state)


  space=[]
  blocker = 0
  path1_vehicle = 0
  path2_vehicle = 0
  result = None
    
  for vehicle in vs:
        if path1<path2:
            if direction in ("N" ,"S"):
                if vehicle[-1] == True:
                    if vehicle[1][1] in range (min(goal_loc[1],goal_vehicle[1][1]),max(goal_loc[1],goal_vehicle[1][1])):
                        for i in range(vehicle[2]):
                            space.append((vehicle[1][0]+i)%(board_size[1]))
                        if  goal_loc[0] in space:
                            blocker += 1
                            
        
            else:
                if vehicle[-1] != True:
                    if vehicle[1][0] in range (min(goal_loc[0],goal_vehicle[1][0]),max(goal_loc[1],goal_vehicle[1][0])):
                        for i in range(vehicle[2]):
                            space.append((vehicle[1][1]+i)%(board_size[0]))
                        if  goal_loc[1] in space:
                            blocker += 1
           
        elif path1>path2:
            if direction in ("N" ,"S"):
                if vehicle[-1] == True:
                    if vehicle[1][1] not in range (min(goal_loc[1],goal_vehicle[1][1]),max(goal_loc[1],goal_vehicle[1][1])):
                        for i in range(vehicle[2]):
                            space.append((vehicle[1][0]+i)%(board_size[1]))
                        if  goal_loc[0] in space:
                            blocker += 1
            else:
                if vehicle[-1] != True:
                    if vehicle[1][0] not in range (min(goal_loc[0],goal_vehicle[1][0]),max(goal_loc[1],goal_vehicle[1][0])):
                        for i in range(vehicle[2]):
                            space.append((vehicle[1][1]+i)%(board_size[0]))
                        if  goal_loc[1] in space:
                            blocker += 1
                        
        elif path1==path2:
            if direction in ("N" ,"S"):
                if vehicle[-1] == True:
                    if vehicle[1][1] in range (min(goal_loc[1],goal_vehicle[1][1]),max(goal_loc[1],goal_vehicle[1][1])):
                        for i in range(vehicle[2]):
                            space.append((vehicle[1][0]+i)%(board_size[1]))
                        if  goal_loc[0] in space:
                            path1_vehicle += 1
                    elif vehicle[1][1] not in range (min(goal_loc[1],goal_vehicle[1][1]),max(goal_loc[1],goal_vehicle[1][1])):
                        for i in range(vehicle[2]):
                            space.append((vehicle[1][0]+i)%(board_size[1]))
                        if  goal_loc[0] in space:
                            path2_vehicle  += 1
            else:
                if vehicle[-1] != True:
                    if vehicle[1][0] in range (min(goal_loc[0],goal_vehicle[1][0]),max(goal_loc[1],goal_vehicle[1][0])):
                        for i in range(vehicle[2]):
                            space.append((vehicle[1][1]+i)%(board_size[0]))
                        if  goal_loc[1] in space:
                            path1_vehicle += 1
                    elif vehicle[1][0] not in range (min(goal_loc[0],goal_vehicle[1][0]),max(goal_loc[1],goal_vehicle[1][0])):
                        for i in range(vehicle[2]):
                            space.append((vehicle[1][1]+i)%(board_size[0]))
                        if  goal_loc[1] in space:
                            path2_vehicle += 1

  if path1 == path2:
      result =  min(path1_vehicle,path2_vehicle)
  else: 
      result =  blocker


  #return heur_min_moves(state)
  return result+heur_min_moves(state)
  #return number_blocker
  #return min(number_blocker,heur_min_moves(state))
                  
                  

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
  return sN.gval + weight * sN.hval #replace this

def anytime_weighted_astar(initial_state, heur_fn, weight=1., timebound = 10):
#IMPLEMENT  
  '''Provides an implementation of anytime weighted a-star, as described in the HW1 handout'''
  '''INPUT: a rush hour state that represents the start state and a timebound (number of seconds)'''
  '''OUTPUT: A goal state (if a goal is found), else False'''
  '''implementation of weighted astar algorithm'''
  wrapped_fval_function = (lambda sN:fval_function(sN,weight))
  
  se = SearchEngine("custom","full")
  se.init_search(initial_state, rushhour_goal_fn, heur_fn, wrapped_fval_function)
  
  final = False
  costbound = (float('inf'), float('inf'), float('inf'))
  time_remaining = timebound
  
  
  while time_remaining>0.000001:
    saved_time = os.times()[0]
    result = se.search(time_remaining, costbound)
    time_remaining -= (os.times()[0] - saved_time)
      
    if result:
        if costbound[2] >= (result.gval+heur_fn(result)): 
            costbound = (float('inf'), float('inf'),result.gval+heur_fn(result))
        final = result
    else:
        break
    
  return final
  
  
  
  
  
  return 0 #replace this

def anytime_gbfs(initial_state, heur_fn, timebound = 10):
#IMPLEMENT  
  '''Provides an implementation of anytime greedy best-first search, as described in the HW1 handout'''
  '''INPUT: a rush hour state that represents the start state and a timebound (number of seconds)'''
  '''OUTPUT: A goal state (if a goal is found), else False'''
  '''implementation of anytime greedybfs algorithm'''
  
  se = SearchEngine('best_first', 'full')
  se.init_search(initial_state,rushhour_goal_fn,heur_fn)
    
  final = False

  costbound = (float('inf'), float('inf'), float('inf'))
  time_remaining = timebound
    
  while time_remaining > 0.000001:
    saved_time = os.times()[0]
    result = se.search(time_remaining, costbound)
    time_remaining -= (os.times()[0] - saved_time)
    if result:
        if costbound[0] >= result.gval: 
            costbound = (result.gval, float('inf'), float('inf'))
        final = result
    else:
        break
    
  return final


#####My Own Functions ################################################################
  
def find_goal_vehicle(state): #find the goal vehicle 
      vs = Rushhour.get_vehicle_statuses(state)
      for i in vs:
          if i[-1] == True :
              goal_vehicle = i
      return goal_vehicle


def find_vehicle_head_and_tail(vehicle,board_size): #Finds the front and tail location of the given vehicle, 
#use board size to check if vehicle over the board limit
    if vehicle[3]==True:
        if (vehicle[1][0]+vehicle[2])>(board_size[1]):
            V_tail = (vehicle[1][0]+vehicle[2]-board_size[1]-1,vehicle[1][1])
        else:
            V_tail = (vehicle[1][0]+vehicle[2]-1,vehicle[1][1])
    else:
        if (vehicle[1][1]+vehicle[2])>(board_size[0]):
            V_tail = (vehicle[1][0],vehicle[1][1]+vehicle[2]-board_size[0]-1)
        else:
            V_tail = (vehicle[1][0],vehicle[1][1]+vehicle[2]-1)

    return vehicle[1], V_tail



def heur_min_moves_2(state): #Return the value of both path rather than the minimum 

  goal_vehicle = find_goal_vehicle(state)

  (board_size, goal_loc, direction)  = Rushhour.get_board_properties(state)
  
  V_front, V_tail = find_vehicle_head_and_tail(goal_vehicle,board_size)
  


  if direction in [ "N" , "W"]:
      if direction  == "N":
          (path1 , path2)= ((abs(V_front[1]-goal_loc[1])),(board_size[0]-abs(V_front[1]-goal_loc[1])))
      else:
          (path1 , path2)= ((abs(V_front[0]-goal_loc[0])),(board_size[1]-abs(V_front[0]-goal_loc[0])))


  else: 
      if direction == "S":
          (path1 , path2)= ((abs(V_tail[1]-goal_loc[1])),(board_size[0]-abs(V_tail[1]-goal_loc[1])))

      else:
          (path1 , path2)= ((abs(V_tail[0]-goal_loc[0])),(board_size[1]-abs(V_tail[0]-goal_loc[0])))

  return path1, path2
                         




