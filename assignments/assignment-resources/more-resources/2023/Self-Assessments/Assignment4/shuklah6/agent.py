"""
An AI player for Othello. 
"""

import random
import sys
import time

# You can use the functions in othello_shared to write your AI
from othello_shared import find_lines, get_possible_moves, get_score, play_move

util_cache = {}


def eprint(*args, **kwargs):  # you can use this for debugging, as it will print to sterr and not stdout
    print(*args, file=sys.stderr, **kwargs)


# Method to compute utility value of terminal state
def compute_utility(board, color):
    p1_score, p2_score = get_score(board)
    if color == 1:
        return p1_score - p2_score
    elif color == 2:
        return p2_score - p1_score
    return 0

def _check_stable_square(board, x, y):
    """
    A square is stable if the row, column and diagonals it belongs to:
    1. Have the same colour disc as the square till either end of the row/column/diagonal.
    2. Has two opposite colour discs which enclose the current disc as well as other discs of the same colour
    """
    # Check along the column
    u = x - 1
    d = x + 1
    encapsulated = False
    while u >= 0 or d < len(board):
        if board[x][u] == board[x][y]:
            u -= 1
        if board[x][d] == board[x][y]:
            d += 1
        if board[x][u] != board[x][y] != 0 and board[x][d] != board[x][y] != 0:
            encapsulated = True
            break
        if board[x][u] == 0 and board[x][d] == 0:
            break
    if u >= 0 and d <= len(board) and not encapsulated:
        return 0

    # Check along the row
    l = y - 1
    r = y + 1
    encapsulated = False
    while l >= 0 or r < len(board):
        if board[l][y] == board[x][y]:
            u -= 1
        if board[r][y] == board[x][y]:
            d += 1
        if board[l][y] != board[x][y] != 0 and board[r][y] != board[x][y] != 0:
            encapsulated = True
            break
        if board[l][y] == 0 and board[r][y] == 0:
            break
    if l >= 0 and r <= len(board) and not encapsulated:
        return 0

    # Check the diagonal \
    u = x - 1
    d = y + 1
    l = y - 1
    r = y + 1
    encapsulated = False
    while l >= 0 or r < len(board):
        if board[l][u] == board[x][y]:
            u -= 1
            l -= 1
        if board[r][d] == board[x][y]:
            d += 1
            r += 1
        if board[l][u] != board[x][y] != 0 and board[r][d] != board[x][y] != 0:
            encapsulated = True
            break
        if board[l][u] == 0 and board[r][d] == 0:
            break
    if (l >= 0 and u >= 0) and (r <= len(board) and d <= len(board)) and not encapsulated:
        return 0

    # Check the diagonal /
    u = x - 1
    d = y + 1
    l = y - 1
    r = y + 1
    encapsulated = False
    while l >= 0 or r < len(board):
        if board[l][d] == board[x][y]:
            d += 1
            l -= 1
        if board[r][u] == board[x][y]:
            u -= 1
            r += 1
        if board[l][d] != board[x][y] != 0 and board[r][u] != board[x][y] != 0:
            encapsulated = True
            break
        if board[l][d] == 0 and board[r][u] == 0:
            break
    if (l >= 0 and d <= len(board) ) and (r <= len(board) and u >= 0) and not encapsulated:
        return 0

    return 1

# Better heuristic value of board
def compute_heuristic(board, color):  # not implemented, optional
    # IMPLEMENT
    """
    The difference in discs owned by a player does not give an accurate idea of the game state.
    A better way to calculcate better game states would be to count the number of stable discs
    a player owns, as those discs are guaranteed to be in the possession of that player for the
    rest of the game.
    """
    board_size = len(board)
    counter = {0: 0, 1: 0, 2: 0}
    for i in range(board_size):
        for j in range(board_size):
            if board[i][j] == 0:
                continue
            # Corners are stable pieces
            if (i == 0 or i == board_size - 1) and (j == 0 or j == board_size - 1):
                counter[board[i][j]] += 1
            else:
                stable = _check_stable_square(board, i, j)
                counter[board[i][j]] += stable

    if color == 1:
        return counter[1] - counter[2]
    elif color == 2:
        return counter[2] - counter[1]
    else:
        return 0

