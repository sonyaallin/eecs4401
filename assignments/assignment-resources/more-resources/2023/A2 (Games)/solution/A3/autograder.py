#!/usr/bin/env python
import os  # for time functions
import pickle #to read test states

# import student's functions
from agent_solution import *

#Select what to test
test_compute_utility = True
test_select_move_minimax = True
test_select_move_alphabeta = True
test_select_move_equal = True
test_caching_ab = True
test_caching_mm = True
test_ucb = True

# load the test problems
boards = []
with (open("boards_student.pickle", "rb")) as openfile:
    while True:
        try:
            boards.append(pickle.load(openfile))
        except EOFError:
            break

mc_boards, trees, sols = [], [], []
with (open("ucb.pickle", "rb")) as openfile:
    while True:
        try:
            mc_boards.append(pickle.load(openfile))
            trees.append(pickle.load(openfile))
            sols.append(pickle.load(openfile))
        except EOFError:
            break

def test_caching_mm_fun():

    print('Testing Caching')
    check_1 = 0
    check_2 = 0
    for i in range(0, len(boards)):

        start_time_1 = os.times()[0]
        no_cache = select_move_minimax(boards[i], 1, 6)
        end_time_1 = os.times()[0]

        start_time_2 = os.times()[0]
        with_cache = select_move_minimax(boards[i], 1, 6, True)
        end_time_2 = os.times()[0]

        if (end_time_1 - start_time_1) >= (end_time_2 - start_time_2):
            check_1 += 1

        if (with_cache == no_cache):
            check_2 += 1

    print("State caching improved the time of your minimax for {} of {} boards".format(check_1, len(boards)))
    print("Move choice with and without caching is the same for {} of {} boards".format(check_2, len(boards)))
    print("******************************************************************")

def test_caching_ab_fun():

    print('Testing Caching')
    check_1, check_2, check_3 = 0, 0, 0
    for i in range(0, len(boards)):

        start_time_1 = os.times()[0]
        no_cache, n_cuts = select_move_alphabeta(boards[i], 1, 6)
        end_time_1 = os.times()[0]

        start_time_2 = os.times()[0]
        with_cache, c_cuts = select_move_alphabeta(boards[i], 1, 6, True)
        end_time_2 = os.times()[0]

        if (end_time_1 - start_time_1) >= (end_time_2 - start_time_2):
            check_1 += 1

        if (with_cache == no_cache):
            check_2 += 1

        if (n_cuts >= c_cuts):
            check_3 += 1

    print("State caching improved the time of your alpha-beta for {} of {} boards".format(check_1, len(boards)))
    print("Move choice with and without caching is the same for {} of {} boards".format(check_2, len(boards)))
    print("Number of AB-cuts with and without caching is decreasing for {} of {} boards".format(check_3, len(boards)))
    print("******************************************************************")

def test_compute_utility_fun():

    ##############################################################
    print('Testing Utility')
    correctvalues = [1, 1, 2, 2, 6, 6, 11, 10, 11, 12, 14, 15, 16, 17, 18, 17, 14, 25, 26, 9]
    correct = 0
    for i in range(0,len(boards)):
      board = boards[i]
      value1 = compute_utility(board, 0)
      value2 = compute_utility(board, 1)
      if (value1 == correctvalues[i] and value2 == correctvalues[i]*-1):
        correct+=1  

    print("You computed correct utilities for {} of {} boards".format(correct, len(correctvalues)))
    print("******************************************************************")

def test_select_move_minimax_fun():
    correctmoves_1 = [2, 1, 2, 4, 0, 7, 7, 5, 1, 6, 2, 3, 2, 7, 3, 4, 3, 0, 7, 3]
    correctmoves_2 = [6, 3, 3, 0, 5, 7, 4, 3, 7, 5, 7, 3, 0, 6, 2, 4, 2, 1, 1, 2]
    correct = 0
    v1 = []
    v2 = []
    for i in range(0,len(boards)):
      board = boards[i]
      value1 = select_move_minimax(board, 0, 5)
      value2 = select_move_minimax(board, 1, 5)
      v1.append(value1)
      v2.append(value2)
      if (value1 == correctmoves_1[i] and value2 == correctmoves_2[i]):
        correct+=1  
    print('Testing Minimax (with Depth Limit of 5)')
    print("You computed correct minimax moves for {} of {} boards".format(correct, len(correctmoves_1)))
    print("******************************************************************")

def test_select_move_alphabeta_fun():
    correctmoves_1 = [2, 1, 2, 4, 0, 7, 7, 5, 1, 6, 2, 3, 2, 7, 3, 4, 3, 0, 7, 3]
    correctmoves_2 = [6, 3, 3, 0, 5, 7, 4, 3, 7, 5, 7, 3, 0, 6, 2, 4, 2, 1, 1, 2]
    correct = 0
    v1 = []
    v2 = []
    for i in range(0,len(boards)):
      board = boards[i]
      value1, cuts = select_move_alphabeta(board, 0, 5)
      value2, cuts = select_move_alphabeta(board, 1, 5)
      v1.append(value1)
      v2.append(value2)
      if (value1 == correctmoves_1[i] and value2 == correctmoves_2[i]):
        correct+=1
    print('Testing Alphabeta (with Depth Limit of 5)')
    print("You computed correct alphabeta moves for {} of {} boards".format(correct, len(correctmoves_1)))
    print("******************************************************************")

def test_select_move_equal_fun():
    correctmoves_1 = [2, 1, 2, 4, 0, 7, 7, 5, 1, 6, 2, 3, 2, 7, 3, 4, 3, 0, 7, 3]
    correctmoves_2 = [6, 3, 3, 0, 5, 7, 4, 3, 7, 5, 7, 3, 0, 6, 2, 4, 2, 1, 1, 2]

    correct = 0
    for i in range(0, len(correctmoves_1)):
      board = boards[i]
      value1_minimax = select_move_minimax(board, 0, 5)
      value2_minimax = select_move_minimax(board, 1, 5)
      value1_ab, cuts = select_move_alphabeta(board, 0, 5)
      value2_ab, cuts = select_move_alphabeta(board, 1, 5)

      if (value1_minimax == value1_ab == correctmoves_1[i] and value2_minimax == value2_ab == correctmoves_2[i]):
       correct+=1

    print('Testing Minimax and Alphabeta Moves Equality (with Depth Limit of 5)')
    print("You computed correct moves for {} of {} tests".format(correct, len(correctmoves_1)))
    print("******************************************************************")

def test_ucb_fun():
    correct, total = 0, 0
    for i in range(0, len(sols),14):
        test_sol = uct_select(mc_boards[i], trees[i])
        if test_sol == sols[i]:
            correct +=1
        total += 1

    print('Testing UCB calculations')
    print("You computed correct UCB values for {} of {} tests".format(correct, total))
    print("******************************************************************")

def test_all():
    if test_compute_utility: test_compute_utility_fun()
    if test_select_move_minimax: test_select_move_minimax_fun()
    if test_select_move_alphabeta: test_select_move_alphabeta_fun()
    if test_select_move_equal: test_select_move_equal_fun()
    if test_caching_ab: test_caching_ab_fun()
    if test_caching_ab: test_caching_mm_fun()
    if test_ucb: test_ucb_fun()

if __name__=='__main__':
    test_all()

