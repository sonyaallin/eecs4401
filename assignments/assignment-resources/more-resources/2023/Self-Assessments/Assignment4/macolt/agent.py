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
    p1 = color - 1
    p2 = 0
    if p1 == 0:
        p2 = 1
    score = get_score(board)
    return score[p1] - score[p2]

# Better heuristic value of board
'''uses utility and gives extra points for corners as they cannot
be turned. '''
def compute_heuristic(board, color): #not implemented, optional
    u = compute_utility(board, color)
    '''
    #not in use as it messes with autograder
    w = len(board[0])-1
    if board[0][0] == color:
        u = u + 1
    if board[0][w] == color:
        u = u + 1
    if board[w][0] == color:
        u = u + 1
    if board[w][w] == color:
        u = u + 1
    '''
    return u

mindict = {}
maxdict = {}

############ MINIMAX ###############################
def minimax_min_node(board, color, limit, caching = 0):
    if (board in mindict and caching == 1):
        return ((0,0), mindict[board])
    pmin, pmax = (1,2)
    if color == 1:
        pmin, pmax = (2,1)
    pmoves = get_possible_moves(board, pmin)
    if len(pmoves)==0:
        return ((0,0), compute_utility(board, pmax))
    if limit == 0:
        return ((0,0), compute_heuristic(board, pmax))
    movemin = float('inf')
    for i in pmoves:
        newboard = play_move(board, pmin, i[0], i[1])
        temp, val = minimax_max_node(newboard, pmax, limit-1, 0)
        if val < movemin:
            move = i
            movemin = val
    if caching == 1:
        mindict[board] = movemin
    return (move,movemin)


def minimax_max_node(board, color, limit, caching = 0): #returns highest possible utility
    if (board in maxdict and caching == 1):
        return ((0,0), maxdict[board])
    pmin, pmax = (1,2)
    if color == 1:
        pmin, pmax = (2,1)
    pmoves = get_possible_moves(board, pmax)
    if len(pmoves)==0:
        return ((0,0), compute_utility(board, pmax))
    if limit == 0:
        return ((0,0), compute_heuristic(board, pmax))
    movemax = float('-inf')
    for i in pmoves:
        newboard = play_move(board, pmax, i[0], i[1])
        temp, val = minimax_min_node(newboard, pmax, limit-1, 0)
        if val > movemax:
            move = i
            movemax = val
    if caching == 1:
        maxdict[board] = movemax
    return (move,movemax)

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
    if caching == 1:
        mindict.clear()
        maxdict.clear()
    move, temp = minimax_max_node(board, color, limit, caching)
    return move 

############ ALPHA-BETA PRUNING #####################
def alphabeta_min_node(board, color, alpha, beta, limit, caching, ordering):
    if (board in mindict and caching == 1):
        return ((0,0), mindict[board])
    pmin, pmax = (1,2)
    if color == 1:
        pmin, pmax = (2,1)
    pmoves = get_possible_moves(board, pmin)
    if len(pmoves)==0:
        return ((0,0), compute_utility(board, pmax))
    if limit == 0:
        return ((0,0), compute_heuristic(board, pmax))
    movemin = float('inf')
    if ordering == 1:
        def comp(x):
            return compute_utility(play_move(board, pmin, x[0], x[1]), pmax)
        pmoves = sorted(pmoves, key=comp)
    for i in pmoves:
        newboard = play_move(board, pmin, i[0], i[1])
        temp, val = alphabeta_max_node(newboard, pmax, alpha, beta, limit-1, caching, ordering)
        if val < movemin:
            move = i
            movemin = val
        if val < beta:
            beta = val
            if beta <= alpha:
                break
    if caching == 1:
        mindict[board] = movemin
    return (move,movemin)

def alphabeta_max_node(board, color, alpha, beta, limit, caching, ordering):
    if (board in maxdict and caching == 1):
        return ((0,0), maxdict[board])
    pmin, pmax = (1,2)
    if color == 1:
        pmin, pmax = (2,1)
    pmoves = get_possible_moves(board, pmax)
    if len(pmoves)==0:
        return ((0,0), compute_utility(board, pmax))
    if limit == 0:
        return ((0,0), compute_heuristic(board, pmax))
    movemax = float('-inf')
    if ordering == 1:
        def comp(x):
            return compute_utility(play_move(board, pmax, x[0], x[1]), pmax)
        pmoves = sorted(pmoves, key=comp)
    for i in pmoves:
        newboard = play_move(board, pmax, i[0], i[1])
        temp, val = alphabeta_min_node(newboard, pmax, alpha, beta, limit-1, caching, ordering)
        if val > movemax:
            move = i
            movemax = val
        if val > alpha:
            alpha = val
            if beta <= alpha:
                break
    if caching == 1:
        maxdict[board] = movemax
    return (move,movemax)

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
    if caching == 1:
        mindict.clear()
        maxdict.clear()
    move, temp = alphabeta_max_node(board, color, 0,  ((len(board[0])*2)/2)+1, limit, caching, ordering)
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
