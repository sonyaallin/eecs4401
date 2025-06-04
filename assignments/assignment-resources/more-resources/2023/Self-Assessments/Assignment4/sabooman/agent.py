"""
An AI player for Othello.
"""

import random
import sys
import time

# You can use the functions in othello_shared to write your AI
from othello_shared import find_lines, get_possible_moves, get_score, play_move

minimax = {}


def eprint(*args,
           **kwargs):  # you can use this for debugging, as it will print to sterr and not stdout
    print(*args, file=sys.stderr, **kwargs)


# Method to compute utility value of terminal state
def compute_utility(board, color):
    # IMPLEMENT
    curr_play, opponent = get_score(board)
    if color == 1:
        return curr_play - opponent  # change this!
    else:
        return opponent - curr_play


# Better heuristic value of board
def compute_heuristic(board, color):  # not implemented, optional
    """ The compute_heuristic function gives a higher value to nodes at edges
    and corners.
    Otherwise, it is similar to compute utility.
    """
    curr_play, opponent = 0, 0
    for i in range(len(board)):
        for j in range(len(board)):
            # edges
            if i == 0 or i == (len(board) - 1) or j == 0 or j == (
                    len(board) - 1):
                if board[i][j] == 1:
                    curr_play += 2
                if board[i][j] == 2:
                    opponent += 2
            # corners
            elif (i == 0 and j == 0) or (i == 0 and j == len(board) - 1) or \
                    (i == len(board) - 1 and j == 0) or \
                    (i == len(board) - 1) or (j == len(board) - 1):
                if board[i][j] == 1:
                    curr_play += 3
                if board[i][j] == 2:
                    opponent += 3
            # else-where
            elif board[i][j] == 1:
                curr_play += 1
            elif board[i][j] == 2:
                opponent += 1
    if color == 1:
        return curr_play - opponent  # change this!
    else:
        return opponent - curr_play


############ MINIMAX ###############################
def minimax_min_node(board, color, limit, caching=0):
    # IMPLEMENT (and replace the line below)
    # opponent
    opponent = other_player(color)
    movements = get_possible_moves(board, opponent)
    utilities = []

    if not movements or limit == 0:
        return None, compute_utility(board, color)
    for move in movements:
        new_board = play_move(board, opponent, move[0], move[1])
        if caching == 1:
            if new_board in minimax.keys():
                utilities.append(minimax[new_board])
            else:
                min_max_val = \
                    minimax_max_node(new_board, color, limit - 1,
                                     caching)[1]
                utilities.append(min_max_val)
                minimax[new_board] = min_max_val
        else:
            utilities.append(minimax_max_node(new_board, color,
                                              limit - 1, caching)[1])
    best_util = min(utilities)
    return movements[utilities.index(best_util)], best_util


def minimax_max_node(board, color, limit,
                     caching=0):  # returns highest possible utility
    # IMPLEMENT (and replace the line below)
    # AI
    movements = get_possible_moves(board, color)
    utilities = []
    if not movements or limit == 0:
        return None, compute_utility(board, color),
    for move in movements:
        new_board = play_move(board, color, move[0], move[1])
        if caching == 1:
            if new_board in minimax.keys():
                utilities.append(minimax[new_board])
            else:
                min_max_val = \
                    minimax_min_node(new_board, color, limit - 1,
                                     caching)[1]
                utilities.append(min_max_val)
                minimax[new_board] = min_max_val
        else:
            utilities.append(
                minimax_min_node(new_board, color, limit - 1,
                                 caching)[1])
    best_util = max(utilities)
    return movements[utilities.index(best_util)], best_util


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
    chosen_move = minimax_max_node(board, color, limit, caching)
    return chosen_move[0]


def other_player(player):
    """Return the integer value of the opponent player"""
    if player == 1:
        return 2
    return 1


############ ALPHA-BETA PRUNING #####################
def alphabeta_min_node(board, color, alpha, beta, limit, caching=0, ordering=0):
    # IMPLEMENT (and replace the line below)
    opponent = other_player(color)
    movements = get_possible_moves(board, opponent)
    best_util = float("Inf")
    movements_sorted = []
    best_move = ()
    if not movements or limit == 0:
        return None, compute_utility(board, color)
    if ordering == 1:
        for move in movements:
            new_board = play_move(board, opponent, move[0], move[1])
            movements_sorted.append((move, compute_utility(new_board, color)))
        movements_sorted.sort(key=lambda x: x[1], reverse=True)
        movements = [item[0] for item in movements_sorted]

    for move in movements:
        new_board = play_move(board, opponent, move[0], move[1])
        if caching == 1:
            if new_board in minimax.keys():
                best_util = min(best_util, minimax[new_board])
            else:
                min_max_val = alphabeta_max_node(new_board, color,
                                                 alpha, beta, limit - 1,
                                                 caching, ordering)[1]
                best_util = min(best_util, min_max_val)
                minimax[new_board] = min_max_val
        else:
            min_max_val = alphabeta_max_node(new_board, color,
                                             alpha, beta, limit - 1,
                                             caching, ordering)[1]
            best_util = min(best_util, min_max_val)

        if beta > best_util:
            beta = best_util
            best_move = move
            if beta <= alpha:
                break
    return best_move, best_util


def alphabeta_max_node(board, color, alpha, beta, limit, caching=0, ordering=0):
    # IMPLEMENT (and replace the line below)
    movements = get_possible_moves(board, color)
    best_util = -float("Inf")
    best_move = ()
    movements_sorted = []
    if not movements or limit == 0:
        return None, compute_utility(board, color)
    if ordering == 1:
        for move in movements:
            new_board = play_move(board, color, move[0], move[1])
            movements_sorted.append((move, compute_utility(new_board, color)))
        movements_sorted.sort(key=lambda x: x[1], reverse=True)
        movements = [item[0] for item in movements_sorted]
    for move in movements:
        new_board = play_move(board, color, move[0], move[1])
        if caching == 1:
            if new_board in minimax.keys():
                best_util = max(best_util, minimax[new_board])
            else:
                min_max_val = alphabeta_min_node(new_board, color,
                                                 alpha, beta, limit - 1,
                                                 caching, ordering)[1]
                best_util = max(best_util, min_max_val)
                minimax[new_board] = min_max_val
        else:
            min_max_val = alphabeta_min_node(new_board, color,
                                             alpha, beta, limit - 1,
                                             caching, ordering)[1]
            best_util = max(best_util, min_max_val)

        if alpha < best_util:
            alpha = best_util
            best_move = move
            if beta <= alpha:
                break
    return best_move, best_util


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
    chosen_move = alphabeta_max_node(board, color, -float('inf'),
                                     float('inf'), limit, caching, ordering)
    return chosen_move[0]


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

    if minimax == 1:
        eprint("Running MINIMAX")
    else:
        eprint("Running ALPHA-BETA")

    if caching == 1:
        eprint("State Caching is ON")
    else:
        eprint("State Caching is OFF")

    if ordering == 1:
        eprint("Node Ordering is ON")
    else:
        eprint("Node Ordering is OFF")

    if limit == -1:
        eprint("Depth Limit is OFF")
    else:
        eprint("Depth Limit is ", limit)

    if minimax == 1 and ordering == 1:
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
            if minimax == 1:  # run this if the minimax flag is given
                movei, movej = select_move_minimax(board, color, limit, caching)
            else:  # else run alphabeta
                movei, movej = select_move_alphabeta(board, color, limit,
                                                     caching, ordering)

            print("{} {}".format(movei, movej))


if __name__ == "__main__":
    run_ai()
