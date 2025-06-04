"""
An AI player for Othello. 
"""

import random
import sys
import time

# You can use the functions in othello_shared to write your AI
from othello_shared import find_lines, get_possible_moves, get_score, play_move

state_cache = {}

def sorting_func(move_util):
    return move_util[1][1]

def eprint(*args, **kwargs): #you can use this for debugging, as it will print to sterr and not stdout
    print(*args, file=sys.stderr, **kwargs)
    
# Method to compute utility value of terminal state
def compute_utility(board, color):
    score = get_score(board)
    if color == 1:
        return score[0] - score[1]
    return score[1] - score[0]

# Better heuristic value of board
def compute_heuristic(board, color): #not implemented, optional
    possible_moves = len(get_possible_moves(board,color))
    return compute_utility(board, color) + possible_moves

############ MINIMAX ###############################
def minimax_min_node(board, color, limit, caching = 0):
    if (color == 1):
        other_color = 2
    else:
        other_color = 1
    possible_moves = get_possible_moves(board,other_color)
    if (possible_moves == [] or limit == 0):
        return ((0,0),compute_utility(board, color))
    utilities = []
    for move in possible_moves:
        bord = play_move(board,other_color,move[0],move[1])
        if (caching):
            if bord in state_cache:
                utilities.append((move,(0,state_cache[bord])))
                continue
        utilities.append((move,minimax_max_node(bord,color,limit-1,caching)))
        if(caching): 
            state_cache[bord] = utilities[-1][1][1]
    curr_min = utilities[0][1][1] 
    min_util = utilities[0]
    for util in utilities:
        if (util[1][1]<curr_min):
            curr_min = util[1][1]
            min_util = util
    return (min_util[0],curr_min)
    

def minimax_max_node(board, color, limit, caching = 0): #returns highest possible utility
    possible_moves = get_possible_moves(board,color)
    if (possible_moves == [] or limit ==0):
        return ((0,0),compute_utility(board, color))
    utilities = []
    for move in possible_moves:
        bord = play_move(board,color,move[0], move[1])
        if caching and bord in state_cache:
            utilities.append((move,(0,state_cache[bord])))
            continue
        utilities.append((move,minimax_min_node(bord,color,limit-1, caching)))
        if(caching): 
            state_cache[bord] = utilities[-1][1][1]
    curr_max = utilities[0][1][1] 
    max_util = utilities[0]
    for util in utilities:
        if (util[1][1]>curr_max):
            curr_max = util[1][1]
            max_util = util
    return (max_util[0],curr_max)


    

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
    #IMPLEMENT
    return minimax_max_node(board, color, limit, caching)[0]

############ ALPHA-BETA PRUNING #####################
def alphabeta_min_node(board, color, alpha, beta, limit, caching = 0, ordering = 0):
    possible_moves = get_possible_moves(board,3-color)
    if (possible_moves == [] or limit ==0):
        return ((0,0),compute_utility(board, color))
    
    opt_move = (possible_moves[0],((0,0),float('inf')))
    utilities = []
    for move in possible_moves:
        bord = play_move(board,3-color,move[0], move[1])
        if caching and bord in state_cache:
            move_util = (move,(0,state_cache[bord]))
        else:
            move_util = (move,alphabeta_max_node(bord, color, alpha, beta, limit-1,caching, ordering))
            if (caching): 
                state_cache[bord] = move_util[1][1]
        utilities.append(move_util)
    if (ordering):
        utilities = sorted(utilities, key=sorting_func, reverse=True)
    for move_util in utilities:
        if move_util[1][1] < opt_move[1][1]:
            opt_move = move_util
        if move_util[1][1] < beta:
            beta = move_util[1][1]
        if alpha>=beta:
            break
    return (opt_move[0],opt_move[1][1])
    


def alphabeta_max_node(board, color, alpha, beta, limit, caching = 0, ordering = 0):
    possible_moves = get_possible_moves(board,color)
    if (possible_moves == [] or limit ==0):
        return ((0,0),compute_utility(board, color))
    opt_move = (possible_moves[0],((0,0),float('-inf')))
    utilities = []
    for move in possible_moves:
        bord = play_move(board,color,move[0], move[1])
        if caching and bord in state_cache:
            move_util = (move,(0,state_cache[bord]))
        else:
            move_util = (move,alphabeta_min_node(bord, color, alpha, beta, limit-1,caching, ordering))
            if (caching): 
                state_cache[bord] = move_util[1][1]
        utilities.append(move_util)
    if (ordering):
        utilities = sorted(utilities, key=sorting_func, reverse=True)
    for move_util in utilities:
        if move_util[1][1] > opt_move[1][1]:
            opt_move = move_util
        if move_util[1][1] > alpha:
            alpha = move_util[1][1]
        if alpha>=beta:
            break
    return (opt_move[0],opt_move[1][1])



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
    return alphabeta_max_node(board,color,float('-inf'),float('inf'), limit, caching, ordering)[0]

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
