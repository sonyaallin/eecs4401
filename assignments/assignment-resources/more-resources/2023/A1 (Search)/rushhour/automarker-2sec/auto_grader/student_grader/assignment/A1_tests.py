from search import *
from rushhour import *
import itertools
import traceback
import gc
import sys
import pickle
#from test_problems_rushhour import PROBLEMS

import itertools
import traceback
import gc
import sys
import math
import csv

from utils.utilities import sortInnerMostLists, TO_exc, setTO, setMEM, resetMEM

from utils.test_tools import max_grade
from .test_cases_helpers import *
SOLUTION = 'solution.py'

PROBLEMS = []
with (open("/Users/JaglalLab/Desktop/HW/A1/automarker-2sec/auto_grader/student_grader/dependencies/rushhour_tests.pkl", "rb")) as openfile:
    while True:
        try:
            PROBLEMS.append(pickle.load(openfile))
        except EOFError:
            break

GOALS = []
with (open("/Users/JaglalLab/Desktop/HW/A1/automarker-2sec/auto_grader/student_grader/dependencies/rushhour_goals.pkl", "rb")) as openfile:
    while True:
        try:
            GOALS.append(pickle.load(openfile))
        except EOFError:
            break

GOALS = GOALS[0]

STU_SCORES = []
STU_SCORES_GBFS = []
STU_SCORES_ASTAR = []

OFFSET = 1

TIMEBOUND = 1
ASTAR_TIMEBOUND = 1
DEFAULT_TIMEOUT = 3

@max_grade(10)
def test_goal_fn(student_modules):

    stu_solution = student_modules[SOLUTION]
    response = ""
    score = 0

    example = False
    for i in range(0,len(GOALS)):
        s0 = GOALS[i]

        if (stu_solution.rushhour_goal_fn(s0)):
            score += 1
        else:
            example = s0
    
    response += "Goal states correctly detected {} of {} times.\n".format(score, len(GOALS))
    if (example):
        if example == None:
            response += "Function should handle boundary condition (where state is None).\n"
        else:
            response += "Example of incorrect calculation:\n" + example.get_print_state() + "\n"


    return round((score/len(GOALS))*10), response

@max_grade(10)
def test_min_dist(student_modules):

    stu_solution = student_modules[SOLUTION]
    correct_man_dist =  [1, 2, 1, 0, 2, 1, 1, 1, 1, 2, 1, 1, 2, 1, 2, 0, 1, 1, 0, 1, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 3, 6, 10, 13, 14, 17, 24, 27, 31, 29]

    scores = [0, 0]
    count = 0
    timeout = DEFAULT_TIMEOUT
    distances = []

    details = set()
    response = ""

    for i in range(len(PROBLEMS)):

        s0 = PROBLEMS[i]

        try:
            setTO(timeout)

            man_dist = stu_solution.heur_min_dist(s0)

            distances.append(man_dist)

            setTO(0)

            if float(man_dist) > float(correct_man_dist[i] - 0.01) and float(man_dist) < float(correct_man_dist[i] + 0.01):
                scores[0] += 1

        except TO_exc:
            response += "Got TIMEOUT during problem {} when testing min distance\n".format(i)
        except:
            response += "A runtime error occurred while testing min distance: %r\n" % traceback.format_exc()

        count += 1

    #details.add("distances: {}".format(distances))
    details = "\n".join(details)

    scores[1]=(scores[0]/count)*10
    response += "Correct distances computed {} of {} times.\n".format(scores[0], count)

    #score = math.ceil(scores[1])

    return round(scores[1]), response


@max_grade(8)
def test_fval_function(student_modules):
    stu_solution = student_modules[SOLUTION]
    test_state =  Rushhour("START", 6, None, None, None)
    correct_fvals = [7.0, 16, 26, 36, 46, 56, 66, 76, 86, 96]
    weights = [0.1,1,2,3,4, 5, 6,7,8,9]
    fuzz = 0.05
    response = ""

    score = 0
    timeout = DEFAULT_TIMEOUT
    details = set()
    values = []
    for i in range(len(weights)):

        try:
            setTO(timeout)

            test_node = sNode(test_state, 10, stu_solution.fval_function)

            fval = stu_solution.fval_function(test_node, weights[i])

            if (not fval):
                raise RuntimeError("no fval")

            if ((fval >= correct_fvals[i] - fuzz) and (fval <= correct_fvals[i] + fuzz)):
              score += 1

            setTO(0)

            values.append(fval)

        except TO_exc:
            response += "Got TIMEOUT during problem {} when testing fvalue function\n".format(i)
        except:
            response += "A runtime error occurred while testing the fvalue function: %r\n" % traceback.format_exc()

    #details.add("values: {}".format(values))
    details = "\n".join(details)

    return round((score/10)*8), response

