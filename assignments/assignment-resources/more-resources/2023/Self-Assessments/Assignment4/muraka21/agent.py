"""
An AI player for Othello.
"""

import random
from shutil import move
import sys
import time

# You can use the functions in othello_shared to write your AI
from othello_shared import find_lines, get_possible_moves, get_score, play_move


# Explanation for my heuristic:
# In the heuristic I created I wanted to give more weight to pieces that are
# in the corners and beside walls, because the pieces in those places are
# less likely to get turned. I also gave more weight to pieces in the corners
# compared to pieces beside walls, because pieces that are in the corners
# cannot be turned no matter what. So, I started by considering the utility
# of the board to have a base value, and then for every piece in the corners
# I add 2 to the utility of the board and for every piece beside walls I add
# 1 to the utility.


# ----------------------------- Global Variables ------------------------------
CACHE = {}
# ----------------------------------------------------------------------------

# ----------------------------- Helper Functions -----------------------------
def move_util(board, color, move):
    new_board = play_move(board, color, move[0], move[1])
    return compute_utility(new_board, color)
# ----------------------------------------------------------------------------


def eprint(*args, **kwargs): #you can use this for debugging, as it will print to sterr and not stdout
    print(*args, file=sys.stderr, **kwargs)

# Method to compute utility value of terminal state
def compute_utility(board, color):
    #IMPLEMENT
    p1_score, p2_score = get_score(board)
    if color == 1:
        util = p1_score - p2_score
    else:
        util = p2_score - p1_score
    return util

# Better heuristic value of board
def compute_heuristic(board, color): #not implemented, optional
    #IMPLEMENT
    # I want to give emphasis to pieces besides walls and corners
    util = compute_utility(board, color)
    corners = [(0, 0), (0, -1), (-1, 0), (-1, -1)]
    # considering corners
    for corner in corners:
        if board[corner[0]][corner[1]] == color:
            util += 2

    # considering walls
    for i in range(len(board[0])):
        if (0, i) not in corners and board[0][i] == color:
            util += 1
        if (-1, i) not in corners and board[-1][i] == color:
            util += 1
        if (i, 0) not in corners and board[i][0] == color:
            util += 1
        if (i, -1) not in corners and board[i][-1] == color:
            util += 1

    return util #change this!

############ MINIMAX ###############################
def minimax_min_node(board, color, limit, caching = 0):
    #IMPLEMENT (and replace the line below)
    if color == 1:
        other_color = 2
    else:
        other_color = 1

    moves = get_possible_moves(board, other_color)

    # checking for caching
    if caching and board in CACHE:
        return CACHE[board]

    # base case if a terminal was reached
    if moves == []:
        util = compute_utility(board,  color)
        return None, util

    elif limit == 0:
        # maybe use another heuristic
        util = compute_utility(board, color)
        return None, util

    for i in range(len(moves)):
        new_board = play_move(board, other_color, moves[i][0], moves[i][1])
        max_move, util = minimax_max_node(new_board, color, limit - 1, caching)

        if i == 0 or util < min_util:
           min_util = util
           min_move = moves[i]

    return min_move, min_util


def minimax_max_node(board, color, limit, caching = 0): #returns highest possible utility
    #IMPLEMENT (and replace the line below)
    moves = get_possible_moves(board, color)

    # checking for caching
    if caching and board in CACHE:
        return CACHE[board]

    # base case if a terminal was reached
    if moves == []:
        util = compute_utility(board, color)
        return None, util

    elif limit == 0:
        # maybe use another heuristic
        util = compute_utility(board, color)
        return None, util

    for i in range(len(moves)):
        new_board = play_move(board, color, moves[i][0], moves[i][1])
        min_move, util = minimax_min_node(new_board, color, limit - 1, caching)

        if i == 0 or util > max_util:
           max_util = util
           max_move = moves[i]

    return max_move, max_util

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
    max_move, util = minimax_max_node(board, color, limit, caching)
    CACHE.setdefault(board, (max_move, util))
    return max_move #change this!

############ ALPHA-BETA PRUNING #####################
def alphabeta_min_node(board, color, alpha, beta, limit, caching = 0, ordering = 0):
    #IMPLEMENT (and replace the line below)
    curr_beta = beta
    if color == 1:
        other_color = 2
    else:
        other_color = 1
    moves = get_possible_moves(board, other_color)

    # checking for caching
    if caching and board in CACHE:
        return CACHE[board]

    # checking for ordering
    if ordering:
        # sort() will sort moves based on the utility of making the move, hence
        # the move that will lead to the highest utility will be the first in
        # the list
        moves.sort(key=lambda m: move_util(board, other_color, m), reverse=True)

    # checking if there are no moves left
    if moves == []:
        util = compute_utility(board, color)
        return None, util

    elif limit == 0:
        # maybe use another heuristic
        util = compute_utility(board, color)
        return None, util

    for i in range(len(moves)):
        new_board = play_move(board, other_color, moves[i][0], moves[i][1])
        max_move, util = alphabeta_max_node(new_board, color, alpha, curr_beta, limit - 1, caching, ordering)

        if i == 0 or util < min_util:
            min_util = util
            min_move = moves[i]

        if util < curr_beta:
            curr_beta = util

        # checking alpha beta condition
        if  curr_beta <= alpha:
            break

    return min_move, min_util

def alphabeta_max_node(board, color, alpha, beta, limit, caching = 0, ordering = 0):
    #IMPLEMENT (and replace the line below)
    moves = get_possible_moves(board, color)
    curr_alpha = alpha

    if caching == 1 and board in CACHE:
        return CACHE[board]

    # checking for ordering
    if ordering:
        # sort() will sort moves based on the utility of making the move, hence
        # the move that will lead to the highest utility will be the first in
        # the list
        moves.sort(key=lambda m: move_util(board, color, m), reverse=True)

    # checking if there are no moves left
    if moves == []:
        util = compute_utility(board, color)
        return None, util

    elif limit == 0:
        # maybe use another heuristic
        util = compute_utility(board, color)
        return None, util

    for i in range(len(moves)):
        new_board = play_move(board, color, moves[i][0], moves[i][1])
        min_move, util = alphabeta_min_node(new_board, color, curr_alpha, beta, limit - 1, caching, ordering)

        if i == 0 or util > max_util:
           max_util = util
           max_move = moves[i]

        if util > curr_alpha:
            curr_alpha = util

        # checking alpha beta condition
        if  beta <= curr_alpha:
            break

    return max_move, max_util


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
    max_move, util = alphabeta_max_node(board, color, float('-inf'), float('inf'), limit, caching, ordering)
    CACHE.setdefault(board, (max_move, util))
    return max_move #change this!

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
