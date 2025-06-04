#!/usr/bin/env python
import os  # for time functions

from utils.utilities import sortInnerMostLists, TO_exc, setTO, setMEM, resetMEM

from utils.test_tools import max_grade
from .test_cases_helpers import *

# import student's functions
#from solution import *
smallboards = [((0, 0, 0, 0), (0, 2, 1, 0), (0, 1, 1, 1), (0, 0, 0, 0)),
((0, 1, 0, 0), (0, 1, 1, 0), (0, 1, 2, 1), (0, 0, 0, 2)),
((0, 0, 0, 0), (0, 2, 1, 0), (0, 1, 1, 1), (0, 1, 1, 0)),
((0, 1, 0, 0), (0, 2, 2, 0), (0, 1, 2, 1), (0, 0, 2, 2)),
((1, 0, 0, 2), (1, 1, 2, 0), (1, 1, 1, 1), (1, 2, 2, 2)),
((0, 1, 0, 0), (0, 1, 1, 0), (2, 2, 2, 1), (0, 0, 0, 2))]

bigboards = [((0, 0, 0, 0, 0, 0), (0, 0, 2, 2, 0, 0), (0, 1, 1, 2, 2, 0), (2, 2, 1, 2, 0, 0), (0, 1, 0, 1, 2, 0), (0, 0, 0, 0, 0, 0)),
((0, 0, 0, 0, 0, 0), (0, 0, 1, 2, 0, 0), (0, 1, 1, 1, 1, 0), (2, 2, 1, 2, 0, 0), (0, 1, 0, 1, 2, 0), (0, 0, 0, 0, 0, 0)),
((0, 0, 0, 0, 1, 0), (0, 0, 1, 1, 0, 0), (0, 1, 1, 1, 1, 0), (2, 2, 1, 2, 0, 0), (0, 2, 0, 1, 2, 0), (0, 0, 2, 2, 1, 0)),
((0, 0, 0, 0, 0, 0), (0, 0, 0, 2, 0, 0), (0, 1, 2, 2, 2, 0), (0, 2, 2, 2, 0, 0), (0, 1, 0, 0, 0, 0), (0, 0, 0, 0, 0, 0)),
((0, 0, 0, 0, 0, 0), (0, 0, 0, 2, 0, 0), (0, 1, 2, 1, 1, 0), (0, 2, 2, 2, 0, 0), (0, 1, 0, 0, 0, 0), (0, 0, 0, 0, 0, 0))]

xlboards = bigboards = [((0, 0, 0, 0, 0, 0, 0, 0), (0, 0, 2, 2, 0, 0, 0, 0), (0, 1, 1, 2, 2, 0, 0, 0), (2, 2, 1, 2, 0, 0, 0, 0), (0, 1, 0, 1, 2, 0, 0, 0), (0, 0, 0, 0, 0, 0, 0, 0)),
((0, 0, 0, 0, 0, 0, 0, 0), (0, 0, 1, 2, 0, 0, 0, 0), (0, 1, 1, 1, 1, 0, 0, 0), (2, 2, 1, 2, 0, 0, 0, 0), (0, 1, 0, 1, 2, 0, 0, 0), (0, 0, 0, 0, 0, 0, 0, 0)),
((0, 0, 0, 0, 1, 0, 0, 0), (0, 0, 1, 1, 0, 0, 0, 0), (0, 1, 1, 1, 1, 0, 0, 0), (2, 2, 1, 2, 0, 0, 0, 0), (0, 2, 0, 1, 2, 0, 0, 0), (0, 0, 2, 2, 1, 0, 0, 0)),
((0, 0, 0, 0, 0, 0, 0, 0), (0, 0, 0, 2, 0, 0, 0, 0), (0, 1, 2, 2, 2, 0, 0, 0), (0, 2, 2, 2, 0, 0, 0, 0), (0, 1, 0, 0, 0, 0, 0, 0), (0, 0, 0, 0, 0, 0, 0, 0)),
((0, 0, 0, 0, 0, 0, 0, 0), (0, 0, 0, 2, 0, 0, 0, 0), (0, 1, 2, 1, 1, 0, 0, 0), (0, 2, 2, 2, 0, 0, 0, 0), (0, 1, 0, 0, 0, 0, 0, 0), (0, 0, 0, 0, 0, 0, 0, 0))]

SOLUTION = 'agent.py'

#-- Minimax would be worth 25 points

#test_compute_utility = 5

