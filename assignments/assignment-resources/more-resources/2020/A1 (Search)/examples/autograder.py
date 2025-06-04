
import os
import pickle

# import student's functions
from solutions.solution1 import *
from rushhour import * 

#Select what to test
test_goal = True
test_min_moves = False
test_fval_function = False
test_anytime_gbfs = False
test_alternate = False
test_anytime_weighted_astar = False

#load the test problems
TESTPROBLEMS = []
with (open("rushhour_tests.pkl", "rb")) as openfile:
    while True:
        try:
            TESTPROBLEMS.append(pickle.load(openfile))
        except EOFError:
            break
GOALS = pickle.load( open( "rushhour_goals.pkl", "rb" ) )

if test_goal:

    score = 0
    
    for i in range(0,40):
        s0 = GOALS[i]

        if (rushhour_goal_fn(s0)):
            score += 1
    
    print("Goal states correctly detected {} of {} times.".format(score, 40))    
    ##############################################################


if test_min_moves:

    ##############################################################
    # TEST MIN MOVES HEURISTIC
    print('TESTING MIN MOVES')
    PROBLEMS = TESTPROBLEMS[40:]

    #Correct MIN MOVES distances for the initial states of the provided problem set
    correct_min_moves = [2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 3, 7, 10, 14, 14, 17, 24, 28, 31, 29];

    solved = 0; unsolved = []; 

    for i in range(0,len(PROBLEMS)):
        print("PROBLEM {}".format(i))

        s0 = PROBLEMS[i]

        min_moves = heur_min_moves(s0)
        print('calculated min_moves:', str(min_moves))
        #To see state uncomment below
        #print(s0.state_string())

        if min_moves == correct_min_moves[i]:
            solved += 1
        else:
            unsolved.append(i)   

    print("*************************************")  
    print("In the problem set provided, you calculated the correct Min Moves distance for {} states out of {}.".format(solved, len(PROBLEMS)))
    print("States that were incorrect: {}".format(unsolved))  
    print("*************************************\n")
    ##############################################################

if test_alternate:

  ##############################################################
  # TEST ALTERNATE HEURISTIC
  print('Testing alternate heuristic with best_first search')

  solved = 0; unsolved = []; benchmark = 35; timebound = 1 #time limit

  PROBLEMS = TESTPROBLEMS[0:40] #first 40 are for search

  for i in range(0, len(PROBLEMS)): 

    print("*************************************")
    print("PROBLEM {}".format(i))

    s0 = PROBLEMS[i] #Problems get harder as i gets bigger
    se = SearchEngine('best_first', 'full')
    se.init_search(s0, goal_fn=rushhour_goal_fn, heur_fn=heur_min_moves)
    final = se.search(timebound)

    if final:
      final.print_path()  
      solved += 1
    else:
      unsolved.append(i)

  print("\n*************************************")
  print("Of {} initial problems, {} were solved in less than {} seconds by this solver.".format(len(PROBLEMS), solved, timebound))
  print("Problems that remain unsolved in the set are Problems: {}".format(unsolved))
  print("The benchmark implementation solved {} out of {} practice problems given {} seconds.".format(benchmark,len(PROBLEMS),timebound))
  print("*************************************\n")
  ##############################################################
  

if test_fval_function:

  test_state = Rushhour("START", 6, None, None, None)

  correct_fvals = [6, 11, 16]

  ##############################################################
  # TEST fval_function
  print("*************************************") 
  print('Testing fval_function')

  solved = 0
  weights = [0., .5, 1.]
  for i in range(len(weights)):

    test_node = sNode(test_state, hval=10, fval_function=fval_function)
    
    fval = fval_function(test_node, weights[i])
    print ('Test', str(i), 'calculated fval:', str(fval), 'correct:', str(correct_fvals[i]))
    
    if fval == correct_fvals[i]:
      solved +=1  

  print("\n*************************************")  
  print("Your fval_function calculated the correct fval for {} out of {} tests.".format(solved, len(correct_fvals)))  
  print("*************************************\n") 
  ##############################################################

if test_anytime_gbfs:

  PROBLEMS = TESTPROBLEMS[0:40] #first 40 are for search
  len_benchmark = [1, 7, 2, 1, 4, 1, 1, 7, 1, 2, 2, 1, 3, 2, 2, 0, 1, 2, 1, 2, 30, 7, 35, 8, 10, 7, 8, 7, 7, 11, 37, 15, 78, 401, 7, -99, -99, 9, 7, 308]

  ##############################################################
  # TEST ANYTIME GBFS
  print('Testing Anytime GBFS')

  solved = 0; unsolved = []; benchmark = 0; timebound = 3 #3 second time limit 
  for i in range(0, len(PROBLEMS)):
    print("*************************************")  
    print("PROBLEM {}".format(i))

    s0 = PROBLEMS[i] 
    weight = 10
    final = anytime_gbfs(s0, heur_fn=heur_min_moves, timebound=timebound)

    if final:
      if i < len(len_benchmark):
        index = i
      else:
        index = 0      
      final.print_path()  
      if final.gval <= len_benchmark[index] or len_benchmark[index] == -99:
        benchmark += 1
      solved += 1 
    else:
      unsolved.append(i)  

  print("\n*************************************")  
  print("Of {} initial problems, {} were solved in less than {} seconds by this solver.".format(len(PROBLEMS), solved, timebound))  
  print("Of the {} problems that were solved, the cost of {} matched or outperformed the benchmark.".format(solved, benchmark))  
  print("Problems that remain unsolved in the set are Problems: {}".format(unsolved))  
  print("The benchmark implementation solved 5 out of the 20 practice problems given 3 seconds.")
  print("*************************************\n") 

if test_anytime_weighted_astar:

  len_benchmark = [1, 7, 2, 1, 4, 1, 1, 7, 1, 2, 2, 1, 3, 2, 2, 0, 1, 2, 1, 2, -99, 7, -99, 8, 10, 7, 8, 7, 7, 10, -99, -99, -99, 8, 7, -99, -99, 8, 7, -99]

  ##############################################################
  # TEST ANYTIME WEIGHTED A STAR
  print('Testing Anytime Weighted A Star')

  solved = 0; unsolved = []; benchmark = 0; timebound = 3 #3 second time limit 
  PROBLEMS = TESTPROBLEMS[0:40] #first 40 are for search

  for i in range(0, len(PROBLEMS)):
    print("*************************************")  
    print("PROBLEM {}".format(i))

    s0 = PROBLEMS[i] #Problems get harder as i gets bigger
    weight = 10
    final = anytime_weighted_astar(s0, heur_fn=heur_min_moves, weight=weight, timebound=timebound)

    if final:
      if i < len(len_benchmark):
        index = i
      else:
        index = 0      
      final.print_path()  
      if final.gval <= len_benchmark[index] or len_benchmark[index] == -99:
        benchmark += 1
      solved += 1 
    else:
      unsolved.append(i)  

  print("\n*************************************")  
  print("Of {} initial problems, {} were solved in less than {} seconds by this solver.".format(len(PROBLEMS), solved, timebound))  
  print("Of the {} problems that were solved, the cost of {} matched or outperformed the benchmark.".format(solved, benchmark))  
  print("Problems that remain unsolved in the set are Problems: {}".format(unsolved))  
  print("The benchmark implementation solved 12 out of the 20 practice problems given 8 seconds.")
  print("*************************************\n") 

  ##############################################################

