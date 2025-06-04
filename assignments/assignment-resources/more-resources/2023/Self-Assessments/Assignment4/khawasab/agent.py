"""
An AI player for Othello.
"""
import math
import random
import sys
import time

# You can use the functions in othello_shared to write your AI
from othello_shared import find_lines, get_possible_moves, get_score, play_move

caches = [{}, {}]  # this will store our chached states


def eprint(*args, **kwargs):
    # you can use this for debugging, as it will print to sterr and not stdout
    print(*args, file=sys.stderr, **kwargs)


# Method to compute utility value of terminal state
def compute_utility(board, color):
    # IMPLEMENT

    dark, light = get_score(board)
    final = 0
    if color == 2:
        final = light - dark
    else:
        final = dark - light
    return final  # DONE


# Better heuristic value of board
def compute_heuristic(board, color):
    ut = compute_utility(board, color)
    my_moves = len(get_possible_moves(board, color))
    other_moves = len(get_possible_moves(board, 3 - color))

    return ut + my_moves**2 - other_moves


# ########### MINIMAX ############################## #
def minimax_min_node(board, color, limit, caching=0):
    # IMPLEMENT (and replace the line below)

    """for row in board:
        print(row)
    print()"""

    opp = abs(color - 3)

    moves, scores = get_possible_moves(board, opp), {}

    if not moves or limit == 0:  # arrived at terminal state/run out of limit.
        return None, compute_utility(board, color)

    best_node, best_utility = (0, 0), math.inf

    for i, j in moves:
        new_board = play_move(board, abs(color - 3), i, j)
        if caching and (new_board in caches[color - 1]):  # Caching is engaged here
            max_new_board = caches[color - 1][new_board]
        else:
            max_new_board = minimax_max_node(new_board, color, limit - 1)[1]
            caches[color - 1][new_board] = max_new_board  # Add this to the cache
        scores[(i, j)] = max_new_board

    for move, utility in scores.items():
        if utility < best_utility:
            best_node, best_utility = move, utility

    return best_node, best_utility  # DONE


def minimax_max_node(board, color, limit, caching=0):
    # returns highest possible utility
    # IMPLEMENT (and replace the line below)
    """for row in board:
        print(row)
    print()"""

    moves, scores = get_possible_moves(board, color), {}

    if not moves or limit == 0:
        return None, compute_utility(board, color)

    best_node, best_utility = (0, 0), -math.inf

    for i, j in moves:
        new_board = play_move(board, color, i, j)
        if caching and (new_board in caches[color - 1]):
            min_new_board = caches[color - 1][new_board]
        else:
            min_new_board = minimax_min_node(new_board, color, limit - 1)[1]
            caches[color - 1][new_board] = min_new_board  # Add to cache
        scores[(i, j)] = min_new_board

    for move, utility in scores.items():
        if utility > best_utility:
            best_node, best_utility = move, utility

    return best_node, best_utility  # DONE


def select_move_minimax(board, color, limit, caching=0):
    """
    Given a board and a player color, decide on a move.
    The return value is a tuple of integers (i,j), where
    i is the column and j is the row on the board.

    Note that other parameters are accepted by this function:
    If limit is a positive integer, your code should enfoce a depth limit that
    is equal to the value of the parameter.
    Search only to nodes at a depth-limit equal to the limit.  If nodes at this
    level are non-terminal return a heuristic
    value (see compute_utility)
    If caching is ON (i.e. 1), use state caching to reduce the number of state
    evaluations.
    If caching is OFF (i.e. 0), do NOT use state caching to reduce the number of
    state evaluations.
    """
    # IMPLEMENT (and replace the line below)

    move, utility = minimax_max_node(board, color, limit, caching)

    return move  # DONE


# ########### ALPHA-BETA PRUNING #################### #
def alphabeta_min_node(board, color, alpha, beta, limit, caching=0, ordering=0):
    # IMPLEMENT (and replace the line below)
    opp = abs(color - 3)
    moves, scores = get_possible_moves(board, opp), {}

    if not moves or limit == 0:  # arrived at terminal state/run out of limit.
        return None, compute_utility(board, color)

    best_move, best_utility = None, math.inf  # initializing

    if ordering:
        moves = sort_moves(moves, board, color)
        for i, j in moves:
            new_board = play_move(board, color, i, j)
            if caching and (new_board in caches[color - 1]):
                temp_ut = caches[color - 1][new_board]
            else:
                temp_ut = alphabeta_max_node(new_board, color, alpha, beta, limit - 1)[1]
                caches[color - 1][new_board] = temp_ut  # Add to cache

            if temp_ut < best_utility:  # potential utility update
                best_move, best_utility = (i, j), temp_ut

            if beta > best_utility:
                beta = best_utility
                if beta <= alpha:
                    break
    else:
        for i, j in moves:
            new_board = play_move(board, abs(color - 3), i, j)
            if caching and (new_board in caches[color - 1]):
                temp_ut = caches[color - 1][new_board]
            else:
                temp_ut = alphabeta_max_node(new_board, color, alpha, beta, limit - 1)[1]
                caches[color - 1][new_board] = temp_ut  # Add to cache

            if temp_ut < best_utility:  # potential utility update
                best_move, best_utility = (i, j), temp_ut

            if beta > best_utility:
                beta = best_utility
                if beta <= alpha:
                    break

    return best_move, best_utility


