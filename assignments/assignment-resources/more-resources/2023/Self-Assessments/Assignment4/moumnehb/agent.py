"""
An AI player for Othello.
"""
max_cache_dict = {}
min_cache_dict = {}

import random
import sys
import time

# You can use the functions in othello_shared to write your AI
from othello_shared import find_lines, get_possible_moves, get_score, play_move


def eprint(*args,
           **kwargs):  # you can use this for debugging, as it will print to sterr and not stdout
    print(*args, file=sys.stderr, **kwargs)


# Method to compute utility value of terminal state
def compute_utility(board, color):
    score = get_score(board)
    if color == 1:
        return score[0] - score[1]
    return score[1] - score[0]

# this heuristic takes into account the number of pieces of each color,
# it weighs pieces on edges more and those in the corner heavier as well,
# it takes into consideration the the number of possible moves that each
# player can take Better heuristic value of board
def compute_heuristic(board, color):  # not implemented, optional
    p1_count = 0
    p2_count = 0
    for i in range(len(board)):
        for j in range(len(board)):
            if board[i][j] == 1:
                p1_count += 1
                # corners
                if i == 0 and j == 0:
                    p1_count += 3
                if i == 0 and j == len(board) - 1:
                    p1_count += 3
                if i == len(board) - 1 and j == len(board) - 1:
                    p1_count += 3
                if i == len(board) - 1 and j == 0:
                    p1_count += 3
                # edges
                if i == 0:
                    p1_count += 2
                if i == len(board) - 1:
                    p1_count += 2
                if j == len(board) - 1:
                    p1_count += 2
                if j == 0:
                    p1_count += 2
            elif board[i][j] == 2:
                p2_count += 1
                # corners
                if i == 0 and j == 0:
                    p2_count += 3
                if i == 0 and j == len(board) - 1:
                    p2_count += 3
                if i == len(board) - 1 and j == len(board) - 1:
                    p2_count += 3
                if i == len(board) - 1 and j == 0:
                    p2_count += 3
                # edges
                if i == 0:
                    p2_count += 2
                if i == len(board) - 1:
                    p2_count += 2
                if j == len(board) - 1:
                    p2_count += 2
                if j == 0:
                    p2_count += 2
    if color == 1:
        #add number of possible moves that can done by each player
        p1_count += len(get_possible_moves(board,color))
        p2_count += len(get_possible_moves(board,opp_color(color)))
        return p1_count - p2_count
    #add number of possible moves that can done by each player
    p2_count += len(get_possible_moves(board,color))
    p1_count += len(get_possible_moves(board,opp_color(color)))
    return p2_count - p1_count


############ MINIMAX ###############################
def minimax_min_node(board, color, limit, caching=0):
    # IMPLEMENT (and replace the line below)
    if caching:
        if board in min_cache_dict:
            return min_cache_dict[board]
        if board in max_cache_dict:
            return max_cache_dict[board]

    possible_m = get_possible_moves(board, opp_color(color))
    if not possible_m or limit == 0:
        return None, compute_utility(board, color)

    min_util = float('inf')
    best_m = None
    for m in possible_m:
        board1 = play_move(board, opp_color(color), m[0], m[1])
        move, util = minimax_max_node(board1, color, limit - 1, caching)
        if caching:
            min_cache_dict[board1] = (m, util)

        if util < min_util:
            best_m = m
            min_util = util

    return best_m, min_util


def minimax_max_node(board, color, limit,
                     caching=0):  # returns highest possible utility
    # IMPLEMENT (and replace the line below)
    if caching:
        if board in min_cache_dict:
            return min_cache_dict[board]
        if board in max_cache_dict:
            return max_cache_dict[board]

    possible_m = get_possible_moves(board, color)
    if not possible_m or limit == 0:
        return None, compute_utility(board, color)

    max_util = -float('inf')
    best_m = None

    for m in possible_m:
        board1 = play_move(board, color, m[0], m[1])
        move, util = minimax_min_node(board1, color, limit - 1, caching)

        if max_util < util:
            best_m = m
            max_util = util

        if caching:
            max_cache_dict[board1] = (m, util)
    return best_m, max_util


def opp_color(color):
    if color == 1:
        return 2
    return 1


def select_move_minimax(board, color, limit, caching=0):
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
    # IMPLEMENT (and replace the line below)
    min_cache_dict.clear()
    max_cache_dict.clear()
    return minimax_max_node(board, color, limit, caching)[0]