#test_compute_utility_big = 5
#test_minimax_min_node_1 = 5
#test_minimax_max_node_1 = 5
#test_minimax_max_node_2 = 5
#test_select_move_minimax = 5

#-- Alpha-beta would be worth 25 points
#test_alphabeta_min_node_1 = 5
#test_alphabeta_max_node_1 = 5
#test_alphabeta_max_node_2 = 5
#test_select_move_alphabeta = 5
#test_select_move_equal = 5

#- State caching would be worth 12 points
#test_caching_big = 4
#test_caching_xl = 8

#- Node ordering would be worth 18 points
#test_ordering = 18

#-- The depth limit would be worth 20 points
#test_depth = 20

@max_grade(20)
def test_depth(student_modules):

    print('Testing Depth')
    stu_solution = student_modules[SOLUTION] 
    details = set()

    correctmoves_11 = [(0,0),(0,0),(0,0),(0,0),(0,0),(0,0)]
    correctmoves_21 = [(1,3),(1,3),(1,3),(1,3),(1,3),(3,3)]
    correctmoves_12 = [(2,3),(2,3),(2,3),(2,3),(2,3),(2,3)]
    correctmoves_22 = [(0,0),(0,0),(0,0),(0,0),(3,1),(0,0)]

    score = 0
    for j in range(0,2):

      if j == 0:
        correctmoves_1 = correctmoves_11
        correctmoves_2 = correctmoves_21
      else:
        correctmoves_1 = correctmoves_12
        correctmoves_2 = correctmoves_22

      board = smallboards[j]
      try:
        for i in range(1,6):
          value1 = stu_solution.select_move_minimax(board, 1, i)
          value2 = stu_solution.select_move_minimax(board, 2, i)
          if (value1 == correctmoves_1[i] and value2 == correctmoves_2[i]):
            score+=2  
      except TO_exc:
          details.add("Got TIMEOUT during problem {} when testing depth".format(i))
      except:
          details.add("A runtime error occurred while testing depth: %r" % traceback.format_exc())

    details.add("Calculated correct moves at varying depths {}/10 times".format(score/2))
    details = "\n".join(details)    
    return score, details


@max_grade(6)
def test_compute_utility(student_modules):

    stu_solution = student_modules[SOLUTION] 
    details = set()

    ##############################################################
    print('Testing Utility')
    correctvalues = [3, 3, 5, -2, 3, 0]
    score = 0
    for i in range(0,len(smallboards)):
      board = smallboards[i]
      try:
        value1 = stu_solution.compute_utility(board, 1)
        value2 = stu_solution.compute_utility(board, 2)
        if (value1 == correctvalues[i] and value2 == correctvalues[i]*-1):
          score+=1  
      except TO_exc:
          details.add("Got TIMEOUT during problem {} when testing compute_utility".format(i))
      except:
          details.add("A runtime error occurred while testing compute_utility: %r" % traceback.format_exc())

    details.add("You computed correct utilities for {} of {} boards".format(score, len(correctvalues)))
    details = "\n".join(details)

    return score, details


@max_grade(10)
def test_select_move_minimax(student_modules):

    stu_solution = student_modules[SOLUTION]  
    details = set()

    correctmoves_1 = [(0,0),(2,3),(0,0),(3,0),(3,1)]
    correctmoves_2 = [(3,3),(0,0),(3,3),(0,2),(3,1)]
    score = 0
    for i in range(0,len(smallboards)-1):
      board = smallboards[i]
      try:
        value1 = stu_solution.select_move_minimax(board, 1, 6)
        value2 = stu_solution.select_move_minimax(board, 2, 6)
        if (value1 == correctmoves_1[i]):        
          score+=1  
        if (value2 == correctmoves_2[i]):        
          score+=1            
      except TO_exc:
          details.add("Got TIMEOUT during problem {} when testing test_select_move_minimax".format(i))
      except:
          details.add("A runtime error occurred while testing test_select_move_minimax: %r" % traceback.format_exc())
    
    details.add("Calculated correct minimax moves {}/10 times".format(score))
    details = "\n".join(details)    
    return score, details

