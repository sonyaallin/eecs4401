"""
An AI player for Othello. 
"""

import random
import sys
import time

# You can use the functions in othello_shared to write your AI
from othello_shared import find_lines, get_possible_moves, get_score, play_move

cache_dict_dark = {}
cache_dict_light = {}


def eprint(*args, **kwargs):  # you can use this for debugging, as it will print to sterr and not stdout
    print(*args, file=sys.stderr, **kwargs)


# Method to compute utility value of terminal state
def compute_utility(board, color):
    d, l = get_score(board)
    if color == 1:
        return d - l
    elif color == 2:
        return l - d
    else:
        return 0


# Better heuristic value of board
def compute_heuristic(board, color):  # not implemented, optional
    """ Description:

        sum of:
            - 10 * ratio of number of color disks to all disks on board
            - (len(board) - 1) * difference in number of corners taken by color vs opponent
            - 10 * ratio of number of possible moves of color to total number of possible moves
    """
    # number of disks
    d, l = get_score(board)

    # corners taken
    d_corners_taken = 0
    l_corners_taken = 0
    corners = [(0, 0), (0, len(board) - 1), (len(board) - 1, 0), (len(board) - 1, len(board) - 1)]
    for i, j in corners:
        if board[i][j] == 1:
            d_corners_taken += 1
        elif board[i][j] == 2:
            l_corners_taken += 1

    # number of possible moves
    d_moves = len(get_possible_moves(board, 1))
    l_moves = len(get_possible_moves(board, 2))

    if color == 1:
        p = d / (l + d) * 10
        c = (len(board) - 1) * (d_corners_taken - l_corners_taken)
        if l_moves or d_moves:
            m = d_moves / (d_moves + l_moves) * 10
        else:
            m = 0
        return p + c + m
    elif color == 2:
        p = l / (l + d) * 10
        c = (len(board) - 1) * (l_corners_taken - d_corners_taken)
        if l_moves or d_moves:
            m = l_moves / (d_moves + l_moves) * 10
        else:
            m = 0
        return p + c + m
    else:
        return 0


############ MINIMAX ###############################
def minimax_min_node(board, color, limit, caching=0):
    moves = get_possible_moves(board, 3 - color)
    if not moves or limit == 0:
        return tuple(), compute_utility(board, color)
    min_move = tuple()
    min_utility = float("inf")
    for move in moves:
        new_board = play_move(board, 3 - color, move[0], move[1])
        if caching:
            if color == 1:
                if new_board in cache_dict_dark:
                    new_utility = cache_dict_dark[new_board]
                else:
                    new_utility = minimax_max_node(new_board, color, limit - 1, caching)[1]
                    cache_dict_dark[new_board] = new_utility
            else:
                if new_board in cache_dict_light:
                    new_utility = cache_dict_light[new_board]
                else:
                    new_utility = minimax_max_node(new_board, color, limit - 1, caching)[1]
                    cache_dict_light[new_board] = new_utility
        else:
            new_utility = minimax_max_node(new_board, color, limit - 1, caching)[1]
        if min_utility > new_utility:
            min_utility = new_utility
            min_move = move
    return min_move, min_utility


def minimax_max_node(board, color, limit, caching=0):  # returns highest possible utility
    moves = get_possible_moves(board, color)
    if not moves or limit == 0:
        return tuple(), compute_utility(board, color)
    max_move = tuple()
    max_utility = float("-inf")
    for move in moves:
        new_board = play_move(board, color, move[0], move[1])
        if caching:
            if color == 1:
                if new_board in cache_dict_dark:
                    new_utility = cache_dict_dark[new_board]
                else:
                    new_utility = minimax_min_node(new_board, color, limit - 1, caching)[1]
                    cache_dict_dark[new_board] = new_utility
            else:
                if new_board in cache_dict_light:
                    new_utility = cache_dict_light[new_board]
                else:
                    new_utility = minimax_min_node(new_board, color, limit - 1, caching)[1]
                    cache_dict_light[new_board] = new_utility
        else:
            new_utility = minimax_min_node(new_board, color, limit - 1, caching)[1]
        if max_utility < new_utility:
            max_utility = new_utility
            max_move = move
    return max_move, max_utility


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
    move, utility = minimax_max_node(board, color, limit, caching)
    return move


