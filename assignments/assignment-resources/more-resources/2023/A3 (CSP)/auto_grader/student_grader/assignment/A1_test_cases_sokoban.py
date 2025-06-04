from search import *
from sokoban import *
import itertools
import traceback
import gc
import sys

from utils.utilities import sortInnerMostLists, TO_exc, setTO, setMEM, resetMEM

from utils.test_tools import max_grade
from .test_cases_helpers import *

#from dependencies.solutions.additional_problems import ADDITIONAL_PROBLEMS

#TODO define reasonable timeouts
DEFAULT_TIMEOUT = 20
timeout = 20

SOLUTION = 'solution.py'
#PROBLEMS = ADDITIONAL_PROBLEMS

PROBLEMS = (
    SokobanState("START", 0, None, 5, 5, # dimensions
                 ((2, 2),), #robots
                 frozenset(((1, 1), (1, 3))), #boxes 
                 frozenset(((0, 0), (4, 4))), #storage
                 frozenset(((1, 0), (2, 0), (3, 0), (1, 4), (2, 4), (3, 4))) #obstacles
                 ),
    SokobanState("START", 0, None, 5, 5, # dimensions
                 ((2, 2),), #robots
                 frozenset(((1, 1),)), #boxes 
                 frozenset(((0, 0),)), #storage
                 frozenset(((1, 0), (2, 0), (3, 0), (1, 4), (2, 4), (3, 4))) #obstacles
                 ),
    SokobanState("START", 0, None, 5, 5, # dimensions
                 ((2, 2),), #robots
                 frozenset(((1, 3),)), #boxes 
                 frozenset(((4, 4),)), #storage
                 frozenset(((1, 0), (2, 0), (3, 0), (1, 4), (2, 4), (3, 4))) #obstacles
                 ),
    SokobanState("START", 0, None, 6, 4, # dimensions
                 ((2, 1), (2, 2)), #robots
                 frozenset(((1, 1), (1, 2), (4, 1), (4, 2))), #boxes 
                 frozenset(((2, 1), (2, 2), (3, 1), (3, 2))), #storage
                 frozenset() #obstacles
                 ),
    SokobanState("START", 0, None, 6, 4, # dimensions
                 ((2, 1), (2, 2)), #robots
                 frozenset(((1, 1), (1, 2), (4, 1))), #boxes 
                 frozenset(((2, 1), (3, 1), (3, 2))), #storage
                 frozenset() #obstacles
                 ),
    SokobanState("START", 0, None, 6, 4, # dimensions
                 ((2, 1),), #robots
                 frozenset(((1, 1), (1, 2), (4, 1))), #boxes 
                 frozenset(((2, 1), (3, 1), (3, 2))), #storage
                 frozenset() #obstacles
                 ),
    SokobanState("START", 0, None, 6, 4, # dimensions
                 ((2, 1),), #robots
                 frozenset(((1, 1), (1, 2))), #boxes 
                 frozenset(((2, 1), (2, 2))), #storage
                 frozenset() #obstacles
                 ),
    SokobanState("START", 0, None, 6, 4, # dimensions
                 ((2, 1),), #robots
                 frozenset(((1, 1), (4, 2))), #boxes 
                 frozenset(((2, 1), (2, 2))), #storage
                 frozenset() #obstacles
                 ),
    SokobanState("START", 0, None, 6, 4, # dimensions
                 ((2, 1),), #robots
                 frozenset(((1, 1),)), #boxes 
                 frozenset(((2, 1),)), #storage
                 frozenset() #obstacles
                 ),
    SokobanState("START", 0, None, 6, 4, # dimensions
                 ((2, 1),), #robots
                 frozenset(((4, 2),)), #boxes 
                 frozenset(((2, 1),)), #storage
                 frozenset() #obstacles
                 ),
    SokobanState("START", 0, None, 5, 5, # dimensions
                 ((4, 0),), #robots
                 frozenset(((3, 1), (3, 3))), #boxes 
                 frozenset(((0, 0), (0, 4))), #storage
                 frozenset(((2, 0), (2, 1), (2, 3), (2, 4))) #obstacles
                 ),
    SokobanState("START", 0, None, 5, 5, # dimensions
                 ((4, 0),), #robots
                 frozenset(((3, 1), (3, 2))), #boxes 
                 frozenset(((0, 0), (0, 2))), #storage
                 frozenset(((2, 0), (2, 1), (2, 3), (2, 4))) #obstacles
                 ),
    SokobanState("START", 0, None, 5, 5, # dimensions
                 ((4, 0),), #robots
                 frozenset(((3, 1),)), #boxes 
                 frozenset(((0, 0),)), #storage
                 frozenset(((2, 0), (2, 1), (2, 3), (2, 4))) #obstacles
                 ),    
    SokobanState("START", 0, None, 6, 6, # dimensions
                 ((0, 0), (5, 1), (0, 2), (5, 3), (0, 4), (5, 5)), #robots
                 frozenset(((1, 0), (4, 1), (1, 2), (4, 3), (1, 4), (4, 5))), #boxes 
                 frozenset(((5, 0), (0, 1), (5, 2), (0, 3), (5, 4), (0, 5))), #storage
                 frozenset() #obstacles
                 ),
    SokobanState("START", 0, None, 6, 6, # dimensions
                 ((0, 0), (0, 2), (0, 4)), #robots
                 frozenset(((1, 0), (1, 2), (1, 4))), #boxes 
                 frozenset(((5, 0), (5, 2), (5, 4))), #storage
                 frozenset() #obstacles
                 ),
    SokobanState("START", 0, None, 6, 6, # dimensions
                 ((5, 1), (0, 4)), #robots
                 frozenset(((1, 0), (4, 1), (1, 2), (4, 3), (1, 4), (4, 5))), #boxes 
                 frozenset(((5, 0), (0, 1), (5, 2), (0, 3), (5, 4), (0, 5))), #storage
                 frozenset() #obstacles
                 ),
    SokobanState("START", 0, None, 6, 6, # dimensions
                 ((0, 2), (3, 3)), #robots
                 frozenset(((1, 0), (1, 2), (1, 4))), #boxes 
                 frozenset(((5, 0), (5, 2), (5, 4))), #storage
                 frozenset() #obstacles
                 ),
    SokobanState("START", 0, None, 6, 6, # dimensions
                 ((0, 2), (3, 3)), #robots
                 frozenset(((1, 0), (1, 2), (1, 4))), #boxes 
                 frozenset(((5, 0), (0, 3), (0, 5))), #storage
                 frozenset() #obstacles
                 ),
    SokobanState("START", 0, None, 6, 6, # dimensions
                 ((0, 2), (3, 3)), #robots
                 frozenset(((1, 0), (1, 2), (1, 4))), #boxes 
                 frozenset(((5, 0), (5, 2), (0, 5))), #storage
                 frozenset() #obstacles
                 ),
    SokobanState("START", 0, None, 6, 6, # dimensions
                 ((0, 2), (3, 3)), #robots
                 frozenset(((1, 0), (1, 2), (1, 4))), #boxes 
                 frozenset(((5, 0), (0, 3), (5, 4))), #storage
                 frozenset() #obstacles
                 ),
    SokobanState("START", 0, None, 6, 6, # dimensions
                 ((5, 5), (5, 4), (4, 5)), #robots
                 frozenset(((3, 1), (2, 2))), #boxes 
                 frozenset(((0, 0), (0, 1))), #storage
                 frozenset() #obstacles
                 ),
    SokobanState("START", 0, None, 6, 6, # dimensions
                 ((5, 5), (5, 4), (4, 5)), #robots
                 frozenset(((3, 1), (3, 4))), #boxes 
                 frozenset(((0, 0), (0, 1))), #storage
                 frozenset() #obstacles
                 ),
    SokobanState("START", 0, None, 6, 6, # dimensions
                 ((5, 5), (5, 4), (4, 5)), #robots
                 frozenset(((1, 4), (3, 4))), #boxes 
                 frozenset(((0, 0), (0, 1))), #storage
                 frozenset() #obstacles
                 ),
    SokobanState("START", 0, None, 6, 6, # dimensions
                 ((5, 5), (5, 4), (4, 5)), #robots
                 frozenset(((2, 2), (1, 4))), #boxes 
                 frozenset(((0, 0), (0, 1))), #storage
                 frozenset() #obstacles
                 ),
    SokobanState("START", 0, None, 6, 6, # dimensions
                 ((5, 5), (5, 4)), #robots
                 frozenset(((3, 1), (2, 2), (1, 4), (3, 4))), #boxes 
                 frozenset(((0, 0), (0, 1), (1, 0), (1, 1))), #storage
                 frozenset() #obstacles
                 ),
    SokobanState("START", 0, None, 6, 6, # dimensions
                 ((5, 5), (5, 4)), #robots
                 frozenset(((3, 1), (3, 4))), #boxes 
                 frozenset(((0, 0), (0, 1))), #storage
                 frozenset() #obstacles
                 ),
    SokobanState("START", 0, None, 6, 6, # dimensions
                 ((5, 5), (5, 4)), #robots
                 frozenset(((1, 4), (3, 4))), #boxes 
                 frozenset(((0, 0), (0, 1))), #storage
                 frozenset() #obstacles
                 ),
    SokobanState("START", 0, None, 6, 6, # dimensions
                 ((5, 5), (5, 4)), #robots
                 frozenset(((2, 2), (1, 4))), #boxes 
                 frozenset(((0, 0), (0, 1))), #storage
                 frozenset() #obstacles
                 ),
    SokobanState("START", 0, None, 8, 8, # dimensions
                 ((0, 5), (1, 6), (2, 7)), #robots
                 frozenset(((5, 1), (4, 3), (6, 2), (5, 5), (6, 5))), #boxes 
                 frozenset(((0, 0), (1, 0), (2, 0), (0, 1), (1, 1), (0, 2))), #storage
                 frozenset() #obstacles
                 ),
    SokobanState("START", 0, None, 8, 8, # dimensions
                 ((0, 5), (1, 6), (2, 7)), #robots
                 frozenset(((6, 4), (6, 6), (5, 6), (6, 1), (4, 5), (5, 2))), #boxes 
                 frozenset(((0, 0), (1, 0), (2, 0), (0, 1), (1, 1), (0, 2))), #storage
                 frozenset() #obstacles
                 ),
    SokobanState("START", 0, None, 8, 8, # dimensions
                 ((0, 5), (1, 6)), #robots
                 frozenset(((5, 4), (5, 5), (6, 3), (4, 2), (6, 5), (5, 3))), #boxes 
                 frozenset(((0, 0), (1, 0), (2, 0), (0, 1), (1, 1), (0, 2))), #storage
                 frozenset() #obstacles
                 ),
    SokobanState("START", 0, None, 8, 8, # dimensions
                 ((0, 5), (1, 6)), #robots
                 frozenset(((4, 5), (5, 3), (4, 4), (6, 6))), #boxes 
                 frozenset(((0, 0), (1, 0), (2, 0), (0, 1), (1, 1), (0, 2))), #storage
                 frozenset() #obstacles
                 ),
    SokobanState("START", 0, None, 8, 8, # dimensions
                 ((0, 5), (1, 6)), #robots
                 frozenset(((6, 6), (5, 6), (6, 2), (4, 3), (5, 1), (6, 5))), #boxes 
                 frozenset(((0, 0), (1, 0), (2, 0), (0, 1), (1, 1), (0, 2))), #storage
                 frozenset() #obstacles
                 ),
    SokobanState("START", 0, None, 8, 8, # dimensions
                 ((0, 5), (1, 6)), #robots
                 frozenset(((5, 6), (4, 4), (4, 3), (6, 5), (6, 2))), #boxes 
                 frozenset(((0, 0), (1, 0), (2, 0), (0, 1), (1, 1), (0, 2))), #storage
                 frozenset() #obstacles
                 ),
    SokobanState("START", 0, None, 8, 8, # dimensions
                 ((0, 5), (1, 6)), #robots
                 frozenset(((6, 6), (4, 5), (4, 1), (4, 3), (5, 2), (5, 3))), #boxes 
                 frozenset(((0, 0), (1, 0), (2, 0), (0, 1), (1, 1), (0, 2))), #storage
                 frozenset() #obstacles
                 ),
    SokobanState("START", 0, None, 8, 8, # dimensions
                 ((0, 5), (1, 6)), #robots
                 frozenset(((6, 4), (6, 6), (5, 6), (6, 1), (4, 5), (5, 2))), #boxes 
                 frozenset(((0, 0), (1, 0), (2, 0), (0, 1), (1, 1), (0, 2))), #storage
                 frozenset() #obstacles
                 ),
    SokobanState("START", 0, None, 8, 8, # dimensions
                 ((0, 5), (1, 6)), #robots
                 frozenset(((5, 6), (4, 5), (6, 2), (5, 2), (4, 6))), #boxes 
                 frozenset(((0, 0), (1, 0), (2, 0), (0, 1), (1, 1), (0, 2))), #storage
                 frozenset() #obstacles
                 ),
    SokobanState("START", 0, None, 8, 8, # dimensions
                 ((0, 5), (1, 6)), #robots
                 frozenset(((5, 5), (6, 6), (4, 5), (5, 6), (6, 2), (4, 3))), #boxes 
                 frozenset(((0, 0), (1, 0), (2, 0), (0, 1), (1, 1), (0, 2))), #storage
                 frozenset() #obstacles
                 ),
    SokobanState("START", 0, None, 8, 8, # dimensions
                 ((0, 5), (1, 6)), #robots
                 frozenset(((6, 2), (5, 6), (4, 4), (6, 3))), #boxes 
                 frozenset(((0, 0), (1, 0), (2, 0), (0, 1), (1, 1), (0, 2))), #storage
                 frozenset() #obstacles
                 ),
    SokobanState("START", 0, None, 8, 8, # dimensions
                 ((0, 5), (1, 6)), #robots
                 frozenset(((6, 3), (4, 5), (6, 1), (5, 5), (4, 3))), #boxes 
                 frozenset(((0, 0), (1, 0), (2, 0), (0, 1), (1, 1), (0, 2))), #storage
                 frozenset() #obstacles
                 )
    )