@max_grade(10)
def test_select_move_alphabeta(student_modules):

    stu_solution = student_modules[SOLUTION]  
    details = set()

    correctmoves_1 = [(0,0),(2,3),(0,0),(3,0),(3,1)]
    correctmoves_2 = [(3,3),(0,0),(3,3),(0,2),(3,1)]
    correct = 0
    for i in range(0,len(smallboards)-1):
      board = smallboards[i]
      try:
        value1 = stu_solution.select_move_alphabeta(board, 1, 6)
        value2 = stu_solution.select_move_alphabeta(board, 2, 6)
        if (value1 == correctmoves_1[i]):
          correct+=1  
        if (value2 == correctmoves_2[i]):
          correct+=1           
      except TO_exc:
          details.add("Got TIMEOUT during problem {} when testing test_select_move_alphabeta".format(i))
      except:
          details.add("A runtime error occurred while testing test_select_move_alphabeta: %r" % traceback.format_exc())

    details.add("Calculated correct alphabeta moves {}/10 times".format(correct))
    details = "\n".join(details)    
    return correct, details

@max_grade(5)
def test_select_move_equal(student_modules):

    stu_solution = student_modules[SOLUTION]  
    details = set()

    correctmoves_1 = [(0,0),(2,3),(0,0),(3,0),(3,1)]
    correctmoves_2 = [(3,3),(0,0),(3,3),(0,2),(3,1)]
    correct = 0
    for i in range(0,len(smallboards)-1):
      board = smallboards[i]
      try:
        value1_minimax = stu_solution.select_move_minimax(board, 1, 6)
        value2_minimax = stu_solution.select_move_minimax(board, 2, 6)
        value1_ab = stu_solution.select_move_alphabeta(board, 1, 6)
        value2_ab = stu_solution.select_move_alphabeta(board, 2, 6)
        if (value1_minimax == value1_ab == correctmoves_1[i] and value2_minimax == value2_ab == correctmoves_2[i]):
          correct+=1  
      except TO_exc:
          details.add("Got TIMEOUT during problem {} when testing test_select_move_equal".format(i))
      except:
          details.add("A runtime error occurred while testing test_select_move_equal: %r" % traceback.format_exc())

    details.add("Same alphabeta strategy as minimax {}/5 times".format(correct))
    details = "\n".join(details)    
    return correct, details

@max_grade(10)
def test_caching_big(student_modules):

    stu_solution = student_modules[SOLUTION]  
    details = set()

    print('Testing Caching Big')
    check_1 = 0
    check_2 = 0  
    for i in range(0,len(bigboards)):

      try:
        start_time_1 = os.times()[0]
        no_cache = stu_solution.select_move_alphabeta(bigboards[i], 1, 6)
        end_time_1 = os.times()[0]

        start_time_2 = os.times()[0]
        with_cache = stu_solution.select_move_alphabeta(bigboards[i], 1, 6, 1)
        end_time_2 = os.times()[0]

        if (end_time_1 - start_time_1) >= (end_time_2 - start_time_2):
          check_1 += 1

        if (with_cache == no_cache):
           check_2 += 1       

      except TO_exc:
          details.add("Got TIMEOUT during problem {} when testing test_caching_big".format(i))
      except:
          details.add("A runtime error occurred while testing test_caching_big: %r" % traceback.format_exc())

    details.add("State caching improved the time of your alpha-beta for {} of {} boards".format(check_1, len(bigboards))) 
    details.add("Move choice with and without caching is the same for {} of {} boards".format(check_2, len(bigboards)))
    if check_1 > 3: check_1 = 5
    details = "\n".join(details)    
    return check_1 + check_2, details

@max_grade(10)
def test_caching_xl(student_modules):

    stu_solution = student_modules[SOLUTION]  
    details = set()

    print('Testing Caching XL')
    check_1 = 0
    check_2 = 0  
    for i in range(0,len(xlboards)):

      try:
        start_time_1 = os.times()[0]
        no_cache = stu_solution.select_move_alphabeta(xlboards[i], 1, 8)
        end_time_1 = os.times()[0]

        start_time_2 = os.times()[0]
        with_cache = stu_solution.select_move_alphabeta(xlboards[i], 1, 8, 1)
        end_time_2 = os.times()[0]

        if (end_time_1 - start_time_1) >= (end_time_2 - start_time_2):
          check_1 += 1

        if (with_cache == no_cache):
           check_2 += 1       

      except TO_exc:
          details.add("Got TIMEOUT during problem {} when testing test_caching_xl".format(i))
      except:
          details.add("A runtime error occurred while testing test_caching_xl: %r" % traceback.format_exc())

    

    details.add("State caching improved the time of your alpha-beta for {} of {} boards".format(check_1, len(xlboards))) 
    details.add("Move choice with and without caching is the same for {} of {} boards".format(check_2, len(xlboards))) 
    if check_1 > 3: check_1 = 5
    details = "\n".join(details)    
    return check_1 + check_2, details

