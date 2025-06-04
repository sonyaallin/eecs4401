"""
An AI player for Othello. 
"""

import random
import sys
import time

# You can use the functions in othello_shared to write your AI
from othello_shared import find_lines, get_possible_moves, get_score, play_move

min_cache = dict()
max_cache = dict()
alpha_cache = dict()
beta_cache = dict()

def eprint(*args, **kwargs): #you can use this for debugging, as it will print to sterr and not stdout
    print(*args, file=sys.stderr, **kwargs)
    
# Method to compute utility value of terminal state
def compute_utility(board, color):
    score = get_score(board)
    if color == 1:
        return score[0] - score[1]
    return score[1] - score[0]


# Better heuristic value of board
def compute_heuristic(board, color):  # not implemented, optional
    # referenced from http://www.radagast.se/othello/Help/strategy.html, here i implemented the mobility score,
    # corner cases, and the frontier score.
    length = len(board)
    corner_score = 0
    frontier_score = 0
    corners = [board[0][0], board[length - 1][0], board[0][length - 1], board[length - 1][length - 1]]
    for c in corners:
        if c == color:
            corner_score += 3

    for i in range(length - 1):
        for j in range(length - 1):
            if board[i][j] == color:
                top = board[i - 1][j] == 0
                bottom = board[i + 1][j] == 0
                left = board[i][j - 1] == 0
                right = board[i][j + 1] == 0
                frontier_score -= (top + bottom + left + right)

    return compute_utility(board, color) + len(get_possible_moves(board, color)) + corner_score + frontier_score

############ MINIMAX ###############################
def minimax_min_node(board, color, limit, caching = 0):
    #IMPLEMENT (and replace the line below)

    if caching:
        if (board, 3 - color) in min_cache:
            return min_cache[(board, 3 - color)]

    children = get_possible_moves(board, 3 - color)
    if not children or limit == 0:
        result = None, compute_utility(board, color)
        if caching:
            min_cache[(board, 3 - color)] = result
        return result
    else:
        smallest = None, float("inf")
        for c in children:
            utility = minimax_max_node(play_move(board, 3 - color, c[0], c[1]), color, limit - 1, caching)[1]
            if utility < smallest[1]:
                smallest = c, utility

        if caching:
            min_cache[(board, 3 - color)] = smallest
        return smallest


def minimax_max_node(board, color, limit, caching = 0): #returns highest possible utility

    if caching:
        if (board, color) in max_cache:
            return max_cache[(board, color)]
    children = get_possible_moves(board, color)
    if not children or limit == 0:
        result = None, compute_utility(board, color)
        if caching:
            max_cache[(board, color)] = result
        return result
    else:
        biggest = None, float("-inf")
        for c in children:
            utility = minimax_min_node(play_move(board, color, c[0], c[1]), color, limit - 1, caching)[1]
            if utility > biggest[1]:
                biggest = c, utility

        if caching:
            max_cache[(board, color)] = biggest
        return biggest

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

    if caching:
        if (board, 3 - color) in beta_cache:
            return beta_cache[(board, 3 - color)]

    children = get_possible_moves(board, 3 - color)
    if not children or limit == 0:
        result = (-1, -1), compute_utility(board, color)
        if caching:
            beta_cache[(board, 3 - color)] = result
        return result
    else:
        smallest = (-1, -1), float("inf")

        next_boards = [(play_move(board, 3 - color, c[0], c[1]), (c[0], c[1])) for c in children]
        if ordering:
            next_boards.sort(key=lambda board: compute_utility(board[0], color))

        for b in next_boards:
            utility = alphabeta_max_node(b[0], color, alpha, beta, limit - 1, caching, ordering)[1]
            if utility < smallest[1]:
                smallest = b[1], utility
            beta = min(beta, smallest[1])
            if beta <= alpha:
                break

        if caching:
            beta_cache[(board, color)] = smallest
        return smallest

def alphabeta_max_node(board, color, alpha, beta, limit, caching = 0, ordering = 0):
    #IMPLEMENT (and replace the line below)
    if caching:
        if (board, color) in alpha_cache:
            return alpha_cache[(board, color)]

    children = get_possible_moves(board, color)
    if not children or limit == 0:
        result = (-1, -1), compute_utility(board, color)
        if caching:
            alpha_cache[(board, color)] = result
        return result
    else:
        biggest = (-1, -1), float("-inf")

        next_boards = [(play_move(board, color, c[0], c[1]), (c[0], c[1])) for c in children]
        if ordering:
            next_boards.sort(key=lambda board: compute_utility(board[0], color), reverse=True)

        for b in next_boards:
            utility = alphabeta_min_node(b[0], color, alpha, beta, limit - 1, caching, ordering)[1]
            if utility > biggest[1]:
                biggest = b[1], utility

            alpha = max(alpha, biggest[1])
            if beta <= alpha:
                break
        if caching:
            alpha_cache[(board, color)] = biggest
        return biggest


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
