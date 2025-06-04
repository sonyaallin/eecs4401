#!/usr/bin/env python
import os  # for time functions
import traceback
import pickle

from utils.utilities import sortInnerMostLists, TO_exc, setTO, setMEM, resetMEM

from utils.test_tools import max_grade
from .test_cases_helpers import *

# Load the test problems
boards = []
with (open("../../submissions/solution/boards.pickle", "rb")) as openfile:
    while True:
        try:
            boards.append(pickle.load(openfile))
        except EOFError:
            break

boards = boards[0:1000:25] #pick 40 boards

mc_boards, trees, sols = [], [], []
with (open("../../submissions/solution/ucb.pickle", "rb")) as openfile:
    while True:
        try:
            mc_boards.append(pickle.load(openfile))
            trees.append(pickle.load(openfile))
            sols.append(pickle.load(openfile))
        except EOFError:
            break

# # import student's functions
# #from solution import *
# boards = [((0, 0, 0, 0), (0, 2, 1, 0), (0, 1, 1, 1), (0, 0, 0, 0)),
# ((0, 1, 0, 0), (0, 1, 1, 0), (0, 1, 2, 1), (0, 0, 0, 2)),
# ((0, 0, 0, 0), (0, 2, 1, 0), (0, 1, 1, 1), (0, 1, 1, 0)),
# ((0, 1, 0, 0), (0, 2, 2, 0), (0, 1, 2, 1), (0, 0, 2, 2)),
# ((1, 0, 0, 2), (1, 1, 2, 0), (1, 1, 1, 1), (1, 2, 2, 2)),
# ((0, 1, 0, 0), (0, 1, 1, 0), (2, 2, 2, 1), (0, 0, 0, 2))]

# boards = [((0, 0, 0, 0, 0, 0), (0, 0, 2, 2, 0, 0), (0, 1, 1, 2, 2, 0), (2, 2, 1, 2, 0, 0), (0, 1, 0, 1, 2, 0), (0, 0, 0, 0, 0, 0)),
# ((0, 0, 0, 0, 0, 0), (0, 0, 1, 2, 0, 0), (0, 1, 1, 1, 1, 0), (2, 2, 1, 2, 0, 0), (0, 1, 0, 1, 2, 0), (0, 0, 0, 0, 0, 0)),
# ((0, 0, 0, 0, 1, 0), (0, 0, 1, 1, 0, 0), (0, 1, 1, 1, 1, 0), (2, 2, 1, 2, 0, 0), (0, 2, 0, 1, 2, 0), (0, 0, 2, 2, 1, 0)),
# ((0, 0, 0, 0, 0, 0), (0, 0, 0, 2, 0, 0), (0, 1, 2, 2, 2, 0), (0, 2, 2, 2, 0, 0), (0, 1, 0, 0, 0, 0), (0, 0, 0, 0, 0, 0)),
# ((0, 0, 0, 0, 0, 0), (0, 0, 0, 2, 0, 0), (0, 1, 2, 1, 1, 0), (0, 2, 2, 2, 0, 0), (0, 1, 0, 0, 0, 0), (0, 0, 0, 0, 0, 0))]

# boards = boards = [((0, 0, 0, 0, 0, 0, 0, 0), (0, 0, 2, 2, 0, 0, 0, 0), (0, 1, 1, 2, 2, 0, 0, 0), (2, 2, 1, 2, 0, 0, 0, 0), (0, 1, 0, 1, 2, 0, 0, 0), (0, 0, 0, 0, 0, 0, 0, 0)),
# ((0, 0, 0, 0, 0, 0, 0, 0), (0, 0, 1, 2, 0, 0, 0, 0), (0, 1, 1, 1, 1, 0, 0, 0), (2, 2, 1, 2, 0, 0, 0, 0), (0, 1, 0, 1, 2, 0, 0, 0), (0, 0, 0, 0, 0, 0, 0, 0)),
# ((0, 0, 0, 0, 1, 0, 0, 0), (0, 0, 1, 1, 0, 0, 0, 0), (0, 1, 1, 1, 1, 0, 0, 0), (2, 2, 1, 2, 0, 0, 0, 0), (0, 2, 0, 1, 2, 0, 0, 0), (0, 0, 2, 2, 1, 0, 0, 0)),
# ((0, 0, 0, 0, 0, 0, 0, 0), (0, 0, 0, 2, 0, 0, 0, 0), (0, 1, 2, 2, 2, 0, 0, 0), (0, 2, 2, 2, 0, 0, 0, 0), (0, 1, 0, 0, 0, 0, 0, 0), (0, 0, 0, 0, 0, 0, 0, 0)),
# ((0, 0, 0, 0, 0, 0, 0, 0), (0, 0, 0, 2, 0, 0, 0, 0), (0, 1, 2, 1, 1, 0, 0, 0), (0, 2, 2, 2, 0, 0, 0, 0), (0, 1, 0, 0, 0, 0, 0, 0), (0, 0, 0, 0, 0, 0, 0, 0))]

