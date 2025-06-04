from search import *
from lunarlockout import LunarLockoutState, lockout_goal_state, PROBLEMS
import itertools
import traceback
import gc
import sys

import itertools
import traceback
import gc
import sys
import math

from utils.utilities import sortInnerMostLists, TO_exc, setTO, setMEM, resetMEM

from utils.test_tools import max_grade
from .test_cases_helpers import *

SOLUTION = 'solution.py'

STU_SCORES = []
STU_SCORES_GBFS = []
STU_SCORES_ASTAR = []   

OFFSET = 1

TIMEBOUND = 2
ASTAR_TIMEBOUND = 2
DEFAULT_TIMEOUT = 5 

subset = 5

@max_grade(10)
def test_L(student_modules):    
##############################################################
    # TEST L DISTANCE

    stu_solution = student_modules[SOLUTION]                    

    print('Testing L Distance')

    #Correct L distances for the initial states of the provided problem set
    correct_L_dist = [2, 1, 2, 2, 1, 2, 2, 1, 1, 2, 2, 2, 2, 2, 2, 5, 5, 5, 5, 5]

    solved = 0; unsolved = []; scores =[0,0]
    timeout = DEFAULT_TIMEOUT    
    details = set()
    distances = []

    for i in range(0,subset):
        #print("PROBLEM {}".format(i))

      s0 = PROBLEMS[i]
      try:
          setTO(timeout)

          L_dist = stu_solution.heur_L_distance(s0)
          distances.append(L_dist)
          setTO(0)

          if float(L_dist) > float(correct_L_dist[i] - 0.0000000001) and float(L_dist) < float(correct_L_dist[i] + 0.0000000001):   
              scores[0] += 1  

      except TO_exc:
          details.add("Got TIMEOUT during problem {} when testing manhattan distance".format(i))
      except:
          details.add("A runtime error occurred while testing manhattan distance: %r" % traceback.format_exc())

    details = "\n".join(details)

    scores[1]=(scores[0]/20)*10

    score = math.ceil(scores[1])
   
    ##############################################################
    return score, details        

@max_grade(10)
def test_fval_function(student_modules):    

  stu_solution = student_modules[SOLUTION]                    

  test_state = PROBLEMS[20]

  correct_fvals = [0, 5, 10]
  weights = [0., .5, 1.]  
  fuzz = 0.05;

  score = 0    
  timeout = DEFAULT_TIMEOUT
  details = set()
  for i in range(len(weights)):

    try:
        setTO(timeout)

        test_node = sNode(test_state, 10, stu_solution.fval_function)

        fval = stu_solution.fval_function(test_node, weights[i])

        if ((fval >= correct_fvals[i] - fuzz) and (fval <= correct_fvals[i] + fuzz)):
            score +=1  

        setTO(0)

    except TO_exc:
        details.add("Got TIMEOUT during problem {} when testing fvalue function".format(i))
    except:
        details.add("A runtime error occurred while testing the fvalue function: %r" % traceback.format_exc())

    details = "\n".join(details)

    return score, details  

@max_grade(35)
def test_alternate(student_modules):    

  ##############################################################
  # TEST ALTERNATE HEURISTIC
  print('Testing alternate heuristic with best_first search')

  stu_solution = student_modules[SOLUTION]
  solved = 0; unsolved = []; benchmark = 12; timebound = 2 #time limit
  benchmark_lengths_bfs = [20, 5, 29, 12, 13, -99, 18, 41, 16, -99, 42, 38, -99, 43, 37, -99, -99, -99, -99, -99]
  scores = [0,0,0,0] #4 scores for alternate heuristic, 5 for gbfs, 5 for weighted a-star 
  total_bfs = sum(i != -99 for i in benchmark_lengths_bfs)
  manhattan_benchmark_lengths_bfs =[20, 5, 29, 12, 13, -99, 18, 41, 16, -99, 42, 38, -99, 43, 37, -99, -99, -99, -99, -99]
  total_manhattan_bfs = sum(i != -99 for i in manhattan_benchmark_lengths_bfs)
  solved = []

  details = set()

  timebound = TIMEBOUND
  timeout = DEFAULT_TIMEOUT 

  for i in range(0,subset):
    s0 = PROBLEMS[i]

    try:
        se = SearchEngine('best_first', 'full')
        se.init_search(s0, lockout_goal_state, heur_fn=stu_solution.heur_alternate)
        STU_SCORES.append(-99)

        setTO(timeout)
        final = se.search(timebound)
        setTO(0)

        if final:
            solved.append(i)
            STU_SCORES[i] = final.gval
            scores[0] += 1
            if final.gval <= benchmark_lengths_bfs[i] or benchmark_lengths_bfs[i] == -99:
                scores[1] += 1                  
                
    except TO_exc:
       details.add("Got TIMEOUT during problem {} when testing alternate heuristic".format(i))
    except:
        details.add("A runtime error occurred while testing alternate heuristic: %r" % traceback.format_exc())

    #are the scores better than l_dist solution and alt solution?
  score = 0; margin = 1; # not sure what this margin was about
  #no points for no solutions
  if scores[0] > 0 and scores[0] < 5: #more than 1 -- 5 points
    score = 5
  if (scores[0] < total_manhattan_bfs and scores[0] >= 5): #between 5 and lower benchmark -- 5 to 10 points
    student_margin = scores[0]-5;
    if (student_margin > 0): score = 5 + math.ceil((student_margin/total_manhattan_bfs)*5);      
  if (scores[0] >= total_manhattan_bfs): #between lower benchmark and upper benchmark -- up to 10 points
    score = 10
    margin = total_bfs-total_manhattan_bfs;
    student_margin = scores[0]-total_manhattan_bfs;
    if (student_margin > 0): score = score + math.ceil((student_margin/margin)*10);
  scores[3] = 0
  if (scores[0] >= total_bfs): #last five points for over upper benchmark 
    score = 20
    margin = 40-total_bfs;
    student_margin = scores[0]-total_bfs;
    if (student_margin > 0): score = score + math.ceil((student_margin/margin)*5);       

  bfs_score = score;

  details.add("Best First Search, with the student heuristic, solved {}/40 problems.".format(scores[0]))
  details.add("Best First Search, with manhattan distance, solved {}/40 problems.".format(total_manhattan_bfs))     
  details.add("Best First Search, with an alternate heuristic, solved {}/40 problems.".format(total_bfs))
  details.add("The student outperformed the 'better' benchmark {} times.".format(scores[1]))       
  details.add("Score for alternate heuristic portion: {}/25.".format(bfs_score))  

  details = "\n".join(details)   

  return score, details    