@max_grade(5)
def test_ordering_1(student_modules):

    stu_solution = student_modules[SOLUTION]  
    details = set()

    print('Testing Ordering')
    check_1 = 0
    check_2 = 0  
    for i in range(0,len(bigboards)):

      try:
        start_time_1 = os.times()[0]
        no_order = stu_solution.select_move_alphabeta(bigboards[i], 1, 6, 1, 0)
        end_time_1 = os.times()[0]

        start_time_2 = os.times()[0]
        with_order = stu_solution.select_move_alphabeta(bigboards[i], 1, 6, 1, 1)
        end_time_2 = os.times()[0]

        if (end_time_1 - start_time_1) >= (end_time_2 - start_time_2):
          check_1 += 1

        if (with_order == no_order):
           check_2 += 1       

      except TO_exc:
          details.add("Got TIMEOUT during problem {} when testing test_ordering_1".format(i))
      except:
          details.add("A runtime error occurred while testing test_ordering_1: %r" % traceback.format_exc())

    details.add("Node ordering improved the ordering of your alpha-beta for {} of {} boards".format(check_1, len(bigboards))) 
    details.add("Move choice with and without ordering is the same for {} of {} boards".format(check_2, len(bigboards))) 
    
    details = "\n".join(details)    
    return check_1, details


@max_grade(5)
def test_ordering_2(student_modules):

    stu_solution = student_modules[SOLUTION]  
    details = set()

    print('Testing Ordering')
    check_1 = 0
    check_2 = 0  
    for i in range(0,len(xlboards)):

      try:
        start_time_1 = os.times()[0]
        no_order = stu_solution.select_move_alphabeta(xlboards[i], 1, 3, 1, 0)
        end_time_1 = os.times()[0]

        start_time_2 = os.times()[0]
        with_order = stu_solution.select_move_alphabeta(xlboards[i], 1, 3, 1, 1)
        end_time_2 = os.times()[0]

        if (end_time_1 - start_time_1) >= (end_time_2 - start_time_2):
          check_1 += 1

        if (with_order == no_order):
           check_2 += 1       

      except TO_exc:
          details.add("Got TIMEOUT during problem {} when testing test_ordering_2".format(i))
      except:
          details.add("A runtime error occurred while testing test_ordering_2: %r" % traceback.format_exc())

    details.add("Node ordering improved the ordering of your alpha-beta for {} of {} boards".format(check_1, len(bigboards))) 
    details.add("Move choice with and without ordering is the same for {} of {} boards".format(check_2, len(bigboards))) 
    
    details = "\n".join(details)    
    return check_1, details

@max_grade(10)
def test_alphabeta_min_node_1(student_modules):

    stu_solution = student_modules[SOLUTION]  
    details = set()

    print('Testing Alpha Beta Min Node - Player 1')
    answers = [((2,4),-10),((1,1),-4),((3,0),-6),((0,1),-8),((5,2),-6)]
    correct = 0
    correctval = 0
    for i in range(0,len(bigboards)):
      board = bigboards[i]
      try:
        color = 1
        (move, value) = stu_solution.alphabeta_min_node(board, color, float("-Inf"), float("Inf"), 1, 0, 0)
        answer = answers[i][0]
        answer_value = answers[i][1]

        if (answer[0] == move[0] and answer[1] == move[1]):
          correct+=1
        if (answer_value == value):
          correctval+=1      

      except TO_exc:
          details.add("Got TIMEOUT during problem {} when testing test_alphabeta_min_node_1".format(i))
      except:
          details.add("A runtime error occurred while testing test_alphabeta_min_node_1: %r" % traceback.format_exc())

    details.add("You computed correct alpha-beta min moves for {} of {} boards".format(correct, len(bigboards))) 
    details.add("You computed correct alpha-beta min values for {} of {} boards".format(correctval, len(bigboards))) 

    details = "\n".join(details)    
    return correct+correctval, details

