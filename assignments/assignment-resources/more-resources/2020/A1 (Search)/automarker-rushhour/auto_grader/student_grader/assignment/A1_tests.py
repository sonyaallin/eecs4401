from search import *
from rushhour import *
import itertools
import traceback
import gc
import sys

import itertools
import traceback
import gc
import sys
import math
import os
import pickle

from utils.utilities import sortInnerMostLists, TO_exc, setTO, setMEM, resetMEM

from utils.test_tools import max_grade
from .test_cases_helpers import *

SOLUTION = 'solution.py'

STU_SCORES = []
STU_SCORES_GBFS = []
STU_SCORES_ASTAR = []   

TIMEBOUND = 1
ASTAR_TIMEBOUND = 1
DEFAULT_TIMEOUT = 1

#load the test problems
PROBLEMS = []
with (open("student_grader/dependencies/rushhour_tests.pkl", "rb")) as openfile:
    while True:
        try:
            PROBLEMS.append(pickle.load(openfile))
        except EOFError:
            break

#load the test goals
GOALS = pickle.load( open( "student_grader/dependencies/rushhour_goals.pkl", "rb" ) )

@max_grade(10)
def test_min_moves(student_modules):

    stu_solution = student_modules[SOLUTION]                    
    #Correct MIN MOVES distances for the initial states of the provided problem set
    correct_min_moves = [1, 3, 2, 1, 3, 1, 1, 2, 1, 2, 2, 1, 3, 2, 2, 0, 1, 2, 1, 2, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 3, 7, 10, 14, 14, 17, 24, 28, 31, 29];

    scores = [0, 0]
    timeout = DEFAULT_TIMEOUT
    distances = []

    details = set()

    for i in range(len(PROBLEMS)):

        s0 = PROBLEMS[i]

        try:
            setTO(timeout)

            moves_dist = stu_solution.heur_min_moves(s0)            
            distances.append(moves_dist)
        
            setTO(0)

            if float(moves_dist) > float(correct_min_moves[i] - 0.0000000001) and float(moves_dist) < float(correct_min_moves[i] + 0.0000000001):   
                scores[0] += 1     
    
        except TO_exc:
            details.add("Got TIMEOUT during problem {} when testing manhattan distance".format(i))
        except:
            details.add("A runtime error occurred while testing min_moves distance: %r" % traceback.format_exc())
    
    details.add("Correct min_moves distances calculated {} of {} times".format(scores[0], 60))

    details = "\n".join(details)

    scores[1]=(scores[0]/60)*10

    score = math.ceil(scores[1])

    return score, details            

@max_grade(10)
def test_fval_function(student_modules):

    stu_solution = student_modules[SOLUTION]
    test_state = Rushhour("START", 6, None, None, None)
    correct_fvals = [6,16,26,36,46,56,66,76,86,96]
    weights = [0,1,2,3,4, 5, 6,7,8,9]
    fuzz = 0.5

    fvals = []
    score = 0    
    timeout = DEFAULT_TIMEOUT
    details = set()
    for i in range(len(weights)):

        try:
            setTO(timeout)

            test_node = sNode(test_state, 10, stu_solution.fval_function)

            fval = stu_solution.fval_function(test_node, weights[i])

            fvals.append(fval)

            if ((fval >= correct_fvals[i] - fuzz) and (fval <= correct_fvals[i] + fuzz)):
              score +=1  

            setTO(0)

        except TO_exc:
            details.add("Got TIMEOUT during problem {} when testing fvalue function".format(i))
        except:
            details.add("A runtime error occurred while testing the fvalue function: %r" % traceback.format_exc())

    details = "\n".join(details)

    return score, details

@max_grade(25)
def test_heuristic(student_modules):

    stu_solution = student_modules[SOLUTION]
 
    scores = [0,0,0,0] #4 scores for alternate heuristic, 5 for gbfs, 5 for weighted a-star 
    details = set()

    timebound = TIMEBOUND
    timeout = DEFAULT_TIMEOUT 

    solved = []

    for i in range(10,len(PROBLEMS)):

        s0 = PROBLEMS[i]

        try:
            se = SearchEngine('best_first', 'full')
            se.init_search(s0, rushhour_goal_fn_final, heur_fn=stu_solution.heur_alternate)

            #setTO(timeout)
            final = se.search(timebound)
            #setTO(0)

            se = SearchEngine('best_first', 'full')
            se.init_search(s0, rushhour_goal_fn_final, heur_fn=stu_solution.heur_min_moves)

            #setTO(timeout)
            baseline = se.search(timebound)
            #setTO(0)

            if final and not baseline:
                scores[0] += 1

            if final and baseline:
                scores[1] += 1

            if not final and not baseline:
                scores[2] += 1  

            if not final and baseline:
                scores[3] += 1  

                
        except TO_exc:
           details.add("Got TIMEOUT during problem {} when testing alternate heuristic".format(i))
        except:
            details.add("A runtime error occurred while testing alternate heuristic: %r" % traceback.format_exc())

    #are the scores better than manhattan solution and alt solution?
    score = 0

    details.add("{}/{} problems were solved using Best First Search with the student heuristic and not solved with the min_moves heuristic.".format(scores[0],len(PROBLEMS)-10))
    details.add("{}/{} problems were solved using Best First Search with the student heuristic and the min_moves heuristic.".format(scores[1],len(PROBLEMS)-10))
    details.add("{}/{} problems were not solved using Best First Search with any heuristic.".format(scores[2],len(PROBLEMS)-10))
    details.add("{}/{} problems were not solved using Best First Search with the student heuristic, yet were solved using the min_moves heuristic.".format(scores[3],len(PROBLEMS)-10))

    details = "\n".join(details)  

    print(scores) 

    return scores, details  