@max_grade(35)
def test_anytime_weighted_astar(student_modules):    
    
    scores = [0,0,0]
    details = set()

    stu_solution = student_modules[SOLUTION]

    astartimebound = ASTAR_TIMEBOUND
    astartimeout = DEFAULT_TIMEOUT #safe margin 

    benchmark_lengths_astar = [18, 4, 21, 10, 8, -99, 16, 41, 16, -99, 39, 38, -99, 35, 29, -99, -99, -99, -99, -99]
    total_astar = sum(i != -99 for i in benchmark_lengths_astar)
    ldist_benchmark_lengths_astar = [18, 4, 21, 10, 8, -99, 16, 41, 16, -99, 39, 38, -99, 35, 29, -99, -99, -99, -99, -99]
    total_ldist_astar = sum(i != -99 for i in ldist_benchmark_lengths_astar)

    for i in range(0,subset):

        s0 = PROBLEMS[i]

        try:
            weight = 10

            setTO(astartimeout)
            final = stu_solution.anytime_weighted_astar(s0, heur_fn=stu_solution.heur_alternate, weight=weight, timebound=astartimebound)
            setTO(0)

            STU_SCORES_ASTAR.append(-99)

            if final:
                scores[0] += 1
                STU_SCORES_ASTAR[i] = final.gval  
                if final.gval <= benchmark_lengths_astar[i] or benchmark_lengths_astar[i] == -99:
                    scores[1] += 1   

        except TO_exc:
            details.add("Got TIMEOUT during problem {} while testing weighted a-star".format(i))
        except:
            details.add("A runtime error occurred while testing weighted a-star: %r" % traceback.format_exc())

    details.add("Weighted astar, with the student heuristic, solved {}/40 problems.".format(scores[0]))
    details.add("Weighted astar, with ldist distance, solved {}/40.".format(total_ldist_astar)) 
    details.add("Weighted astar, with an alternate heuristic, solved {}/40 problems.".format(total_astar))
    details.add("The student outperformed the 'better' benchmark {} times.".format(scores[1]))     

    score = 0; margin = 1; #not sure what this was about
    if isinstance(scores,int):
        details.add("--> Problem running student solution.") 

    #no points for no solutions
    elif scores[0] > 0 and scores[0] < 5: #more than 1 -- you get 5 points
        score = 5
    elif (scores[0] < total_ldist_astar and scores[0] >= 5): #between 5 and lower benchmark -- 5 to 10 points
        student_margin = scores[0]-5;
        if (student_margin > 0): score = 5 + math.ceil((student_margin/total_ldist_astar)*5);        
    elif (scores[0] >= total_astar and scores[1] >= total_astar): #over benchmark and short, automatic perfect mark
        score = 25
        details.add("--> Matched or beat length of benchmark at least {} times.".format(total_astar)) 
    elif (scores[0] >= total_astar):  
        score = 20
        margin = 40-total_astar;
        student_margin = scores[0]-total_astar;
        if (student_margin > 0): 
            score = score + math.ceil((student_margin/margin)*5);   
            details.add("--> Margin over benchmark: {} problems.".format(scores[0]-total_astar))      
    elif (scores[0] >= total_ldist_astar): 
        score = 10
        margin = total_astar-total_ldist_astar;
        student_margin = scores[0]-total_ldist_astar;
        if (student_margin > 0): score = score + math.ceil((student_margin/margin)*10);        

    details = "\n".join(details)   

    return score, details  