@max_grade(6)
def test_alphabeta_max_node_1(student_modules):

    stu_solution = student_modules[SOLUTION]  
    details = set()

    answers = [(),((5,5),8),((1,5),12),(),((3,4),4)]
    correct = 0
    correctval = 0
    selected = [1,2,4] #some boards have moves that are tied in value
    for i in selected:
      board = bigboards[i]
      try:
        color = 1
        (move, value) = stu_solution.alphabeta_max_node(board, color, float("-Inf"), float("Inf"), 1, 0, 0)
        answer = answers[i][0]
        answer_value = answers[i][1]

        if (answer[0] == move[0] and answer[1] == move[1]):
          correct+=1
        if (answer_value == value):
          correctval+=1      

      except TO_exc:
          details.add("Got TIMEOUT during problem {} when testing test_alphabeta_max_node_1".format(i))
      except:
          details.add("A runtime error occurred while testing test_alphabeta_max_node_1: %r" % traceback.format_exc())

    details.add("You computed correct alpha-beta max moves for {} of {} boards".format(correct, len(selected))) 
    details.add("You computed correct alpha-beta max values for {} of {} boards".format(correctval, len(selected))) 

    details = "\n".join(details)    
    return correct+correctval, details

@max_grade(10)
def test_minimax_min_node_1(student_modules):

    stu_solution = student_modules[SOLUTION]  
    details = set()
    ##############################################################
    # Must program some trees where we know cut set
    ##############################################################

    print('Testing Minimax Min Node - Player 1')
    answers = [((2,4),-10),((1,1),-4),((3,0),-6),((0,1),-8),((5,2),-6)]
    correct = 0
    correctval = 0
    for i in range(0,len(bigboards)):
      board = bigboards[i]
      try:
        color = 1
        (move, value) = stu_solution.minimax_min_node(board, color, 1, 0)
        answer = answers[i][0]
        answer_value = answers[i][1]

        if (answer[0] == move[0] and answer[1] == move[1]):
          correct+=1
        if (answer_value == value):
          correctval+=1      

      except TO_exc:
          details.add("Got TIMEOUT during problem {} when testing test_minimax_min_node_1".format(i))
      except:
          details.add("A runtime error occurred while testing test_minimax_min_node_1: %r" % traceback.format_exc())

    details.add("You computed correct minimax min moves for {} of {} boards".format(correct, len(bigboards))) 
    details.add("You computed correct minimax min values for {} of {} boards".format(correctval, len(bigboards))) 

    details = "\n".join(details)    
    return correct+correctval, details

@max_grade(6)
def test_minimax_max_node_1(student_modules):

    stu_solution = student_modules[SOLUTION]  
    details = set()

    print('Testing Minimax Max Node - Player 1')  
    answers = [(),((5,5),8),((1,5),12),(),((3,4),4)]
    correct = 0
    correctval = 0
    selected = [1,2,4] #some boards have moves that are tied in value
    for i in selected:
      board = bigboards[i]
      try:
        color = 1
        (move, value) = stu_solution.minimax_max_node(board, color, 1, 0)
        answer = answers[i][0]
        answer_value = answers[i][1]

        if (answer[0] == move[0] and answer[1] == move[1]):
          correct+=1
        if (answer_value == value):
          correctval+=1      

      except TO_exc:
          details.add("Got TIMEOUT during problem {} when testing test_minimax_max_node_1".format(i))
      except:
          details.add("A runtime error occurred while testing test_minimax_max_node_1: %r" % traceback.format_exc())

    details.add("You computed correct minimax max moves for {} of {} boards".format(correct, len(selected))) 
    details.add("You computed correct minimax max values for {} of {} boards".format(correctval, len(selected))) 
    details = "\n".join(details)    
    return correct+correctval, details

# @max_grade(10)
# def test_alphabeta_min_node_2(student_modules):

#     stu_solution = student_modules[SOLUTION]  
#     details = set()

#     print('Testing Alpha Beta Min Node - Player 2')
#     answers = [((3,0),-6),((5,5),-8),((1,5),-12),((5,2),-2),((3,4),-4)]
#     correct = 0
#     correctval = 0
#     for i in range(0,len(bigboards)):
#       board = bigboards[i]
#       try:
#         color = 2
#         (move, value) = stu_solution.alphabeta_min_node(board, color, float("-Inf"), float("Inf"), 1, 0, 0)
#         answer = answers[i][0]
#         answer_value = answers[i][1]

#         if (answer[0] == move[0] and answer[1] == move[1]):
#           correct+=1
#         if (answer_value == value):
#           correctval+=1      
#       except TO_exc:
#           details.add("Got TIMEOUT during problem {} when testing manhattan distance".format(i))
#       except:
#           details.add("A runtime error occurred while testing manhattan distance: %r" % traceback.format_exc())

