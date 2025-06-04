"""
An AI player for Othello. 
"""

import random
import sys
import time

# You can use the functions in othello_shared to write your AI
from othello_shared import find_lines, get_possible_moves, get_score, play_move

def eprint(*args, **kwargs): #you can use this for debugging, as it will print to sterr and not stdout
    print(*args, file=sys.stderr, **kwargs)
    
# Method to compute utility value of terminal state
def compute_utility(board, color):
    score = get_score(board)
    if color == 1:
        return score[0] - score[1]
    else:
        return score[1] - score[0]

# Better heuristic value of board
def compute_heuristic(board, color): #not implemented, optional
    #IMPLEMENT
    return 0 #change this!

############ MINIMAX ###############################
minimax_min_cache = dict()
minimax_max_cache = dict()
def minimax_min_node(board, color, limit, caching = 0):
    #IMPLEMENT (and replace the line below)
    if caching != 0:
        if minimax_min_cache.get(board) is not None:
            return minimax_min_cache[board]
    next_player = 1
    if color == 1:
        next_player = 2
    
    # get all possible moves from the next player
    possible_moves = get_possible_moves(board, next_player)
    # TERMINAL
    if possible_moves == [] or limit == 0:
        return (None, compute_utility(board, color))

    min_util = float("inf")
    min_move = None
    for move in possible_moves:
        next_board = play_move(board, next_player, move[0], move[1])
        _, util = minimax_max_node(next_board, color, limit-1, caching)
        if util < min_util:
            min_util = util
            min_move = move
    
    if caching != 0:
        minimax_min_cache[board] = (min_move, min_util)
        
    return (min_move, min_util)

def minimax_max_node(board, color, limit, caching = 0): #returns highest possible utility
    #IMPLEMENT (and replace the line below)
    if caching != 0:
        if minimax_max_cache.get(board) is not None:
            return minimax_max_cache[board]
    
    
    # get all possible moves from the current player
    possible_moves = get_possible_moves(board, color)
    # TERMINAL
    if possible_moves == [] or limit == 0:
        return (None, compute_utility(board, color))

    max_util = -float("inf")
    max_move = None
    for move in possible_moves:
        next_board = play_move(board, color, move[0], move[1])
        _, util = minimax_min_node(next_board, color, limit-1, caching)
        if util > max_util:
            max_util = util
            max_move = move
    if caching != 0:
        minimax_max_cache[board] = (max_move, max_util)
    
    return (max_move, max_util)

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
    #IMPLEMENT (and replace the line below)
    minimax_min_cache.clear()
    minimax_max_cache.clear()
    return minimax_max_node(board, color, limit, caching)[0]

############ ALPHA-BETA PRUNING #####################
alphabeta_min_cache = dict()
alphabeta_max_cache = dict()
def alphabeta_min_node(board, color, alpha, beta, limit, caching = 0, ordering = 0):
    if caching != 0:
        if alphabeta_min_cache.get(board) is not None:
            return alphabeta_min_cache[board]
        
    next_player = 1
    if color == 1:
        next_player = 2
    
    # get all possible moves from the current player
    possible_moves = get_possible_moves(board, next_player)
    # TERMINAL
    if possible_moves == [] or limit == 0:
        return (None, compute_utility(board, color))

    min_util = float("inf")
    min_move = None
    
    # ordering
    if ordering != 0:
        temp_sort = []
        for move in possible_moves:
            next_board = play_move(board, next_player, move[0], move[1])
            temp_sort.append((move, compute_utility(next_board, next_player)))
        temp_sort.sort(key = lambda tup: tup[1], reverse=True)
        possible_moves = []
        for sorted in temp_sort:
            possible_moves.append(sorted[0])
    
    for move in possible_moves:
        next_board = play_move(board, next_player, move[0], move[1])
        _, util = alphabeta_max_node(next_board, color, alpha, beta, limit-1, caching, ordering)
        if util < min_util:
            min_util = util
            min_move = move
        beta = min(min_util, beta)
        if beta <= alpha:
            return (min_move, min_util)
    
    if caching != 0:
        alphabeta_min_cache[board] = (min_move, min_util)

    return (min_move, min_util)

def alphabeta_max_node(board, color, alpha, beta, limit, caching = 0, ordering = 0):
    if caching != 0:
        if alphabeta_max_cache.get(board) is not None:
            return alphabeta_max_cache[board]
    
    # get all possible moves from the current player
    possible_moves = get_possible_moves(board, color)
    # TERMINAL
    if possible_moves == [] or limit == 0:
        return (None, compute_utility(board, color))

    max_util = -float("inf")
    max_move = None
    
    # ordering
    if ordering != 0:
        temp_sort = []
        for move in possible_moves:
            next_board = play_move(board, color, move[0], move[1])
            temp_sort.append((move, compute_utility(next_board, color)))
        temp_sort.sort(key = lambda tup: tup[1], reverse=True)
        possible_moves = []
        for sorted in temp_sort:
            possible_moves.append(sorted[0])
    
    for move in possible_moves:
        next_board = play_move(board, color, move[0], move[1])
        _, util = alphabeta_min_node(next_board, color, alpha, beta, limit-1, caching, ordering)
        if util > max_util:
            max_util = util
            max_move = move
        beta = max(max_util, beta)
        if beta <= alpha:
            return (max_move, max_util)
    
    if caching != 0:
        alphabeta_max_cache[board] = (max_move, max_util)

    return (max_move, max_util)

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
    #IMPLEMENT (and replace the line below)
    alphabeta_min_cache.clear()
    alphabeta_max_cache.clear()
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