############ ALPHA-BETA PRUNING #####################
def alphabeta_min_node(board, color, alpha, beta, limit, caching=0, ordering=0):
    moves = get_possible_moves(board, 3 - color)
    if not moves or limit == 0:
        return tuple(), compute_utility(board, color)
    ut_val = float("inf")
    ut_move = tuple()
    if ordering:
        new_boards = [play_move(board, 3 - color, i, j) for i, j in moves]
        board_utils = [compute_utility(new_board, color) for new_board in new_boards]
        while new_boards:
            m = max(board_utils)
            best_index = board_utils.index(m)
            board_utils.remove(m)
            new_board = new_boards.pop(best_index)
            move = moves.pop(best_index)
            if caching:
                if color == 1:
                    if new_board in cache_dict_dark:
                        new_utility = cache_dict_dark[new_board]
                    else:
                        new_utility = alphabeta_max_node(new_board, color, alpha, beta, limit - 1, caching, ordering)[1]
                        cache_dict_dark[new_board] = new_utility
                else:
                    if new_board in cache_dict_light:
                        new_utility = cache_dict_light[new_board]
                    else:
                        new_utility = alphabeta_max_node(new_board, color, alpha, beta, limit - 1, caching, ordering)[1]
                        cache_dict_light[new_board] = new_utility
            else:
                new_utility = alphabeta_max_node(new_board, color, alpha, beta, limit - 1, caching, ordering)[1]
            if ut_val < new_utility:
                ut_val = new_utility
                ut_move = move
            if alpha < ut_val:
                alpha = ut_val
                if beta <= alpha:
                    break
        return ut_move, ut_val

    for move in moves:
        new_board = play_move(board, 3 - color, move[0], move[1])
        if caching:
            if color == 1:
                if new_board in cache_dict_dark:
                    new_utility = cache_dict_dark[new_board]
                else:
                    new_utility = alphabeta_max_node(new_board, color, alpha, beta, limit - 1, caching, ordering)[1]
                    cache_dict_dark[new_board] = new_utility
            else:
                if new_board in cache_dict_light:
                    new_utility = cache_dict_light[new_board]
                else:
                    new_utility = alphabeta_max_node(new_board, color, alpha, beta, limit - 1, caching, ordering)[1]
                    cache_dict_light[new_board] = new_utility
        else:
            new_utility = alphabeta_max_node(new_board, color, alpha, beta, limit - 1, caching, ordering)[1]
        if new_utility < ut_val:
            ut_val = new_utility
            ut_move = move
        if beta > ut_val:
            beta = ut_val
            if beta <= alpha:
                break
    return ut_move, ut_val


def alphabeta_max_node(board, color, alpha, beta, limit, caching=0, ordering=0):
    moves = get_possible_moves(board, color)
    if not moves or limit == 0:
        return tuple(), compute_utility(board, color)
    ut_val = float("-inf")
    ut_move = tuple()
    if ordering:
        new_boards = [play_move(board, color, i, j) for i, j in moves]
        board_utils = [compute_utility(new_board, color) for new_board in new_boards]
        while new_boards:
            m = max(board_utils)
            best_index = board_utils.index(m)
            board_utils.remove(m)
            new_board = new_boards.pop(best_index)
            move = moves.pop(best_index)
            if caching:
                if color == 1:
                    if new_board in cache_dict_dark:
                        new_utility = cache_dict_dark[new_board]
                    else:
                        new_utility = alphabeta_min_node(new_board, color, alpha, beta, limit - 1, caching, ordering)[1]
                        cache_dict_dark[new_board] = new_utility
                else:
                    if new_board in cache_dict_light:
                        new_utility = cache_dict_light[new_board]
                    else:
                        new_utility = alphabeta_min_node(new_board, color, alpha, beta, limit - 1, caching, ordering)[1]
                        cache_dict_light[new_board] = new_utility
            else:
                new_utility = alphabeta_min_node(new_board, color, alpha, beta, limit - 1, caching, ordering)[1]
            if ut_val < new_utility:
                ut_val = new_utility
                ut_move = move
            if alpha < ut_val:
                alpha = ut_val
                if beta <= alpha:
                    break
        return ut_move, ut_val
    for move in moves:
        new_board = play_move(board, color, move[0], move[1])
        if caching:
            if color == 1:
                if new_board in cache_dict_dark:
                    new_utility = cache_dict_dark[new_board]
                else:
                    new_utility = alphabeta_min_node(new_board, color, alpha, beta, limit - 1, caching, ordering)[1]
                    cache_dict_dark[new_board] = new_utility
            else:
                if new_board in cache_dict_light:
                    new_utility = cache_dict_light[new_board]
                else:
                    new_utility = alphabeta_min_node(new_board, color, alpha, beta, limit - 1, caching, ordering)[1]
                    cache_dict_light[new_board] = new_utility
        else:
            new_utility = alphabeta_min_node(new_board, color, alpha, beta, limit - 1, caching, ordering)[1]
        if ut_val < new_utility:
            ut_val = new_utility
            ut_move = move
        if alpha < ut_val:
            alpha = ut_val
            if beta <= alpha:
                break
    return ut_move, ut_val


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
    move, utility = alphabeta_max_node(board, color, float("-inf"), float("inf"), limit, caching, ordering)
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

    color = int(arguments[0])  # Player color: 1 for dark (goes first), 2 for light.
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

    if (minimax == 1 and ordering == 1): eprint("Node Ordering should have no impact on Minimax")

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
                movei, movej = select_move_alphabeta(board, color, limit, caching, ordering)

            print("{} {}".format(movei, movej))


if __name__ == "__main__":
    run_ai()
