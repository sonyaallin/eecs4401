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
    dark_score, light_score = get_score(board)
    if color == 1:
        light_score *= -1
    if color == 2:
        dark_score *= -1
    return dark_score + light_score

# Better heuristic value of board
def compute_heuristic(board, color): #not implemented, optional
    """This heuristic gives a significant bonus for holding the corners, based on my own preferred strategy in Othello due to their position as untakeable pieces"""
    dark_score, light_score = get_score(board)
    if color == 1:
        light_score *= -1
    if color == 2:
        dark_score *= -1
    bonus = 0
    if board[0][0] == color:
        bonus += 5
    if board[-1][0] == color:
        bonus += 5
    if board[0][-1] == color:
        bonus += 5
    if board[-1][-1] == color:
        bonus += 5   
    return dark_score + light_score + bonus

def other_color(color):
    return color % 2 + 1

max_cache = {}
min_cache = {}

############ MINIMAX ###############################
def minimax_min_node(board, color, limit, caching = 0):
    if caching and board in min_cache:
        return min_cache[board]
    possible_moves = get_possible_moves(board, other_color(color))
    if (len(possible_moves) == 0) or (limit == 0):
        return ((0,0), compute_utility(board, color))
    move_utilities = []
    for move in possible_moves:
        next_board = play_move(board, other_color(color), move[0], move[1])
        move_utilities.append((move, minimax_max_node(next_board, color, limit-1, caching)[1]))
    #eprint("Depth: {} Min utilities: {}".format(limit, move_utilities))
    retval = min(move_utilities, key=lambda x: x[1])
    if caching:
        min_cache[board] = retval
    return retval

def minimax_max_node(board, color, limit, caching = 0): #returns highest possible utility
    possible_moves = get_possible_moves(board, color)
    if (len(possible_moves) == 0) or (limit == 0):
        return ((0,0), compute_utility(board, color))
    move_utilities = []
    for move in possible_moves:
        next_board = play_move(board, color, move[0], move[1])
        move_utilities.append((move, minimax_min_node(next_board, color, limit-1, caching)[1]))
    #eprint("Depth: {} Max utilities: {}".format(limit, move_utilities))
    retval = max(move_utilities, key=lambda x: x[1])
    if caching:
        max_cache[board] = retval
    return retval

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
    move_utility = minimax_max_node(board, color, limit, caching)
    #eprint("Move found: {}, minmax utility: {}".format(move_utility[0], move_utility[1]))
    return move_utility[0]

############ ALPHA-BETA PRUNING #####################
def alphabeta_min_node(board, color, alpha, beta, limit, caching = 0, ordering = 0):
    if caching and board in min_cache:
        return min_cache[board]
    possible_moves = get_possible_moves(board, other_color(color))
    if (len(possible_moves) == 0) or (limit == 0):
        return ((0,0), compute_utility(board, color))
    move_utilities = []
    beta = float("inf")
    if ordering:
        move_boards = [(move, play_move(board, color, move[0], move[1])) for move in possible_moves]
        move_boards.sort(key=lambda x: compute_utility(x[1], color))
        for move, next_board in move_boards:
            value = alphabeta_max_node(next_board, color, alpha, beta, limit-1, caching, ordering)[1]
            move_utilities.append((move, value))
            if beta > value:
                beta = value
                if beta <= alpha:
                    break
    else:
        for move in possible_moves:
            next_board = play_move(board, other_color(color), move[0], move[1])
            value = alphabeta_max_node(next_board, color, alpha, beta, limit-1, caching, ordering)[1]
            move_utilities.append((move, value))
            if beta > value:
                beta = value
                if beta <= alpha:
                    break
    #eprint("Depth: {} Min utilities: {}".format(limit, move_utilities))
    retval = min(move_utilities, key=lambda x: x[1])
    if caching:
        min_cache[board] = retval
    return retval

def alphabeta_max_node(board, color, alpha, beta, limit, caching = 0, ordering = 0):
    if caching and board in max_cache:
        return max_cache[board]
    possible_moves = get_possible_moves(board, color)
    if (len(possible_moves) == 0) or (limit == 0):
        return ((0,0), compute_utility(board, color))
    move_utilities = []
    alpha = -float("inf")
    if ordering:
        move_boards = [(move, play_move(board, color, move[0], move[1])) for move in possible_moves]
        move_boards.sort(key=lambda x: compute_utility(x[1], color), reverse=True)
        for move, next_board in move_boards:
            value = alphabeta_min_node(next_board, color, alpha, beta, limit-1, caching, ordering)[1]
            move_utilities.append((move, value))
            if alpha < value:
                alpha = value
                if alpha >= beta:
                    break
    else:
        for move in possible_moves:
            next_board = play_move(board, other_color(color), move[0], move[1])
            value = alphabeta_min_node(next_board, color, alpha, beta, limit-1, caching, ordering)[1]
            move_utilities.append((move, value))
            if alpha < value:
                alpha = value
                if alpha >= beta:
                    break
    #eprint("Depth: {} Max utilities: {}".format(limit, move_utilities))
    retval = max(move_utilities, key=lambda x: x[1])
    if caching:
        max_cache[board] = retval
    return retval

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
    move_utility = alphabeta_max_node(board, color, -float("inf"), float("inf"), limit, caching, ordering)
    #eprint("Move found: {}, minmax utility: {}".format(move_utility[0], move_utility[1]))
    return move_utility[0]

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