"""def sort_moves(moves, board, color):
    if len(moves) == 1:
        new_board = play_move(board, color, moves[0][0], moves[0][1])
        return [(new_board, compute_utility(new_board, color), moves[0])]

    temp = sort_moves(moves[1:], board, color)  # List for other than 0

    new_board = play_move(board, color, moves[0][0], moves[0][1])
    temp_utility = compute_utility(new_board, color)

    has_been_inserted = False

    for i in range(len(temp)):
        temp_board, utility, move = temp[i]
        if utility > temp_utility:
            temp.insert(i, (new_board, temp_utility, moves[0]))
            has_been_inserted = True

    if not has_been_inserted:
        temp.append((new_board, temp_utility, moves[0]))

    return temp


def sort_moves(moves, board, color):
    final = []
    for i, j in moves:
        new_board = play_move(board, color, i, j)
        ut = compute_utility(new_board, color)
        inserted = False
        for i in range(len(final)):
            temp_board, temp_ut, temp_move = final[i]
            if temp_ut > ut:
                final.insert(i, (new_board, ut, (i, j)))
                inserted = True
        if not inserted:
            final.append((new_board, ut, (i, j)))

    for item in final:
        print(item[1])
    print('--')
    return final"""


def sort_moves(moves, board, color):
    boards = [play_move(board, color, move[0], move[1]) for move in moves]
    uts = [compute_utility(board, color) for board in boards]

    final = []

    while len(boards) > 0:
        i = uts.index(max(uts))
        uts.remove(uts[i])

        temp_move = moves.pop(i)
        boards.pop(i)
        final.append(temp_move)

    return final


def alphabeta_max_node(board, color, alpha, beta, limit, caching=0, ordering=0):
    # IMPLEMENT (and replace the line below)

    moves, scores = get_possible_moves(board, color), {}

    if not moves or limit == 0:  # arrived at terminal state/run out of limit.
        return None, compute_utility(board, color)

    best_move, best_utility = None, -math.inf  # initializing

    if ordering:
        moves = sort_moves(moves, board, color)
        for i, j in moves:
            new_board = play_move(board, color, i, j)
            if caching and (new_board in caches[color - 1]):
                temp_ut = caches[color - 1][new_board]
            else:
                temp_ut = alphabeta_min_node(new_board, color, alpha, beta, limit - 1)[1]
                caches[color - 1][new_board] = temp_ut  # Add to cache

            if temp_ut > best_utility:  # potential utility update
                best_move, best_utility = (i, j), temp_ut

            if alpha < best_utility:
                alpha = best_utility
                if beta <= alpha:
                    break
    else:
        for i, j in moves:
            new_board = play_move(board, color, i, j)
            if caching and (new_board in caches[color - 1]):
                temp_ut = caches[color - 1][new_board]
            else:
                temp_ut = alphabeta_min_node(new_board, color, alpha, beta, limit - 1)[1]
                caches[color - 1][new_board] = temp_ut  # Add to cache

            if temp_ut > best_utility:  # potential utility update
                best_move, best_utility = (i, j), temp_ut

            if alpha < best_utility:
                alpha = best_utility
                if beta <= alpha:
                    break

    return best_move, best_utility  # change this!


def select_move_alphabeta(board, color, limit, caching=0, ordering=0):
    """
    Given a board and a player color, decide on a move.
    The return value is a tuple of integers (i,j), where
    i is the column and j is the row on the board.

    Note that other parameters are accepted by this function:
    If limit is a positive integer, your code should enfoce a depth limit that
    is equal to the value of the parameter.
    Search only to nodes at a depth-limit equal to the limit.  If nodes at this
    level are non-terminal return a heuristic
    value (see compute_utility)
    If caching is ON (i.e. 1), use state caching to reduce the number of state
    evaluations.
    If caching is OFF (i.e. 0), do NOT use state caching to reduce the number of
    state evaluations.
    If ordering is ON (i.e. 1), use node ordering to expedite pruning and reduce
    the number of state evaluations.
    If ordering is OFF (i.e. 0), do NOT use node ordering to expedite pruning
    and reduce the number of state evaluations.
    """
    # IMPLEMENT (and replace the line below)
    return alphabeta_max_node(board, color, -math.inf, math.inf, limit, caching, ordering)[0]



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
        # The first number is the score for player 1 (dark), the second for
        # player 2 (light)
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
