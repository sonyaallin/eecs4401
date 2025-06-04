#Look for #IMPLEMENT tags in this file. These tags indicate what has
#to be implemented to complete the Snowman Puzzle domain.

#   You may add only standard python imports---i.e., ones that are automatically
#   available on TEACH.CS
#   You may not remove any imports.
#   You may not import or otherwise source any of your own files

# import os for time functions
import os
from search import * #for search engines
from snowman import SnowmanState, Direction, snowman_goal_state #for snowball specific classes and problems
from test_problems import PROBLEMS

#snowball HEURISTICS
def heur_simple(state):
  '''trivial admissible snowball heuristic'''
  '''INPUT: a snowball state'''
  '''OUTPUT: a numeric value that serves as an estimate of the distance of the state (# of moves required to get) to the goal.'''   
  return len(state.snowballs)

def heur_zero(state):
  return 0

def heur_manhattan_distance(state):
  destinationdists=[]

  for item_x in state.snowballs:
    destinationdists.append(abs(item_x[0]-state.destination[0]) + abs(item_x[1]-state.destination[1]))   

  return sum(destinationdists)

def heur_alternate(state): 
  snowballdists=[] 
  destinationdists=[]

  for item_x in state.snowballs:
    snowballdists.append(abs(item_x[0]-state.robot[0]) + abs(item_x[1]-state.robot[1]))
    destinationdists.append(abs(item_x[0]-state.destination[0]) + abs(item_x[1]-state.destination[1]))   

  total_dist = sum(destinationdists) + min(snowballdists) 

  if(trappedincorner(state)): 
    total_dist = total_dist + 100000000    

  return total_dist

  #in 5 seconds ....
  #total_dist = sum(destinationdists) + min(snowballdists) solves 12 of 20
  #total_dist = sum(destinationdists) + min(snowballdists) and trappedincorner solves 14 of 20
  #total_dist = max(snowballdists) and trappedincorner solves 11 of 20
  #total_dist = max(snowballdists) solves 8 of 20    

def trappedincorner(state):
    for snowball in state.snowballs:
      if snowball not in state.destination:
        if (snowball[0] == 0 or snowball[0] == state.width) and (snowball[1] == 0 or snowball[1] == state.height):   
          return True  
        if (snowball[0] == 0 and state.destination[0]!=0) or (snowball[1] == 0 and state.destination[1]!=0):
          return True  
        if (snowball[0] == state.width and state.destination[0]!=state.width) or (snowball[1] == state.height and state.destination[1]!=state.height):
          return True  

def fval_function(sN, weight):
  return sN.gval + weight*sN.hval 

def anytime_gbfs(initial_state, heur_fn, timebound = 10):
  '''implementation of weighted astar algorithm'''
  se = SearchEngine('best_first', 'full')
  se.init_search(initial_state, snowman_goal_state, heur_fn)  
  current_best = []
  time_elapsed = 0
  initial_time_bound = timebound
  iteration = 0
  costbound = None

  #anytime gbfs
  start_search_time = os.times()[0] #initialize start_time
  while time_elapsed < initial_time_bound:    
    final = se.search(timebound, costbound)
    if final != False:
      current_best = final
      costbound = [current_best.gval, 100000000, 100000000]
      print("Time elapsed at iteration {} = {}".format(iteration, time_elapsed))
      iteration += 1
    time_elapsed = os.times()[0] - start_search_time    
    timebound = initial_time_bound - time_elapsed    
    
  return current_best


def anytime_weighted_astar(initial_state, heur_fn, weight=1., timebound = 10):
  
  '''implementation of weighted astar algorithm'''
  se = SearchEngine('best_first', 'full')
  wrapped_fval_function= (lambda sN: fval_function(sN,weight))
  se.init_search(initial_state, snowman_goal_state, heur_fn, wrapped_fval_function)  
  current_best = []
  time_elapsed = 0
  initial_time_bound = timebound
  iteration = 0
  costbound = None
  
  #anytime weighted a-star
  start_search_time = os.times()[0] #initialize start_time
  while time_elapsed < initial_time_bound and weight >= 1:    
    final = se.search(timebound, costbound)
    if final != False:
      current_best = final
      costbound = [100000000, 100000000, current_best.gval]
      weight -= 1
      print("Time elapsed at iteration {} = {} (weight is {})".format(iteration, time_elapsed, weight))
      iteration += 1
    time_elapsed = os.times()[0] - start_search_time    
    timebound = initial_time_bound - time_elapsed    
    
  return current_best

if __name__ == "__main__":
  #TEST CODE
  solved = 0; unsolved = []; counter = 0; percent = 0; timebound = 2; #2 second time limit for each problem
  print("*************************************")  
  print("Running A-star")     

  for i in range(0, 10): #note that there are 40 problems in the set that has been provided.  We just run through 10 here for illustration.

    print("*************************************")  
    print("PROBLEM {}".format(i))
    
    s0 = PROBLEMS[i] #Problems will get harder as i gets bigger

    se = SearchEngine('astar', 'full')
    se.init_search(s0, goal_fn=snowman_goal_state, heur_fn=heur_displaced)
    final = se.search(timebound)

    if final:
      final.print_path()
      solved += 1
    else:
      unsolved.append(i)    
    counter += 1

  if counter > 0:  
    percent = (solved/counter)*100

  print("*************************************")  
  print("{} of {} problems ({} %) solved in less than {} seconds.".format(solved, counter, percent, timebound))  
  print("Problems that remain unsolved in the set are Problems: {}".format(unsolved))      
  print("*************************************") 

  solved = 0; unsolved = []; counter = 0; percent = 0; timebound = 8; #8 second time limit 
  print("Running Anytime Weighted A-star")   

  for i in range(0, 10):
    print("*************************************")  
    print("PROBLEM {}".format(i))

    s0 = PROBLEMS[i] #Problems get harder as i gets bigger
    weight = 10
    final = anytime_weighted_astar(s0, heur_fn=heur_displaced, weight=weight, timebound=timebound)

    if final:
      final.print_path()   
      solved += 1 
    else:
      unsolved.append(i)
    counter += 1      

  if counter > 0:  
    percent = (solved/counter)*100   
      
  print("*************************************")  
  print("{} of {} problems ({} %) solved in less than {} seconds.".format(solved, counter, percent, timebound))  
  print("Problems that remain unsolved in the set are Problems: {}".format(unsolved))      
  print("*************************************") 