###### BEGIN TESTS ######
@max_grade(10)
def test_fval_function(student_modules):

    stu_solution = student_modules[SOLUTION]
    test_state = SokobanState("START", 6, None, None, None, None, None, None, None)
    correct_fvals = [6,6.4,6.8, 7.2, 7.6, 8, 8.4, 8.8, 9.2, 9.6]
    weights = [0.,.1,.2,.3,.4, .5, .6,.7,.8,.9]
    fuzz = 0.05

    score = 0    
    timeout = DEFAULT_TIMEOUT
    details = set()


    for i in range(len(weights)):

        try:
            setTO(timeout)

            test_node = sNode(test_state, 10, stu_solution.fval_function, weights[i])

            fval = stu_solution.fval_function(test_node, weights[i])

            if ((fval >= correct_fvals[i] - fuzz) and (fval <= correct_fvals[i] + fuzz)):
              score +=1  

            setTO(0)

        except TO_exc:
            details.add("Got TIMEOUT while testing anytime weighted a star")
        except:
            details.add("A runtime error occurred while testing the fvalue function: %r" % traceback.format_exc())

    details = "\n".join(details)

    return score, details


@max_grade(40)
def test_manhattan(student_modules):

    stu_solution = student_modules[SOLUTION]
    #correct_man_dist = [8, 6, 2, 4, 8, 2, 3, 1, 3, 4, 11, 8, 7, 4, 11, 8, 10, 8, 
    #                    12, 12, 12, 13, 13, 12, 10, 13, 13, 12, 10, 6, 35, 45, 28, 
    #                    32, 41, 29, 43, 35, 36, 32]                        
    correct_man_dist = [6, 2, 4, 4, 4, 4, 2, 3, 1, 3, 8, 7, 4, 12, 12, 12, 12, 8, 
                        10, 8, 6, 9, 10, 7, 12, 9, 10, 7, 32, 44, 41, 29, 43, 35, 
                        36, 44, 35, 45, 28, 32]
    score = [0,0]
    timeout = DEFAULT_TIMEOUT

    details = set()

    for i in range(len(PROBLEMS)):

        s0 = PROBLEMS[i]

        try:
            setTO(timeout)

            man_dist = stu_solution.heur_manhattan_distance(s0)

            setTO(0)

            if man_dist == correct_man_dist[i]:
                score[0] += 1
            elif abs(man_dist - correct_man_dist[i]) < .1*(correct_man_dist[i]):
                score[1] += 1                

        except TO_exc:
            details.add("Got TIMEOUT while testing manhattan distance")
        except:
            details.add("A runtime error occurred while testing manhattan distance: %r" % traceback.format_exc())

    details = "\n".join(details)

    return score, details