SOLUTION = 'agent.py'
timeout = 20

#-- Minimax worth 30 points

#test_compute_utility = 5
#test_minimax_min_node_1 = 5
#test_minimax_max_node_1 = 5
#test_minimax_max_node_2 = 5
#test_select_move_minimax = 10

#-- Alpha-beta would be worth 30 points
#test_alphabeta_min_node_1 = 5
#test_alphabeta_max_node_1 = 5
#test_alphabeta_max_node_2 = 5
#test_select_move_equal = 5
#test_select_move_alphabeta = 10

#- State caching would be worth 10 points
#test_caching_big = 4
#test_caching_xl = 6

#- Node ordering would be worth 10 points
#test_ordering = 10

#-- The depth limit would be worth 10 points
#test_depth = 10


# @max_grade(10)
# def test_compute_utility(student_modules):

#     stu_solution = student_modules[SOLUTION] 
#     details = set()

#     ##############################################################
#     print('Testing Utility')
#     correctvalues = [0, -2, -2, -2, -2, -2, -2, -1, -1, -1, 0, 0, 4, -1, -2, -2, -1, -2, -3, -7, -2, -8, -2, -2, -1, -1, -2, -2, -2, -1, -6, -7, -1, -1, 4, -6, -1, -1, -2, -2]
#     #correctvalues = [0,-2,-2,-2,-2,-2,-2,-1,-1,-1,0,0,4,-1,-2,-2,-1,-2,-3,-7,-2,-8,-2
#     #[(-2, 2), (-1, 1), (-1, 1), (-2, 2), (-2, 2), (-2, 2), (-1, 1), (-6, 6), (-7, 7), (-1, 1), (-1, 1), (4, -4), (-6, 6), (-1, 1), (-1, 1), (-2, 2), (-2, 2)]
#     answers = []
#     score = 0
#     for i in range(0,len(boards)):
#       board = boards[i]
#       try:
#         setTO(timeout)        
#         value1 = stu_solution.compute_utility(board, 1)
#         value2 = stu_solution.compute_utility(board, 0)
#         answers.append(value1)
#         setTO(0)
#         if (value1 == correctvalues[i] and value2 == correctvalues[i]*-1):
#           score+=1  
#       except TO_exc:
#           details.add("Got TIMEOUT during problem {} when testing compute_utility".format(i))
#       except:
#           details.add("A runtime error occurred while testing compute_utility: %r" % traceback.format_exc())

#     details.add("You computed correct utilities for {} of {} boards".format(score, len(correctvalues)))
#     details = "\n".join(details)

#     score = score/4 #adjust, is only worth 5 points
#     #print(answers)

#     return score, details


