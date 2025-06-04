from search import *
from sokoban import *
import itertools
import traceback
import gc
import sys
from test_problems_sokoban import PROBLEMS

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


STU_SCORES = []
STU_SCORES_GBFS = []
STU_SCORES_ASTAR = []

OFFSET = 0

TIMEBOUND = 10
ASTAR_TIMEBOUND = 10
DEFAULT_TIMEOUT = 20
SOLUTION_FILE = "./sol_comparison.csv"


@max_grade(10)
def test_manhattan(student_modules):
    stu_solution = student_modules[SOLUTION]
    correct_man_dist = [6, 2, 4, 4, 4, 4, 2, 3, 1, 3, 8, 7, 4, 12, 12, 12, 12, 8, 10, 8, 6, 9, 10, 7, 12, 9, 10, 7, 32, 44, 41, 29, 43, 35, 36, 44, 35, 45, 28, 32]

    scores = [0, 0]
    timeout = DEFAULT_TIMEOUT
    distances = []

    details = set()

    for i in range(len(PROBLEMS)):

        s0 = PROBLEMS[i]

        try:
            setTO(timeout)

            man_dist = stu_solution.heur_manhattan_distance(s0)

            distances.append(man_dist)

            setTO(0)

            if float(man_dist) > float(correct_man_dist[i] - 0.0000000001) and float(man_dist) < float(correct_man_dist[i] + 0.0000000001):
                scores[0] += 1

        except TO_exc:
            details.add("Got TIMEOUT during problem {} when testing manhattan distance".format(i))
        except:
            details.add("A runtime error occurred while testing manhattan distance: %r" % traceback.format_exc())

    #details.add("distances: {}".format(distances))
    details = "\n".join(details)

    scores[1]=(scores[0]/40)*10

    score = math.ceil(scores[1])

    return score, details

# @max_grade(5)
# def test_fval_xdp_function(student_modules):
#     stu_solution = student_modules[SOLUTION]
#     test_state = SokobanState("START", 6, None, None, None, None, None, None, None)
#     correct_fvals = [16.0, 14.56, 13.85, 13.40, 13.08, 12.84, 12.65, 12.5, 12.36, 12.25]
#     weights = [1,2,3,4,5, 6,7,8,9,10]
#     fuzz = 0.05
#
#     score = 0
#     timeout = DEFAULT_TIMEOUT
#     details = set()
#     values = []
#     for i in range(len(weights)):
#
#         try:
#             setTO(timeout)
#
#             test_node = sNode(test_state, 10, stu_solution.fval_function_XDP)
#
#             fval = stu_solution.fval_function_XDP(test_node, weights[i])
#             if ((fval >= correct_fvals[i] - fuzz) and (fval <= correct_fvals[i] + fuzz)):
#                 score += 0.5
#
#             setTO(0)
#
#             values.append(fval)
#
#         except TO_exc:
#             details.add("Got TIMEOUT during problem {} when testing fvalue function".format(i))
#         except:
#             details.add("A runtime error occurred while testing the fvalue function: %r" % traceback.format_exc())
#
#     #details.add("values: {}".format(values))
#     details = "\n".join(details)
#
#     return score, details


#@max_grade(5)
#def test_fval_xup_function(student_modules):
#    stu_solution = student_modules[SOLUTION]
#    test_state = SokobanState("START", 6, None, None, None, None, None, None, None)
#    correct_fvals = [16.0, 12.12, 11.25, 10.88, 10.68, 10.55, 10.47, 10.40, 10.35, 10.32]
#    weights = [1,2,3,4,5, 6,7,8,9,10]
#    fuzz = 0.05
#
#    score = 0
#    timeout = DEFAULT_TIMEOUT
#    details = set()
#    values = []
#    for i in range(len(weights)):
#
#        try:
#            setTO(timeout)
#
#            test_node = sNode(test_state, 10, stu_solution.fval_function_XUP)
#
#            fval = stu_solution.fval_function_XUP(test_node, weights[i])
#            if ((fval >= correct_fvals[i] - fuzz) and (fval <= correct_fvals[i] + fuzz)):
#                score += 0.5
#
#            setTO(0)
#
#            values.append(fval)
#
#        except TO_exc:
#            details.add("Got TIMEOUT during problem {} when testing fvalue function".format(i))
#        except:
#            details.add("A runtime error occurred while testing the fvalue function: %r" % traceback.format_exc())
#
#    #details.add("values: {}".format(values))
#    details = "\n".join(details)
#
#    return score, details