@max_grade(5)
def test_alternate_heuristic_1sec(student_modules):
    stu_solution = student_modules[SOLUTION]

    score = 0
    as_good = 0    
    timeout = DEFAULT_TIMEOUT
    details = set()

    timebound = 1
    benchmark_solutions = 23
    manhattan_benchmark_solutions = 21       
    benchmark_lengths = [17, 5, 9, 31, 26, 19, 8, 14, 5, 9, 33, 23, 11, -99, 12, -99, 38, 22, 24, 22, -99, 37, -99, 55, 48, 22, 26, 22, -99, -99, -99, -99, -99, -99, -99, -99, -99, -99, -99, -99]
    manhattan_benchmark_lengths = [13, 5, 9, 29, 22, 18, 9, 14, 5, 9, 35, 23, 11, -99, 12, -99, 30, 22, 27, -99, 30, -99, -99, 26, -99, 40, 32, -99, -99, -99, -99, -99, -99, -99, -99, -99, -99, -99, -99, -99]
    sample_probs = [0, 5, 10, 20, 30] 

    #print(stu_solution)


    for i in range(len(PROBLEMS)):
    #for i in sample_probs:

        s0 = PROBLEMS[i]

        try:
            setTO(timeout)

            se = SearchEngine('best_first', 'full')
            final = se.search(initState=s0, heur_fn=stu_solution.heur_alternate, timebound=timebound, goal_fn=sokoban_goal_state)

            setTO(0)

            if final:
                score += 1
                if final.gval <= benchmark_lengths[i] or benchmark_lengths[i] == -99:
                    as_good += 1

        except TO_exc:
            details.add("Got TIMEOUT while testing alternate heuristic with 1 sec")
        except:
            details.add("A runtime error occurred while testing alternate heuristic with 1 sec: %r" % traceback.format_exc())

    details = "\n".join(details)

    return score, details

