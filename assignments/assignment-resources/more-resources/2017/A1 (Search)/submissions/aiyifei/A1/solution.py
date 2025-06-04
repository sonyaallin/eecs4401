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
    length = 0
    for key in state.snowballs:
      # The case that it is not a stack
      if 0 <= state.snowballs[key] and state.snowballs[key] <= 2: 
        length += abs(key[0]-state.destination[0]) + abs(key[1]-state.destination[1])
      elif 3 <= state.snowballs[key] and state.snowballs[key] <= 5:
        length += 2 * (abs(key[0]-state.destination[0]) + abs(key[1]-state.destination[1]))
      elif state.snowballs[key] == 6:
        length += 3 * (abs(key[0]-state.destination[0]) + abs(key[1]-state.destination[1]))
    return length

def heur_alternate(state): 
#IMPLEMENT
    '''a better heuristic'''
    '''INPUT: a snowball state'''
    '''OUTPUT: a numeric value that serves as an estimate of the distance of the state to the goal.'''        
    #heur_manhattan_distance has flaws.   
    #Write a heuristic function that improves upon heur_manhattan_distance to estimate distance between the current state and the goal.
    #Your function should return a numeric value for the estimate of the distance to the goal.
    h_val = 0
    # The strategy we are going to use:
    # We add the distance with weight between the robot and the snowballs, the weight depending on the snowball size.
    # Bigger size with larger weight.
    l = calculate_obstacle_board(state)
    h_val += heur_manhattan_distance(state)
    for key in state.snowballs:
      if state.snowballs[key] == 0 and key != state.destination and state.gval >= 1:
        if key not in state.parent.snowballs:
          h_val -= 2 * (abs(key[0] - state.destination[0]) + abs(key[1] - state.destination[1]))
      elif state.snowballs[key] == 1 and key != state.destination and state.gval >= 1:
        if key not in state.parent.snowballs:
          h_val -= (abs(key[0] - state.destination[0]) + abs(key[1] - state.destination[1]))
      # Check if snowball is on the yard which cannot be pushed to destination
      flag = 0
      if key[0] == state.width - 1:
        if state.destination[0] < key[0]:
          h_val = float("inf")
          break
        elif state.destination[1] != key[1]:
          if key[1] < state.destination[1]:
            for i in range(key[1]+1, state.destination[1]):
              if (key[0], i) in state.obstacles:
                h_val = float("inf")
                flag = 1
                break
            if flag == 1:
              break
          elif state.destination[1] < key[1]:
            for i in range(state.destination[1]+1, key[1]):
              if (key[0], i) in state.obstacles:
                h_val = float("inf")
                flag = 1
                break
            if flag == 1:
              break
      elif key[0] == 0:
        if state.destination[0] > key[0]:
          h_val = float("inf")
          break
        elif state.destination[1] != key[1]:
          if key[1] < state.destination[1]:
            for i in range(key[1]+1, state.destination[1]):
              if (key[0], i) in state.obstacles:
                h_val = float("inf")
                flag = 1
                break
            if flag == 1:
              break
          elif state.destination[1] < key[1]:
            for i in range(state.destination[1]+1, key[1]):
              if (key[0], i) in state.obstacles:
                h_val = float("inf")
                flag = 1
                break
            if flag == 1:
              break
      if key[1] == state.height - 1:
        if state.destination[1] < key[1]:
          h_val = float("inf")
          break
        elif state.destination[0] != key[0]:
          if key[0] < state.destination[0]:
            for i in range(key[0]+1, state.destination[0]):
              if (i, key[1]) in state.obstacles:
                h_val = float("inf")
                flag = 1
                break
            if flag == 1:
              break
          elif state.destination[0] < key[0]:
            for i in range(state.destination[0]+1, key[0]):
              if (i, key[1]) in state.obstacles:
                h_val = float("inf")
                flag = 1
                break
            if flag == 1:
              break
      elif key[1] == 0:
        if state.destination[1] > key[1]:
          h_val = float("inf")
          break
        elif state.destination[0] != key[0]:
          if key[0] < state.destination[0]:
            for i in range(key[0]+1, state.destination[0]):
              if (i, key[1]) in state.obstacles:
                h_val = float("inf")
                flag = 1
                break
            if flag == 1:
              break
          elif state.destination[0] < key[0]:
            for i in range(state.destination[0]+1, key[0]):
              if (i, key[1]) in state.obstacles:
                h_val = float("inf")
                flag = 1
                break
            if flag == 1:
              break
      # Move check_obstacle_board function here
      if key != state.destination:
        if (key[0], key[1] - 1) in l:
          if ((key[0] - 1, key[1]) in l) or ((key[0] + 1, key[1]) in l):
            h_val = float("inf")
            break
        elif (key[0], key[1] + 1) in l:
          if ((key[0] - 1, key[1]) in l) or ((key[0] + 1, key[1]) in l):
            h_val = float("inf")
            break
      if (state.snowballs[key] == 6) and (key != state.destination):
        h_val = float("inf")
        break
    if h_val < float("inf"):
      h_val += check_unecessary_step1(state)
    return h_val

