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
from test_problems import PROBLEMS #20 test problems

# Create a global variable to hold previous moves that a search has performed
moves = []
multi = [1, 1.125, 1.25, 2, 2, 2, 3]

#snowball HEURISTICS
def heur_simple(state):
  '''trivial admissible snowball heuristic'''
  '''INPUT: a snowball state'''
  '''OUTPUT: a numeric value that serves as an estimate of the distance of the state (# of moves required to get) to the goal.'''   
  return len(state.snowballs)

def heur_zero(state):
  return 0

def heur_manhattan_distance(state):
#IMPLEMENT
    '''admissible snowball puzzle heuristic: manhattan distance'''
    '''INPUT: a snowball state'''
    '''OUTPUT: a numeric value that serves as an estimate of the distance of the state to the goal.'''      
    #We want an admissible heuristic, which is an optimistic heuristic. 
    #It must always underestimate the cost to get from the current state to the goal.
    #The sum of the Manhattan distances between the snowballs and the destination for the Snowman is such a heuristic.  
    #When calculating distances, assume there are no obstacles on the grid.
    #You should implement this heuristic function exactly, even if it is tempting to improve it.
    #Your function should return a numeric value; this is the estimate of the distance to the goal.
    
    #Set a variable to hold the total manhattan distance
    man_dist = 0
    #Get the coordinates of the goal
    goal = state.destination
    #Get the list of coordinates of each of the snowballs
    snowball_coords = state.snowballs.keys()
    #Loop through the list
    for coord in snowball_coords:
    	if(state.snowballs[coord] == 6):
    		mult = 3
    	elif(state.snowballs[coord] > 2):
    		mult = 2
    	else:
    		mult = 1
    	#Calculate the distance between each snowball and the goal
    	dist = (abs(coord[0] - goal[0]) + abs(coord[1] - goal[1]) )* mult
    	#Add the distance to the total distance
    	man_dist += dist
    
    return man_dist

def heur_alternate(state): 
#IMPLEMENT
    '''a better heuristic'''
    '''INPUT: a snowball state'''
    '''OUTPUT: a numeric value that serves as an estimate of the distance of the state to the goal.'''        
    #heur_manhattan_distance has flaws.   
    #Write a heuristic function that improves upon heur_manhattan_distance to estimate distance between the current state and the goal.
    #Your function should return a numeric value for the estimate of the distance to the goal.

	#Create a hash for the current state
    s_hash = state.hashable_state()
	#Check if we have gone to this state before
    if s_hash in moves:
    	#If we have then we don't want to explore further down this node
        return float("inf")
    else:
    	#If we haven't then put it in the list of moves made
        moves.append(s_hash)

    #Set a variable to hold the total manhattan distance
    man_dist = 0
    #Get the coordinates of the goal
    goal = state.destination
    #Get the list of coordinates of each of the snowballs
    snowball_coords = state.snowballs.keys()
    
    #Create a list of all corners on the map
    corners = [(0,0), (0,state.height), (state.width,state.height), (state.width, 0)]
    
    #Remove the corner that contains the goal(if the goal is in the corner)
    try:
    	corners.remove(goal)
    except:
    	pass


    #Loop through the list of snowballs
    for coord in snowball_coords:
    	#If the snowball is in the corner then we don't want to explore further
    	if coord in corners:
    		return float("inf")
    	if (coord[0] == 0 and goal[0] !=0) or (coord[0] == state.width and goal[0] != state.width) or (coord[1] == 0 and goal[1] !=0) or (coord[1] == state.height and goal[1] != state.height):
    		return float("inf") 
    	else:
    		mult = multi[state.snowballs[coord]]
    	if(state.snowballs[coord] < 2 or (state.snowballs[coord] > 3 and state.snowballs[coord] < 6)) and (coord == goal):
    	 	mult += 10
    		
    	#Calculate the distance between each snowball and the goal
    	dist = (abs(coord[0] - goal[0]) + abs(coord[1] - goal[1]) )* mult
    	#Add the distance to the total distance
    	man_dist += dist
    
    man_dist += (abs(state.robot[0] - goal[0]) + abs(state.robot[1] - goal[1])) * 0.75
    
    if(man_dist == 0 or len(moves) > 500):
        moves.clear()
    return man_dist

def fval_function(sN, weight):
#IMPLEMENT
    """
    Provide a custom formula for f-value computation for Anytime Weighted A star.
    Returns the fval of the state contained in the sNode.

    @param sNode sN: A search node (containing a SnowballState)
    @param float weight: Weight given by Anytime Weighted A star
    @rtype: float
    """
  
    #Many searches will explore nodes (or states) that are ordered by their f-value.
    #For UCS, the fvalue is the same as the gval of the state. For best-first search, the fvalue is the hval of the state.
    #You can use this function to create an alternate f-value for states; this must be a function of the state and the weight.
    #The function must return a numeric f-value.
    #The value will determine your state's position on the Frontier list during a 'custom' search.
    #You must initialize your search engine object as a 'custom' search engine if you supply a custom fval function.
    return sN.gval + weight * sN.hval

def anytime_gbfs(initial_state, heur_fn, timebound = 10):
#IMPLEMENT
    '''Provides an implementation of anytime greedy best-first search, as described in the HW1 handout'''
    '''INPUT: a snowball state that represents the start state and a timebound (number of seconds)'''
    '''OUTPUT: A goal state (if a goal is found), else False'''

    se = SearchEngine("best_first")
    se.init_search(initial_state, goal_fn=snowman_goal_state, heur_fn=heur_fn)
    state = False
    gval = float("inf")
    while timebound > 0:
    	n_state = se.search(timebound, (gval, float("inf"), float("inf")))
    	if n_state != False:
                gval = n_state.gval
                state = n_state
    	timebound = timebound - os.times()[0]
    return state

def anytime_weighted_astar(initial_state, heur_fn, weight=1., timebound = 10):
#IMPLEMENT
    '''Provides an implementation of anytime weighted a-star, as described in the HW1 handout'''
    '''INPUT: a snowball state that represents the start state and a timebound (number of seconds)'''
    '''OUTPUT: A goal state (if a goal is found), else False''' 
    wrapped_fval_function = (lambda sN: fval_function(sN, weight))
    se = SearchEngine("custom")
    se.init_search(initial_state, goal_fn=snowman_goal_state, heur_fn=heur_fn, fval_function=wrapped_fval_function)
    state = se.search(timebound)
    timebound = timebound - os.times()[0]
    while timebound > 0:
    	n_state = se.search(timebound, (float("inf"), float("inf"), state.gval))
    	if n_state != False:
    		state = n_state
    	timebound = timebound - os.times()[0]
    return state

if __name__ == "__main__":
  #TEST CODE
  solved = 0; unsolved = []; counter = 0; percent = 0; timebound = 2; #2 second time limit for each problem
  print("*************************************")  
  print("Running A-star")     

  for i in range(0, 10): #note that there are 20 problems in the set that has been provided.  We just run through 10 here for illustration.

    print("*************************************")  
    print("PROBLEM {}".format(i))
    
    s0 = PROBLEMS[i] #Problems will get harder as i gets bigger

    se = SearchEngine('astar', 'full')
    se.init_search(s0, goal_fn=snowman_goal_state, heur_fn=heur_simple)
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
    final = anytime_weighted_astar(s0, heur_fn=heur_simple, weight=weight, timebound=timebound)

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


