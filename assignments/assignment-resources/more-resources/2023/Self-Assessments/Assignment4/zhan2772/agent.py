"""
An AI player for Othello. 
"""
import random
import sys
import time

# You can use the functions in othello_shared to write your AI
from othello_shared import find_lines, get_possible_moves, get_score, play_move

'''
Description of the heuristic: the new heuristic is the weighted sum of the 
following three aspects:
1. the different of number of coins
2. the different of the number of choice next move
3. the number of corners can be occupied
Since the corner plays a very important role in Othello, it has the highest 
weight.
'''

cache_max = {}
cache_min = {}


def eprint(*args,
           **kwargs):  # you can use this for debugging, as it will print to sterr and not stdout
    print(*args, file=sys.stderr, **kwargs)


def next_player(color):
    return 2 if color == 1 else 1


# Method to compute utility value of terminal state
def compute_utility(board, color):
    p1, p2 = get_score(board)
    if color == 1:
        return p1 - p2
    else:
        return p2 - p1


# Better heuristic value of board
def compute_heuristic(board, color):
    score_1, score_2 = get_score(board)
    choice_1 = len(get_possible_moves(board, color))
    choice_2 = len(get_possible_moves(board, 2 if color == 1 else 1))
    corner_1 = 0
    corner_2 = 0

    n = len(board)
    for loc in [(0, 0), (0, n - 1), (n - 1, 0), (n - 1, n - 1)]:
        if board[loc[0]][loc[1]] == color:
            corner_1 += 1
        elif board[loc[0]][loc[1]] == 2 if color == 1 else 1:
            corner_2 += 1

    coin_diff = ((score_1 - score_2) / (
                score_1 + score_2)) if score_1 + score_2 != 0 else 0
    choice_diff = ((choice_1 - choice_2) / (
                choice_1 + choice_2)) if choice_1 + choice_2 != 0 else 0
    corner_diff = ((corner_1 - corner_2) / (
                corner_1 + choice_2)) if corner_1 + choice_2 != 0 else 0

    return 0.15 * (coin_diff * 100) + 0.15 * (choice_diff * 100) + 0.7 * (
                corner_diff * 100)


############ MINIMAX ###############################
def minimax_min_node(board, color, limit, caching=0):
    moves = get_possible_moves(board, next_player(color))
    if len(moves) == 0 or limit == 0:
        return None, compute_utility(board, color)

    minU = float("Inf")
    next_move = None
    for move in moves:
        new_board = play_move(board, next_player(color), move[0], move[1])
        if caching == 1 and new_board in cache_max.keys():
            U = cache_max.get(new_board)
        else:
            _, U = minimax_max_node(new_board, color, limit - 1, caching)
            if caching == 1:
                cache_max[new_board] = U

        if U < minU:
            minU = U
            next_move = move

    return next_move, minU


def minimax_max_node(board, color, limit, caching=0):
    # returns highest possible utility
    moves = get_possible_moves(board, color)
    if len(moves) == 0 or limit == 0:
        return None, compute_utility(board, color)

    maxU = float("-Inf")
    next_move = None
    for move in moves:
        new_board = play_move(board, color, move[0], move[1])
        if caching == 1 and new_board in cache_min.keys():
            U = cache_min.get(new_board)
        else:
            _, U = minimax_min_node(new_board, color, limit - 1, caching)
            if caching == 1:
                cache_min[new_board] = U

        if U > maxU:
            maxU = U
            next_move = move

    return next_move, maxU


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
    moves = get_possible_moves(board, color)
    if len(moves) == 0 or limit == 0:
        return compute_utility(board, color)

    next_move, _ = minimax_max_node(board, color, limit, caching)

    return next_move


############ ALPHA-BETA PRUNING #####################
def alphabeta_min_node(board, color, alpha, beta, limit, caching=0, ordering=0):
    moves = get_possible_moves(board, next_player(color))
    if len(moves) == 0 or limit == 0:
        return None, compute_utility(board, color)

    if ordering == 1:
        vals = []
        for move in moves:
            new_board = play_move(board, next_player(color), move[0], move[1])
            vals.append(compute_utility(new_board, color))
        _, moves = zip(*sorted(zip(vals, moves), reverse=True))

    ut_val = float("Inf")
    next_move = None
    for move in moves:
        new_board = play_move(board, next_player(color), move[0], move[1])
        if caching == 1 and new_board in cache_max.keys():
            val = cache_max.get(new_board)
        else:
            _, val = alphabeta_max_node(new_board, color, alpha,
                                        beta, limit - 1, caching, ordering)
            if caching == 1:
                cache_max[new_board] = val

        if val < ut_val:
            ut_val = val
            next_move = move
        if beta > ut_val:
            beta = ut_val
            if beta <= alpha:
                break

    return next_move, ut_val


def alphabeta_max_node(board, color, alpha, beta, limit, caching=0, ordering=0):
    moves = get_possible_moves(board, color)
    if len(moves) == 0 or limit == 0:
        return None, compute_utility(board, color)

    if ordering == 1:
        vals = []
        for move in moves:
            new_board = play_move(board, color, move[0], move[1])
            vals.append(compute_utility(new_board, color))
        _, moves = zip(*sorted(zip(vals, moves), reverse=True))

    ut_val = float("-Inf")
    next_move = None
    for move in moves:
        new_board = play_move(board, color, move[0], move[1])
        if caching == 1 and new_board in cache_min.keys():
            val = cache_min.get(new_board)
        else:
            _, val = alphabeta_min_node(new_board, color, alpha,
                                        beta, limit - 1, caching, ordering)
            if caching == 1:
                cache_min[new_board] = val

        if val > ut_val:
            ut_val = val
            next_move = move
        if alpha < ut_val:
            alpha = ut_val
            if beta <= alpha:
                break

    return next_move, ut_val


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
    moves = get_possible_moves(board, color)
    if len(moves) == 0 or limit == 0:
        return compute_utility(board, color)

    next_move, _ = alphabeta_max_node(board, color, float("-Inf"), float("Inf"),
                                      limit, caching, ordering)

    return next_move


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

    if (minimax == 1 and ordering == 1): eprint(
        "Node Ordering should have no impact on Minimax")

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
