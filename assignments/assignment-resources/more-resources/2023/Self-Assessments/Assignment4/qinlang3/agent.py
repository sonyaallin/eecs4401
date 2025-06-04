"""
An AI player for Othello. 
"""

import random
import sys
import time

stat_dict = {}

# You can use the functions in othello_shared to write your AI
from othello_shared import find_lines, get_possible_moves, get_score, play_move

def eprint(*args, **kwargs): #you can use this for debugging, as it will print to sterr and not stdout
    print(*args, file=sys.stderr, **kwargs)
    
# Method to compute utility value of terminal state
def compute_utility(board, color):
    dark_count, light_count = get_score(board)
    if color == 1:  # dark
        return dark_count - light_count
    else:           # light
        return light_count - dark_count

# Better heuristic value of board
def compute_heuristic(board, color): #not implemented, optional
    #IMPLEMENT
    return 0 #change this!

############ MINIMAX ###############################
def minimax_min_node(board, color, limit, caching = 0):
    if caching and board in stat_dict:
        return stat_dict[board]
    if color == 1:
        opp = 2
    else:
        opp = 1
    moves = get_possible_moves(board, opp)
    if len(moves) == 0 or limit == 0:
        return None, compute_utility(board, color)
    opt_utility = float('inf')
    for m in moves:
        new_board = play_move(board, opp, m[0], m[1])
        move, utility = minimax_max_node(new_board, color, limit-1, caching)
        if caching:
            stat_dict[new_board] = (m, utility)
        if utility < opt_utility:
            opt_utility = utility
            opt_move = m
    return opt_move, opt_utility


def minimax_max_node(board, color, limit, caching = 0): #returns highest possible utility
    if caching and board in stat_dict:
        return stat_dict[board]
    moves = get_possible_moves(board, color)
    if len(moves) == 0 or limit == 0:
        return (None, compute_utility(board, color))
    opt_utility = float('-inf')
    for m in moves:
        new_board = play_move(board, color, m[0], m[1])
        move, utility = minimax_min_node(new_board, color, limit-1, caching)
        if caching:
            stat_dict[new_board] = (m, utility)
        if utility > opt_utility:
            opt_utility = utility
            opt_move = m
    return (opt_move, opt_utility)

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
    global stat_dict 
    stat_dict = {}
    move, utility = minimax_max_node(board, color, limit, caching)
    return move


############ ALPHA-BETA PRUNING #####################
def alphabeta_min_node(board, color, alpha, beta, limit, caching = 0, ordering = 0):
    if caching and board in stat_dict:
        return stat_dict[board]
    if color == 1:
        opp = 2
    else:
        opp = 1
    moves = get_possible_moves(board, opp)
    if len(moves) == 0 or limit == 0:
        return (None, compute_utility(board, color))
    opt_utility = float('inf')
    boards = {}
    for m in moves:
        new_board = play_move(board, opp, m[0], m[1])
        boards[new_board] = [compute_utility(new_board, color), m]
    if ordering:
        boards = sorted(boards.items(), key=lambda x:x[1])
    for b in boards:
        if ordering:
            new_board = b[0]
            m = b[1][1]
        else:
            new_board = b
            m = boards[b][1]
        move, utility = alphabeta_max_node(new_board, color, alpha, beta, limit-1, caching, ordering)
        if caching:
            stat_dict[board] = (m, utility)
        if utility < opt_utility:
            opt_utility = utility
            opt_move = m
        if beta > opt_utility:
            beta = opt_utility
            if beta <= alpha: break
    return (opt_move, opt_utility)

def alphabeta_max_node(board, color, alpha, beta, limit, caching = 0, ordering = 0):
    if caching and board in stat_dict:
        return stat_dict[board]
    if color == 1:
        opp = 2
    else:
        opp = 1
    moves = get_possible_moves(board, color)
    if len(moves) == 0 or limit == 0:
        return (None, compute_utility(board, color))
    opt_utility = float('-inf')
    boards = {}
    for m in moves:
        new_board = play_move(board, color, m[0], m[1])
        boards[new_board] = [compute_utility(new_board, color), m]
    if ordering:
        boards = sorted(boards.items(), key=lambda x:x[1], reverse=True)
    for b in boards:
        if ordering:
            new_board = b[0]
            m = b[1][1]
        else:
            new_board = b
            m = boards[b][1]
        move, utility = alphabeta_min_node(new_board, color, alpha, beta, limit-1, caching, ordering)
        if caching:
            stat_dict[new_board] = (m, utility)
        if utility > opt_utility:
            opt_utility = utility
            opt_move = m
        if alpha < opt_utility:
            alpha = opt_utility
            if beta <= alpha: break
    return (opt_move, opt_utility)

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
    global stat_dict 
    stat_dict = {}
    move, utility = alphabeta_max_node(board, color, float('-inf'), float('inf'), limit, caching, ordering)
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
