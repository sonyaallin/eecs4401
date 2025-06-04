"""
An AI player for Othello. 
"""

import random
import sys
import time
import math
# You can use the functions in othello_shared to write your AI
from othello_shared import find_lines, get_possible_moves, get_score, play_move

#global variable for caching states
board_state_util = {} #mapping from already seen board states to their utilities

def eprint(*args, **kwargs): #you can use this for debugging, as it will print to sterr and not stdout
    print(*args, file=sys.stderr, **kwargs)
    
# Method to compute utility value of terminal state
def compute_utility(board, color):
    #IMPLEMENT
    score = get_score(board)
    if(color == 1):
        return score[0] - score[1]
    return score[1] - score[0]

"""
    Going to use a composite heuristic which leverages coin parity(what we did in compute_utility)
    and mobility(how many moves can each color make). 
    https://courses.cs.washington.edu/courses/cse573/04au/Project/mini1/RUSSIA/Final_Paper.pdf
"""
def compute_heuristic(board, color): 

    coin_parity = 100 * (compute_utility(board, color)) / (sum(get_score(board)))

    possible_moves_color = len(get_possible_moves(board, color))
    possible_moves_other = len(get_possible_moves(board, 1 if color == 2 else 1))

    if(possible_moves_color + possible_moves_other != 0):
        return 100 *(possible_moves_color - possible_moves_other) / (possible_moves_other + possible_moves_color) + coin_parity
    
    return 0 + coin_parity


# helper function to order to successor states of a board
def func(move, board, color):
    new_board = play_move(board, color, move[0], move[1])
    return compute_utility(new_board, color)

def func2(move, board, color):
    new_board = play_move(board, 1 if color == 2 else 2, move[0], move[1])
    return compute_utility(new_board, color)

############ MINIMAX ###############################
def minimax_min_node(board, color, limit, caching = 0):
    #IMPLEMENT (and replace the line below)
    if (caching and board_state_util.get(board, False)):
        return board_state_util[board] 

    possible_moves = get_possible_moves(board, 1 if color == 2 else 2)
    min_util_move = (0,0)
    min_util = math.inf
    for move in possible_moves:
        new_board = play_move(board, 1 if color == 2 else 2 , move[0], move[1])
        if get_possible_moves(new_board, color):
            if (limit - 1 != 0):
                m, u = minimax_max_node(new_board, color, limit - 1, caching)
            else:
                m, u = move, compute_utility(new_board, color) # heursitic call since we reached depth limit

        else: # we are at terminal node
            m, u = move, compute_utility(new_board, color)

        if u < min_util:
            min_util_move, min_util = move, u

    if (caching):
        board_state_util[board] = (min_util_move, min_util)

    return (min_util_move, min_util)

def minimax_max_node(board, color, limit, caching = 0): #returns highest possible utility
    #IMPLEMENT (and replace the line below)
    if (caching and board_state_util.get(board, False)):
        return board_state_util[board] 

    possible_moves = get_possible_moves(board, color)
    max_util_move = (0,0)
    max_util = -1 * math.inf
    for move in possible_moves:
        new_board = play_move(board, color, move[0], move[1])
        if get_possible_moves(new_board, 1 if color == 2 else 2):
            if(limit - 1 != 0):
                m, u = minimax_min_node(new_board, color, limit - 1, caching)
            else:
                m, u = move, compute_utility(new_board, color) # heursitic call since we reached depth limit

        else: # we are at terminal node
             m, u = move, compute_utility(new_board, color)

        if u > max_util:
            max_util_move, max_util = move, u

    if (caching):
        board_state_util[board] = (max_util_move, max_util)
    return (max_util_move, max_util)

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
    if get_possible_moves(board, color) == []:
        return ((None, None), 0)

    return minimax_max_node(board, color, limit, caching)[0]

############ ALPHA-BETA PRUNING #####################
def alphabeta_min_node(board, color, alpha, beta, limit, caching = 0, ordering = 0):
    #IMPLEMENT (and replace the line below)
    if (caching and board_state_util.get(board, False)):
        return board_state_util[board] 

    possible_moves = get_possible_moves(board, 1 if color == 2 else 2)
    if ordering:
        possible_moves = sorted(possible_moves, key=lambda move: func2(move, board, color), reverse = False)
    min_util_move = (0,0)
    min_util = math.inf

    for move in possible_moves:
        new_board = play_move(board, 1 if color == 2 else 2, move[0], move[1])

        if get_possible_moves(new_board, color):
            if(limit - 1 !=  0):
                m, u = alphabeta_max_node(new_board, color, alpha, beta, limit - 1, caching, ordering)
            else:
                m, u = move, compute_utility(new_board, color) # heursitic call since we reached depth limit
        
        else:
            m, u = move, compute_utility(new_board, color) # it is a terminal state

        if u < min_util:
            min_util = u 
            min_util_move = move

        if min_util < beta:
            beta = min_util       
            if beta <= alpha: break # we don't need to explore any further  

    if (caching):
        board_state_util[board] = (min_util_move, min_util)

    return (min_util_move, min_util)

def alphabeta_max_node(board, color, alpha, beta, limit, caching = 0, ordering = 0):
    #IMPLEMENT (and replace the line below)
    if (caching and board_state_util.get(board, False)):
        return board_state_util[board] 

    possible_moves = get_possible_moves(board, color)
    if ordering:
        possible_moves = sorted(possible_moves, key=lambda move: func(move, board, color), reverse=True)
    max_util_move = (0,0)
    max_util = -1 * math.inf

    for move in possible_moves:
        new_board = play_move(board, color, move[0], move[1])

        if get_possible_moves(new_board, 1 if color == 2 else 2):
            if(limit - 1!= 0):
                m, u = alphabeta_min_node(new_board, color, alpha, beta, limit - 1, caching, ordering)
            else:
                m, u = move, compute_utility(new_board, color) # heursitic call since we reached depth limit

        else:
            m, u = move, compute_utility(new_board, color) # it is a terminal state

        if u > max_util:
            max_util = u 
            max_util_move = move

        if max_util > alpha:
            alpha = max_util       
            if beta <= alpha: break # we don't need to explore any further  

    if (caching):
        board_state_util[board] = (max_util_move, max_util)

    return (max_util_move, max_util)

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
    if get_possible_moves(board, color) == []:
        return ((None, None), 0)

    return alphabeta_max_node(board, color, -1 * math.inf, math.inf, limit, caching, ordering)[0]

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