############ MINIMAX ###############################
def minimax_min_node(board, color, limit, caching=0):
    # IMPLEMENT (and replace the line below)
    successors = get_possible_moves(board, 3 - color)
    if limit == 0 or len(successors) == 0:
        return (), compute_utility(board, color)
    else:
        min_score = None
        next_move = None
        for move in successors:
            new_board = play_move(board, 3 - color, move[0], move[1])
            temp_move = None
            score = None
            if caching:
                temp_move = move
                score = util_cache.get(new_board)
                if score is None:
                    temp_move, score = minimax_max_node(new_board, color, limit - 1,
                                                        caching)
                    util_cache[new_board] = score
            else:
                temp_move, score = minimax_max_node(new_board, color, limit - 1,
                                                    caching)

            if min_score is None or score < min_score:
                min_score = score
                next_move = move
        return next_move, min_score


def minimax_max_node(board, color, limit, caching=0):  # returns highest possible utility
    # IMPLEMENT (and replace the line below)
    successors = get_possible_moves(board, color)
    if limit == 0 or len(successors) == 0:
        return (), compute_utility(board, color)
    else:
        max_score = None
        next_move = None
        for move in successors:
            new_board = play_move(board, color, move[0], move[1])
            temp_move = None
            score = None
            if caching:
                temp_move = move
                score = util_cache.get(new_board)
                if score is None:
                    temp_move, score = minimax_min_node(new_board, color, limit - 1,
                                                        caching)
                    util_cache[new_board] = score
            else:
                temp_move, score = minimax_min_node(new_board, color, limit - 1,
                                                    caching)
            if max_score is None or score > max_score:
                max_score = score
                next_move = move
        return next_move, max_score


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
    move, score = minimax_max_node(board, color, limit, caching)
    return move


############ ALPHA-BETA PRUNING #####################

def alphabeta_min_node(board, color, alpha, beta, limit, caching=0, ordering=0):
    # IMPLEMENT (and replace the line below)
    successors = get_possible_moves(board, 3 - color)
    if limit == 0 or len(successors) == 0:
        return (), compute_utility(board, color)
    else:
        next_score = compute_utility(board, color)
        next_move = ()
        if ordering:
            if len(successors) > 1:
                order_vals = []
                for mv in successors:
                    order_vals.append(compute_utility(play_move(board, 3 - color, mv[0], mv[1]), color))
                successors = [successor for (successor, util) in sorted(zip(successors, order_vals), reverse=True)]
        for move in successors:
            new_board = play_move(board, 3 - color, move[0], move[1])
            temp_move = None
            temp_score = None
            if caching:
                temp_move = move
                temp_score = util_cache.get(new_board)
                if temp_score is None:
                    temp_move, temp_score = alphabeta_max_node(new_board, color, alpha, beta, limit - 1, caching,
                                                               ordering)
                    util_cache[new_board] = temp_score
            else:
                temp_move, temp_score = alphabeta_max_node(new_board, color, alpha, beta, limit - 1, caching, ordering)

            if beta > temp_score:
                beta = temp_score
                next_score = temp_score
                next_move = move
                if beta <= alpha:
                    break

        return next_move, next_score


def alphabeta_max_node(board, color, alpha, beta, limit, caching=0, ordering=0):
    # IMPLEMENT (and replace the line below)
    successors = get_possible_moves(board, color)
    if limit == 0 or len(successors) == 0:
        return (), compute_utility(board, color)
    else:
        next_score = compute_utility(board, color)
        next_move = ()
        if ordering:
            order_vals = []
            for mv in successors:
                order_vals.append(compute_utility(play_move(board, color, mv[0], mv[1]), color))
            successors = [successor for (successor, util) in sorted(zip(successors, order_vals), key=lambda x: x[1],
                                                                    reverse=True)]
        for move in successors:
            new_board = play_move(board, color, move[0], move[1])
            temp_move = None
            temp_score = None

            if caching:
                temp_move = move
                temp_score = util_cache.get(new_board)
                if temp_score is None:
                    temp_move, temp_score = alphabeta_min_node(new_board, color, alpha, beta, limit - 1, caching,
                                                               ordering)
                    util_cache[new_board] = temp_score
            else:
                temp_move, temp_score = alphabeta_min_node(new_board, color, alpha, beta, limit - 1, caching, ordering)

            if alpha < temp_score:
                alpha = temp_score
                next_score = temp_score
                next_move = move
                if beta <= alpha:
                    break
        return next_move, next_score


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
    move, score = alphabeta_max_node(board, color, float('-inf'), float('inf'), limit, caching, ordering)
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
