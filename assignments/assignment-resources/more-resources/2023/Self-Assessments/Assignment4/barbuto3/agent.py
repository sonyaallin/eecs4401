"""
An AI player for Othello. 
"""

import random
import sys
import time
import numpy as np

cache = {}

# You can use the functions in othello_shared to write your AI
from othello_shared import find_lines, get_possible_moves, get_score, play_move

def eprint(*args, **kwargs): #you can use this for debugging, as it will print to sterr and not stdout
    print(*args, file=sys.stderr, **kwargs)
    
# Method to compute utility value of terminal state
def compute_utility(board, color):
    p1_count, p2_count = get_score(board)
    return (p2_count-p1_count) * (-1)**(color) # flip sign of result based on player color

# static weighting (near and at corners)
def get_heuristic_score(board):
    p1_count = 0
    p2_count = 0
    for i in range(len(board)):
        for j in range(len(board)):
            if board[i][j] == 1:
                p1_count += 1
            elif board[i][j] == 2:
                p2_count += 1

    n = len(board)
    # corners are 'GOOD'
    corners = [board[0][0], board[0][n-1], board[n-1][0], board[n-1][n-1]]
    for c in corners:
        if c == 1: p1_count += 4
        elif c == 2: p2_count += 4

    # cells diagonally adjacent to corner are 'BAD'
    diag_adj_corners = [board[1][1], board[1][n-2], board[n-2][1], board[n-2][n-2]]
    for c in diag_adj_corners:
        if c == 1: p2_count += 4 
        elif c == 2: p1_count += 4

    # cells directly adjacent to cornerns are usually 'BAD'
    diag_adj_corners = [board[0][1], board[1][0], board[1][n-1], board[0][n-2], board[n-2][0], board[n-1][1], board[n-1][n-2], board[n-2][n-1]]
    for c in diag_adj_corners:
        if c == 1: p2_count += 2 
        elif c == 2: p1_count += 2
    return p1_count, p2_count

# Better heuristic value of board
def compute_heuristic(board, color): #not implemented, optional
    p1_count, p2_count = get_heuristic_score(board)
    return (p2_count-p1_count) * (-1)**(color) # flip sign of result based on player color

############ MINIMAX ###############################
def minimax_min_node(board, color, limit, caching = 0):
    # check if current board cached
    if caching and board in cache: return cache[board]

    opponent_color = (color % 2) + 1 # opponent
    moves = get_possible_moves(board, opponent_color)
    if not moves or limit==0: # terminal state
        return None, compute_utility(board, color)

    best_move, best_util = None, float('Inf')
    for row, col in moves:
        # simulate opponent playing the move
        result_board = play_move(board, opponent_color, row, col)

        # update util
        m, util = minimax_max_node(result_board, color, limit-1, caching)
        if caching: cache[result_board] = (row, col), util # add to cache
        if util < best_util:
            best_move, best_util = (row, col), util

    return best_move, best_util

def minimax_max_node(board, color, limit, caching = 0): #returns highest possible utility
    # check if current board cached
    if caching and board in cache: return cache[board]

    moves = get_possible_moves(board, color)
    if not moves or limit==0: # terminal state
        return None, compute_utility(board, color)
        
    best_move, best_util = None, float('-Inf')
    for row, col in moves:
        # simulate playing the move
        result_board = play_move(board, color, row, col)

        # update util
        m, util = minimax_min_node(result_board, color, limit-1, caching)
        if caching: cache[result_board] = (row, col), util # add to cache
        if util > best_util:
            best_move, best_util = (row, col), util

    return best_move, best_util

def select_move_minimax(board, color, limit, caching = 0):
    """
    Given a board and a player color, decide on a move. 
    The return value is a tuple of integers (i,j), where
    i is the column and j is the row on the board.  

    Note that other parameters are accepted by this function:
    If limit is a positive integer, your code should enfoce a depth limit that is equal to the value of the parameter.
    Search only to nodes at a depth-limit equal to the limit.  If nodes at this level are non-terminal return a heuristic 
    value (see compute_utility)
    If caching is ON (i.e. 1), use state caching to reduce the number of state evaluations.
    If caching is OFF (i.e. 0), do NOT use state caching to reduce the number of state evaluations.    
    """

    move, utility = minimax_max_node(board, color, limit, caching)
    return move

