"""
An AI player for Othello.
"""

"""
My heuristic function is very simple.
If the game is over, it will return infinity or negative infinity, depending on the winner of the game.
If the game is not over, it will simply return the current utility value of the board.
"""

import random
import sys
import time

# You can use the functions in othello_shared to write your AI
from othello_shared import find_lines, get_possible_moves, get_score, play_move

cache = {}


def eprint(*args, **kwargs):  # you can use this for debugging, as it will print to sterr and not stdout
    print(*args, file=sys.stderr, **kwargs)


# Method to compute utility value of terminal state
def compute_utility(board, color):
    p1_count, p2_count = get_score(board)

    if color == 1:
        return p1_count - p2_count

    return p2_count - p1_count


# Better heuristic value of board
def compute_heuristic(board, color):
    utility = compute_utility(board, color)

    if not get_possible_moves(board, color):
        if utility < 0:
            return float('-inf')
        if utility > 0 and not get_possible_moves(board, 3 - color):
            return float('inf')

    return utility


# HELPER FUNCTIONS ##################################
def get_cached_value(board, caching):
    if caching == 1 and board in cache:
        return cache[board]


def common_minimax_start(board, original_color, color, limit, caching, possible_moves):
    if limit == 0 or not possible_moves:
        heuristic = compute_heuristic(board, original_color)

        if original_color != color:
            heuristic = -heuristic

        move, value = None, heuristic

        if caching == 1:
            cache[board] = move, value

        return move, value


def common_minimax_end(board, decider, moves, nodes, caching):
    best_move_index = decider(range(len(nodes)), key=lambda i: nodes[i][1])
    move, value = moves[best_move_index], nodes[best_move_index][1]

    if caching == 1:
        cache[board] = move, value

    return move, value


# MINIMAX ###########################################
def minimax_min_node(board, color, limit, caching=0):
    cached_value = get_cached_value(board, caching)
    if cached_value is not None and (cached_value[0] is not None or abs(cached_value[1]) == float('inf')):
        return cached_value

    opposite_color = 3 - color
    possible_moves = get_possible_moves(board, opposite_color)
    common = common_minimax_start(board, color, opposite_color, limit, caching, possible_moves)

    if common is not None:
        return common

    move_results = [play_move(board, opposite_color, i, j) for i, j in possible_moves]
    max_nodes = list(map(lambda new_board: minimax_max_node(new_board, color, limit - 1, caching), move_results))

    return common_minimax_end(board, min, possible_moves, max_nodes, caching)


def minimax_max_node(board, color, limit, caching=0):
    cached_value = get_cached_value(board, caching)
    if cached_value is not None and (cached_value[0] is not None or abs(cached_value[1]) == float('inf')):
        return cached_value

    possible_moves = get_possible_moves(board, color)
    common = common_minimax_start(board, color, color, limit, caching, possible_moves)

    if common is not None:
        return common

    move_results = [play_move(board, color, i, j) for i, j in possible_moves]
    min_nodes = list(map(lambda new_board: minimax_min_node(new_board, color, limit - 1, caching), move_results))

    return common_minimax_end(board, max, possible_moves, min_nodes, caching)


def select_move_minimax(board, color, limit, caching=0):
    """
    Given a board and a player color, decide on a move.
    The return value is a tuple of integers (i,j), where
    i is the column and j is the row on the board.

    Note that other parameters are accepted by this function:
    If limit is a positive integer, your code should enforce a depth limit that is equal to the value of the parameter.
    Search only to nodes at a depth-limit equal to the limit. If nodes at this level are non-terminal return a heuristic
    value (see compute_utility)
    If caching is ON (i.e. 1), use state caching to reduce the number of state evaluations.
    If caching is OFF (i.e. 0), do NOT use state caching to reduce the number of state evaluations.
    """
    return minimax_max_node(board, color, limit, caching)[0]


# ALPHA-BETA PRUNING ################################
def alphabeta_min_node(board, color, alpha, beta, limit, caching=0, ordering=0):
    cached_value = get_cached_value(board, caching)
    if cached_value is not None and (cached_value[0] is not None or abs(cached_value[1]) == float('inf')):
        return cached_value

    opposite_color = 3 - color
    possible_moves = get_possible_moves(board, opposite_color)
    common = common_minimax_start(board, color, opposite_color, limit, caching, possible_moves)

    if common is not None:
        return common

    value = float('inf')
    max_nodes = []

    move_results = [play_move(board, opposite_color, i, j) for i, j in possible_moves]

    if ordering == 1:
        move_result_utilities = map(lambda b: compute_utility(b, color), move_results)
        _, possible_moves, move_results = zip(*sorted(zip(move_result_utilities, possible_moves, move_results), key=lambda x: x[0], reverse=True))

    for successor in move_results:
        max_nodes += [alphabeta_max_node(successor, color, alpha, beta, limit - 1, caching, ordering)]
        value = min(value, max_nodes[-1][1])

        if beta > value:
            beta = value

            if beta <= alpha:
                break

    return common_minimax_end(board, min, possible_moves, max_nodes, caching)


