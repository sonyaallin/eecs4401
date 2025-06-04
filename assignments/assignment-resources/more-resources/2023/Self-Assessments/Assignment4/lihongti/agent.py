"""
An AI player for Othello.
"""

import random
import sys
import time

# You can use the functions in othello_shared to write your AI
from othello_shared import find_lines, get_possible_moves, get_score, play_move


def helper_oppo_color(x: int):
    if x == 1:
        return 2
    if x == 2:
        return 1


def eprint(*args,
           **kwargs):  # you can use this for debugging, as it will print to sterr and not stdout
    print(*args, file=sys.stderr, **kwargs)


# Method to compute utility value of terminal state
def compute_utility(board, color):
    color1, color2 = get_score(board)
    if color == 1:
        return color1 - color2
    else:
        return color2 - color1


# Better heuristic value of board
def compute_heuristic(board, color):  # not implemented, optional
    # IMPLEMENT
    return 0  # change this!


############ MINIMAX ###############################
def minimax_min_node(board, color, limit, caching=0):
    # IMPLEMENT (and replace the line below)
    oppo_color = helper_oppo_color(color)
    move_lst = get_possible_moves(board, oppo_color)
    # min_move, max_util = node_helper(board, oppo_color, limit, caching)
    if not move_lst or limit == 0:
        return None, compute_utility(board, color)

    # child list
    re_max_u = float('inf')
    min_move = None
    for move in move_lst:
        tmp_new_state = play_move(board, oppo_color, move[0], move[1])
        max_move, max_u = minimax_max_node(tmp_new_state, color, limit - 1,
                                           caching)
        # if max_move is None:
        #     return move, compute_utility(board, oppo_color)
        if max_u <= re_max_u:
            re_max_u = max_u
            min_move = move
    return min_move, re_max_u


def minimax_max_node(board, color, limit,
                     caching=0):  # returns highest possible utility
    # IMPLEMENT (and replace the line below)
    move_lst = get_possible_moves(board, color)
    # min_move, max_util = node_helper(board, oppo_color, limit, caching)
    if not move_lst or limit == 0:
        return None, compute_utility(board, color)
    # if limit == 0:
    #     return node_helper(board, color, limit, caching)

    # child list
    re_max_u = float('-inf')
    min_move = None
    test_lst = []
    for move in move_lst:
        tmp_new_state = play_move(board, color, move[0], move[1])
        child_move, child_u = minimax_min_node(tmp_new_state, color, limit - 1,
                                               caching)
        test_lst.append((child_move, child_u, move))
        # if max_move is None:
        #     return move, compute_utility(board, color)
        if child_u > re_max_u:
            re_max_u = child_u
            min_move = move

    return min_move, re_max_u


def node_helper(board, color, limit,
                caching=0):  # returns highest possible utility
    # IMPLEMENT (and replace the line below)
    move_lst = get_possible_moves(board, color)
    if not move_lst:
        return None, compute_utility(board, color)
    state_lst = []
    re_u = float('inf') * -1
    temp_tu = ()
    for move in move_lst:
        temp_state = play_move(board, color, move[0], move[1])
        temp_util = compute_utility(temp_state, color)
        if temp_util >= re_u:
            re_u = temp_util
            temp_tu = move, re_u
    return temp_tu


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

    we_move, we_u = minimax_max_node(board, color, limit, caching)

    # minimax_min_node(board, color, limit, caching)

    return we_move  # change this!


############ ALPHA-BETA PRUNING #####################
def alphabeta_min_node(board, color, alpha, beta, limit, caching=0, ordering=0):
    # IMPLEMENT (and replace the line below)
    oppo_color = helper_oppo_color(color)
    move_lst = get_possible_moves(board, oppo_color)

    if ordering == 1:
        move_lst.sort(key=lambda tmove : compute_utility(play_move(board, color, tmove[0], tmove[1])))
        move_lst.reverse()
    # min_move, max_util = node_helper(board, oppo_color, limit, caching)
    if not move_lst or limit == 0:
        return None, compute_utility(board, color)

    # child list
    re_max_u = float('inf')  # beta
    min_move = None
    for move in move_lst:
        tmp_new_state = play_move(board, oppo_color, move[0], move[1])
        max_move, max_u = alphabeta_max_node(tmp_new_state, color, alpha, beta,
                                             limit - 1, caching)

        if max_u < beta:
            beta = max_u

        if alpha > beta:
            return move, max_u

        if max_u < re_max_u:
            re_max_u = max_u
            min_move = move
    return min_move, re_max_u


def alphabeta_max_node(board, color, alpha, beta, limit, caching=0, ordering=0):
    # IMPLEMENT (and replace the line below)
    move_lst = get_possible_moves(board, color)

    # ordering
    if ordering == 1:
        move_lst.sort(key=lambda tmove : compute_utility(play_move(board, color, tmove[0], tmove[1])))
        move_lst.reverse()

    # min_move, max_util = node_helper(board, oppo_color, limit, caching)
    if not move_lst or limit == 0:
        return None, compute_utility(board, color)

    # child list
    re_max_u = float('-inf')  # alpha
    min_move = None
    test_lst = []
    for move in move_lst:
        tmp_new_state = play_move(board, color, move[0], move[1])
        child_move, child_u = alphabeta_min_node(tmp_new_state, color, alpha,
                                                 beta, limit - 1, caching)
        test_lst.append((child_move, child_u, move))

        if child_u > alpha:
            alpha = child_u

        if alpha > beta:
            return move, child_u

        if child_u > re_max_u:
            re_max_u = child_u
            min_move = move
    return min_move, re_max_u


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
    move, u = alphabeta_max_node(board, color, float('-inf'), float('inf'), limit)
    return move


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