@max_grade(6)
def test_fval_XUP_function(student_modules):
    stu_solution = student_modules[SOLUTION]
    test_state = Rushhour("START", 6, None, None, None)
    correct_fvals = [154.16198487095664, 16.0, 12.12403840463596, 11.25606581781675, 10.888194417315589, 10.686253353280438, 10.55890166873203, 10.471330124179719, 10.40744386111339, 10.358789223405562]
    weights = [0.1,1,2,3,4, 5, 6,7,8,9]
    fuzz = 0.05

    score = 0
    timeout = DEFAULT_TIMEOUT
    details = set()
    values = []
    response = ""
    for i in range(len(weights)):

        try:
            setTO(timeout)

            test_node = sNode(test_state, 10, stu_solution.fval_function)

            fval = stu_solution.fval_function_XUP(test_node, weights[i])

            if (not fval):
                raise RuntimeError("no fval")

            if ((fval >= correct_fvals[i] - fuzz) and (fval <= correct_fvals[i] + fuzz)):
              score += 1

            setTO(0)

            values.append(fval)

        except TO_exc:
            response += "Got TIMEOUT during problem {} when testing fvalue function\n".format(i)
        except:
            response += "A runtime error occurred while testing the fvalue function: %r\n" % traceback.format_exc()

    #details.add("values: {}".format(values))
    details = "\n".join(details)

    return round((score/10)*6), response


@max_grade(6)
def test_fval_XDP_function(student_modules):
    stu_solution = student_modules[SOLUTION]
    test_state = Rushhour("START", 6, None, None, None)
    correct_fvals = [21.622776601683796, 16.0, 14.567764362830022, 13.854886655416845, 13.405124837953327, 13.08711915483254, 12.846464004723153, 12.655894325996286, 12.5, 12.369311953264576]
    weights = [0.1,1,2,3,4, 5, 6,7,8,9]
    fuzz = 0.05
    response = ""

    score = 0
    timeout = DEFAULT_TIMEOUT
    details = set()
    values = []

    for i in range(len(weights)):

        try:
            setTO(timeout)

            test_node = sNode(test_state, 10, stu_solution.fval_function)

            fval = stu_solution.fval_function_XDP(test_node, weights[i])

            if (not fval):
                raise RuntimeError("no fval")

            if ((fval >= correct_fvals[i] - fuzz) and (fval <= correct_fvals[i] + fuzz)):
              score += 1

            setTO(0)

            values.append(fval)

        except TO_exc:
            response += "Got TIMEOUT during problem {} when testing fvalue function\n".format(i)
        except:
            response += "A runtime error occurred while testing the fvalue function: %r\n" % traceback.format_exc()

    #details.add("values: {}".format(values))
    details = "\n".join(details)

    return round((score/10)*6), response