#     details.add("You computed correct alpha-beta max moves for {} of {} boards".format(correct, len(selected))) 
#     details.add("You computed correct alpha-beta max values for {} of {} boards".format(correctval, len(selected))) 

#     details = "\n".join(details)    
#     return correct+correctval, details

@max_grade(6)
def test_alphabeta_max_node_2(student_modules):

    stu_solution = student_modules[SOLUTION]  
    details = set()

    print('Testing Alpha Beta Max Node - Player 2')
    answers = [((0,0),0),((1,1),4),((3,0),6),((0,0),0),((5,2), 6),((0,0), 0)]
    correct = 0
    correctval = 0
    selected = [1,2,4] #some boards have moves that are tied in value
    for i in selected:
      board = bigboards[i]
      try:
        color = 2
        (move, value) = stu_solution.alphabeta_max_node(board, color, float("-Inf"), float("Inf"), 1, 0, 0)
        answer = answers[i][0]
        answer_value = answers[i][1]

        if (answer[0] == move[0] and answer[1] == move[1]):
          correct+=1
        if (answer_value == value):
          correctval+=1      
      except TO_exc:
          details.add("Got TIMEOUT during problem {} when testing test_alphabeta_max_node_2".format(i))
      except:
          details.add("A runtime error occurred while testing test_alphabeta_max_node_2: %r" % traceback.format_exc())

    details.add("You computed correct alpha-beta max moves for {} of {} boards".format(correct, len(selected))) 
    details.add("You computed correct alpha-beta max values for {} of {} boards".format(correctval, len(selected))) 

    details = "\n".join(details)    
    return correct+correctval, details

# @max_grade(10)
# def test_minimax_min_node_2(student_modules):

#     stu_solution = student_modules[SOLUTION]  
#     details = set()

#     ##############################################################
#     # Must program some trees where we know cut set
#     ##############################################################

#     print('Testing Minimax Min Node - Player 2')
#     answers = [((3,0),-6),((5,5),-8),((1,5),-12),((5,2),-2),((3,4),-4)]
#     correct = 0
#     correctval = 0
#     for i in range(0,len(bigboards)):
#       board = bigboards[i]
#       try:
#         color = 2
#         (move, value) = stu_solution.minimax_min_node(board, color, 1, 0)
#         answer = answers[i][0]
#         answer_value = answers[i][1]

#         if (answer[0] == move[0] and answer[1] == move[1]):
#           correct+=1
#         if (answer_value == value):
#           correctval+=1      
#       except TO_exc:
#           details.add("Got TIMEOUT during problem {} when testing manhattan distance".format(i))
#       except:
#           details.add("A runtime error occurred while testing manhattan distance: %r" % traceback.format_exc())

#     details.add("Test 1: You computed correct minimax max moves for {} of {} boards".format(correct, len(selected))) 
#     details.add("Test 1: You computed correct minimax max values for {} of {} boards".format(correctval, len(selected))) 
    
#     details = "\n".join(details)    
#     return correct+correctval, details

@max_grade(6)
def test_minimax_max_node_2(student_modules):

    stu_solution = student_modules[SOLUTION]  
    details = set()

    print('Testing Minimax Max Node - Player 2')  
    answers = [((0,0),0),((1,1),4),((3,0),6),((0,0),0),((5,2), 6),((0,0), 0)]
    correct = 0
    correctval = 0
    selected = [1,2,4] #some boards have moves that are tied in value
    for i in selected:
      board = bigboards[i]
      try:
        color = 2
        (move, value) = stu_solution.minimax_max_node(board, color, 1, 0)
        answer = answers[i][0]
        answer_value = answers[i][1]

        if (answer[0] == move[0] and answer[1] == move[1]):
          correct+=1
        if (answer_value == value):
          correctval+=1      
      except TO_exc:
          details.add("Got TIMEOUT during problem {} when testing test_minimax_max_node_2".format(i))
      except:
          details.add("A runtime error occurred while testing test_minimax_max_node_2: %r" % traceback.format_exc())

    details.add("Test 2: You computed correct minimax max moves for {} of {} boards".format(correct, len(selected))) 
    details.add("Test 2: You computed correct minimax max values for {} of {} boards".format(correctval, len(selected))) 

    details = "\n".join(details)    
    return correct+correctval, details