############ ALPHA-BETA PRUNING #####################
def alphabeta_min_node(board, color, alpha, beta, limit, caching = 0, ordering = 0):
    # check if current board cached
    if caching and board in cache: return cache[board]
    
    opponent_color = (color % 2) + 1 # opponent
    moves = get_possible_moves(board, opponent_color)
    if not moves or limit == 0: # terminal state
        return None, compute_utility(board, color)

    best_move = None
    if ordering:
        # order moves by utility in non-increasing order (i.e. explore 'promising' paths first)
        moves.sort(key=(lambda m : compute_utility( play_move(board, opponent_color, m[0], m[1]), opponent_color )), reverse=True)
    for row, col in moves:
        # simulate opponent playing the move
        result_board = play_move(board, opponent_color, row, col)

        # update beta, check if needs pruning
        m, util = alphabeta_max_node(result_board, color, alpha, beta, limit-1, caching, ordering)
        if caching: cache[result_board] = (row, col), util # add to cache
        if util < beta:
            best_move, beta = (row, col), util
        if alpha >= beta: # pruning condition
            break
    return best_move, beta

def alphabeta_max_node(board, color, alpha, beta, limit, caching = 0, ordering = 0):
    # check if current board cached
    if caching and board in cache: return cache[board]
    
    moves = get_possible_moves(board, color)
    if not moves or limit == 0: # terminal state
        return None, compute_utility(board, color)

    best_move = None
    if ordering:
        # order moves by utility in non-increasing order (i.e. explore 'promising' paths first)
        moves.sort(key=(lambda m : compute_utility( play_move(board, color, m[0], m[1]), color )), reverse=True)
    for row, col in moves:
        # simulate playing the move
        result_board = play_move(board, color, row, col)

        # update alpha, check if needs pruning
        m, util = alphabeta_min_node(result_board, color, alpha, beta, limit-1, caching, ordering)
        if caching: cache[result_board] = (row, col), util # add to cache
        if util > alpha:
            best_move, alpha = (row, col), util
        if alpha >= beta: # pruning condition
            break
    return best_move, alpha

def select_move_alphabeta(board, color, limit, caching = 0, ordering = 0):
    """
    Given a board and a player color, decide on a move. 
    The return value is a tuple of integers (i,j), where
    i is the column and j is the row on the board.  

    Note that other parameters are accepted by this function:
    If limit is a positive integer, your code should enfoce a depth limit that is equal to the value of the parameter.
    Search only to nodes at a depth-limit equal to the limit.  If nodes at this level are non-terminal return a heuristic 
    value (see compute_utility)
    If caching is ON (i.e. 1), use state caching to reduce the number of state evaluations.
    If caching is OFF (i.e. 0), do NOT use state caching to reduce the number of state evaluations.    
    If ordering is ON (i.e. 1), use node ordering to expedite pruning and reduce the number of state evaluations. 
    If ordering is OFF (i.e. 0), do NOT use node ordering to expedite pruning and reduce the number of state evaluations. 
    """
    move, utility = alphabeta_max_node(board, color, float("-Inf"), float("Inf"), limit, caching, ordering)
    return move

####################################################
def run_ai():
    """
    This function establishes communication with the game manager.
    It first introduces itself and receives its color.
    Then it repeatedly receives the current score and current board state
    until the game is over.
    """
    print("Othello AI") # First line is the name of this AI
    arguments = input().split(",")
    
    color = int(arguments[0]) #Player color: 1 for dark (goes first), 2 for light. 
    limit = int(arguments[1]) #Depth limit
    minimax = int(arguments[2]) #Minimax or alpha beta
    caching = int(arguments[3]) #Caching 
    ordering = int(arguments[4]) #Node-ordering (for alpha-beta only)

    if (minimax == 1): eprint("Running MINIMAX")
    else: eprint("Running ALPHA-BETA")

    if (caching == 1): eprint("State Caching is ON")
    else: eprint("State Caching is OFF")

    if (ordering == 1): eprint("Node Ordering is ON")
    else: eprint("Node Ordering is OFF")

    if (limit == -1): eprint("Depth Limit is OFF")
    else: eprint("Depth Limit is ", limit)

    if (minimax == 1 and ordering == 1): eprint("Node Ordering should have no impact on Minimax")

    while True: # This is the main loop
        # Read in the current game status, for example:
        # "SCORE 2 2" or "FINAL 33 31" if the game is over.
        # The first number is the score for player 1 (dark), the second for player 2 (light)
        next_input = input()
        status, dark_score_s, light_score_s = next_input.strip().split()
        dark_score = int(dark_score_s)
        light_score = int(light_score_s)

        if status == "FINAL": # Game is over.
            print
        else:
            board = eval(input()) # Read in the input and turn it into a Python
                                  # object. The format is a list of rows. The
                                  # squares in each row are represented by
                                  # 0 : empty square
                                  # 1 : dark disk (player 1)
                                  # 2 : light disk (player 2)

            # Select the move and send it to the manager
            if (minimax == 1): #run this if the minimax flag is given
                movei, movej = select_move_minimax(board, color, limit, caching)
            else: #else run alphabeta
                movei, movej = select_move_alphabeta(board, color, limit, caching, ordering)
            
            print("{} {}".format(movei, movej))

if __name__ == "__main__":
    run_ai()