# @max_grade(5)
# def test_comparison(student_modules):
#     score = 0.0
#     details = set()
#     solution = []
#
#
#     with open(SOLUTION_FILE) as csv_file:
#         csv_reader = csv.reader(csv_file, delimiter=',')
#         for row_tmp in csv_reader:
#             row = row_tmp
#             for i in range(len(row)):
#                 row[i] = int(row[i].strip())
#             solution.append(row)
#
#     stu_compariosn = student_modules[SOLUTION]
#     addrs = str(stu_compariosn).split(' ')
#     if len(addrs) < 2:
#         details.add("File Not Found")
#         return score, details
#     addrs[1] = addrs[1].replace('\'', '')
#     addrs[1] = addrs[1].replace('solution.py', 'comparison.csv')
#     if not os.path.isfile(addrs[1]):
#         print(addrs[1], "not found")
#         details.add("File Not Found")
#         return score, details
#     with open(addrs[1]) as csv_file:
#         csv_reader = csv.reader(csv_file, delimiter=',')
#         student_answer = dict()
#         for row_tmp in csv_reader:
#             if len(row_tmp) == 0:
#                 continue
#             row = row_tmp
#             for i in range(len(row)):
#                 row[i] = row[i].strip()
#             if not row[0].isnumeric():
#                 continue
#             problem = int(row[0])
#             variant = int(row[1])
#
#             if "wuziyue" in addrs[1] or "wurober2" or "ganjun2" or "baileyga" in addrs[1]:
#                 variant += 1
#
#             if row[3].isnumeric():
#                 ex_path = int(row[3])
#             else:
#                 ex_path = -1
#             gen_path = int(row[4])
#             if len(row) > 5 and row[5].isnumeric():
#                 cost = int(row[5])
#             else:
#                 cost = -1
#             if variant == 1:
#                 w = -1
#             else:
#                 w = int(row[2])
#             student_answer[(problem, variant, w, ex_path, gen_path, cost)] = 1
#
#     solution = [[0, 1, -1, 239, 327, 4], [1, 1, -1, 11637, 25310, 21], [2, 1, -1, 38924, 65852, 10]]
#     for s in solution:
#         for key, _ in student_answer.items():
#             found = True
#             for i in range(len(key)):
#                 if key[i] != s[i]:
#                     found = False
#                     break
#             if found:
#                 score += 1
#                 break
#
#     score = round(score * 5.0 / len(solution), 1)
#     if "wuziyue" in addrs[1] or "wurober2" in addrs[1]:
#         score -= 2
#         score = max(0, score)
#         details.add("Variant number is 0 based")
#
#     return score, details

@max_grade(10)
def test_fval_function(student_modules):
    stu_solution = student_modules[SOLUTION]
    test_state = SokobanState("START", 6, None, None, None, None, None, None, None)
    correct_fvals = [6, 16, 26, 36, 46, 56, 66, 76, 86, 96]
    weights = [0,1,2,3,4, 5, 6,7,8,9]
    fuzz = 0.05

    score = 0
    timeout = DEFAULT_TIMEOUT
    details = set()
    values = []
    for i in range(len(weights)):

        try:
            setTO(timeout)

            test_node = sNode(test_state, 10, stu_solution.fval_function)

            fval = stu_solution.fval_function(test_node, weights[i])

            if ((fval >= correct_fvals[i] - fuzz) and (fval <= correct_fvals[i] + fuzz)):
              score += 1

            setTO(0)

            values.append(fval)

        except TO_exc:
            details.add("Got TIMEOUT during problem {} when testing fvalue function".format(i))
        except:
            details.add("A runtime error occurred while testing the fvalue function: %r" % traceback.format_exc())

    #details.add("values: {}".format(values))
    details = "\n".join(details)

    return score, details

