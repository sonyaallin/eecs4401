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
    #Your function should return a numeric value; this is the estimate of the distance to the goal

    manhattan_distance_sum = 0

    for key in state.snowballs: #keys are coordinates of each snowball
        if state.snowballs[key] == 3 or state.snowballs[key] == 4 or state.snowballs[key] == 5:
            manhattan_dist = (abs((state.destination[0] - key[0])) + abs((state.destination[1] - key[1]))) * 2
        elif state.snowballs[key] == 6:
            manhattan_dist = (abs((state.destination[0] - key[0])) + abs((state.destination[1] - key[1]))) * 3
        else:
            manhattan_dist = abs((state.destination[0] - key[0])) + abs((state.destination[1] - key[1]))
        manhattan_distance_sum += manhattan_dist
    return manhattan_distance_sum

def corner_edge_deadlock_check(state, key):
    ''' Returns True if there is a corner deadlock, False if none is detected'''

    if key == state.destination:
        return False

    #booleans to make if statements clearer
    any_left = ((key[0]) == 0) or ((key[0] - 1, key[1]) in state.obstacles and (key[0] - 1, key[1]) != state.destination)
    any_right = ((key[0]) == state.width - 1) or ((key[0] + 1, key[1]) in state.obstacles and (key[0] + 1, key[1]) != state.destination)
    any_top = ((key[1]) == 0) or ((key[0], key[1] - 1) in state.obstacles and (key[0], key[1] - 1) != state.destination)
    any_bottom = ((key[1]) == state.height - 1) or ((key[0], key[1] + 1) in state.obstacles and (key[0], key[1] + 1) != state.destination)

    goal_next_wall = ((state.destination[0]) == 0) or (state.destination[0] == state.width - 1 ) \
                     or (state.destination[1] == 0) or (state.destination[1] == state.height - 1)
    snowball_next_wall = ((key[0]) == 0) or (key[0] == state.width - 1) \
                     or ((key[1]) == 0) or (key[1] == state.height - 1)


    if snowball_next_wall: # snowball next to wall and goal isnt
        if not goal_next_wall:
            return True

    if any_left or any_right: # blocked in left/right and top/bottom
        if any_top or any_bottom:
            return True

    if any_top: # blocked from top and left/right, or blocked from top and bottom and right/left
        if any_left or any_right:
            return True
        if any_bottom and (any_right or any_left):
            return True

    if any_bottom: # blocked from bottom and left/right
        if any_left or any_right:
            return True
          
    return False

def heur_alternate(state):
#IMPLEMENT
    '''a better heuristic'''
    '''INPUT: a snowball state'''
    '''OUTPUT: a numeric value that serves as an estimate of the distance of the state to the goal.'''
    #heur_manhattan_distance has flaws.
    #Write a heuristic function that improves upon heur_manhattan_distance to estimate distance between the current state and the goal.
    #Your function should return a numeric value for the estimate of the distance to the goal.

    heur_val = 0
    global prev_val
    global past_position
    global past_robot_state

    try: #remember previous heuristics
        if past_position == state.snowballs and (past_robot_state == state.robot):
            return prev_val
        else:
            past_position = state.snowballs
            past_robot_state = state.robot
    except NameError:
        past_position = state.snowballs
        past_robot_state = state.robot

    for key in state.snowballs: #keys are coordinates of each snowball
        if corner_edge_deadlock_check(state, key):
           heur_val = float("inf")
           break

        #prefer paths directly to the goal
        #idea from: http://theory.stanford.edu/~amitp/GameProgramming/Heuristics.html
        dx1 = key[0] - state.destination[0]
        dy1 = key[1] - state.destination[1]
        dx2 = state.robot[0] - key[0]
        dy2 = state.robot[1] - key[1]
        cross = abs(dx1*dy2 - dx2*dy1)
        heur_val += cross * 1.2

        #use euclidean distance
        euclidean_dist = ((state.destination[0] - key[0])**2 + (state.destination[1] - key[1])**2)**.5
        heur_val += euclidean_dist

    prev_val = heur_val
    past_position = state.snowballs
    past_robot_state = state.robot

    return heur_val

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

    return sN.gval + weight*sN.hval

def anytime_gbfs(initial_state, heur_fn, timebound = 10):
#IMPLEMENT
    '''Provides an implementation of anytime greedy best-first search, as described in the HW1 handout'''
    '''INPUT: a snowball state that represents the start state and a timebound (number of seconds)'''
    '''OUTPUT: A goal state (if a goal is found), else False'''

    se = SearchEngine('best_first', 'full')
    se.init_search(initial_state, goal_fn=snowman_goal_state, heur_fn=heur_fn)

    best_gval = float("inf")
    goal_state = False

    while timebound > 0: #the maximum amount of time, in seconds, to spend on this search.
        cost_bound = (best_gval, float("inf"), float("inf")) #3-tuple for pruning, (g_bound, h_bound, g_plus_h_bound)

        initial_time = os.times()[0]
        goal = se.search(timebound=timebound, costbound=cost_bound)
        end_time = os.times()[0]

        if goal:
            goal_state = goal
            if goal.gval < best_gval:
                best_gval = goal.gval

        if not goal:
            break

        timebound -= (end_time - initial_time)

    return goal_state

def anytime_weighted_astar(initial_state, heur_fn, weight=1., timebound = 10):
#IMPLEMENT
    '''Provides an implementation of anytime weighted a-star, as described in the HW1 handout'''
    '''INPUT: a snowball state that represents the start state and a timebound (number of seconds)'''
    '''OUTPUT: A goal state (if a goal is found), else False'''

    se = SearchEngine('custom', 'default')
    wrapped_fval_function = (lambda sN: fval_function(sN, weight))
    se.init_search(initial_state, goal_fn=snowman_goal_state, heur_fn=heur_fn,
                   fval_function = wrapped_fval_function)

    best_g_plus_h = float("inf")
    goal_state = False
    cost_bound = (float("inf"), float("inf"), best_g_plus_h) # 3-tuple for pruning, (g_bound, h_bound, g_plus_h_bound)

    while timebound > 0: # the maximum amount of time, in seconds, to spend on this search.
        initial_time = os.times()[0]
        goal = se.search(timebound=timebound, costbound=cost_bound) #begin search
        end_time = os.times()[0]

        if goal:
            goal_state = goal
            if goal.gval < best_g_plus_h:
                best_g_plus_h = goal.gval
            cost_bound = (float("inf"), float("inf"), best_g_plus_h)

        if not goal:
            break

        timebound -= (end_time - initial_time) #deduct time elapsed

    return goal_state

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

