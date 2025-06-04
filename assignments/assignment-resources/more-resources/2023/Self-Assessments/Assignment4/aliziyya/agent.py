"""
An AI player for Othello. 
"""

import random
import sys
import time
from cmath import inf

# You can use the functions in othello_shared to write your AI
from othello_shared import find_lines, get_possible_moves, get_score, play_move

state_cache = {}

def eprint(*args, **kwargs): #you can use this for debugging, as it will print to sterr and not stdout
    print(*args, file=sys.stderr, **kwargs)

def other_player(color):
    if color == 1:
        return 2
    return 1

# Method to compute utility value of terminal state
def compute_utility(board, color):
    p1, p2 = get_score(board)
    if color == 1:
        return p1 - p2
    return p2 - p1

# Better heuristic value of board
def compute_heuristic(board, color): #not implemented, optional
    # no (•_•)
    return 0 #change this! no

############ MINIMAX ###############################
def minimax_min_node(board, color, limit, caching = 0):
    oc = other_player(color)
    possibilities = get_possible_moves(board, oc)
    min_util = inf
    worst = None
    
    if len(possibilities) == 0 or limit == 0: 
        return (None, compute_utility(board, color))

    for move in possibilities:
        curr = play_move(board, oc, move[0], move[1])
        if caching != 0:
            if curr not in state_cache.keys():
                opp_move, curr_ut = minimax_max_node(curr, color, limit-1, caching)
                state_cache[curr] = curr_ut
            else:
                curr_ut = state_cache[curr]
        else:
            opp_move, curr_ut = minimax_max_node(curr, color, limit-1, caching)
        
        if curr_ut < min_util:
            min_utility = curr_ut
            worst = move
        
    return(worst, min_utility)



def minimax_max_node(board, color, limit, caching = 0): #returns highest possible utility
    possibilities = get_possible_moves(board, color)
    max_util = -inf
    best = None
    
    if len(possibilities) == 0 or limit == 0: 
        return (None, compute_utility(board, color))

    for move in possibilities:
        curr = play_move(board, color, move[0], move[1])
        if caching != 0:
            if curr not in state_cache.keys():
                opp_move, curr_ut = minimax_min_node(curr, color, limit-1, caching)
                state_cache[curr] = curr_ut
            else:
                curr_ut = state_cache[curr]  
        else:
            opp_move, curr_ut = minimax_min_node(curr, color, limit-1, caching)
        
        if curr_ut >= max_util:
            max_util = curr_ut
            best = move

    return(best, max_util)



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
    move, util = minimax_max_node(board, color, limit-1, caching)
    return move 

############ ALPHA-BETA PRUNING #####################
def alphabeta_min_node(board, color, alpha, beta, limit, caching = 0, ordering = 0):
    #IMPLEMENT (and replace the line below)
    oc = other_player(color)
    min_util = inf
    worst = None
    possibilities = get_possible_moves(board, oc)
    sub_boards = []

    if (len(possibilities) == 0) or (limit == 0): 
        return (None, compute_utility(board, color))


    for move in possibilities:
            sub = play_move(board, oc, move[0], move[1])
            sub_boards.append((move, sub))
    if ordering != 0:
        sub_boards = qsort_board(sub_boards, color)
    for pair in sub_boards:
        if caching == 0:
            opp, curr_u = alphabeta_max_node(pair[1], color, alpha, beta, limit-1, caching, ordering)
        else:
            if pair[1] not in state_cache.keys():
                opp, curr_u = alphabeta_max_node(pair[1], color, alpha, beta, limit-1, caching, ordering)
                state_cache[pair[1]] = curr_u
            else:
                curr_u = state_cache[pair[1]]  
        if curr_u < min_util:
            min_util = curr_u
            worst = pair[0]
            alpha = min(beta, min_util)
            if alpha >= beta:
                break
    return(worst, min_util)

    

def alphabeta_max_node(board, color, alpha, beta, limit, caching = 0, ordering = 0):
    #IMPLEMENT (and replace the line below)
    max_util = -inf
    best = None
    possibilities = get_possible_moves(board, color)
    sub_boards = []

    if len(possibilities) == 0 or limit == 0: 
        return (None, compute_utility(board, color))
    
    for move in possibilities:
        sub = play_move(board, color, move[0], move[1])
        sub_boards.append((move, sub))
    if ordering != 0:
        sub_boards = qsort_board(sub_boards, color)
    for pair in sub_boards:
        if caching == 0:
            opp, curr_u = alphabeta_min_node(pair[1], color, alpha, beta, limit-1, caching, ordering)
        else:
            if pair[1] not in state_cache.keys():
                opp, curr_u = alphabeta_min_node(pair[1], color, alpha, beta, limit-1, caching, ordering)
                state_cache[pair[1]] = curr_u
            else:
                curr_u = state_cache[pair[1]]  
        if curr_u > max_util:
            max_util = curr_u
            best = pair[0]
            alpha = max(alpha, max_util)
            if alpha >= beta:
                break
    return(best, max_util)
    
def qsort_board(sub_boards, color):
    if len(sub_boards) <= 1:
        return sub_boards
    else:
        pivot = len(sub_boards)//2
        pivot_util = compute_utility(sub_boards[pivot][1], color)
        right = []
        left = []
        for pair in sub_boards:
            if pair != sub_boards[pivot]:
                util = compute_utility(pair[1], color)
                if util > pivot_util:
                    left.append(pair)
                else:
                    right.append(pair)
    return qsort_board(left, color) + [sub_boards[pivot]] + qsort_board(right, color)

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
    move, utility = alphabeta_max_node(board, color, -inf, inf, limit-1, caching, ordering)

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
