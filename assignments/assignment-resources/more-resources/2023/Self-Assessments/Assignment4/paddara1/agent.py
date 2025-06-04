"""
An AI player for Othello. 
"""
import random
import re
import sys
import time

# You can use the functions in othello_shared to write your AI
from othello_shared import find_lines, get_possible_moves, get_score, play_move

CACHE = dict()  # maps board states to their minimax value

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
def minimax_min_node(board, color, limit, caching = 0):
    # done
    if caching == 1:
        if type(board) is tuple and type(board[0]) is tuple and board in CACHE:
            return CACHE[board]

    # get color of opponent
    if color == 1:
        opposite_color = 2
    else:
        opposite_color = 1

    moves = get_possible_moves(board, opposite_color)
    if not moves or limit == 0:  # if there are no moves or depth limit is reached
        utility = compute_utility(board, color)
        if moves:  # if there are moves
            move = moves[0]
        else:
            move = None
        return move, utility

    curr_min_utility = float('inf')
    curr_min_move = None
    for move in moves:
        next_state = play_move(board, opposite_color, move[0], move[1])  # next_state is the board after opponent's move
        if caching == 1 and next_state in CACHE:  # check cache
            new_move, utility = CACHE[next_state]
        else:
            new_move, utility = minimax_max_node(next_state, color, limit - 1, caching)

        if utility < curr_min_utility:
            curr_min_utility = utility
            curr_min_move = move
        if caching == 1:
            CACHE[next_state] = (new_move, utility)  # cache the state
    
    return curr_min_move, curr_min_utility

def minimax_max_node(board, color, limit, caching = 0): #returns highest possible utility
    # done
    if caching == 1:
        if type(board) is tuple and type(board[0]) is tuple and board in CACHE:
            return CACHE[board]

    moves = get_possible_moves(board, color)
    if not moves or limit == 0:  # if there are no moves or depth limit is reached
        utility = compute_utility(board, color)
        if moves:  # if there are moves
            move = moves[0]
        else:
            move = None
        return move, utility

    curr_max_utility = float('-inf')
    curr_max_move = None
    for move in moves:
        next_state = play_move(board, color, move[0], move[1])
        if caching == 1 and next_state in CACHE:  # check cache
            new_move, utility = CACHE[next_state]
        else:
            new_move, utility = minimax_min_node(next_state, color, limit - 1, caching)

        if utility > curr_max_utility:
            curr_max_utility = utility
            curr_max_move = move
        if caching == 1:
            CACHE[next_state] = (new_move, utility)  # cache the state

    return curr_max_move, curr_max_utility
    

def select_move_minimax(board, color, limit, caching = 0):
    """
    Given a board and a player color, decide on a move. 
    The return value is a tuple of integers (i,j), where
    i is the column and j is the row on the board.  

    Note that other parameters are accepted by this function:
    If limit is a positive integer, your code should enforce a depth limit that is equal to the value of the parameter.
    Search only to nodes at a depth-limit equal to the limit.  If nodes at this level are non-terminal return a heuristic 
    value (see compute_utility)
    If caching is ON (i.e. 1), use state caching to reduce the number of state evaluations.
    If caching is OFF (i.e. 0), do NOT use state caching to reduce the number of state evaluations.    
    """
    # done
    return minimax_max_node(board, color, limit, caching)[0]

############ ALPHA-BETA PRUNING #####################
def alphabeta_min_node(board, color, alpha, beta, limit, caching = 0, ordering = 0):
    # alphabeta pruning
    if caching == 1:
        if type(board) is tuple and type(board[0]) is tuple and board in CACHE:
            return CACHE[board]
    
    if color == 1:
        opposite_color = 2
    else:
        opposite_color = 1

    moves = get_possible_moves(board, opposite_color)
    if not moves or limit == 0:
        utility = compute_utility(board, color)
        if moves:  # if there are moves
            move = moves[0]
        else:
            move = None

        return move, utility

    next_states = []  # List[Tuple] containing (new board, move) for all children
    for move in moves:
        next_states.append((play_move(board, opposite_color, move[0], move[1]), move))
    if ordering == 1:
        next_states.sort(key=lambda x: compute_utility(x[0], color))  # sort by utility

    curr_min_utility = float('inf')
    curr_min_move = None
    for state, move in next_states:
        if caching == 1 and state in CACHE:
            new_move, utility = CACHE[state]
        else:
            new_move, utility = alphabeta_max_node(state, color, alpha, beta, limit - 1, caching, ordering)
        if utility < curr_min_utility:
            curr_min_utility = utility
            curr_min_move = move
        
        if caching == 1:
            CACHE[state] = (new_move, utility)  # cache the state
        
        if alpha >= curr_min_utility:
            return curr_min_move, curr_min_utility

        beta = min(beta, curr_min_utility)
            
    return curr_min_move, curr_min_utility


def alphabeta_max_node(board, color, alpha, beta, limit, caching = 0, ordering = 0):
    if caching == 1:
        if type(board) is tuple and type(board[0]) is tuple and board in CACHE:
            return CACHE[board]

    moves = get_possible_moves(board, color)
    if not moves or limit == 0:  # if there are no moves or depth limit is reached
        utility = compute_utility(board, color)
        if moves:  # if there are moves
            move = moves[0]
        else:
            move = None
        return move, utility
    
    next_states = []  # List[Tuple] containing (new board, move) for all children
    for move in moves:
        next_states.append((play_move(board, color, move[0], move[1]), move))
    if ordering == 1:
        next_states.sort(key=lambda x: compute_utility(x[0], color), reverse=True)  # sort by utility

    curr_max_utility = float('-inf')
    curr_max_move = None
    for state, move in next_states:
        if caching == 1 and state in CACHE:
            new_move, utility = CACHE[state]
        else:
            new_move, utility = alphabeta_min_node(state, color, alpha, beta, limit - 1, caching, ordering)
        if utility > curr_max_utility:
            curr_max_utility = utility
            curr_max_move = move
        
        if caching == 1:
            CACHE[state] = (new_move, utility)  # cache the state

        if curr_max_utility >= beta:
            return curr_max_move, curr_max_utility

        alpha = max(alpha, curr_max_utility)

    return curr_max_move, curr_max_utility

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
    return alphabeta_max_node(board, color, float('-inf'), float('inf'), limit, caching, ordering)[0]

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
    # minimax = 1
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