@max_grade(5)
def test_alternate_heuristic_5sec_and_weighted_astar(student_modules):
    stu_solution = student_modules[SOLUTION]

    score = [0,0,0,0,0]
    as_good = 0
    timeout = DEFAULT_TIMEOUT
    details = set()

    timebound = 5
    benchmark_solutions = 24
    manhattan_benchmark_solutions = 22   
    #benchmark_lengths = [17, 5, 9, 31, 26, 19, 8, 14, 5, 9, 33, 23, 11, -99, 12, -99, 38, 22, 24, 22, -99, 37, -99, 55, 48, 22, 26, 22, -99, -99, -99, -99, -99, -99, -99, -99, -99, -99, -99, -99]
    len_benchmark = [13, 5, 9, 17, 16, 16, 8, 13, 5, 9, 29, 23, 11, -99, 12, -99, 26, 20, 24, 26, -99, 17, -99, 23, 39, 19, 20, 22, -99, -99, -99, -99, -99, -99, -99, -99, -99, -99, -99, -99]
    manhattan_benchmark_lengths = [13, 5, 9, 29, 22, 18, 9, 14, 5, 9, 35, 23, 11, -99, 12, -99, 30, 22, 27, -99, 30, 97, -99, 26, -99, 40, 32, -99, -99, -99, -99, -99, -99, -99, -99, -99, -99, -99, -99, -99]
    stu_bfs_lens =[]
    stu_astar_lens =[]    

    #sample_probs = [0, 5, 10, 20, 30] 
    sample_probs = range(len(PROBLEMS))   

    #for i in range(len(PROBLEMS)):
    for i in sample_probs:

        s0 = PROBLEMS[i]

        try:
            setTO(timeout)

            se = SearchEngine('best_first', 'full')
            final = se.search(initState=s0, heur_fn=stu_solution.heur_alternate, timebound=timebound, goal_fn=sokoban_goal_state)

            setTO(0)

            if final:
                score[0] += 1
                stu_bfs_lens.append(final.gval)
            else:
                stu_bfs_lens.append(-99)

        except TO_exc:
            details.add("Got TIMEOUT while testing alternate heuristic with 5 sec")
        except:
            details.add("A runtime error occurred while testing alternate heuristic with 5 sec: %r" % traceback.format_exc())

    timebound = 8

    #for i in range(len(PROBLEMS)): 
    for i in sample_probs:

        s0 = PROBLEMS[i]

        try:
            setTO(timeout)

            final = stu_solution.weighted_astar(s0, timebound)

            setTO(0)

            if final:
                score[1] += 1
                stu_astar_lens.append(final.gval)                
            else:
                stu_astar_lens.append(-99)

        except TO_exc:
            details.add("Got TIMEOUT while testing weighted a-star with 8 sec limit")
        except:
            details.add("A runtime error occurred while testing weighted a-star with 8 sec limit: %r" % traceback.format_exc())

    for i in range(len(stu_astar_lens)):
        
        if stu_astar_lens[i] > stu_bfs_lens[i]:
                score[2] += 1

        if (stu_astar_lens[i] != -99 and (stu_astar_lens[i] <= len_benchmark[sample_probs[i]])) or (len_benchmark[sample_probs[i]] == -99 and stu_astar_lens[i] > 0):
                if stu_astar_lens[i] == len_benchmark[sample_probs[i]]:
                    score[3] += 1                     
                else:
                    score[4] += 1   

    details = "\n".join(details)

    return score, details

