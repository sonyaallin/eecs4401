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
    
    md = 0 #manhattan distance
    for sb in state.snowballs: 
        md += abs(sb[0] - state.destination[0]) + abs(sb[1] - state.destination[1])
    return md

def cornered(snowball, width, height, obstacles):
  '''
  helper functions to determine if a snowball is cornered.
  A snowball is cornered when 2 of the 4 directions are blocked or out of bound
  '''
  
  right = snowball[0] + 1
  sb_right = (right,snowball[1])
  left = snowball[0] - 1
  sb_left = (left,snowball[1])
  down = snowbal[1] + 1
  sb_down = (snowball[0],down)
  up = snowball[1] - 1
  sb_up = (snowball[0],up)  
  
  bd = 0 # blocked directions
  if down is height:
    db += 1
  if up < 0:
    db += 1
  if right is width:
    db +=1
  if left < 0:
    db +=1

def heur_alternate(state): 
#IMPLEMENT
    '''a better heuristic'''
    '''INPUT: a snowball state'''
    '''OUTPUT: a numeric value that serves as an estimate of the distance of the state to the goal.'''        
    #heur_manhattan_distance has flaws.   
    #Write a heuristic function that improves upon heur_manhattan_distance to estimate distance between the current state and the goal.
    #Your function should return a numeric value for the estimate of the distance to the goal.
     
    # checking walls
    walls = set()
    for i in range(state.width):
      walls.add((i,0))
      walls.add((i, state.height-1))
    for j in range(state.height):
      walls.add((0, j))
      walls.add((state.width-1, j))
      
    # main corners
    mc = set(((0,0),(state.width-1,0),(0,state.height-1),(state.width-1,state.height-1)))
      
    md = 0 
    for sb in state.snowballs:
      if sb in walls and (state.destination not in walls):
        md = float('Inf')
      elif sb in mc and (state.destination not in mc):
        md = float('Inf')
      else:
        md += abs(sb[0] - state.destination[0]) + abs(sb[1] - state.destination[1])    
    
    # distance of the robot to the target
    md = md + (abs(state.robot[0] - state.destination[0]) + abs(state.robot[1] - state.destination[1]))
    
    
    return md

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
    return sN.gval + (weight * sN.hval)

def anytime_gbfs(initial_state, heur_fn, timebound = 10):
#IMPLEMENT
    '''Provides an implementation of anytime greedy best-first search, as described in the HW1 handout'''
    '''INPUT: a snowball state that represents the start state and a timebound (number of seconds)'''
    '''OUTPUT: A goal state (if a goal is found), else False''' 
    
    t = os.times()[0] + timebound
    se = SearchEngine('best_first', 'full')
    se.init_search(initial_state, snowman_goal_state, heur_fn)
    tl = t - os.times()[0]

    result = False
    prev_cost = float('Inf')
    while tl > 0:
        goal = se.search(tl)
        if goal != False:
            if goal.gval < prev_cost:
                result = goal
                prev_cost = goal.gval
        else:
            break
        tl = t - os.times()[0]

    return result

def anytime_weighted_astar(initial_state, heur_fn, weight=1., timebound = 10):
#IMPLEMENT
    '''Provides an implementation of anytime weighted a-star, as described in the HW1 handout'''
    '''INPUT: a snowball state that represents the start state and a timebound (number of seconds)'''
    '''OUTPUT: A goal state (if a goal is found), else False'''

    t = os.times()[0] + timebound
    se = SearchEngine('custom')
    lambda_fval = (lambda sN: fval_function(sN, weight))
    se.init_search(initial_state, snowman_goal_state, heur_fn, lambda_fval)
    tl = t - os.times()[0]
    
    result = se.search(tl)
    temp = result
    while temp and (tl > 0):
        temp = se.search(tl, (float('Inf'), float('Inf'), temp.gval + heur_fn(temp) - 1))
        if temp:
            result = temp
        tl = (t - os.times()[0])
 
    return result

if __name__ == "__main__":
  #TEST CODE
  #solved = 0; unsolved = []; counter = 0; percent = 0; timebound = 2; #2 second time limit for each problem
  #print("*************************************")  
  #print("Running A-star")     

  #for i in range(0, 10): #note that there are 20 problems in the set that has been provided.  We just run through 10 here for illustration.

    #print("*************************************")  
    #print("PROBLEM {}".format(i))
    
    #s0 = PROBLEMS[i] #Problems will get harder as i gets bigger

    #se = SearchEngine('astar', 'full')
    #se.init_search(s0, goal_fn=snowman_goal_state, heur_fn=heur_simple)
    #final = se.search(timebound)

    #if final:
      #final.print_path()
      #solved += 1
    #else:
      #unsolved.append(i)    
    #counter += 1

  #if counter > 0:  
    #percent = (solved/counter)*100

  #print("*************************************")  
  #print("{} of {} problems ({} %) solved in less than {} seconds.".format(solved, counter, percent, timebound))  
  #print("Problems that remain unsolved in the set are Problems: {}".format(unsolved))      
  #print("*************************************") 

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