@max_grade(25)
def test_heuristic(student_modules):
    stu_solution = student_modules[SOLUTION]

    scores = [0,0,0,0] #4 scores for alternate heuristic, 5 for gbfs, 5 for weighted a-star
    details = set()

    timebound = TIMEBOUND
    timeout = DEFAULT_TIMEOUT

    benchmark_lengths_bfs =[13, 5, 9, -99, 22, 18, 9, 14, 5, 9, 33, 23, 11, -99, 12, -99, 30, 32, 27, 43, 30, 32, 25, 24, 56, 22, 30, 34, 188, 172, -99, 113, 163, 100, 189, 158, -99, 135, 130, -99]
    total_bfs = sum(i != -99 for i in benchmark_lengths_bfs)-OFFSET
    manhattan_benchmark_lengths_bfs = [13, 5, 9, 29, 22, 18, 9, 14, 5, 9, 35, 23, 11, -99, 12, -99, 30, 22, 27, -99, 30, 97, -99, 26, -99, 40, 32, -99, -99, -99, -99, -99, -99, -99, -99, -99, -99, -99, -99, -99]
    total_manhattan_bfs = sum(i != -99 for i in manhattan_benchmark_lengths_bfs)-OFFSET
    solved = []
    lengths = []

    for i in range(len(PROBLEMS)):

        s0 = PROBLEMS[i]

        try:
            se = SearchEngine('best_first', 'full')
            se.init_search(s0, sokoban_goal_state, heur_fn=stu_solution.heur_alternate)
            STU_SCORES.append(-99)

            setTO(timeout)
            final, stat = se.search(timebound)
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
           details.add("Got TIMEOUT during problem {} when testing alternate heuristic".format(i))
        except:
            details.add("A runtime error occurred while testing alternate heuristic: %r" % traceback.format_exc())

    #are the scores better than manhattan solution and alt solution?
    score = 0
    #no points for no solutions
    if scores[0] > 0 and scores[0] < 5: #more than 1 -- you get 5 points
        score = 5
    if (scores[0] < total_manhattan_bfs and scores[0] >= 5): #between 5 and lower benchmark -- you get 5 to 10 points
        student_margin = scores[0]-5;
        if (student_margin > 0): score = 5 + math.ceil((student_margin/total_manhattan_bfs)*5);
    if (scores[0] >= total_manhattan_bfs): #between lower benchmark and upper bencchmark -- up to 20 points
        score = 10
        margin = total_bfs-total_manhattan_bfs;
        student_margin = scores[0]-total_manhattan_bfs;
        if (student_margin > 0): score = score + math.ceil((student_margin/margin)*10);
    scores[3] = 0
######EVI CHANGED#################################################
    #
    # if (scores[0] >= total_bfs): #last five points for over upper benchmark
    #     score = 15
    #     margin = 40-total_bfs;
    #     student_margin = scores[0]-total_bfs;
    #     if (student_margin > 0): score = score + math.ceil((student_margin/margin)*5);

    if (scores[0] -total_bfs>=1 and scores[0] -total_bfs<3 ): #last five points for over upper benchmark
        score = 20
        margin = 40-total_bfs;
        student_margin = scores[0]-total_bfs;
        if (student_margin > 0): score = score + 3;

    if (scores[0] -total_bfs>=3 ): #last five points for over upper benchmark
        score = 20
        margin = 40-total_bfs;
        student_margin = scores[0]-total_bfs;
        if (student_margin > 0): score = score + 5;
######END EVI CHANGED#################################################

    bfs_score = score;

    details.add("Best First Search, with the student heuristic, solved {}/40 problems.".format(scores[0]))
    details.add("Best First Search, with manhattan distance, solved {}/40 problems.".format(total_manhattan_bfs))
    details.add("Best First Search, with an alternate heuristic, solved {}/40 problems.".format(total_bfs))
    details.add("The student outperformed the 'better' benchmark {} times.".format(scores[1]))
    details.add("Score for alternate heuristic portion: {}/20.".format(bfs_score))
    #details.add("Lengths: {}.".format(lengths))

    details = "\n".join(details)

    return score, details