@max_grade(15)
def test_weighted_astar(student_modules):
    stu_solution = student_modules[SOLUTION]
    solved, score1, score2, count = 0, 0, 0, 0
    weights = [10, 5, 2, 1]
    details = set()

    result = ""
    timeout = DEFAULT_TIMEOUT
    for j in range(5, 15):  # tiny problems only!
        m = PROBLEMS[j]  # Problems get harder as j gets bigger
        state_counts = []
        gvals = []
        solved = 0
        for weight in weights:
            try:
                setTO(timeout)            
                final, stats = stu_solution.weighted_astar(m, heur_fn=stu_solution.heur_min_dist, weight=weight,
                                              timebound=2)  # nice liberal timebound on this one :)
                if final:
                    solved += 1
                    state_counts.append(stats.states_expanded)
                    gvals.append(final.gval)
                else:
                    state_counts.append(-99)
                    gvals.append(-99)

            except TO_exc:
                result += "\nGot TIMEOUT during problem {} when testing fvalue function\n\n".format(i)
            except:
                result += "\nA runtime error occurred while testing the fvalue function: %r\n" % traceback.format_exc()

        # now test the state_counts and gvals
        if solved == 0:
            flag = False  # solved nothing!
        else:
            flag = True

        for i in range(0, len(state_counts) - 2):  # forward check
            if state_counts[i + 1] != -99 and gvals[i + 1] == -99:  # no solution, means no comparison to be made
                if state_counts[i] > state_counts[i + 1] or gvals[i] < gvals[i + 1]:  # state counts should be increasing and gvals decreasing
                    flag = False
        if flag: score1 += 1  # did we pass?
        else:
            result += "State counts decreased of gvals increased with lower weight for problem {}\n".format(score1)


        if solved == 0:
            flag = False  # solved nothing!
        else:
            flag = True

        for i in range(len(state_counts) - 1, 0, -1):  # backward check
            if state_counts[i - 1] != -99 and gvals[i - 1] == -99:  # no solution, means no comparison to be made
                if gvals[i - 1] == -99 and gvals[i] != -99:  # no solution with a lower weight, but a solution with a higher one ... is weird.
                    flag = False
        if flag: score2 += 1  # did we pass?
        count += 1

    summary_score = ((score1 + score2)/(2*count))*15
    result += "\n*************************************\n"
    #result += "Of the 40 runs over 10 problems, {} solutions were found with weighted a star in the time allotted.\n".format(
    #    solved)
    result += "Weighted a-star expanded more nodes as weights decreased {} of 10 times\n".format(score1)
    result += "Score is {} of 15.\n".format(summary_score)
    result += "*************************************\n"
    #details = "\n".join(details)
    return round(summary_score), result

@max_grade(15)
def test_heuristic(student_modules):
    stu_solution = student_modules[SOLUTION]

    scores = [0,0,0,0] #4 scores for alternate heuristic, 5 for gbfs, 5 for weighted a-star
    details = set()

    timebound = TIMEBOUND
    timeout = DEFAULT_TIMEOUT

    benchmark_lengths_bfs = [1, 15, 2, 1, 4, 1, 1, 12, 1, 2, 2, 1, 3, 2, 2, 0, 1, 2, 1, 2, 32, 7, -99, 8, 10, 7, 8, 7, 7, 13, 37, 15, 78, -99, 7, -99, -99, 9, 7, -99, 2, 2, 2, 2, 6, 5, 2, 2, 2, 5, 3, 7, 10, -99, -99, -99, -99, 28, -99, -99]
    total_bfs = sum(i != -99 for i in benchmark_lengths_bfs)-OFFSET
    manhattan_benchmark_lengths_bfs = [1, 8, 2, 2, -99, 1, 1, 11, 1, 2, 2, 1, 4, 3, 2, 0, 1, 3, 4, 3, 32, 10, -99, 10, -99, 7, 8, 7, 7, 13, 15, 9, -99, 8, 11, -99, -99, 10, 7, -99, 2, 2, 4, 2, 6, 7, 3, 2, 4, 8, 5, -99, 10, -99, -99, -99, -99, 28, -99, -99]
    total_manhattan_bfs = sum(i != -99 for i in manhattan_benchmark_lengths_bfs)-OFFSET
    #best_lengths = [1, 15, 2, 1, 4, 1, 1, 12, 1, 2, 2, 1, 3, 2, 2, 0, 1, 2, 1, 2, 32, 7, -99, 8, 10, 7, 8, 7, 7, 13, 34, 15, -99, 8, 7, -99, -99, 9, 7, 25, 2, 2, 2, 2, 6, 5, 2, 2, 2, 5, 3, 7, 10, -99, -99, -99, -99, 28, -99, -99]

    total_both = 1 
    for i in range(len(benchmark_lengths_bfs)):
        if (benchmark_lengths_bfs[i] != -99 or manhattan_benchmark_lengths_bfs[i] != -99):
            total_both += 1

    solved = []
    lengths = []
    response = ""
    for i in range(len(PROBLEMS)):

        s0 = PROBLEMS[i]

        try:
            se = SearchEngine('best_first', 'full')
            se.init_search(s0, rushhour_goal_fn_ta, heur_fn=stu_solution.heur_alternate)
            STU_SCORES.append(-99)

            setTO(timeout)
            final, stats = se.search(timebound)
            setTO(0)

            if final:
                lengths.append(final.gval)
                solved.append(i)
                STU_SCORES[i] = final.gval
                scores[0] += 1
                if final.gval <= benchmark_lengths_bfs[i] or benchmark_lengths_bfs[i] == -99:
                    scores[1] += 1
            else:
                lengths.append(-99)

        except TO_exc:
           response += "Got TIMEOUT during problem {} when testing alternate heuristic\n".format(i)
        except:
            response += "A runtime error occurred while testing alternate heuristic: %r\n" % traceback.format_exc()

    #are the scores better than manhattan solution and alt solution?
    score = scores[0]

    score = 0;
    if scores[0] > 1 and scores[0] < 20: #more than 20, 4 points
        score = 5 #base amount
    elif scores[0] >= 20 and scores[0] < total_manhattan_bfs: #more than 20, 5 points
        score = 5 + ((scores[0]-20)/(total_manhattan_bfs-20))*5; #up to 10 points
    elif (scores[0] >= total_manhattan_bfs and scores[0] < total_bfs): 
        score = 10 + ((scores[0]-total_manhattan_bfs)/(total_bfs-total_manhattan_bfs))*3; #up to 13
    elif (scores[0] >= total_bfs and scores[0] < total_both): #up to 15
        score = 13 + ((scores[0]-total_bfs)/(total_both-total_bfs))*2;
    if (scores[0] >= total_both):   
        score = 15       

    bfs_score = score;
    score = round(score)

    response += "Best First Search, with basic heuristic distance, solved {}/60 problems.\n".format(total_manhattan_bfs)
    response += "Best First Search, with an 'improved' heuristic, solved {}/60 problems.\n".format(total_bfs)
    response += "Best First Search, with YOUR heuristic, solved {}/60 problems.\n".format(scores[0])
    response += "You outperformed the 'improved' benchmark {} times.\n".format(scores[1])
    response += "Score for this portion of the assignment: {}/15.\n".format(bfs_score)    
    #response += "total both {} {} Lengths: {}.".format(total_both, len(PROBLEMS), lengths)

    #details = "\n".join(details)

    return score, response

