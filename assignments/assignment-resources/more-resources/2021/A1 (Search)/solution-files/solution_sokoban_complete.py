#Look for #IMPLEMENT tags in this file. These tags indicate what has
#to be implemented to complete the warehouse domain.

#   You may add only standard python imports---i.e., ones that are automatically
#   available on TEACH.CS
#   You may not remove any imports.
#   You may not import or otherwise source any of your own files (NB I have imported a file, doh)

import os #for time functions
from search import * #for search engines
from sokoban import SokobanState, Direction, PROBLEMS #for Sokoban specific classes and problems
from munkres import Munkres #this is the hungarian algorithm

def sokoban_goal_state(state):
  '''
  @return: Whether all boxes are stored.
  '''
  for box in state.boxes:
    if box not in state.storage:
      return False
  return True

#SOKOBAN HEURISTICS
def trivial_heuristic(state):
  count = 0
  for box in state.boxes:
    if box not in state.storage:
        count += 1
  return count

def trappedincorner(state):
    for box in state.boxes:
      if box not in state.storage:
        if (box[0] == 0 or box[0] == state.height-1) and (box[1] == 0 or box[1] == state.width-1):   
          return True        

def heur_minmatch(a,b):
  #heuristic finds the min distance between all combinations of items in a and items in b
  #initialize Distance Matrix (will hold distances of boxes to storage)
  DistanceMatrix = [[0 for x in range(len(a))] for y in range(len(b))] 

  #calculate distances of unstored boxes to unused storage boxes   
  count1 = 0
  for item_x in a:
    count2 = 0
    for item_y in b:
      DistanceMatrix[count2][count1] = abs(item_x[0]-item_y[0]) + abs(item_x[1]-item_y[1])
      count2+=1
    count1+=1

  #calculate min assignment of boxes to storage
  m = Munkres()
  indeces = m.compute(DistanceMatrix)
  total_cost = 0
  for r, c in indeces:
    x = DistanceMatrix[r][c]
    total_cost += x

  return total_cost

def heur_minmatch_all(state):
	return heur_minmatch(state.boxes, state.storage) + heur_minmatch(state.boxes, state.robots)

def heur_minmatch_and_corner(state):
	if (trappedincorner(state) == True):
	 	return 10000000000000
	else:
		return heur_minmatch_all(state)

def heur_zero(state):
    '''Zero Heuristic can be used to make A* search perform uniform cost search'''
    return 0

def fval_function(state, arguments):
  '''default fval function is Best First Search'''
  return (1-arguments[0])*state.gval + arguments[0]*state.hval 

def weighted_astar(initail_state, timebound):
  '''implementation of weighted astar algorithm'''
  se = SearchEngine('custom', 'full')
  start_search_time = os.times()[0] #initialize start_time
  current_best = []
  time_elapsed = 0
  initial_time_bound = timebound;
  arguments = [1]
  iteration = 0

  #anytime a-star
  while time_elapsed < initial_time_bound and arguments[0] >= 0:        
    final = se.search(initail_state, sokoban_goal_state, heur_minmatch_all, timebound, fval_function, arguments)
    if final != False:
    	current_best = final
    time_elapsed += os.times()[0] - start_search_time    
    arguments[0] -= 0.2
    start_search_time = os.times()[0]
    timebound = initial_time_bound - time_elapsed
    print("Time elapsed at iteration {} = {}".format(iteration, time_elapsed))
    iteration += 1

  return current_best

#TEST CODE
from additional_problems import ADDITIONAL_PROBLEMS

timebound = 5 #2 second time limit 
solved = 0; additional_solved = 0; additional_unsolved = []; unsolved = [] 
for i in range(0,39):
  print("*************************************")	
  print("PROBLEM {}", i)

  s0 = PROBLEMS[i] #Problems get harder as i gets bigger
  goal = weighted_astar(s0, timebound)

  if goal:
    goal.print_path()	 
    solved += 1 
  else:
    unsolved.append(i)

for i in range(0,39):
  print("*************************************")  
  print("ADDITIONAL_PROBLEM {}", i)    
  s0 = ADDITIONAL_PROBLEMS[i] #Problems get harder as i gets bigger
  goal = weighted_astar(s0, timebound)

  if goal:
    goal.print_path()   
    additional_solved += 1
  else:
    additional_unsolved.append(i)

print("Of 40 initial problems, {} were solved in less than {} seconds by this solver.".format(solved, timebound))  
print("Problems that remain unsolved in the set are Problems: {}".format(unsolved))     
print("Of 40 additional problems, {} were solved in less than {} seconds by this solver.".format(solved, timebound))    
print("Problems that remain unsolved in the set are Problems: {}".format(additional_unsolved))        