@max_grade(20)
def test_select_move_alphabeta(student_modules):

    stu_solution = student_modules[SOLUTION]  
    details = set()
    
    correctmoves_1a = [5, 1, 1, 1, 2, 2, 1, 1, 1, 7, 1, 6, 6, 3, 1, 2, 2, 0, 3, 3, 2, 2, 2, 6, 6, 1, 6, 4, 6, 1, 3, 3, 3, 7, 0, 3, 3, 2, 2]
    correctmoves_2a = [2, 5, 5, 5, 0, 4, 5, 5, 0, 6, 0, 0, 0, 1, 5, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 1, 5, 7, 0, 0, 0, 0, 0, 4, 3, 0, 0, 1]
    
    correctmoves_1 = [5, 1, 1, 1, 2, 2, 1, 1, 1, 7, 1, 6, 6, 3, 1, 2, 2, 0, 3, 3, 2, 2, 2, 6, 6, 1, 0, 4, 3, 1, 6, 3, 3, 7, 0]
    correctmoves_2 = [2, 5, 5, 5, 2, 4, 5, 5, 0, 6, 0, 0, 0, 1, 5, 1, 1, 1, 1, 2, 0, 0, 0, 0, 0, 0, 1, 5, 7, 0, 0, 0, 3, 0, 4]  
  
    answers1 = []
    answers2 = []
    correct = 0
    alternate_depth = 0
    for i in range(0,35):
      board = boards[i]
      try:
        setTO(timeout)
        value1 = stu_solution.select_move_alphabeta(board, 1, 5)
        if isinstance(value1, tuple): 
          value1 = value1[0]
        value2 = stu_solution.select_move_alphabeta(board, 0, 5)
        if isinstance(value2, tuple): 
          value2 = value2[0]        
        setTO(0)
        if (value1 == correctmoves_1[i]):
          correct+=1  
        if (value2 == correctmoves_2[i]):
          correct+=1    
        answers1.append(value1)     
        answers2.append(value2)  
      except TO_exc:
          details.add("Got TIMEOUT during problem {} when testing test_select_move_alphabeta".format(i))
      except:
          details.add("A runtime error occurred while testing test_select_move_alphabeta: %r" % traceback.format_exc())

    for i in range(0,35):
      board = boards[i]
      try:
        setTO(timeout)
        value1 = stu_solution.select_move_alphabeta(board, 1, 6)
        if isinstance(value1, tuple): 
          value1 = value1[0]
        value2 = stu_solution.select_move_alphabeta(board, 0, 6)
        if isinstance(value2, tuple): 
          value2 = value2[0]        
        setTO(0)
        if (value1 == correctmoves_1a[i]):
          alternate_depth+=1  
        if (value2 == correctmoves_2a[i]):
          alternate_depth+=1     
      except TO_exc:
          details.add("Got TIMEOUT during problem {} when testing test_select_move_alphabeta".format(i))
      except:
          details.add("A runtime error occurred while testing test_select_move_alphabeta: %r" % traceback.format_exc())

    details.add("Calculated correct alphabeta moves {}/70 times at depth 6.".format(correct))
    
    #print(answers1)
    #print(answers2)
    correct = correct/70*20
    if (alternate_depth < 10):
      correct = correct-10
      details.add("Correct moves are NOT selected at all depths!")

    details = "\n".join(details) 

    return correct, details

# @max_grade(10)
# def test_ucb_fun(student_modules):

#     stu_solution = student_modules[SOLUTION] 
#     details = set() 

#     correct, total = 0, 0
#     for i in range(0, len(sols), 14):
#         test_sol = stu_solution.ucb_select(mc_boards[i], trees[i])
#         if test_sol == sols[i]:
#             correct += 1
#         total += 1

#     details.add("You computed correct UCB values for {} of {} tests".format(correct, total))
#     details = "\n".join(details) 
#     return correct, details