@max_grade(25)
def test_anytime_gbfs(student_modules):
    scores = [0,0,0]
    details = set()

    stu_solution = student_modules[SOLUTION]

    astartimebound = ASTAR_TIMEBOUND
    astartimeout = DEFAULT_TIMEOUT
    timebound = TIMEBOUND

    benchmark_lengths_gbfs = [13, 5, 9, -99, 16, 16, 8, 13, 5, 9, 29, 23, 11, -99, 12, -99, 25, 28, 22, 29, 24, 26, 22, 20, 51, 19, 27, 29, 188, 172, -99, 113, 163, 100, 189, 156, -99, 135, 124, -99]
    total_gbfs = sum(i != -99 for i in benchmark_lengths_gbfs)-OFFSET
    manhattan_benchmark_lengths_gbfs = [13, 5, 9, 22, 16, 16, 8, 13, 5, 9, 29, 23, 11, -99, 12, -99, 26, 20, 22, -99, 25, 92, -99, 24, -99, 35, 27, -99, -99, -99, -99, -99, -99, -99, -99, -99, -99, -99, -99, -99]
    total_manhattan_gbfs = sum(i != -99 for i in manhattan_benchmark_lengths_gbfs)-OFFSET
    solved = []
    solved_bfs = []
    lengths = []

    for i in range(len(PROBLEMS)):

        s0 = PROBLEMS[i]

        try:
            setTO(astartimeout)
            se = SearchEngine('best_first', 'full')
            se.init_search(s0, sokoban_goal_state, heur_fn=stu_solution.heur_alternate)
            STU_SCORES.append(-99)
            testresult, teststat = se.search(timebound)
            setTO(0)
            if testresult != False:
                solved_bfs.append(i)
                STU_SCORES[i] = testresult.gval

            STU_SCORES_GBFS.append(-99)

            setTO(astartimeout)
            final = stu_solution.anytime_gbfs(s0, heur_fn=stu_solution.heur_alternate, timebound=astartimebound)
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
                    #details.add("--> Problem {}: anytime solution {} and best first search {}.".format(i,STU_SCORES_GBFS[i],STU_SCORES[i]))
            else:
                lengths.append(-99)
                if STU_SCORES[i] > 0:
                    scores[2] += 1 #lengths that exceed best first search (is a PROBLEM)
                    #details.add("--> Problem {}: No anytime solution, but best first search solution of {}.".format(i,STU_SCORES[i]))

        except TO_exc:
            details.add("Got TIMEOUT during problem {} while testing anytime gbfs".format(i))
        except:
            details.add("A runtime error occurred while testing anytime gbfs: %r" % traceback.format_exc())

    #are the scores better than manhattan solution and alt solution?
    score = 0;
    if isinstance(scores,int):
        details.add("--> Problem running student solution.")
    #no points for no solutions
    elif scores[0] > 0 and scores[0] < 5: #more than 1 -- 5 points
        score = 5
    elif (scores[0] < total_manhattan_gbfs and scores[0] >= 5): #between 5 and lower benchmark -- 5 to 10 points
        student_margin = scores[0]-5;
        if (student_margin > 0): score = 5 + math.ceil((student_margin/total_manhattan_gbfs)*5);
    elif (scores[0] >= total_manhattan_gbfs and scores[0] < total_gbfs): #up to 20 points between benchmarks
        score = 10
        margin = total_gbfs-total_manhattan_gbfs;
        student_margin = scores[0]-total_manhattan_gbfs;
        if (student_margin > 0): score = score + math.ceil((student_margin/margin)*10);
    elif (scores[0] >= total_gbfs): #last 5 for beating the upper benchmark
        score = 20
        margin = 40-total_gbfs;
        student_margin = scores[0]-total_gbfs;
        ###Evi Changed#######
            #    if (student_margin > 0):
            #        score = score + math.ceil((student_margin/margin)*5);
            #        details.add("--> Margin over benchmark: {} problems.".format(scores[0]-total_gbfs))

        if (student_margin >= 1 and student_margin < 3):
            score = score + 3;
            details.add("--> Margin over benchmark: {} problems.".format(scores[0]-total_gbfs))
        elif (student_margin >= 3 ):
            score = score + 5;
            details.add("--> Margin over benchmark: {} problems.".format(scores[0]-total_gbfs))
###########   END Evi Changed###########


    gbfs_score = score;

    if (scores[2] > 0):  #something weird if anytime gbfs is outperformed by regular old bfs
       details.add("--> WARNING: Anytime solutions were outperformed by best first search.".format(scores[2]))

    details.add("Anytime gbfs, with the student heuristic, solved {}/40 problems.".format(scores[0]))
    details.add("Anytime gbfs, with manhattan distance, solved {}/40 problems.".format(total_manhattan_gbfs))
    details.add("Anytime gbfs, with an alternate heuristic, solved {}/40 problems.".format(total_gbfs))
    details.add("The student outperformed the 'better' benchmark {} times.".format(scores[1]))
    details.add("Score for anytime_gbfs tests: {}/25.".format(score))
    #details.add("Lengths: {}.".format(lengths))
    #details.add("Solved By Best First Search: {}.".format(solved_bfs))

    details = "\n".join(details)

    return score, details