@max_grade(25)
def test_anytime_gbfs(student_modules):

    scores = [0,0,0]
    details = set()

    stu_solution = student_modules[SOLUTION]

    timebound = 1

    BFS = []
    ABFS1 = []
    ABFS2 = []

    for i in range(10,len(PROBLEMS)):

        s0 = PROBLEMS[i]

        try:

            se = SearchEngine('best_first', 'full')
            se.init_search(s0, rushhour_goal_fn_final, heur_fn=stu_solution.heur_min_moves)
            final = se.search(timebound)
            final1 = stu_solution.anytime_gbfs(s0, heur_fn=stu_solution.heur_min_moves, timebound=timebound) 
            final2 = stu_solution.anytime_gbfs(s0, heur_fn=stu_solution.heur_min_moves, timebound=timebound*2)

            if final:
                BFS.append(final.gval)
            else: 
                BFS.append(float('inf'))                   

            if final1:
                ABFS1.append(final1.gval)
            else: 
                ABFS1.append(float('inf'))                 

            if final2:
                ABFS2.append(final2.gval)
            else: 
                ABFS2.append(float('inf'))   

        except TO_exc:
            details.add("Got TIMEOUT during problem {} while testing anytime gbfs".format(i))
        except:
            details.add("A runtime error occurred while testing anytime gbfs: %r" % traceback.format_exc())
    
    for i in range(len(BFS)):
        if BFS[i] >= ABFS1[i] and ABFS1[i] >= ABFS2[i]:
            scores[0] += 1
        else:
            if BFS[i] < ABFS1[i] or BFS[i] < ABFS2[i]:
                scores[1] += 1

            if ABFS1[i] < ABFS2[i]:
                scores[2] += 1
    
    details.add("Given more time, anytime gbfs improved the length of solutions for {}/{} problems.".format(scores[0], len(PROBLEMS)-10))
    details.add("Given the same time, regular BFS performed better than anytime gbfs on {}/{} problems.".format(scores[1], len(PROBLEMS)-10))
    details.add("Given more time, anytime gbfs worsened the length of solutions for {}/{} problems.".format(scores[2], len(PROBLEMS)-10))

    details = "\n".join(details)   

    return scores, details  

@max_grade(25)
def test_anytime_weighted_astar(student_modules):

    scores = [0,0,0,0]
    details = set()

    stu_solution = student_modules[SOLUTION]

    timebound = 1

    AS1 = []
    AS2 = []

    for i in range(10,len(PROBLEMS)):

        s0 = PROBLEMS[i]

        try:

            se = SearchEngine('best_first', 'full')
            final1 = stu_solution.anytime_weighted_astar(s0, heur_fn=stu_solution.heur_min_moves, timebound=timebound) 
            final2 = stu_solution.anytime_weighted_astar(s0, heur_fn=stu_solution.heur_min_moves, timebound=timebound*2)
                
            if final1:
                AS1.append(final1.gval)
            else: 
                AS1.append(float('inf'))                   

            if final2:
                AS2.append(final2.gval)
            else: 
                AS2.append(float('inf')) 

        except TO_exc:
            details.add("Got TIMEOUT during problem {} while testing anytime gbfs".format(i))
        except:
            details.add("A runtime error occurred while testing anytime gbfs: %r" % traceback.format_exc())
    
    for i in range(len(AS1)):
        if (AS2[i] < float('inf')):
            scores[0] += 1
        if AS2[i] == AS1[i] and AS2[i] != float('inf'):
            scores[1] += 1 
        if AS2[i] < AS1[i]:
            scores[2] += 1            
        if AS1[i] < AS2[i]:
            scores[3] += 1

    details.add("With heur_min_moves, anytime astar solved {} of {} problems.".format(scores[0], len(PROBLEMS)-10))    
    details.add("More time resulted in the same performance on {}/{} problems.".format(scores[1], len(PROBLEMS)-10))
    details.add("More time improved performance of anytime astar on {}/{} problems.".format(scores[2], len(PROBLEMS)-10))
    details.add("More time worsened performance of anytime astar on {}/{} problems.".format(scores[3], len(PROBLEMS)-10))

    details = "\n".join(details)   

    return scores, details  

@max_grade(25)
def test_goal_fn(student_modules):

    scores = [0, 0]
    details = set()
    score = 0

    stu_solution = student_modules[SOLUTION]
    
    for i in range(0,40):
        s0 = GOALS[i]

        if (rushhour_goal_fn_final(s0)):
            if (stu_solution.rushhour_goal_fn(s0)):
                scores[0] += 1
                score += 1
    
    details.add("Goal states correctly detected {} of {} times.".format(scores[0], 40))    

    details = "\n".join(details)

    return score, details  