@max_grade(10)
def test_depth(student_modules):

    print('Testing Depth')
    stu_solution = student_modules[SOLUTION] 
    details = set()

    # correctmoves_11 = [(0,0),(0,0),(0,0),(0,0),(0,0),(0,0)]
    # correctmoves_21 = [(1,3),(1,3),(1,3),(1,3),(1,3),(3,3)]
    # correctmoves_12 = [(2,3),(2,3),(2,3),(2,3),(2,3),(2,3)]
    # correctmoves_22 = [(0,0),(0,0),(0,0),(0,0),(3,1),(0,0)]

    correctmoves_11 = [0, 0, 0, 2, 2]
    correctmoves_21 = [4, 5, 5, 5, 5]
    correctmoves_12 = [0, 0, 0, 0, 0]
    correctmoves_22 = [2, 2, 0, 2, 2]

    answers = []
    score = 0
    for j in range(0,2):
      if j == 0:
        correctmoves_1 = correctmoves_11
        correctmoves_2 = correctmoves_21
      else:
        correctmoves_1 = correctmoves_12
        correctmoves_2 = correctmoves_22

      board = boards[j*20]
      try:
        for i in range(2,7):
          setTO(timeout)
          value1 = stu_solution.select_move_minimax(board, 0, i)
          value2 = stu_solution.select_move_minimax(board, 1, i)
          answers.append((value1, value2))          
          setTO(0)

          if (value1 == correctmoves_1[i-2] and value2 == correctmoves_2[i-2]):
            score+=1  
      except TO_exc:
          details.add("Got TIMEOUT during problem {} when testing depth".format(i-2))
      except:
          details.add("A runtime error occurred while testing depth: %r" % traceback.format_exc())

    details.add("Calculated correct moves at varying depths {}/10 times".format(score))
    details = "\n".join(details) 
    return score, details



@max_grade(20)
def test_select_move_minimax(student_modules):

    stu_solution = student_modules[SOLUTION]  
    details = set()

    # correctmoves_1 = [(3,3),(0,0),(3,3),(0,2),(3,1),(3,3),(0,0),(3,3),(0,2),(3,1),(3,3),(0,0),(3,3),(0,2),(3,1),(3,3),(0,0),(3,3),(0,2),(3,1),(3,3),(0,0),(3,3),(0,2),(3,1),(3,3),(0,0),(3,3),(0,2),(3,1),(3,3),(0,0),(3,3),(0,2),(3,1)]
    # correctmoves_2 = [(3,3),(0,0),(3,3),(0,2),(3,1),(3,3),(0,0),(3,3),(0,2),(3,1),(3,3),(0,0),(3,3),(0,2),(3,1),(3,3),(0,0),(3,3),(0,2),(3,1),(3,3),(0,0),(3,3),(0,2),(3,1),(3,3),(0,0),(3,3),(0,2),(3,1),(3,3),(0,0),(3,3),(0,2),(3,1)]
    # correctmoves_1 = [2, 5, 5, 5, 0, 4, 5, 5, 0, 6, 0, 0, 0, 1, 5, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 1, 5, 7, 0, 0, 0, 0, 0, 4,2, 0, 3, 3, 2, 2, 2, 6, 6, 1, 6, 4, 6, 1, 3, 3, 3, 7, 0]
    # correctmoves_2 = [5, 1, 1, 1, 2, 2, 1, 1, 1, 7, 1, 6, 6, 3, 1, 2, 2, 0, 3, 3, 2, 2, 2, 6, 6, 1, 6, 4, 6, 1, 3, 3, 3, 7, 0,2, 0, 3, 3, 2, 2, 2, 6, 6, 1, 6, 4, 6, 1, 3, 3, 3, 7, 0]

    correctmoves_1a = [2, 5, 5, 5, 0, 4, 5, 5, 0, 6, 0, 0, 0, 1, 5, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 1, 5, 7, 0, 0, 0, 0, 0, 4, 3, 0, 0, 1]
    correctmoves_2a = [5, 1, 1, 1, 2, 2, 1, 1, 1, 7, 1, 6, 6, 3, 1, 2, 2, 0, 3, 3, 2, 2, 2, 6, 6, 1, 6, 4, 6, 1, 3, 3, 3, 7, 0, 3, 3, 2, 2]

    correctmoves_1 =[2, 2, 0, 0, 1, 0, 0, 7, 3, 0]
    correctmoves_2 =[5, 2, 1, 6, 2, 2, 6, 3, 3, 4]

    answers1 = []
    answers2 = []
    score, ct = 0, 0
    alternate_depth = 0
    for i in range(0,len(boards)-1,4):
      board = boards[i]
      try:
        setTO(timeout)
        value1 = stu_solution.select_move_minimax(board, 0, 5)
        value2 = stu_solution.select_move_minimax(board, 1, 5)
        setTO(0)
        if (value1 == correctmoves_1[ct]):        
          score+=1  
        if (value2 == correctmoves_2[ct]):        
          score+=1       
        answers1.append(value1)     
        answers2.append(value2)     
      except TO_exc:
          details.add("Got TIMEOUT during problem {} when testing test_select_move_minimax".format(i))
      except:
          details.add("A runtime error occurred while testing test_select_move_minimax: %r" % traceback.format_exc())
      ct = ct + 1
    

    #print(answers1)
    #print(answers2)
    for i in range(0,len(boards)-1,4):
      board = boards[i]
      try:
        setTO(timeout)
        value1 = stu_solution.select_move_minimax(board, 0, 6)
        value2 = stu_solution.select_move_minimax(board, 1, 6)
        setTO(0)
        if (value1 == correctmoves_1a[i]):        
          alternate_depth+=1  
        if (value2 == correctmoves_2a[i]):        
          alternate_depth+=1          
      except TO_exc:
          details.add("Got TIMEOUT during problem {} when testing test_select_move_minimax".format(i))
      except:
          details.add("A runtime error occurred while testing test_select_move_minimax: %r" % traceback.format_exc())

    details.add("Calculated correct minimax moves {}/20 times at depth 6.".format(score))
    

    if (alternate_depth != 20):
      score = score-10
      details.add("Correct moves are NOT selected at all depths!".format(score))

    details = "\n".join(details) 

    return score, details