@max_grade(15)
def test_iterative_gbfs(student_modules):
    scores = [0,0,0]
    details = set()

    stu_solution = student_modules[SOLUTION]

    astartimebound = ASTAR_TIMEBOUND
    astartimeout = DEFAULT_TIMEOUT
    timebound = TIMEBOUND

    benchmark_lengths_gbfs = [1, 7, 2, 1, 4, 1, 1, 7, 1, 2, 2, 1, 3, 2, 2, 0, 1, 2, 1, 2, 32, 7, -99, 8, 10, 7, 8, 7, 7, 11, 37, 15, 78, -99, 7, -99, -99, 9, 7, -99, 2, 2, 2, 2, 4, 3, 2, 2, 2, 3, 3, 7, 10, -99, -99, -99, -99, 28, -99, -99]
    total_gbfs = sum(i != -99 for i in benchmark_lengths_gbfs)-OFFSET
    manhattan_benchmark_lengths_gbfs = [1, 7, 2, 1, -99, 1, 1, 7, 1, 2, 2, 1, 3, 2, 2, 0, 1, 2, 1, 2, 32, 8, -99, 8, -99, 7, 8, 7, 7, 9, 15, 8, -99, 8, 11, -99, -99, 8, 7, -99, 2, 2, 2, 2, 4, 3, 2, 2, 2, 3, 3, -99, 10, -99, -99, -99, -99, 28, -99, -99]
    total_manhattan_gbfs = sum(i != -99 for i in manhattan_benchmark_lengths_gbfs)-OFFSET

    total_both = 1 
    for i in range(len(benchmark_lengths_gbfs)):
        if (benchmark_lengths_gbfs[i] != -99 or manhattan_benchmark_lengths_gbfs[i] != -99):
            total_both += 1

    solved = []
    solved_bfs = []
    lengths = []
    response = ""

    for i in range(len(PROBLEMS)):

        s0 = PROBLEMS[i]

        try:
            setTO(astartimeout)
            se = SearchEngine('best_first', 'full')
            se.init_search(s0, rushhour_goal_fn_ta, heur_fn=stu_solution.heur_alternate)
            STU_SCORES.append(-99)
            testresult, teststat = se.search(timebound-0.5) #make it hard
            setTO(0)
            if testresult != False:
                solved_bfs.append(i)
                STU_SCORES[i] = testresult.gval

            STU_SCORES_GBFS.append(-99)

            setTO(astartimeout)
            final, stats = stu_solution.iterative_gbfs(s0, heur_fn=stu_solution.heur_alternate, timebound=astartimebound)
            setTO(0)

            if final:
                lengths.append(final.gval)
                solved.append(i)
                scores[0] += 1
                STU_SCORES_GBFS[i] = final.gval
                if final.gval <= benchmark_lengths_gbfs[i] or benchmark_lengths_gbfs[i] == -99:
                    scores[1] += 1
                if STU_SCORES_GBFS[i] != -99 and STU_SCORES_GBFS[i] > STU_SCORES[i]:
                    scores[2] += 1 #lengths that exceed best first search (is a PROBLEM)
                    #response += "--> Problem {}: anytime solution {} and best first search {}.\n".format(i,STU_SCORES_GBFS[i],STU_SCORES[i])
            else:
                lengths.append(-99)
                if STU_SCORES[i] > 0:
                    scores[2] += 1 #lengths that exceed best first search (is a PROBLEM)
                    #response += "--> Problem {}: No anytime solution, but best first search solution of {}.\n".format(i,STU_SCORES[i])

        except TO_exc:
            response += "\nGot TIMEOUT during problem {} while testing anytime gbfs\n".format(i)
        except:
            response += "\nA runtime error occurred while testing anytime gbfs: %r\n" % traceback.format_exc()

    #score = scores[0]
    # #are the scores better than manhattan solution and alt solution?
    score = 0;
    if scores[0] > 1 and scores[0] < 20: #more than 20, 4 points
        score = 5 #base amount
    elif scores[0] >= 20 and scores[0] < total_manhattan_gbfs: #more than 20, 4 points
        score = 5 + ((scores[0]-20)/(total_manhattan_gbfs-20))*5;
    elif (scores[0] >= total_manhattan_gbfs and scores[0] < total_gbfs): 
        score = 10 + ((scores[0]-total_manhattan_gbfs)/(total_gbfs-total_manhattan_gbfs))*3;
    elif (scores[0] >= total_gbfs and scores[0] < total_both): #over upper benchmark is 10 points
        score = 13 + ((scores[0]-total_gbfs)/(total_both-total_gbfs))*2;
    if (scores[0] >= total_both):   
        score = 15       

    #gbfs_score = score;
    score = round(score)

    if (scores[2] > 0):  #something weird if anytime gbfs is outperformed by regular old bfs
       response += "\n--> WARNING: Some anytime solutions were outperformed by best first search.\n".format(scores[2])


    response += "Anytime gbfs, with with a basic heuristic distance, solved {}/60 problems.\n".format(total_manhattan_gbfs)
    response += "Anytime gbfs, with an 'improved' heuristic, solved {}/60 problems.\n".format(total_gbfs)
    response += "Anytime gbfs, with YOUR heuristic, solved {}/60 problems.\n".format(scores[0])
    response += "You outperformed the 'improved' benchmark {} times.\n".format(scores[1])
    response += "Score for this portion of the assignment: {}/15.\n".format(score)
    #response += "total both {} {} lengths {}.".format(total_both, len(PROBLEMS), lengths)

    #details = "\n".join(details)

    return score, response

