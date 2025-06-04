"""
An AI player for Othello. 
"""

from platform import node
import random
import sys
import time

# You can use the functions in othello_shared to write your AI
from othello_shared import find_lines, get_possible_moves, get_score, play_move

caching_states = {}

def eprint(*args, **kwargs): #you can use this for debugging, as it will print to sterr and not stdout
    print(*args, file=sys.stderr, **kwargs)
    
# Method to compute utility value of terminal state
def compute_utility(board, color):
    scores = get_score(board)
    if color == 1:
        return scores[0] - scores[1]
    else:
        return scores[1] - scores[0]

# Better heuristic value of board
def compute_heuristic(board, color): #not implemented, optional
    """
    The heuristic I've chosen involves calculating the score similar to how it does
    for compute_utility, and additonally every player whose possible moves include 
    a corner case I add 1 to that player's score. A player which has corner moves 
    in their possible moves, has additional likelihood of winning, as indicated by 
    the higher score of the player.
    """

    other_color = get_other_color(color)
    possible_moves1 = get_possible_moves(board, color)
    possible_moves2 = get_possible_moves(board, other_color)
    dimension = len(board)
    corners = [(0, 0), (0, dimension -1), (dimension - 1, 0), (dimension - 1, dimension - 1)]
    scores = get_score(board)
    score1 = scores[0]
    score2 = scores[1]

    for move in corners:
        if move in possible_moves1:
            score1 += 1
        if move in possible_moves2:
            score2 += 1
    if color == 1:
        check = scores[0] - scores[1]
    else:
        check = scores[1] - scores[0]

    return check

############ MINIMAX ###############################
def minimax_min_node(board, color, limit, caching = 0):
    
    other_color = get_other_color(color)
    possible_moves = get_possible_moves(board, other_color)
    min_utility = sys.maxsize
    min_move = (0, 0)

    if not possible_moves or limit == 0:
        return (None, compute_utility(board, color))
    for move in possible_moves:
        new_state = play_move(board, other_color, move[0], move[1])
        if caching == 1:
            if new_state in caching_states:
                result = caching_states[new_state]
            else:
                if limit > 0:
                    result = minimax_max_node(new_state, color, limit - 1, caching)
                else: 
                    result = minimax_max_node(new_state, color, limit, caching)
                caching_states[new_state] = result
        else:
            if limit > 0:
                result = minimax_max_node(new_state, color, limit - 1, caching)
            else: 
                result = minimax_max_node(new_state, color, limit, caching)
        if result[1] < min_utility:
            min_utility = result[1]
            min_move = move
    return (min_move, min_utility)

def minimax_max_node(board, color, limit, caching = 0): #returns highest possible utility
    
    possible_moves = get_possible_moves(board, color)
    max_utility = -sys.maxsize - 1
    max_move = (0, 0)

    if not possible_moves or limit == 0:
        return (None, compute_utility(board, color))
    for move in possible_moves:
        new_state = play_move(board, color, move[0], move[1])
        if caching == 1:
            if new_state in caching_states:
                result = caching_states[new_state]
            else:
                if limit > 0:
                    result = minimax_min_node(new_state, color, limit - 1, caching)
                else: 
                    result = minimax_min_node(new_state, color, limit, caching)
                caching_states[new_state] = result
        else:
            if limit > 0:
                result = minimax_min_node(new_state, color, limit - 1, caching)
            else: 
                result = minimax_min_node(new_state, color, limit, caching)
        if result[1] > max_utility:
            max_utility = result[1]
            max_move = move
    return (max_move, max_utility)

def get_other_color(color):
    """
    Returns the color of the opponent
    """
    if color == 1:
        return 2
    return 1

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
    return minimax_max_node(board, color, limit, caching)[0]


############ ALPHA-BETA PRUNING #####################
def alphabeta_min_node(board, color, alpha, beta, limit, caching = 0, ordering = 0):
    
    other_color = get_other_color(color)
    possible_moves = get_possible_moves(board, other_color)
    min_utility = float('inf')
    min_move = (0, 0)

    if ordering == 1:
        possible_moves = node_ordering(possible_moves, board, color)

    if not possible_moves or limit == 0:
        return (None, compute_utility(board, color))
    for move in possible_moves:
        new_state = play_move(board, other_color, move[0], move[1])
        if caching == 1:
            if new_state in caching_states:
                result = caching_states[new_state]
            else:
                if limit > 0:
                    result = alphabeta_max_node(new_state, color, alpha, beta, limit - 1, caching, ordering)
                else: 
                    result = alphabeta_max_node(new_state, color, alpha, beta, limit, caching, ordering)
                caching_states[new_state] = result
        else:
            if limit > 0:
                result = alphabeta_max_node(new_state, color, alpha, beta, limit - 1, caching, ordering)
            else: 
                result = alphabeta_max_node(new_state, color, alpha, beta, limit, caching, ordering)
        min_utility = min(min_utility, result[1])
        if beta > min_utility:
            beta = min_utility
            min_move = move
            if beta <= alpha:
                break

    return (min_move, min_utility)

def alphabeta_max_node(board, color, alpha, beta, limit, caching = 0, ordering = 0):
    
    possible_moves = get_possible_moves(board, color)
    max_utility = -float('inf')
    max_move = (0, 0)

    if not possible_moves or limit == 0:
        return (None, compute_utility(board, color))

    if ordering == 1:
        possible_moves = node_ordering(possible_moves, board, color)

    for move in possible_moves:
        new_state = play_move(board, color, move[0], move[1])
        if caching == 1:
            if new_state in caching_states:
                result = caching_states[new_state]
            else:
                if limit > 0:
                    result = alphabeta_min_node(new_state, color, alpha, beta, limit - 1, caching, ordering)
                else: 
                    result = alphabeta_min_node(new_state, color, alpha, beta, limit, caching, ordering)
                caching_states[new_state] = result
        else:
            if limit > 0:
                result = alphabeta_min_node(new_state, color, alpha, beta, limit - 1, caching, ordering)
            else: 
                result = alphabeta_min_node(new_state, color, alpha, beta, limit, caching, ordering)
        max_utility = max(max_utility, result[1])
        if alpha < max_utility:
            alpha = max_utility
            max_move = move
            if beta <= alpha:
                break

    return (max_move, max_utility)

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
    return alphabeta_max_node(board, color, -float('inf'), float('inf'), limit, caching, ordering)[0]

def node_ordering(possible_moves, board, color):
    """
    Orders the moves in the order of descending utilities
    """
    temp, result = [], []
    for move in possible_moves:
        new_state = play_move(board, color, move[0], move[1])
        temp.append((compute_utility(new_state, color), move))
    temp.sort(reverse=True)
    for items in temp:
        result.append(items[1])
    return result

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