@max_grade(10)
def test_select_move_equal(student_modules):

    stu_solution = student_modules[SOLUTION]  
    details = set()

    correctmoves_1a = [5, 1, 1, 1, 2, 2, 1, 1, 1, 7, 1, 6, 6, 3, 1, 2, 2, 0, 3, 3, 2, 2, 2, 6, 6, 1, 6, 4, 6, 1, 3, 3, 3, 7, 0, 3, 3, 2, 2]
    correctmoves_2a = [2, 5, 5, 5, 0, 4, 5, 5, 0, 6, 0, 0, 0, 1, 5, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 1, 5, 7, 0, 0, 0, 0, 0, 4, 3, 0, 0, 1]

    correctmoves_1 = [5, 2, 1, 6, 2, 2, 6, 3, 3, 4]
    correctmoves_2 = [2, 2, 0, 0, 1, 0, 0, 7, 3, 0]
 
    answers1 = []
    answers2 = []    
    correct, ct, alternate_depth = 0, 0, 0
    for i in range(0,len(boards)-1,4):
      board = boards[i]
      try:
        setTO(timeout)
        value1_minimax = stu_solution.select_move_minimax(board, 1, 5)
        value2_minimax = stu_solution.select_move_minimax(board, 0, 5)
        value1_ab = stu_solution.select_move_alphabeta(board, 1, 5)
        value2_ab = stu_solution.select_move_alphabeta(board, 0, 5)
        if isinstance(value1_ab, tuple): 
          value1_ab = value1_ab[0]
        if isinstance(value2_ab, tuple): 
          value2_ab = value2_ab[0]   

        answers1.append(value1_ab)     
        answers2.append(value2_ab)  
        setTO(0)
        if (value1_minimax == value1_ab == correctmoves_1[ct] and value2_minimax == value2_ab == correctmoves_2[ct]):
          correct+=1  
      except TO_exc:
          details.add("Got TIMEOUT during problem {} when testing test_select_move_equal".format(i))
      except:
          details.add("A runtime error occurred while testing test_select_move_equal: %r" % traceback.format_exc())
      ct = ct + 1

    for i in range(0,len(boards)-1,4):
      board = boards[i]
      try:
        setTO(timeout)
        value1_minimax = stu_solution.select_move_minimax(board, 1, 6)
        value2_minimax = stu_solution.select_move_minimax(board, 0, 6)
        value1_ab = stu_solution.select_move_alphabeta(board, 1, 6)
        value2_ab = stu_solution.select_move_alphabeta(board, 0, 6)
        if isinstance(value1_ab, tuple): 
          value1_ab = value1_ab[0]
        if isinstance(value2_ab, tuple): 
          value2_ab = value2_ab[0]   

        # answers1.append(value1_ab)     
        # answers2.append(value2_ab)  
        setTO(0)
        if (value1_minimax == value1_ab == correctmoves_1a[i] and value2_minimax == value2_ab == correctmoves_2a[i]):
          alternate_depth+=1  
      except TO_exc:
          details.add("Got TIMEOUT during problem {} when testing test_select_move_equal".format(i))
      except:
          details.add("A runtime error occurred while testing test_select_move_equal: %r" % traceback.format_exc())


    details.add("Same alphabeta strategy as minimax {}/10 times at depth 6.".format(correct))
    
    if (alternate_depth != 10):
      correct = correct-5
      details.add("Correct moves are NOT selected at all depths!")


    details = "\n".join(details)  

    # print(answers1)
    # print(answers2)  

    return correct, details

