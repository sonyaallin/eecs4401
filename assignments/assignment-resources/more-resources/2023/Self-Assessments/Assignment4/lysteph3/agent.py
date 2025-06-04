"""
An AI player for Othello. 
"""

import random
import sys
import time
import math
from wsgiref import util

# You can use the functions in othello_shared to write your AI
from othello_shared import find_lines, get_possible_moves, get_score, play_move

"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ Description for my Heuristic ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    For my heuristic, I decided that I wanted to compute the immediate moves that were possible on that board 
state and compare it with the opponents immediate moves, and also compare the number of corner spaces that the
board state had included. The goal of my heuristic is to compare the mobilities of each board state, since the
mobility of each player is a great predictor of who has more board control at the moment, and can also greatly
influence the amount of disks that could be claimed by the player. Furthermore, I also wanted to compare the 
number of corner pieces that the board state had. The reasoning for this is because corner pieces are the most
"stable" position in the board. This is because no other disk is able to claim that piece, since it cannot be
cornered. Hence I thought that comparing the number of corner pieces would be a good metric to compare the "good-
-ness of the board". I then added these two computations with compute_utility's return value, to get the value of
the "goodness".
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
"""

cached_moves_min = {}
cached_moves_max = {}

def eprint(*args, **kwargs): #you can use this for debugging, as it will print to sterr and not stdout
    print(*args, file=sys.stderr, **kwargs)
    
# Method to compute utility value of terminal state
def compute_utility(board, color):
    if color == 1:
        return get_score(board)[0] - get_score(board)[1]
    elif color == 2:
        return get_score(board)[1] - get_score(board)[0]


def _count_corners(board, color):
    count = 0
    if board[0][0] == color: count += 1
    if board[(len(board)-1)][0] == color: count += 1
    if board[len(board)-1][len(board[0])-1] == color: count += 1
    if board[0][len(board[0]) - 1] == color: count += 1
    return count

# Better heuristic value of board
def compute_heuristic(board, color): #not implemented, optional
    
    player_possible = get_possible_moves(board, color)
    other_possible = get_possible_moves(board, _otherplayer(color))
    
    # Mobility Heuristic
    
    mobility_heur = len(get_possible_moves(board, color)) - len(get_possible_moves(board, _otherplayer(color)))

    # Corner Heuristic
    
    corner_heur = _count_corners(board, color) - _count_corners(board, _otherplayer(color))
    
    return compute_utility(board,color) + corner_heur + mobility_heur

############ MINIMAX ###############################
def _otherplayer(color):
    return 1 if color == 2 else 2        

def minimax_min_node(board, color, limit, caching = 0):

    global cached_moves_min
    
    key = hash(board)
    if caching and key in cached_moves_min: 
        return cached_moves_min[key]

    if limit <= 0:
        return None, compute_utility(board, color)
        
    possible_moves = get_possible_moves(board, _otherplayer(color))
    
    if possible_moves == []: # terminal state
        utility = compute_utility(board, color)
        if caching: cached_moves_min[key] = None, utility
        return None, utility
    
    running_best_utility = math.inf
    running_best_move = None
    
    for move in possible_moves:
        board_after = play_move(board, _otherplayer(color), move[0], move[1])
        new_move, utility = minimax_max_node(board_after, color, limit - 1, caching)
        if running_best_utility > utility:
            running_best_utility = utility
            running_best_move = move
    
    if caching: cached_moves_min[key] = running_best_move, running_best_utility
    return running_best_move, running_best_utility


def minimax_max_node(board, color, limit, caching = 0): #returns highest possible utility
    
    global cached_moves_max
    
    key = hash(board)
    if caching and key in cached_moves_max: 
        return cached_moves_max[key]

    if limit <= 0:
        return None, compute_utility(board, (color))

    possible_moves = get_possible_moves(board, color)
    
    if possible_moves == []: # terminal state
        utility = compute_utility(board, color)
        if caching: cached_moves_max[key] = None, utility
        return None, utility
    
    running_best_utility = -math.inf
    running_best_move = None
    
    for move in possible_moves:
        board_after = play_move(board, color, move[0], move[1])
        new_move, utility = minimax_min_node(board_after, color, limit - 1, caching)
        if running_best_utility < utility:
            running_best_utility = utility
            running_best_move = move
    if caching: cached_moves_max[key] = running_best_move, running_best_utility
    return running_best_move, running_best_utility
    
                
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
    global cached_moves_max, cached_moves_min
    if caching: cached_moves_max, cached_moves_min = {}, {}
    return minimax_max_node(board, color,limit,caching)[0]

############ ALPHA-BETA PRUNING #####################
def alphabeta_min_node(board, color, alpha, beta, limit, caching = 0, ordering = 0):
    
    global cached_moves_min
    
    key = hash(board)
    if caching and key in cached_moves_min: 
        return cached_moves_min[key]

    if limit <= 0:
        return None, compute_utility(board, color)
        
    possible_moves = get_possible_moves(board, _otherplayer(color))
    
    if possible_moves == []: # terminal state
        utility = compute_utility(board, color)
        if caching: cached_moves_min[key] = None, utility
        return None, utility
    
    if ordering: possible_moves = sorted(possible_moves, key = lambda move: 
        compute_utility(board, color) - 
        sum(len(line) for line in find_lines(board, move[0], move[1], _otherplayer(color))) * 2
        - 1)
    
    running_best_utility = math.inf
    running_best_move = None
    
    for move in possible_moves:
        board_after = play_move(board, _otherplayer(color), move[0], move[1])
        new_move, utility = alphabeta_max_node(board_after, color, alpha, beta, limit - 1, caching, ordering )
        if running_best_utility > utility:
            running_best_utility = utility
            running_best_move = move
    
        if running_best_utility < beta:
            beta = running_best_utility
            if beta <= alpha: break
    
    if caching: cached_moves_min[key] = running_best_move, running_best_utility
    return running_best_move, running_best_utility

def alphabeta_max_node(board, color, alpha, beta, limit, caching = 0, ordering = 0):
    
    global cached_moves_max
    
    key = hash(board)
    if caching and key in cached_moves_max: 
        return cached_moves_max[key]

    if limit <= 0:
        return None, compute_utility(board, (color))

    possible_moves = get_possible_moves(board, color)
    
    if possible_moves == []: # terminal state
        utility = compute_utility(board, color)
        if caching: cached_moves_max[key] = None, utility
        return None, utility
    
    if ordering: possible_moves = sorted(possible_moves, key = lambda move: 
        compute_utility(board, color) + 
        sum(len(line) for line in find_lines(board, move[0], move[1], color)) * 2
        + 1, 
        reverse=True)
    
    running_best_utility = -math.inf
    running_best_move = None
    
    for move in possible_moves:
        board_after = play_move(board, color, move[0], move[1])
        new_move, utility = alphabeta_min_node(board_after, color, alpha, beta, limit - 1, caching, ordering)
        if running_best_utility < utility:
            running_best_utility = utility
            running_best_move = move
        
        if running_best_utility > alpha:
            alpha = running_best_utility
            if beta <= alpha: break
        
    if caching: cached_moves_max[key] = running_best_move, running_best_utility
    return running_best_move, running_best_utility
    

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

    global cached_moves_max, cached_moves_min
    if caching: cached_moves_max, cached_moves_min = {}, {}
    return alphabeta_max_node(board, color, -math.inf, math.inf, limit,caching, ordering)[0]
    

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