@max_grade(15)
def test_iterative_weighted_astar(student_modules):
    scores = [0,0,0]
    details = set()

    stu_solution = student_modules[SOLUTION]

    astartimebound = ASTAR_TIMEBOUND
    astartimeout = DEFAULT_TIMEOUT
    response = ""
    benchmark_lengths_astar = [1, 7, 2, 1, 4, 1, 1, 7, 1, 2, 2, 1, 3, 2, 2, 0, 1, 2, 1, 2, -99, 7, -99, 8, 10, 7, 8, 7, 7, 9, -99, -99, -99, 8, 7, -99, -99, 8, 7, -99, 2, 2, 2, 2, 4, 3, 2, 2, 2, 3, 3, 7, 10, -99, -99, -99, -99, 28, -99, -99]
    manhattan_benchmark_lengths_astar = [1, 7, 2, 1, 4, 1, 1, 7, 1, 2, 2, 1, 3, 2, 2, 0, 1, 2, 1, 2, -99, 7, -99, 8, 10, 7, 8, 7, 7, 9, -99, -99, -99, 8, 7, -99, -99, 8, 7, -99, 2, 2, 2, 2, 4, 3, 2, 2, 2, 3, 3, 7, 10, -99, -99, -99, -99, 28, -99, -99]
    total_astar = sum(i != -99 for i in benchmark_lengths_astar)-OFFSET
    total_manhattan_astar = sum(i != -99 for i in manhattan_benchmark_lengths_astar)-OFFSET-OFFSET
    lengths = []
    STU_SCORES_ASTAR = []

    total_both = 1 
    for i in range(len(benchmark_lengths_astar)):
        if (benchmark_lengths_astar[i] != -99 or manhattan_benchmark_lengths_astar[i] != -99):
            total_both += 1

    for i in range(len(PROBLEMS)):

        s0 = PROBLEMS[i]

        try:
            weight = 10

            setTO(astartimeout)
            final, stats = stu_solution.iterative_astar(s0, heur_fn=stu_solution.heur_alternate, weight=weight, timebound=astartimebound)
            setTO(0)            

            if final:
                STU_SCORES_ASTAR.append(final.gval)
                lengths.append(final.gval)
                scores[0] += 1
                if final.gval < benchmark_lengths_astar[i] or benchmark_lengths_astar[i] == -99:
                    scores[1] += 1
            else:
                STU_SCORES_ASTAR.append(-99)
                lengths.append(-99)

        except TO_exc:
            response += "Got TIMEOUT during problem {} while testing weighted a-star\n".format(i)
        except:
            response += "A runtime error occurred while testing weighted a-star: %r\n" % traceback.format_exc()


    response += "Weighted astar, with a basic heuristic distance, solved {}/60.\n".format(total_manhattan_astar)
    response += "Weighted astar, with an 'improved' heuristic, solved {}/60 problems.\n".format(total_astar)
    response += "Weighted astar, with YOUR heuristic, solved {}/60 problems.\n".format(scores[0])
    response += "You outperformed the 'improved' benchmark in terms of length {} times.\n".format(scores[1])
    #response += "total both {} {} Lengths {}.".format(total_both, len(PROBLEMS), lengths)

    score = scores[0]

    score = 0;
    if scores[0] > 1 and scores[0] < 20: #more than 20, 4 points
        score = 5 #base amount
    elif scores[0] >= 20 and scores[0] < total_manhattan_astar: #more than 20, 4 points
        score = 5 + ((scores[0]-20)/(total_manhattan_astar-20))*5;
    elif (scores[0] >= total_manhattan_astar and scores[0] < total_astar): 
        score = 10 + ((scores[0]-total_manhattan_astar)/(total_astar-total_manhattan_astar))*3;
    elif (scores[0] >= total_astar and scores[0] < total_both): #over upper benchmark is 10 points
        score = 13 + ((scores[0]-total_astar)/(total_both-total_astar))*2;
    if (scores[0] >= total_both or (scores[0] >= total_astar and scores[1] > total_astar/2)):   
        score = 15       

    # score = 0;
    # if scores[0] > 0 and scores[0] < total_manhattan_astar: #5
    #     score = (scores[0]/total_manhattan_astar)*5;
    # if (scores[0] >= total_manhattan_astar): #5 points
    #     score = 5 + ((scores[0]-total_manhattan_astar)/(total_astar-total_manhattan_astar))*5;
    # if (scores[0] >= total_astar): #over upper benchmark is 10 points
    #     score = 10 + ((scores[0]-total_astar)/(total_both-total_astar))*5;
    # if (scores[0] >= total_both):   
    #     score = 15     
    score = round(score)
    response += "Score for this portion of the assignment: {}/15.\n".format(score)

    #details = "\n".join(details)

    return score, response