# @max_grade(10)
# def test_caching(student_modules):

#     stu_solution = student_modules[SOLUTION]  
#     details = set()

#     print('Testing Caching')
#     check_1 = 0
#     check_2 = 0  
#     for i in range(0,len(boards),4):

#       try:
#         setTO(timeout)
#         start_time_1 = os.times()[0]
#         no_cache = stu_solution.select_move_minimax(boards[i], 1, 6)
#         if isinstance(no_cache, tuple): no_cache = no_cache[0]
#         end_time_1 = os.times()[0]
#         setTO(0)
#         setTO(timeout)
#         start_time_2 = os.times()[0]
#         with_cache = stu_solution.select_move_minimax(boards[i], 1, 6, 1)
#         if isinstance(with_cache, tuple): with_cache = with_cache[0]        
#         end_time_2 = os.times()[0]
#         setTO(0)
#         if (end_time_1 - start_time_1) >= (end_time_2 - start_time_2):
#           check_1 += 1

#         if (with_cache == no_cache):
#            check_2 += 1       

#       except TO_exc:
#           details.add("Got TIMEOUT during problem {} when testing test_caching_big".format(i))
#       except:
#           details.add("A runtime error occurred while testing test_caching_big: %r" % traceback.format_exc())

#     details.add("State caching improved the time of your minmax for {} of {} boards".format(check_1, len(boards)/4)) 
#     details.add("Move choice with and without caching is the same for {} of {} boards".format(check_2, len(boards)/4))
#     if check_1 > 1: check_1 = 10
#     details = "\n".join(details)  

#     score = check_1 + check_2

#     return score/2, details


# @max_grade(5)
# def test_alphabeta_max_node_1(student_modules):

#     stu_solution = student_modules[SOLUTION]  
#     details = set()

#     answers = [(),((5,5),8),((1,5),12),(),((3,4),4)]
#     correct = 0
#     correctval = 0
#     selected = [1,2,4] #some boards have moves that are tied in value
#     for i in selected:
#       board = boards[i]
#       try:
#         setTO(timeout)        
#         color = 1
#         (move, value) = stu_solution.select_move_alphabeta(board, color, float("-Inf"), float("Inf"), 1, 0, 0)
#         answer = answers[i][0]
#         answer_value = answers[i][1]
#         setTO(0)
#         if (answer[0] == move[0] and answer[1] == move[1]):
#           correct+=1
#         if (answer_value == value):
#           correctval+=1      

#       except TO_exc:
#           details.add("Got TIMEOUT during problem {} when testing test_alphabeta_max_node_1".format(i))
#       except:
#           details.add("A runtime error occurred while testing test_alphabeta_max_node_1: %r" % traceback.format_exc())

#     details.add("You computed correct alpha-beta max moves for {} of {} boards".format(correct, len(selected))) 
#     details.add("You computed correct alpha-beta max values for {} of {} boards".format(correctval, len(selected))) 

#     details = "\n".join(details)    
#     score = correct+correctval
#     score = score *(5/6) #max is 5
#     return score, details

# @max_grade(5)
# def test_minimax_max_node_1(student_modules):

#     stu_solution = student_modules[SOLUTION]  
#     details = set()

