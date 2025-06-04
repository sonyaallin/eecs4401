"""
An AI player for Othello.
"""

import random
import sys
import time

# You can use the functions in othello_shared to write your AI
from othello_shared import find_lines, get_possible_moves, get_score, play_move

CACHE = {}  # key: board, val: Tuple(move, utility)


def eprint(*args, **kwargs):  # you can use this for debugging, as it will print to sterr and not stdout
    print(*args, file=sys.stderr, **kwargs)

# Method to compute utility value of terminal state


def compute_utility(board, color):
    p1, p2 = get_score(board)
    if color == 1:
        return p1 - p2
    return p2 - p1

# Better heuristic value of board


def compute_heuristic(board, color):  # not implemented, optional
    # IMPLEMENT

    return compute_utility(board, color)  # PLACEHOLDER

    return 0  # change this!

############ MINIMAX ###############################


def minimax_min_node(board, color, limit, caching=0):
    # IMPLEMENT (and replace the line below)

    if color == 1:
        opp_color = 2
    else:
        opp_color = 1

    moves_list = get_possible_moves(board, opp_color)
    if limit == 0 and len(moves_list) != 0:
        return (None, compute_heuristic(board, color))
    elif len(moves_list) == 0:
        return (None, compute_utility(board, color))

    min_utility = float('inf')
    min_move = None

    for move in moves_list:
        new_board = play_move(board, opp_color, move[0], move[1])
        if caching and new_board in CACHE:
            temp_utility = CACHE[new_board]
        else:
            temp_utility = minimax_max_node(
                new_board, color, limit - 1, caching)
            if caching:
                # CACHE.setdefault(new_board, temp_utility)
                CACHE[new_board] = temp_utility
        if temp_utility[1] < min_utility:
            min_utility = temp_utility[1]
            min_move = move

    return (min_move, min_utility)


def minimax_max_node(board, color, limit, caching=0):  # returns highest possible utility
    # IMPLEMENT (and replace the line below)

    moves_list = get_possible_moves(board, color)

    if limit == 0 and len(moves_list) != 0:
        return (None, compute_heuristic(board, color))
    elif len(moves_list) == 0:
        return (None, compute_utility(board, color))

    max_utility = -float('inf')
    max_move = None

    for move in moves_list:
        new_board = play_move(board, color, move[0], move[1])
        if caching and new_board in CACHE:
            temp_utility = CACHE[new_board]
        else:
            temp_utility = minimax_min_node(
                new_board, color, limit - 1, caching)
            if caching:
                # CACHE.setdefault(new_board, temp_utility)
                CACHE[new_board] = temp_utility
        if temp_utility[1] > max_utility:
            max_utility = temp_utility[1]
            max_move = move

    return (max_move, max_utility)


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
    if not limit:
        depth = -1
    else:
        depth = limit

    best_move = minimax_max_node(board, color, depth, caching)
    return best_move[0]

############ ALPHA-BETA PRUNING #####################


def alphabeta_min_node(board, color, alpha, beta, limit, caching=0, ordering=0):
    # IMPLEMENT (and replace the line below)

    if color == 1:
        opp_color = 2
    else:
        opp_color = 1

    moves_list = get_possible_moves(board, opp_color)
    if limit == 0 and len(moves_list) != 0:
        return (None, compute_heuristic(board, color))
    elif len(moves_list) == 0:
        return (None, compute_utility(board, color))

    min_move = None

    order_list = []
    if ordering:
        for move in moves_list:
            new_board = play_move(board, opp_color, move[0], move[1])
            utility = compute_utility(new_board, color)
            order_list.append((utility, new_board, move))
        order_list.sort(reverse=True)

    for i in range(len(moves_list)):
        if order_list:
            move = order_list[i][2]
            new_board = order_list[i][1]
        else:
            move = moves_list[i]
            new_board = play_move(board, opp_color, move[0], move[1])
        if caching and new_board in CACHE:
            temp_utility = CACHE[new_board]
        else:
            temp_utility = alphabeta_max_node(
                new_board, color, alpha, beta, limit - 1, caching, ordering)
            if caching:
                CACHE.setdefault(new_board, temp_utility)
                # CACHE[new_board] = temp_utility
        if temp_utility[1] < beta:
            beta = temp_utility[1]
            min_move = move
        if alpha >= beta:
            break

    return (min_move, beta)


def alphabeta_max_node(board, color, alpha, beta, limit, caching=0, ordering=0):
    # IMPLEMENT (and replace the line below)

    moves_list = get_possible_moves(board, color)
    if limit == 0 and len(moves_list) != 0:
        return (None, compute_heuristic(board, color))
    elif len(moves_list) == 0:
        return (None, compute_utility(board, color))

    max_move = None

    order_list = []
    if ordering:
        for move in moves_list:
            new_board = play_move(board, color, move[0], move[1])
            utility = compute_utility(new_board, color)
            order_list.append((utility, new_board, move))
        order_list.sort(reverse=True)

    for i in range(len(moves_list)):
        if order_list:
            move = order_list[i][2]
            new_board = order_list[i][1]
        else:
            move = moves_list[i]
            new_board = play_move(board, color, move[0], move[1])
        if caching and new_board in CACHE:
            temp_utility = CACHE[new_board]
        else:
            temp_utility = alphabeta_min_node(
                new_board, color, alpha, beta, limit - 1, caching, ordering)
            if caching:
                CACHE.setdefault(new_board, temp_utility)
                # CACHE[new_board] = temp_utility
        if temp_utility[1] > alpha:
            alpha = temp_utility[1]
            max_move = move
        if alpha >= beta:
            break

    return (max_move, alpha)


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
    if not limit:
        depth = -1
    else:
        depth = limit

    best_move = alphabeta_max_node(
        board, color, -float('inf'), float('inf'), depth, caching, ordering)
    return best_move[0]

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

    # Player color: 1 for dark (goes first), 2 for light.
    color = int(arguments[0])
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
            # Read in the input and turn it into a Python
            board = eval(input())
            # object. The format is a list of rows. The
            # squares in each row are represented by
            # 0 : empty square
            # 1 : dark disk (player 1)
            # 2 : light disk (player 2)

            # Select the move and send it to the manager
            if (minimax == 1):  # run this if the minimax flag is given
                movei, movej = select_move_minimax(
                    board, color, limit, caching)
            else:  # else run alphabeta
                movei, movej = select_move_alphabeta(
                    board, color, limit, caching, ordering)

            print("{} {}".format(movei, movej))


if __name__ == "__main__":
    run_ai()
