"""
An AI player for Othello. 
"""

import random
import sys
import time
import math

# You can use the functions in othello_shared to write your AI
from othello_shared import find_lines, get_possible_moves, get_score, play_move

# Global variables for caching
min_cache = {}
max_cache = {}

def eprint(*args, **kwargs): #you can use this for debugging, as it will print to sterr and not stdout
    print(*args, file=sys.stderr, **kwargs)
    
# Method to compute utility value of terminal state
def compute_utility(board, color):
    p1_score, p2_score = get_score(board)
    if color == 1:
        return p1_score - p2_score
    else:
        return p2_score - p1_score

# Better heuristic value of board
def compute_heuristic(board, color): #not implemented, optional
    #IMPLEMENT
    return 0 #change this!

############ MINIMAX ###############################
def minimax_min_node(board, color, limit, caching = 0):
    # Return if depth limit is reached
    if limit == 0:
        return (None, compute_utility(board, color))
    
    # Return minimax value if caching is enabled
    if caching:
        if board in min_cache:
            return min_cache[board]

    opposite_color = 2 if (color == 1) else 1
    opposite_moves = get_possible_moves(board, opposite_color)

    # Return if terminal node is reached
    if not opposite_moves:
        return (None, compute_utility(board, color))

    min_move = None
    min_utility = math.inf

    for move in opposite_moves:
        new_board = play_move(board, opposite_color, move[0], move[1])
        utility = minimax_max_node(new_board, color, limit-1, caching)[1]

        # Update the move that minimizes utility
        if min_utility > utility:
            min_move = move
            min_utility = utility

    # Store minimax value if caching is enabled
    if caching:
        min_cache[board] = (min_move, min_utility)

    return (min_move, min_utility)

def minimax_max_node(board, color, limit, caching = 0): #returns highest possible utility
    # Return if depth limit is reached
    if limit == 0:
        return (None, compute_utility(board, color))
    
    # Return minimax value if caching is enabled
    if caching:
        if board in max_cache:
            return max_cache[board]

    moves = get_possible_moves(board, color)

    # Return if terminal node is reached
    if not moves:
        return (None, compute_utility(board, color))

    max_move = None
    max_utility = -math.inf

    for move in moves:
        new_board = play_move(board, color, move[0], move[1])
        utility = minimax_min_node(new_board, color, limit-1, caching)[1]

        # Update the move that maximizes utility
        if max_utility < utility:
            max_move = move
            max_utility = utility
    
    # Store minimax value if caching is enabled
    if caching:
        max_cache[board] = (max_move, max_utility)

    return (max_move, max_utility)

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
    return minimax_max_node(board, color, limit, caching)[0]

############ ALPHA-BETA PRUNING #####################
def alphabeta_min_node(board, color, alpha, beta, limit, caching = 0, ordering = 0):
    # Return if depth limit is reached
    if limit == 0:
        return (None, compute_utility(board, color))

    # Return minimax value if caching is enabled
    if caching:
        if board in min_cache:
            return min_cache[board]

    opposite_color = 2 if (color == 1) else 1
    opposite_moves = get_possible_moves(board, opposite_color)

    # Order moves in ascending order if ordering is enabled
    if ordering:
        ordering_func = lambda x: compute_utility(play_move(board, opposite_color, x[0], x[1]), color)
        opposite_moves.sort(key=ordering_func)

    # Return if terminal node is reached
    if not opposite_moves:
        return (None, compute_utility(board, color))

    min_move = None
    min_utility = math.inf

    for move in opposite_moves:
        new_board = play_move(board, opposite_color, move[0], move[1])
        utility = alphabeta_max_node(new_board, color, alpha, beta, limit-1, caching, ordering)[1]

        # Update the move that minimizes utility
        if min_utility > utility:
            min_move = move
            min_utility = utility

        # Update beta and cut nodes (beta cut) if necessary
        if beta > min_utility:
            beta = min_utility
            # Beta cut
            if beta <= alpha:
                break

    # Store minimax value if caching is enabled
    if caching:
        min_cache[board] = (min_move, min_utility)

    return (min_move, min_utility)

def alphabeta_max_node(board, color, alpha, beta, limit, caching = 0, ordering = 0):
    # Return if depth limit is reached
    if limit == 0:
        return (None, compute_utility(board, color))

    # Return minimax value if caching is enabled
    if caching:
        if board in max_cache:
            return max_cache[board]

    moves = get_possible_moves(board, color)

    # Order moves in descending order if ordering is enabled
    if ordering:
        ordering_func = lambda x: compute_utility(play_move(board, color, x[0], x[1]), color)
        moves.sort(key=ordering_func, reverse=True)

    # Return if terminal node is reached
    if not moves:
        return (None, compute_utility(board, color))

    max_move = None
    max_utility = -math.inf

    for move in moves:
        new_board = play_move(board, color, move[0], move[1])
        utility = alphabeta_min_node(new_board, color, alpha, beta, limit-1, caching, ordering)[1]

        # Update the move that maximizes utility
        if max_utility < utility:
            max_move = move
            max_utility = utility

        # Update alpha and cut nodes (alpha cut) if necessary
        if alpha < max_utility:
            alpha = max_utility
            if beta <= alpha:
                break

    # Store minimax value if caching is enabled
    if caching:
        max_cache[board] = (max_move, max_utility)

    return (max_move, max_utility)

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
    return alphabeta_max_node(board, color, -math.inf, math.inf, limit, caching, ordering)[0]

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