@max_grade(25)
def test_anytime_weighted_astar(student_modules):
    scores = [0,0,0]
    details = set()

    stu_solution = student_modules[SOLUTION]

    astartimebound = ASTAR_TIMEBOUND
    astartimeout = DEFAULT_TIMEOUT #safe margin

    benchmark_lengths_astar = [13, 5, 9, 17, 14, 16, 8, 13, 5, 9, 29, 23, 11, -99, 12, -99, 22, 20, 20, -99, 18, 18, -99, 18, 37, 18, 21, 18, -99, -99, -99, -99, -99, -99, -99, -99, -99, -99, -99, -99]
    total_astar = sum(i != -99 for i in benchmark_lengths_astar)-OFFSET
    manhattan_benchmark_lengths_astar = [13, 5, 9, 17, 14, 16, 8, 13, 5, 9, -99, 23, -99, -99, 12, -99, 22, 18, 20, -99, 18, 18, 22, 18, -99, 18, 22, 18, -99, -99, -99, -99, -99, -99, -99, -99, -99, -99, -99, -99]
    total_manhattan_astar = sum(i != -99 for i in manhattan_benchmark_lengths_astar)
    lengths = []

    for i in range(len(PROBLEMS)):

        s0 = PROBLEMS[i]

        try:
            weight = 10

            setTO(astartimeout)
            final = stu_solution.anytime_weighted_astar(s0, heur_fn=stu_solution.heur_alternate, weight=weight, timebound=astartimebound)
            setTO(0)

            STU_SCORES_ASTAR.append(-99)

            if final:
                lengths.append(final.gval)
                scores[0] += 1
                STU_SCORES_ASTAR[i] = final.gval
                if final.gval <= benchmark_lengths_astar[i] or benchmark_lengths_astar[i] == -99:
                    scores[1] += 1
            else:
                lengths.append(-99)

        except TO_exc:
            details.add("Got TIMEOUT during problem {} while testing weighted a-star".format(i))
        except:
            details.add("A runtime error occurred while testing weighted a-star: %r" % traceback.format_exc())

    details.add("Weighted astar, with the student heuristic, solved {}/40 problems.".format(scores[0]))
    details.add("Weighted astar, with manhattan distance, solved {}/40.".format(total_manhattan_astar))
    details.add("Weighted astar, with an alternate heuristic, solved {}/40 problems.".format(total_astar))
    details.add("The student outperformed the 'better' benchmark {} times.".format(scores[1]))

    #details.add("Lengths {}.".format(lengths))

    score = 0
    if isinstance(scores,int):
        details.add("--> Problem running student solution.")
    #no points for no solutions
    elif scores[0] > 0 and scores[0] < 5: #more than 1 -- 5 points
        score = 5
    elif (scores[0] < total_manhattan_astar and scores[0] >= 5): #between 5 and lower benchmark -- 5 to 10 points
        student_margin = scores[0]-5;
        if (student_margin > 0): score = 5 + math.ceil((student_margin/total_manhattan_astar)*5);
    elif (scores[0] >= total_manhattan_astar and scores[0] < total_astar): #between 10 and 20 here
        score = 10
        margin = total_astar-total_manhattan_astar;
        student_margin = scores[0]-total_manhattan_astar;
        if (student_margin > 0): score = score + math.ceil((student_margin/margin)*10);
    elif (scores[0] >= total_astar and scores[1] >= total_astar): #over benchmark and short, automatic perfect mark
        if scores[1] == total_astar: #1 point for performing as well
            margin = 1
        else: #at least 1 point for performing better
            margin = scores[1] - total_astar;
            margin = math.ceil((margin/(40-total_astar))*5) #last two conditions are pro-rated marks
            if margin < 1: margin = 1
        score = 20 + margin
        details.add("--> Matched or beat length of benchmark at least {} times.".format(scores[1]))
    elif (scores[0] >= total_astar and scores[1] < total_astar):
        score = 20
        margin = 40-total_astar;
        student_margin = scores[0]-total_astar;
        if (student_margin > 0):
            score = score + math.ceil((student_margin/margin)*5);
            details.add("--> Margin over benchmark: {} problems.".format(scores[0]-total_astar))

    details.add("Score for this portion of the assignment: {}/25.".format(score))

    details = "\n".join(details)

    return score, details