############ ALPHA-BETA PRUNING #####################
def alphabeta_min_node(board, color, alpha, beta, limit, caching=0, ordering=0):
    # IMPLEMENT (and replace the line below)
    if caching:
        if board in min_cache_dict:
            return min_cache_dict[board]
        if board in max_cache_dict:
            return max_cache_dict[board]

    possible_m = get_possible_moves(board, opp_color(color))
    if not possible_m or limit == 0:
        return None, compute_utility(board, color)

    min_util = float('inf')
    best_m = None
    for m in possible_m:
        board1 = play_move(board, opp_color(color), m[0], m[1])
        move, utility = alphabeta_max_node(board1, color, alpha, beta,
                                           limit - 1, caching, ordering)
        if utility < min_util:
            best_m = m
            min_util = utility

        if caching:
            min_cache_dict[board1] = (m, utility)

        beta = min(beta, utility)
        if beta <= alpha:
            break

    return best_m, min_util


def alphabeta_max_node(board, color, alpha, beta, limit, caching=0, ordering=0):
    # IMPLEMENT (and replace the line below)
    if caching:
        if board in min_cache_dict:
            return min_cache_dict[board]
        if board in max_cache_dict:
            return max_cache_dict[board]

    m2 = get_possible_moves(board, color)
    if not m2 or limit == 0:
        return None, compute_utility(board, color)

    if ordering:
        m2 = order_moves(board, m2, color)

    best_m = None
    max_util = -float('inf')
    for m in m2:
        board1 = play_move(board, color, m[0], m[1])
        move, utility = alphabeta_min_node(board1, color, alpha, beta,
                                           limit - 1, caching, ordering)

        if utility > max_util:
            best_m = m
            max_util = utility

        if caching:
            max_cache_dict[board1] = (m, utility)

        alpha = max(alpha, utility)
        if beta <= alpha:
            break
    return best_m, max_util


def order_moves(board, possible_m, color):
    """
    :param board:
    :param possible_m:
    :param color:
    :return: list of ordered moves from highest utility to lowest
    """
    utils = {}
    ordered = []
    for m in possible_m:
        board1 = play_move(board, color, m[0], m[1])
        util = compute_utility(board1, color)
        if util in utils:
            if utils[util] != [m]:
                utils[util].append(m)
        else:
            utils[util] = [m]

    sorted_keys = sorted(utils)[::-1]
    for k in sorted_keys:
        ordered.extend(utils[k])
    return ordered


def select_move_alphabeta(board, color, limit, caching=0, ordering=0):
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
    # IMPLEMENT (and replace the line below)
    max_cache_dict.clear()
    min_cache_dict.clear()
    return alphabeta_max_node(board, color, -float('inf'),
                              float('inf'), limit, caching, ordering)[0]


####################################################
def run_ai():
    """
    This function establishes communication with the game manager.
    It first introduces itself and receives its color.
    Then it repeatedly receives the current score and current board state
    until the game is over.
    """
    print("Othello AI")  # First line is the name of this AI
    arguments = input().split(",")

    color = int(
        arguments[0])  # Player color: 1 for dark (goes first), 2 for light.
    limit = int(arguments[1])  # Depth limit
    minimax = int(arguments[2])  # Minimax or alpha beta
    caching = int(arguments[3])  # Caching
    ordering = int(arguments[4])  # Node-ordering (for alpha-beta only)

    if (minimax == 1):
        eprint("Running MINIMAX")
    else:
        eprint("Running ALPHA-BETA")

    if (caching == 1):
        eprint("State Caching is ON")
    else:
        eprint("State Caching is OFF")

    if (ordering == 1):
        eprint("Node Ordering is ON")
    else:
        eprint("Node Ordering is OFF")

    if (limit == -1):
        eprint("Depth Limit is OFF")
    else:
        eprint("Depth Limit is ", limit)

    if (minimax == 1 and ordering == 1):
        eprint("Node Ordering should have no impact on Minimax")

    while True:  # This is the main loop
        # Read in the current game status, for example:
        # "SCORE 2 2" or "FINAL 33 31" if the game is over.
        # The first number is the score for player 1 (dark), the second for player 2 (light)
        next_input = input()
        status, dark_score_s, light_score_s = next_input.strip().split()
        dark_score = int(dark_score_s)
        light_score = int(light_score_s)

        if status == "FINAL":  # Game is over.
            print
        else:
            board = eval(input())  # Read in the input and turn it into a Python
            # object. The format is a list of rows. The
            # squares in each row are represented by
            # 0 : empty square
            # 1 : dark disk (player 1)
            # 2 : light disk (player 2)

            # Select the move and send it to the manager
            if (minimax == 1):  # run this if the minimax flag is given
                movei, movej = select_move_minimax(board, color, limit, caching)
            else:  # else run alphabeta
                movei, movej = select_move_alphabeta(board, color, limit,
                                                     caching, ordering)

            print("{} {}".format(movei, movej))


if __name__ == "__main__":
    run_ai()
