"""
An AI player for Othello. 
"""

import random
import sys
import time
import numpy as np

# You can use the functions in othello_shared to write your AI
from othello_shared import find_lines, get_possible_moves, get_score, play_move

CACHE = {} # Stores max(board,color)

def eprint(*args, **kwargs): #you can use this for debugging, as it will print to sterr and not stdout
    print(*args, file=sys.stderr, **kwargs)
    
# Method to compute utility value of terminal state
def compute_utility(board, color):
    our_score = get_score(board)[color-1]
    other_score = get_score(board)[2-color]
    return our_score - other_score

# Better heuristic value of board
def compute_heuristic(board, color): #not implemented, optional
    # I'll just keep it simple and return the number of stable discs
    N = len(board[0]) # get the dimension
    new_board = []
    for row in board: 
        new_board.append(list(row[:]))

    already_tagged = {}
    frontier = [(0,0),(0,N-1),(N-1,0),(N-1,N-1)]
    directions = [(1,1),(1,-1),(-1,1),(-1,-1)]
    stable_discs = 0
    while len(frontier) > 0:
        popped = frontier.pop(0)
        already_tagged[popped] = True
        x = popped[0]
        y = popped[1]
        if x < 0 or y < 0 or x >= N or y >= N:
            continue
        if board[x][y] == color:
            stable_discs += 1
        for d in directions:
            dx = d[0]+x
            dy = d[1]+y
            new_point = (dx,dy)
            if new_point in already_tagged:
                continue
            frontier.append(new_point)

    return stable_discs #change this!

############ MINIMAX ###############################
def minimax_min_node(board, color, limit, caching = 0):
    # This is not our turn! so use the opponent number
    opponent_color = 3 - color
    if caching == 1 and (board,opponent_color,limit) in CACHE:
        return CACHE[(board,opponent_color,limit)]

    moves = get_possible_moves(board, opponent_color)

    # If we reach a terminal state board, get its utility and return it (w/ None move)
    # Also if the limit is 0 then we hit the rock bottom
    if len(moves) == 0 or limit == 0:
        return None,compute_utility(board, color)

    # otherwise, "make a move" and call minimax MAX node on new boards
    new_boards = list(map(lambda m: play_move(board, opponent_color, m[0], m[1]), moves))
    board_utils = list(map(lambda b: minimax_max_node(b, color, limit-1, caching),new_boards))

    # then check which one resulted in the lowest utilest, and pick that
    x = np.argmin([move_util[1] for move_util in board_utils])
    best_move = moves[x]
    best_util = board_utils[x][1]
    minimax_min_move = best_move,best_util
    if caching == 1:
        CACHE[(board,opponent_color,limit)] = minimax_min_move

    return minimax_min_move

def minimax_max_node(board, color, limit, caching = 0): #returns highest possible utility
    if caching == 1 and (board,color,limit) in CACHE:
        return CACHE[(board,color,limit)]

    moves = get_possible_moves(board, color)

    # If we reach a terminal state board, get its utility and return it (w/ None move)
    # Also if the limit is 0 then we hit the rock bottom
    if len(moves) == 0 or limit == 0:
        return None,compute_utility(board, color)

    # otherwise, "make a move" and call minimax MIN node on new boards
    new_boards = list(map(lambda m: play_move(board, color, m[0], m[1]), moves))
    board_utils = list(map(lambda b: minimax_min_node(b, color, limit-1, caching),new_boards))

    # then check which one resulted in the highest utilest, and pick that
    x = np.argmax([move_util[1] for move_util in board_utils])
    best_move = moves[x]
    best_util = board_utils[x][1]
    minimax_max_move = best_move,best_util
    if caching == 1:
        CACHE[(board, color,limit)] = minimax_max_move

    return minimax_max_move

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
    best_move_util = minimax_max_node(board, color, limit, caching)

    return best_move_util[0]

############ ALPHA-BETA PRUNING #####################
def alphabeta_min_node(board, color, alpha, beta, limit, caching = 0, ordering = 0):
    # Immediately stop if alpha >= beta
    opponent_color = 3 - color
    if caching == 1 and (board,opponent_color,limit) in CACHE:
        return CACHE[(board,opponent_color,limit)]

    moves = get_possible_moves(board, opponent_color)

    # If we reach a terminal state board, get its utility and return it (w/ None move)
    # Also if the limit is 0 then we hit the rock bottom
    if len(moves) == 0 or limit == 0:
        return None,compute_utility(board, color)

    # otherwise, "make a move" and call minimax MIN node on new boards, keep the move
    new_boards = list(map(lambda m: (m,play_move(board, opponent_color, m[0], m[1])), moves))

    # if ordering is enabled, sort the new boards by their utility in ascending order
    if ordering == 1:
        new_boards.sort(key=(lambda b: compute_utility(b[1], color)), reverse=False)

    # start the alphabeta pruning
    board_utils = []
    for i in range(len(new_boards)):
        new_board = new_boards[i][1]
        new_board_move = new_boards[i][0]
        move_util = alphabeta_max_node(new_board, color, alpha, beta, limit-1, caching, ordering)
        beta = min(beta, move_util[1])
        if alpha >= beta:
            return new_board_move, beta
        board_utils.append((move_util,new_board_move))
    # board_utils elements looks like ((board_move, util),move)
    # then check which one resulted in the highest utilest, and pick that
    x = np.argmin([move_util_move[0][1] for move_util_move in board_utils])
    best_move = board_utils[x][1]
    best_util = board_utils[x][0][1]
    minimax_min_move = best_move,best_util
    if caching == 1:
        CACHE[(board, opponent_color,limit)] = minimax_min_move
    return minimax_min_move

def alphabeta_max_node(board, color, alpha, beta, limit, caching = 0, ordering = 0):
    # Immediately stop if alpha >= beta
    if caching == 1 and (board,color,limit) in CACHE:
        return CACHE[(board,color,limit)]

    moves = get_possible_moves(board, color)

    # If we reach a terminal state board, get its utility and return it (w/ None move)
    # Also if the limit is 0 then we hit the rock bottom
    if len(moves) == 0 or limit == 0:
        return None,compute_utility(board, color)

    # otherwise, "make a move" and call minimax MIN node on new boards, keep the move
    new_boards = list(map(lambda m: (m,play_move(board, color, m[0], m[1])), moves))

    # if ordering is enabled, sort the new boards by their utility in descending order
    if ordering == 1:
        new_boards.sort(key=(lambda b: compute_utility(b[1], color)), reverse=True)

    # start the alphabeta pruning
    board_utils = []
    for i in range(len(new_boards)):
        new_board = new_boards[i][1]
        new_board_move = new_boards[i][0]
        move_util = alphabeta_min_node(new_board, color, alpha, beta, limit-1, caching, ordering)
        alpha = max(alpha, move_util[1])
        if alpha >= beta:
            return new_board_move, alpha
        board_utils.append((move_util,new_board_move))
    # board_utils elements looks like ((board_move, util),move)
    # then check which one resulted in the highest utilest, and pick that
    x = np.argmax([move_util_move[0][1] for move_util_move in board_utils])
    best_move = board_utils[x][1]
    best_util = board_utils[x][0][1]
    minimax_max_move = best_move,best_util
    if caching == 1:
        CACHE[(board, color,limit)] = minimax_max_move
    return minimax_max_move

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
    move_util = alphabeta_max_node(board, color, float("-inf"), float("inf"), limit, caching, ordering)
    return move_util[0]

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