def alphabeta_max_node(board, color, alpha, beta, limit, caching=0, ordering=0):
    cached_value = get_cached_value(board, caching)
    if cached_value is not None and (cached_value[0] is not None or abs(cached_value[1]) == float('inf')):
        return cached_value

    possible_moves = get_possible_moves(board, color)
    common = common_minimax_start(board, color, color, limit, caching, possible_moves)

    if common is not None:
        return common

    value = float('-inf')
    min_nodes = []

    move_results = [play_move(board, color, i, j) for i, j in possible_moves]

    if ordering == 1:
        move_result_utilities = map(lambda b: compute_utility(b, color), move_results)
        _, possible_moves, move_results = zip(*sorted(zip(move_result_utilities, possible_moves, move_results), key=lambda x: x[0], reverse=True))

    for successor in move_results:
        min_nodes += [alphabeta_min_node(successor, color, alpha, beta, limit - 1, caching, ordering)]
        value = max(value, min_nodes[-1][1])

        if alpha < value:
            alpha = value

            if beta <= alpha:
                break

    return common_minimax_end(board, max, possible_moves, min_nodes, caching)


def select_move_alphabeta(board, color, limit, caching=0, ordering=0):
    """
    Given a board and a player color, decide on a move.
    The return value is a tuple of integers (i,j), where
    i is the column and j is the row on the board.

    Note that other parameters are accepted by this function:
    If limit is a positive integer, your code should enforce a depth limit that is equal to the value of the parameter.
    Search only to nodes at a depth-limit equal to the limit. If nodes at this level are non-terminal return a heuristic
    value (see compute_utility)
    If caching is ON (i.e. 1), use state caching to reduce the number of state evaluations.
    If caching is OFF (i.e. 0), do NOT use state caching to reduce the number of state evaluations.
    If ordering is ON (i.e. 1), use node ordering to expedite pruning and reduce the number of state evaluations.
    If ordering is OFF (i.e. 0), do NOT use node ordering to expedite pruning and reduce the number of state evaluations.
    """
    return alphabeta_max_node(board, color, float('-inf'), float('inf'), limit, caching, ordering)[0]


#####################################################
def run_ai():
    """
    This function establishes communication with the game manager.
    It first introduces itself and receives its color.
    Then it repeatedly receives the current score and current board state
    until the game is over.
    """
    print('Othello AI')  # First line is the name of this AI
    arguments = input().split(',')

    color = int(arguments[0])  # Player color: 1 for dark (goes first), 2 for light. 
    limit = int(arguments[1])  # Depth limit
    minimax = int(arguments[2])  # Minimax or alpha beta
    caching = int(arguments[3])  # Caching 
    ordering = int(arguments[4])  # Node-ordering (for alpha-beta only)

    if minimax == 1:
        eprint('Running MINIMAX')
    else:
        eprint('Running ALPHA-BETA')

    if caching == 1:
        eprint('State Caching is ON')
    else:
        eprint('State Caching is OFF')

    if ordering == 1:
        eprint('Node Ordering is ON')
    else:
        eprint('Node Ordering is OFF')

    if limit == -1:
        eprint('Depth Limit is OFF')
    else:
        eprint('Depth Limit is ', limit)

    if minimax == 1 and ordering == 1:
        eprint('Node Ordering should have no impact on Minimax')

    while True:  # This is the main loop
        # Read in the current game status, for example:
        # 'SCORE 2 2' or 'FINAL 33 31' if the game is over.
        # The first number is the score for player 1 (dark), the second for player 2 (light)
        next_input = input()
        status, dark_score_s, light_score_s = next_input.strip().split()
        dark_score = int(dark_score_s)
        light_score = int(light_score_s)

        if status != 'FINAL':
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
                movei, movej = select_move_alphabeta(board, color, limit, caching, ordering)

            print(f'{movei} {movej}')


if __name__ == '__main__':
    run_ai()
