"""
An AI player for Othello. 
"""

import random
import sys
import time
import numpy as np

# You can use the functions in othello_shared to write your AI
from othello_shared import find_lines, get_possible_moves, get_score, play_move

# global variable
CACHE_MAX = {}
CACHE_MIN = {}

def eprint(*args, **kwargs): #you can use this for debugging, as it will print to sterr and not stdout
    print(*args, file=sys.stderr, **kwargs)

def opponent(color):
    """ Helper function: return an integer which represents opponent 
    """
    if color == 1:
        return 2
    else:
        return 1

def ordering_moves(board, moves, color):
    """ Helper function: Order 'moves' list based on utilities
    """
    utils = []
    for move in moves:
        new_board = play_move(board, color, *move)
        utils.append(compute_heuristic(new_board, 1))
    # if color == 1:
    #     new_moves = np.array(moves)[np.argsort(utils)[::-1]]
    # else:
    #     new_moves = np.array(moves)[np.argsort(utils)]
    new_moves = np.array(moves)[np.argsort(utils)[::-1]]
    return list(map(tuple, new_moves))
    
# Method to compute utility value of terminal state
def compute_utility(board, color):
    p1, p2 = get_score(board)
    if color == 1:
        return p1 - p2
    else:
        return p2 - p1

# Better heuristic value of board
def compute_heuristic(board, color):
    """ Heuristic function

    There are two main components to this heuristic function:

    1. Instead of counting the number of pieces on the board, I weighted 3 times more for 4 corners of the board. 
    This is mainly because corner peices are stable and have power to flip all pieces along the sides and diagonal line,
    meaning these pieces value much more than other pieces on the board.

    2. I consider the number of moves one can make given the current board configuration.
    """
    p1 = 0
    p2 = 0
    n = len(board)
    corners = [[0, 0], [0, n-1], [n-1, 0], [n-1, n-1]]
    for i in range(len(board)):
        for j in range(len(board)):
            # 4 corners of the board
            # 3 points
            if [i, j] in corners:
                if board[i][j] == 1:
                    p1 += 3
                elif board[i][j] == 2:
                    p2 += 3
            # otherwise
            # 1 point
            else:
                if board[i][j] == 1:
                    p1 += 1
                elif board[i][j] == 2:
                    p2 += 1

    # number of moves one can make given the current board
    p1 += len(get_possible_moves(board, 1))
    p2 += len(get_possible_moves(board, 2))

    if color == 1:
        return p1 - p2
    else:
        return p2 - p1

############ MINIMAX ###############################
def minimax_min_node(board, color, limit, caching = 0):
    # check for chache
    if caching and board in CACHE_MIN:
        return CACHE_MIN[board]

    # oppoonent
    opp = opponent(color)

    # obtain all possible next moves by opponent
    moves = get_possible_moves(board, opp)

    # terminal level
    if not moves or limit == 0:
        return (None, compute_utility(board, color))
    
    # non-terminal level
    best_move = None
    min_utility = float('inf')
    for move in moves:
        new_board = play_move(board, opp, *move)
        _, utility = minimax_max_node(new_board, color, limit-1, caching)
        if utility < min_utility:
            min_utility = utility
            best_move = move
        
        # add to cache
        if caching:
            CACHE_MIN[board] = (move, utility)

    return (best_move, min_utility)

def minimax_max_node(board, color, limit, caching = 0):
    # check for chache
    if caching and board in CACHE_MAX:
        return CACHE_MAX[board]

    # obtain all possible next moves
    moves = get_possible_moves(board, color)

    # terminal level
    if not moves or limit == 0:
        return (None, compute_utility(board, color))
    
    # non-terminal level
    best_move = None
    max_utility = -float('inf')
    for move in moves:
        new_board = play_move(board, color, *move)
        _, utility = minimax_min_node(new_board, color, limit-1, caching)
        if utility > max_utility:
            max_utility = utility
            best_move = move

        # add to cache
        if caching:
            CACHE_MAX[board] = (move, utility)
    
    return (best_move, max_utility)

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
    CACHE_MAX.clear()
    CACHE_MIN.clear()
    return minimax_max_node(board, color, limit, caching)[0]

############ ALPHA-BETA PRUNING #####################
def alphabeta_min_node(board, color, alpha, beta, limit, caching = 0, ordering = 0):
    # check for chache
    if caching and board in CACHE_MIN:
        return CACHE_MIN[board]
    
    # oppoonent
    opp = opponent(color)

    # obtain all possible next moves by opponent
    moves = get_possible_moves(board, opp)

    # terminal level
    if not moves or limit == 0:
        return (None, compute_utility(board, color))

    # ordering moves
    moves = ordering_moves(board, moves, opp)
    
    # non-terminal level
    best_move = None
    min_utility = float('inf')
    for move in moves:
        new_board = play_move(board, opp, *move)
        _, utility = alphabeta_max_node(new_board, color, alpha, beta, limit-1, caching, ordering)
        if utility < min_utility:
            min_utility = utility
            best_move = move

        # add to cache
        if caching:
            CACHE_MIN[board] = (move, utility)

        # check for pruning
        beta = min(beta, utility)
        if alpha >= beta:
            break

    return (best_move, min_utility)

def alphabeta_max_node(board, color, alpha, beta, limit, caching = 0, ordering = 0):
    # check for chache
    if caching and board in CACHE_MAX:
        return CACHE_MAX[board]
    
    # obtain all possible next moves
    moves = get_possible_moves(board, color)

    # terminal level
    if not moves or limit == 0:
        return (None, compute_utility(board, color))

    # ordering moves
    moves = ordering_moves(board, moves, color)
    
    # non-terminal level
    best_move = None
    max_utility = -float('inf')
    for move in moves:
        new_board = play_move(board, color, *move)
        _, utility = alphabeta_min_node(new_board, color, alpha, beta, limit-1, caching, ordering)
        if utility > max_utility:
            max_utility = utility
            best_move = move

        # add to cache
        if caching:
            CACHE_MAX[board] = (move, utility)
        
        # check for pruning
        alpha = max(alpha, utility)
        if alpha >= beta:
            break
    
    return (best_move, max_utility)

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
    CACHE_MAX.clear()
    CACHE_MIN.clear()
    return alphabeta_max_node(board, color, -float('inf'), float('inf'), limit, caching, ordering)[0]

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