def check_unecessary_step1(state):
  val = 0
  # All snowballs and destination are in the left of robot
  # ########
    #X b ? #
    #m     #
    #      #
    #s     #
    ########
  if (all(key[0] < state.robot[0] - 1 for key in state.snowballs)) and (state.destination[0] < state.robot[0] - 1):
    if (all(obs[0] != state.robot[0] - 1 for obs in state.obstacles)):
      val = float("inf")
      return val
  # All snowballs and destination are in the right of robot
  if (all(key[0] > state.robot[0] + 1 for key in state.snowballs)) and (state.destination[0] > state.robot[0] + 1):
    if (all(obs[0] != state.robot[0] + 1 for obs in state.obstacles)):
      val = float("inf")
      return val
  # All snowballs and destination are above the robot
  if (all(key[1] < state.robot[1] - 1 for key in state.snowballs)) and (state.destination[1] < state.robot[1] - 1):
    if (all(obs[1] != state.robot[1] - 1 for obs in state.obstacles)):
      val = float("inf")
      return val
  # All snowballs and destination are under the robot
  if (all(key[1] > state.robot[1] + 1 for key in state.snowballs)) and (state.destination[1] > state.robot[1] + 1):
    if (all(obs[1] != state.robot[1] + 1 for obs in state.obstacles)):
      val = float("inf")
      return val
  return val





def calculate_obstacle_board(state):
  l = []
  for i in range(-1, state.width + 1):
    l.append((i, -1))
    l.append((i, state.height))
  for j in range(0, state.height):
    l.append((-1, j))
    l.append((state.width, j))
  l.extend(state.obstacles)
  return l

def check_obstacle_board(state, l):
  """
  Check the case that the ball is stuck in the corner
  #######
  X ? b##
  #######
  """
  val = 0
  for key in state.snowballs:
    if key != state.destination:
      if (key[0], key[1] - 1) in l:
        if ((key[0] - 1, key[1]) in l) or ((key[0] + 1, key[1]) in l):
          val = float("inf")
          break
      elif (key[0], key[1] + 1) in l:
        if ((key[0] - 1, key[1]) in l) or ((key[0] + 1, key[1]) in l):
          val = float("inf")
          break
  return val

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
    fval = sN.gval + weight * sN.hval
    return fval

def anytime_gbfs(initial_state, heur_fn, timebound = 10):
#IMPLEMENT
    '''Provides an implementation of anytime greedy best-first search, as described in the HW1 handout'''
    '''INPUT: a snowball state that represents the start state and a timebound (number of seconds)'''
    '''OUTPUT: A goal state (if a goal is found), else False'''
    se = SearchEngine(strategy = 'best_first', cc_level = 'default')
    se.init_search(initial_state, snowman_goal_state, heur_fn)
    stop_time = os.times()[0] + timebound
    goal = se.search(timebound = timebound, costbound = None)
    goal_store = False
    while ((stop_time - os.times()[0]) > 0) and (goal):
      goal_store = goal
      goal = se.search(timebound = stop_time - os.times()[0], costbound=(goal_store.gval, float("inf"), float("inf")))
    return goal_store

def anytime_weighted_astar(initial_state, heur_fn, weight=1., timebound = 10):
#IMPLEMENT
    '''Provides an implementation of anytime weighted a-star, as described in the HW1 handout'''
    '''INPUT: a snowball state that represents the start state and a timebound (number of seconds)'''
    '''OUTPUT: A goal state (if a goal is found), else False''' 
    se = SearchEngine(strategy = "custom", cc_level = 'default')
    wrapped_fval_function = (lambda sN: fval_function(sN, weight))
    se.init_search(initial_state, snowman_goal_state, heur_fn = heur_fn, fval_function = wrapped_fval_function)
    stop_time = os.times()[0] + timebound
    goal = se.search(timebound = timebound, costbound = None)
    goal_store = False
    while ((stop_time - os.times()[0]) > 0) and (goal):
      goal_store = goal
      goal = se.search(timebound = stop_time - os.times()[0], costbound=(float("inf"), float("inf"), goal_store.gval))
    return goal_store

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


