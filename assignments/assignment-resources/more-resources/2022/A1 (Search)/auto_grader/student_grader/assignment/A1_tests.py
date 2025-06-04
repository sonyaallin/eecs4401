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

TIMEBOUND = 2
ASTAR_TIMEBOUND = 2
DEFAULT_TIMEOUT = 10

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

@max_grade(10)
def test_weighted_astar(student_modules):
    stu_solution = student_modules[SOLUTION]
    solved, score1, score2 = 0, 0, 0
    weights = [10, 5, 2, 1]
    details = set()

    timeout = DEFAULT_TIMEOUT
    for j in range(0, 5):  # tiny problems only!
        m = PROBLEMS[j]  # Problems get harder as j gets bigger
        state_counts = []
        gvals = []
        solved = 0
        for weight in weights:
            try:
                setTO(timeout)            
                final, stats = stu_solution.weighted_astar(m, heur_fn=stu_solution.heur_manhattan_distance, weight=weight,
                                              timebound=5)  # nice liberal timebound on this one :)
                if final:
                    solved += 1
                    state_counts.append(stats.states_expanded)
                    gvals.append(final.gval)
                else:
                    state_counts.append(-99)
                    gvals.append(-99)

            except TO_exc:
                details.add("Got TIMEOUT during problem {} when testing fvalue function".format(i))
            except:
                details.add("A runtime error occurred while testing the fvalue function: %r" % traceback.format_exc())

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
            details.add("State counts decreased of gvals increased with lower weight for problem {}".format(score1))


        if solved == 0:
            flag = False  # solved nothing!
        else:
            flag = True

        for i in range(len(state_counts) - 1, 0, -1):  # backward check
            if state_counts[i - 1] != -99 and gvals[i - 1] == -99:  # no solution, means no comparison to be made
                if gvals[i - 1] == -99 and gvals[i] != -99:  # no solution with a lower weight, but a solution with a higher one ... is weird.
                    flag = False
        if flag: score2 += 1  # did we pass?

    summary_score = (score1 + score2)
    details.add("\n*************************************")
    details.add("Of the 20 runs over 5 problems, {} solutions were found with weighted a star in the time allotted.".format(
        solved))
    details.add("Weighted a-star expanded more nodes as weights decreased {} of 5 times".format(score1))
    details.add("Score is {} of 10.".format(summary_score))
    details.add("*************************************\n")
    details = "\n".join(details)
    return summary_score, details

@max_grade(5)
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

    return score/2, details

@max_grade(25)
def test_heuristic(student_modules):
    stu_solution = student_modules[SOLUTION]

    scores = [0,0,0,0] #4 scores for alternate heuristic, 5 for gbfs, 5 for weighted a-star
    details = set()

    timebound = TIMEBOUND
    timeout = DEFAULT_TIMEOUT

    benchmark_lengths_bfs = [13, 5, 9, -99, 22, 18, 9, 14, 5, 9, 33, 23, 11, -99, 12, -99, 30, 32, 27, 43, 30, 32, 25, 24, 56, 22, 30, 34, 188, 172, -99, 93, 163, 100, 211, 158, -99, 135, 130, -99]
    total_bfs = sum(i != -99 for i in benchmark_lengths_bfs)-OFFSET
    manhattan_benchmark_lengths_bfs = [13, 5, 9, 29, 22, 18, 9, 14, 5, 9, 35, 23, 11, -99, 12, -99, 30, 22, 27, -99, 30, 97, -99, 26, -99, 99, -99, -99, -99, -99, -99, -99, -99, -99, -99, -99, -99, -99, -99, -99]
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
def test_iterative_gbfs(student_modules):
    scores = [0,0,0]
    details = set()

    stu_solution = student_modules[SOLUTION]

    astartimebound = ASTAR_TIMEBOUND
    astartimeout = DEFAULT_TIMEOUT
    timebound = TIMEBOUND

    benchmark_lengths_gbfs = [13, 5, 9, -99, 18, 16, 8, 13, 5, 9, 29, 23, 11, -99, 12, -99, 27, 31, 23, 28, 28, 26, 25, 24, 50, 20, 28, 31, 188, 172, -99, 93, 163, 100, 211, 158, -99, 135, 124, -99]
    total_gbfs = sum(i != -99 for i in benchmark_lengths_gbfs)-OFFSET
    manhattan_benchmark_lengths_gbfs = [13, 5, 9, 19, 16, 16, 8, 13, 5, 9, 29, 23, 11, -99, 12, -99, 26, 20, 23, -99, 26, 92, -99, 25, -99, 39, 30, -99, -99, -99, -99, -99, -99, -99, -99, -99, -99, -99, -99, -99]
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
    #details.add("lengths {}.".format(lengths))

    details = "\n".join(details)

    return score, details

@max_grade(25)
def test_iterative_weighted_astar(student_modules):
    scores = [0,0,0]
    details = set()

    stu_solution = student_modules[SOLUTION]

    astartimebound = ASTAR_TIMEBOUND
    astartimeout = DEFAULT_TIMEOUT

    benchmark_lengths_astar = [13, 5, 9, -99, 14, 16, 8, 13, 5, 9, 29, 23, 11, -99, 12, -99, 22, 20, 20, -99, 18, 18, 21, 19, 37, 18, 22, 18, -99, -99, -99, -99, -99, -99, -99, -99, -99, -99, -99, -99]
    total_astar = sum(i != -99 for i in benchmark_lengths_astar)-OFFSET
    manhattan_benchmark_lengths_astar = [13, 5, 9, 17, 14, 16, 8, 13, 5, 9, 29, 23, 11, -99, 12, -99, 22, 20, 20, -99, 18, 18, 24, 22, -99, 18, 22, 18, -99, -99, -99, -99, -99, -99, -99, -99, -99, -99, -99, -99]
    total_manhattan_astar = sum(i != -99 for i in manhattan_benchmark_lengths_astar)
    lengths = []
    STU_SCORES_ASTAR = []

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
                if final.gval <= benchmark_lengths_astar[i] or benchmark_lengths_astar[i] == -99:
                    scores[1] += 1
            else:
                STU_SCORES_ASTAR.append(-99)
                lengths.append(-99)

        except TO_exc:
            details.add("Got TIMEOUT during problem {} while testing weighted a-star".format(i))
        except:
            details.add("A runtime error occurred while testing weighted a-star: %r" % traceback.format_exc())

    details.add("Weighted astar, with the student heuristic, solved {}/40 problems.".format(scores[0]))
    details.add("Weighted astar, with manhattan distance, solved {}/40.".format(total_manhattan_astar))
    details.add("Weighted astar, with an alternate heuristic, solved {}/40 problems.".format(total_astar))
    details.add("The student outperformed the 'better' benchmark {} times.".format(scores[1]))
    #details.add("STU_SCORES_ASTAR {}.".format(STU_SCORES_ASTAR))

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
