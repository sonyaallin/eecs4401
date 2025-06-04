"""
An AI player for Othello. 
"""

import random
import pickle
import math
import time
import sys

# You can use the functions in mancala_game to write your AI
from mancala_game import Board, get_possible_moves, eprint, play_move, MCTS
from agent import compute_heuristic

cache = {} #use this for state caching

def eprint(*args, **kwargs): #use this for debugging, to print to sterr
    print(*args, file=sys.stderr, **kwargs)
    
# Method to compute utility value of board
def compute_utility(board, side):
    return board.mancalas[1] - board.mancalas[0] if side == 1 else board.mancalas[0] - board.mancalas[1]

################### MINIMAX METHODS ####################
def minimax_selection_TA(board, color, MAX, limit, caching = False, heur = False):

    #for debugging
    global counter
    if counter > CUTOFF: return None, compute_utility(board, MAX) #for debugging
    counter += 1

    opponent = 0 if color == 1 else 1

    # Get the allowed moves
    all_moves = get_possible_moves(board, color)

    # If there are no moves left, return the utility
    if len(all_moves) == 0 or limit == 0:  # If s is TERMINAL
        if (heur):
            return None, compute_utility(board, MAX), 0  # Return terminal state's utility according to MAX
        else:
            return None, compute_heuristic(board, MAX), 0  # Return terminal state's utility according to MAX


    # Else if there are moves, get their utility and return the min
    ut_val = float("-Inf") if color == MAX else float("Inf")
    move, best_move = None, None
    limit -= 1

    # Get the utility of all the moves
    for each in all_moves:  # ChildList = s.Successors(Player)

        # Get the next board from that move and add the moves to the list
        next_board = play_move(board, color, each)

        #if already in the cache, use the value
        if caching and (next_board, color) in cache:
            move, value = cache[(next_board, color)]
            #eprint("Saw the same state twice")
        else:
            move, value = minimax_selection(next_board, opponent, MAX, limit, caching)
            cache[(next_board, color)] = (move, value)

        #move, value = minimax_selection(next_board, opponent, MAX, limit)
        if (CUTOFF < float('inf')): eprint("each, move choice, value, ut_val -> {}, {} {} {}".format(each, move, value, ut_val))

        if color == MAX and value > ut_val:
            if (CUTOFF < float('inf')): eprint("in MAX update, best move is {}".format(each))
            ut_val = value
            best_move = each
        elif color != MAX and value < ut_val:
            if (CUTOFF < float('inf')): eprint("in MIN update")
            ut_val = value
            best_move = each

    if (CUTOFF < float('inf')): eprint("{} board -> {} {}, color {}, moves {}, move selected {} value {}. Currently at limit {}".format(counter, board.mancalas, board.pockets, color, all_moves, best_move, ut_val, limit))
    return best_move, ut_val

def select_move_minimax(board, color, limit=-1, caching = False):
    #eprint("in minimax, maximizer is {}".format(color))

    # Get the best move according to the max utility
    move, utility = minimax_selection(board, color, color, limit, caching)

    return move

################### ALPHA-BETA METHODS ####################
def alphabeta_selection(board, color, MAX, alpha, beta, limit, caching = False, heur = False):

    #for debugging
    # global counter
    # if counter > CUTOFF:
    #     return None, compute_utility(board, MAX)
    # counter += 1

    opponent = 0 if color == 1 else 1    

    # Get the allowed moves
    all_moves = get_possible_moves(board, color)

    # If there are no moves left, return the utility
    if len(all_moves) == 0 or limit == 0:  # If s is TERMINAL
        if (heur):
            return None, compute_utility(board, MAX), 0  # Return terminal state's utility according to MAX
        else:
            return None, compute_heuristic(board, MAX), 0  # Return terminal state's utility according to MAX


    # Else if there are moves, get their utility and return the min
    ut_val = float("-Inf") if color == MAX else float("Inf")
    move, best_move = None, None
    limit -= 1

    # Get the utility of all the moves
    numcuts = 0
    for each in all_moves:  # ChildList = s.Successors(Player)
        # Get the next board from that move and add the moves to the list
        next_board = play_move(board, color, each)

        #if already in the cache, use the value
        if caching and (next_board, color) in cache:
            move, value = cache[(next_board, color)]
        else:
            move, value, cuts = alphabeta_selection(next_board, opponent, MAX, alpha, beta, limit, caching)
            numcuts += cuts
            cache[(next_board, color)] = (move, value)

        #if (CUTOFF < float('inf')): eprint("each, move choice, value, ut_val -> {}, {} {} {} {} {}".format(each, move, value, ut_val, alpha, beta))

        if color == MAX and value > ut_val:
            #if (CUTOFF < float('inf')): eprint("in MAX update, best move is {}".format(each))
            ut_val = value
            best_move = each
            if alpha < ut_val:
                numcuts += 1
                alpha = ut_val
                if beta <= alpha: break
        if color != MAX and value < ut_val:
            #if (CUTOFF < float('inf')): eprint("in MIN update")
            ut_val = value
            best_move = each
            if beta > ut_val:
                numcuts += 1
                beta = ut_val
                if beta <= alpha: break

    #if (CUTOFF < float('inf')): eprint("{} board -> {} {}, color {}, moves {}, move selected {} value {}. Currently at limit {}, alpha {} beta {}".format(counter, board.mancalas, board.pockets, color, all_moves, best_move, ut_val, limit, alpha, beta))
    return best_move, ut_val, numcuts

def select_move_alphabeta_TA(board, color, limit=-1, caching = False):

    eprint("TA COLOR" + str(color))
    alpha = float("-Inf")
    beta = float("Inf")
    move, utility, num_cuts = alphabeta_selection(board, color, color, alpha, beta, limit, caching)
    return move

####################################################
def run_ai():
    """
    This function establishes communication with the game manager.
    It first introduces itself and receives its color.
    Then it repeatedly receives the current score and current board state
    until the game is over.
    """
    print("Default AI") # First line is the name of this AI
    arguments = input().split(",")
    
    color = int(arguments[0]) #Player color: 1 for dark (goes first), 2 for light. 
    limit = int(arguments[1]) #Depth limit
    minimax = 0
    caching = 0

    if (minimax == 1): eprint("Running MINIMAX")
    else: eprint("Running ALPHA-BETA")

    if (caching == 1): eprint("State Caching is ON")
    else: eprint("State Caching is OFF")

    if (limit == -1): eprint("Depth Limit is OFF")
    else: eprint("Depth Limit is ", limit)

    while True:  # This is the main loop
        # Read in the current game status, for example:
        # "SCORE 2 2" or "FINAL 33 31" if the game is over.
        # The first number is the score for player 1 (dark), the second for player 2 (light)
        next_input = input()
        status, dark_score_s, light_score_s, pockets, mancalas = next_input.strip().split("|")
        pockets = eval(pockets)
        mancalas = eval(mancalas)
        
        if status == "FINAL":  # Game is over.
            print
        else:
            board = Board(pockets, mancalas)

            # Select the move and send it to the manager
            move = select_move_alphabeta_TA(board, color, limit, caching)
            if isinstance(move, tuple) or isinstance(move,list):
                move = move[0]

        eprint("TA MOVE {}".format(move))
        print("{}".format(move))

if __name__ == "__main__":
    run_ai()
