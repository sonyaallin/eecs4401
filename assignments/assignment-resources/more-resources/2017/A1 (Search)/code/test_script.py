
# import student's functions
from solution_complete import *
from test_problems import PROBLEMS, EASY_PROBLEMS, MEDIUM_PROBLEMS, HARD_PROBLEMS

#Select what to test
test_manhattan = False
test_fval_function = False
test_alternate = False
test_anytime_weighted_astar = True
test_anytime_gbfs = False

PROBLEMS = PROBLEMS + EASY_PROBLEMS + MEDIUM_PROBLEMS + HARD_PROBLEMS

if test_manhattan:
    ##############################################################
    # TEST MANHATTAN DISTANCE
    print('Testing Manhattan Distance')

    #Correct Manhattan distances for the initial states of the provided problem set
    correct_man_dist = [6, 4, 4, 11, 5, 5, 6, 7, 9, 5, 9, 9, 4, 24, 17, 5, 16, 25, 14, 14, 14, 9, 9, 15, 15, 7, 15, 15, 7, 12, 11, 14, 10, 8, 7, 7, 6, 12, 8, 10, 9, 6, 6, 9, 8, 6, 5, 10, 7, 8, 9, 6, 13, 9, 11, 12, 10, 4, 7, 12]

    solved = 0; unsolved = []

    for i in range(0, len(PROBLEMS)):
        print("PROBLEM {}".format(i))

        s0 = PROBLEMS[i]

        man_dist = heur_manhattan_distance(s0)
        print('calculated man_dist:', str(man_dist))

        print(s0.state_string()) #To see state

        if i < len(correct_man_dist):
          index = i
        else:
          index = 0

        if man_dist == correct_man_dist[index]:
            solved += 1
        else:
            unsolved.append(i)    

    print("*************************************")  
    print("In the problem set provided, you calculated the correct Manhattan distance for {} states out of {}.".format(solved, len(PROBLEMS)))  
    print("States that were incorrect: {}".format(unsolved))  
    print("*************************************\n") 
    ##############################################################

if test_fval_function:

  test_state = SnowmanState("START", 6, None, None, None, None, None, None, None)

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

if test_alternate:

  ##############################################################
  # TEST ALTERNATE HEURISTIC
  print('Testing alternate heuristic with best_first search')

  solved = 0; unsolved = []; benchmark = 51; timebound = 8 #time limit
  output = [50, 17, 36, 43, 71, 66, 29, 22, 34, 37, 43, 57, 65, 106, -99, 48, -99, -99, -99, -99, 74, 62, 42, 66, 41, -99, 79, 47, 142, 118, -99, 226, -99, 108, 82, 97, 58, -99, 30, 54, 35, 92, 77, -99, 77, 137, 128, 35, 61, 120, 98, 25, 44, 145, 92, 95, 120, 33, 26, 145]
  for i in range(0, len(PROBLEMS)): 

    print("*************************************")
    print("PROBLEM {}".format(i))

    s0 = PROBLEMS[i] #Problems get harder as i gets bigger
    print(s0.state_string())
    se = SearchEngine('best_first', 'full')
    se.init_search(s0, goal_fn=snowman_goal_state, heur_fn=heur_alternate)
    final = se.search(timebound)


    if final:
      output.append(final.gval)
      #final.print_path()  
      solved += 1
    else:
      output.append(-99)
      unsolved.append(i)

  print("\n*************************************")
  print("Of {} initial problems, {} were solved in less than {} seconds by this solver.".format(len(PROBLEMS), solved, timebound))
  print("Problems that remain unsolved in the set are Problems: {}".format(unsolved))
  print("The benchmark implementation solved {} out of {} practice problems given {} seconds.".format(benchmark,len(PROBLEMS),timebound))
  print("*************************************\n")
  #print(output)
  ##############################################################
  

if test_anytime_gbfs:

  len_benchmark = [37, 15, 19, 36, 35, 60, 18, 22, 34, 28, 32, 43, 35, 106, -99, 40, -99, -99, -99, -99, 64, 37, 29, 46, 39, -99, 65, 47, 70, 98, -99, 100, -99, 27, 47, 32, 45, -99, 28, 52, 27, 84, 24, -99, 33, 28, 50, 30, 33, 91, 45, 25, 42, 75, 59, 95, 56, 33, 26, 54]

  ##############################################################
  # TEST ANYTIME GBFS
  print('Testing Anytime GBFS')

  solved = 0; unsolved = []; benchmark = 0; timebound = 8 #8 second time limit 
  for i in range(0, len(PROBLEMS)):
    print("*************************************")  
    print("PROBLEM {}".format(i))

    s0 = PROBLEMS[i] #Problems get harder as i gets bigger
    weight = 10
    final = anytime_gbfs(s0, heur_fn=heur_alternate, timebound=timebound)

    if final:
      #output.append(final.gval)
      if i < len(len_benchmark):
        index = i
      else:
        index = 0      
      final.print_path()   
      if final.gval <= len_benchmark[index] or len_benchmark[index] == -99:
        benchmark += 1
      solved += 1 
    else:
      #output.append(-99)
      unsolved.append(i)  

  print("\n*************************************")  
  print("Of {} initial problems, {} were solved in less than {} seconds by this solver.".format(len(PROBLEMS), solved, timebound))  
  print("Of the {} problems that were solved, the cost of {} matched or outperformed the benchmark.".format(solved, benchmark))  
  print("Problems that remain unsolved in the set are Problems: {}".format(unsolved))  
  print("The benchmark implementation solved 50 out of the 60 practice problems given 8 seconds.")  
  print("*************************************\n") 
  #print(output)

if test_anytime_weighted_astar:

  len_benchmark = [37, 15, 19, 36, 35, 60, 18, 22, 34, 28, 32, 43, 37, 88, -99, 40, -99, -99, -99, -99, 60, 37, 24, 46, 35, -99, 65, 47, 53, 98, -99, 92, -99, 63, 46, 32, 34, -99, 28, 48, 27, 82, 24, -99, 29, 47, 66, 28, 33, 90, 45, 25, 42, 73, 55, 95, 56, 33, 26, 95]
  output = []

  ##############################################################
  # TEST ANYTIME WEIGHTED A STAR
  print('Testing Anytime Weighted A Star')

  solved = 0; unsolved = []; benchmark = 0; timebound = 8 #8 second time limit 
  output = []
  for i in range(0, len(PROBLEMS)):
    print("*************************************")  
    print("PROBLEM {}".format(i))

    s0 = PROBLEMS[i] #Problems get harder as i gets bigger
    weight = 10
    final = anytime_weighted_astar(s0, heur_fn=heur_alternate, weight=weight, timebound=timebound)

    if final:
      if i < len(len_benchmark):
        index = i
      else:
        index = 0      
      final.print_path()   
      output.append(final.gval)
      if final.gval <= len_benchmark[index] or len_benchmark[index] == -99:
        benchmark += 1
      solved += 1 
    else:
      output.append(-99)
      unsolved.append(i)  

  print("\n*************************************")  
  print("Of {} initial problems, {} were solved in less than {} seconds by this solver.".format(len(PROBLEMS), solved, timebound))  
  print("Of the {} problems that were solved, the cost of {} matched or outperformed the benchmark.".format(solved, benchmark))  
  print("Problems that remain unsolved in the set are Problems: {}".format(unsolved))  
  print("The benchmark implementation solved 50 out of the 60 practice problems given 8 seconds.")  
  print("*************************************\n") 
  print(output)
  ##############################################################