# @max_grade(40)
# def test_alternate_heuristic_5sec(student_modules):
#     stu_solution = student_modules[SOLUTION]

#     score = 0
#     as_good = 0
#     timeout = DEFAULT_TIMEOUT
#     details = set()

#     timebound = 5
#     benchmark_solutions = 24
#     manhattan_benchmark_solutions = 22   
#     benchmark_lengths = [17, 5, 9, 31, 26, 19, 8, 14, 5, 9, 33, 23, 11, -99, 12, -99, 38, 22, 24, 22, -99, 37, -99, 55, 48, 22, 26, 22, -99, -99, -99, -99, -99, -99, -99, -99, -99, -99, -99, -99]
#     manhattan_benchmark_lengths = [13, 5, 9, 29, 22, 18, 9, 14, 5, 9, 35, 23, 11, -99, 12, -99, 30, 22, 27, -99, 30, 97, -99, 26, -99, 40, 32, -99, -99, -99, -99, -99, -99, -99, -99, -99, -99, -99, -99, -99]

#     for i in range(len(PROBLEMS)):

#         s0 = PROBLEMS[i]

#         try:
#             setTO(timeout)

#             se = SearchEngine('best_first', 'full')
#             final = se.search(initState=s0, heur_fn=stu_solution.heur_alternate, timebound=timebound, goal_fn=sokoban_goal_state)