#     print('Testing Minimax Max Node - Player 1')  
#     answers = [(),((5,5),8),((1,5),12),(),((3,4),4)]
#     correct = 0
#     correctval = 0
#     selected = [1,2,4] #some boards have moves that are tied in value
#     for i in selected:
#       board = boards[i]
#       try:
#         setTO(timeout)        
#         color = 1
#         (move, value) = stu_solution.select_move_minimax(board, color, 1, 0)
#         answer = answers[i][0]
#         answer_value = answers[i][1]
#         setTO(0)
#         if (answer[0] == move[0] and answer[1] == move[1]):
#           correct+=1
#         if (answer_value == value):
#           correctval+=1      

#       except TO_exc:
#           details.add("Got TIMEOUT during problem {} when testing test_minimax_max_node_1".format(i))
#       except:
#           details.add("A runtime error occurred while testing test_minimax_max_node_1: %r" % traceback.format_exc())

#     details.add("You computed correct minimax max moves for {} of {} boards".format(correct, len(selected))) 
#     details.add("You computed correct minimax max values for {} of {} boards".format(correctval, len(selected))) 
#     details = "\n".join(details)    

#     score = correct+correctval
#     score = score*(5/6) #max is 5   
#     return score, details    

# @max_grade(5)
# def test_alphabeta_max_node_2(student_modules):

#     stu_solution = student_modules[SOLUTION]  
#     details = set()

#     print('Testing Alpha Beta Max Node - Player 2')
#     answers = [((0,0),0),((1,1),4),((3,0),6),((0,0),0),((5,2), 6),((0,0), 0)]
#     correct = 0
#     correctval = 0
#     selected = [1,2,4] #some boards have moves that are tied in value
#     for i in selected:
#       board = boards[i]
#       try:
#         setTO(timeout)        
#         color = 2
#         (move, value) = stu_solution.select_move_alphabeta(board, color, float("-Inf"), float("Inf"), 1, 0, 0)
#         answer = answers[i][0]
#         answer_value = answers[i][1]
#         setTO(0)
#         if (answer[0] == move[0] and answer[1] == move[1]):
#           correct+=1
#         if (answer_value == value):
#           correctval+=1      
#       except TO_exc:
#           details.add("Got TIMEOUT during problem {} when testing test_alphabeta_max_node_2".format(i))
#       except:
#           details.add("A runtime error occurred while testing test_alphabeta_max_node_2: %r" % traceback.format_exc())

#     details.add("You computed correct alpha-beta max moves for {} of {} boards".format(correct, len(selected))) 
#     details.add("You computed correct alpha-beta max values for {} of {} boards".format(correctval, len(selected))) 

#     details = "\n".join(details) 

#     score = correct+correctval
#     score = score*(5/6) #max is 5   
#     return score, details

# @max_grade(5)
# def test_minimax_max_node_2(student_modules):

#     stu_solution = student_modules[SOLUTION]  
#     details = set()

#     print('Testing Minimax Max Node - Player 2')  
#     answers = [((0,0),0),((1,1),4),((3,0),6),((0,0),0),((5,2), 6),((0,0), 0)]
#     correct = 0
#     correctval = 0
#     selected = [1,2,4] #some boards have moves that are tied in value
#     for i in selected:
#       board = boards[i]
#       try:
#         setTO(timeout)        
#         color = 2
#         (move, value) = stu_solution.select_move_minimax(board, color, 1, 0)
#         answer = answers[i][0]
#         answer_value = answers[i][1]
#         setTO(0)
#         if (answer[0] == move[0] and answer[1] == move[1]):
#           correct+=1
#         if (answer_value == value):
#           correctval+=1      
#       except TO_exc:
#           details.add("Got TIMEOUT during problem {} when testing test_minimax_max_node_2".format(i))
#       except:
#           details.add("A runtime error occurred while testing test_minimax_max_node_2: %r" % traceback.format_exc())

#     details.add("Test 2: You computed correct minimax max moves for {} of {} boards".format(correct, len(selected))) 
#     details.add("Test 2: You computed correct minimax max values for {} of {} boards".format(correctval, len(selected))) 

#     details = "\n".join(details)    
#     score = correct+correctval
#     score = score*(5/6) #max is 5   
#     return score, details 




