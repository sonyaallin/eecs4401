"""
An AI player for Othello. 

Compute heuristic description:

1. Count # of corners owned by a player
    - +1 score for each corner
2. Count # of lines owned by a player
    - +board_size -1 for each line from a corner

We compute these two scores for ai color and opponent color and subtract. (ai_score - opponent_score) to compute the heuristic value
"""

import random
import sys
import time
import numpy as np
# You can use the functions in othello_shared to write your AI
from othello_shared import find_lines, get_possible_moves, get_score, play_move

val_minimax = {}
val_alphabeta = {}
def eprint(*args, **kwargs): #you can use this for debugging, as it will print to sterr and not stdout
    print(*args, file=sys.stderr, **kwargs)

def other(color):
    return 2 if color == 1 else 1

# Method to compute utility value of terminal state
def compute_utility(board, color):
    darks, lights = get_score(board) 
    return darks - lights if color == 1 else lights-darks

# Better heuristic value of board
def compute_heuristic(board, color):
    board_size = len(board)
    opponent = other(color)
    corners = [(0, 0), (0, board_size -1), (board_size -1, 0), (board_size - 1, board_size - 1)]
    ai_score = 0
    opponent_score = 0
    for corner in corners:
        if board[corner[0]][corner[1]] == color:
            ai_score += 1
        elif board[corner[0]][corner[1]] == opponent:
            opponent_score += 1
        ai_score += len(find_lines(board, corner[0], corner[1], color))
        opponent_score += len(find_lines(board, corner[0], corner[1], opponent))

    
    return ai_score - opponent_score


############ MINIMAX ###############################
def minimax_min_node(board, color, limit, caching = 0):
    # Base Cases
    possible_moves = get_possible_moves(board, other(color))
    if limit == 0:
        utility = compute_utility(board, color)
        return (None, utility)
    if len(possible_moves) == 0:       
        # possible_moves_other = get_possible_moves(board, color)
        utility = compute_utility(board, color)
        return None, utility
                
    min_move = None
    min_val = np.inf
    for move in possible_moves:
        new_state = play_move(board, other(color), move[0], move[1])
        if caching and new_state in val_minimax:
            new_val = val_minimax[new_state]
        else:            
            new_move, new_val = minimax_max_node(new_state, color, limit - 1, caching)
        if caching:
            val_minimax[new_state] = new_val        
        if new_val < min_val: 
            min_move = move
            min_val = new_val
    
    return min_move, min_val    



def minimax_max_node(board, color, limit, caching = 0): #returns highest possible utility
    # Base Cases
    possible_moves = get_possible_moves(board, color)
    if limit == 0:
        utility = compute_utility(board, color)
        return (None, utility)
    if len(possible_moves) == 0:
        utility = compute_utility(board, color)
        return None, utility
                
    max_move = None
    max_val = -np.inf
    for move in possible_moves:
        new_state = play_move(board, color, move[0], move[1])
        # Case 1 No more moves for both
        if caching and new_state in val_minimax:
            new_val = val_minimax[new_state]
        else:            
            new_move, new_val = minimax_min_node(new_state, color, limit - 1, caching)
        if caching:    
            val_minimax[new_state] = new_val
        if new_val > max_val: 
            max_move = move
            max_val = new_val
    
    return max_move, max_val

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
    move, score = minimax_max_node(board, color, limit, caching)
    return move

############ ALPHA-BETA PRUNING #####################

def alphabeta_min_node(board, color, alpha, beta, limit, caching = 0, ordering = 0):
    opponent = other(color)
    possible_moves = get_possible_moves(board, opponent)
    if ordering:
        possible_moves.sort(key=lambda x: compute_utility(play_move(board, opponent, x[0], x[1]), color))

    if limit == 0:
        utility = compute_utility(board, color)
        return (None, utility)
    if len(possible_moves) == 0:
        utility = compute_utility(board, color)
        return None, utility

    

    min_move = None
    min_val = np.inf
    for move in possible_moves:
        new_state = play_move(board, opponent, move[0], move[1])
        if caching and new_state in val_alphabeta:
            new_val = val_alphabeta[new_state]
        else:            
            new_move, new_val = alphabeta_max_node(new_state, color, alpha, beta, limit - 1, caching)
        if caching:
             val_alphabeta[new_state] = new_val              
        if min_val > new_val:
            min_val = new_val
            min_move = move
        if beta > min_val:
            beta = min_val
            if beta <= alpha:
                break
    
    return min_move, min_val

def alphabeta_max_node(board, color, alpha, beta, limit, caching = 0, ordering = 0):
    possible_moves = get_possible_moves(board, color)
    if ordering:
        possible_moves.sort(key=lambda x: compute_utility(play_move(board, color, x[0], x[1]), color), reverse=True)
    if limit == 0:
        utility = compute_utility(board, color)
        return (None, utility)
    if len(possible_moves) == 0:
        utility = compute_utility(board, color)
        return None, utility

    max_move = None
    max_val = -np.inf
    

    for move in possible_moves:
        new_state = play_move(board, color, move[0], move[1])
        if caching and new_state in val_alphabeta:
            new_val = val_alphabeta[new_state]
        else:            
            new_move, new_val = alphabeta_min_node(new_state, color, alpha, beta, limit - 1, caching)
        if caching:
             val_alphabeta[new_state] = new_val        
        if max_val < new_val:
            max_val = new_val
            max_move = move
        if alpha < max_val:
            alpha = max_val
            if beta <= alpha:
                break
    
    return max_move, max_val

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
    alpha = -np.inf
    beta = np.inf
    move, score = alphabeta_max_node(board, color, alpha, beta, limit, caching, ordering)
    return move #change this!

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