#             setTO(0)

#             if final:
#                 score += 1
#                 if final.gval <= benchmark_lengths[i] or benchmark_lengths[i] == -99:
#                     as_good += 1

#         except TO_exc:
#             details.add("Got TIMEOUT while testing alternate heuristic with 5 sec")
#         except:
#             details.add("A runtime error occurred while testing alternate heuristic with 5 sec: %r" % traceback.format_exc())

#     details = "\n".join(details)

#     return score, details


# @max_grade(40)
# def test_weighted_astar(student_modules):

#     stu_solution = student_modules[SOLUTION]
#     #len_benchmark = [16, 13, 4, 10, 21, 9, 10, 5, 8, 18, -99, -99, 16, 11, 41, 14, 14, 14, -99, -99, 37, -99, 38, -99, -99, 33, 33, 29, 29, 18, -99, -99, -99, 81, -99, -99, -99, -99, -99, -99]
#     #[13, 15, 20, 22, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39]
#     benchmark_solutions = 24
#     manhattan_benchmark_solutions = 22   

#     #len_benchmark = [17, 5, 9, 31, 26, 19, 8, 14, 5, 9, 33, 23, 11, -99, 12, -99, 38, 22, 24, 22, -99, 37, -99, 55, 48, 22, 26, 22, -99, -99, -99, -99, -99, -99, -99, -99, -99, -99, -99, -99]
#     len_benchmark = [13, 5, 9, 17, 16, 16, 8, 13, 5, 9, 29, 23, 11, -99, 12, -99, 26, 20, 24, 26, -99, 17, -99, 23, 39, 19, 20, 22, -99, -99, -99, -99, -99, -99, -99, -99, -99, -99, -99, -99]
#     manhattan_benchmark_lengths = [13, 5, 9, 17, 16, 16, 8, 13, 5, 9, 29, 23, 11, -99, 12, -99, 22, 20, 18, -99, 18, 18, -99, 18, -99, 19, 22, -99, -99, -99, -99, -99, -99, -99, -99, -99, -99, -99, -99, -99]

#     score = [0, 0]
#     as_good = 0
#     timeout = DEFAULT_TIMEOUT
#     details = set()

#     timebound = 8

#     for i in range(len(PROBLEMS)):

#         s0 = PROBLEMS[i]

#         try:
#             setTO(timeout)

#             final = stu_solution.weighted_astar(s0, timebound)

#             setTO(0)

#             if final:
#                 score[0] += 1
#                 if final.gval <= benchmark_lengths[i] or benchmark_lengths[i] == -99:
#                     score[1] += 1

#         except TO_exc:
#             details.add("Got TIMEOUT while testing anytime weighted a star")
#         except:
#             details.add("A runtime error occurred while testing anytime weighted a star: %r" % traceback.format_exc())

#     details = "\n".join(details)

#     return score, details


