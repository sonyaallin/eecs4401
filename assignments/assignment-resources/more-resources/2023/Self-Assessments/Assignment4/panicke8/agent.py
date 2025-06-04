"""
An AI player for Othello. 
"""

#from curses import color_content
import random
import sys
import time

# You can use the functions in othello_shared to write your AI
from othello_shared import find_lines, get_possible_moves, get_score, play_move
# Store the cached values
dict_minimax = {}


def eprint(*args, **kwargs):  # you can use this for debugging, as it will print to sterr and not stdout
    print(*args, file=sys.stderr, **kwargs)

# Method to compute utility value of terminal state


def compute_utility(board, color):
    # IMPLEMENT
    black, white = get_score(board)
    if color == 1:  # Player with black pieces
        return black - white
    return white - black  # Player with white pieces

# Better heuristic value of board


def compute_heuristic(board, color):  # not implemented, optional
    # IMPLEMENT
    return 0  # change this!

############ MINIMAX ###############################


def minimax_min_node(board, color, limit, caching=0):
    # IMPLEMENT (and replace the line below)
    if board in dict_minimax and caching:
        return dict_minimax[board]

    # Need to check opponent's move
    if color == 1:
        opponent_color = 2
    else:
        opponent_color = 1

    lst_moves = get_possible_moves(board, opponent_color)

    # Base case: just return the utility if it exists
    if limit == 0 or len(lst_moves) == 0:
        return None, compute_utility(board, color)
    else:
        lst_utils = []
        # Loop through every move and append the options from here
        for m in lst_moves:
            lst_utils.append(minimax_max_node(
                play_move(board, opponent_color, m[0], m[1]), color, limit - 1)[1])

        # Min node computation
        minimum = min(lst_utils)
        min_index = lst_utils.index(minimum)
        ideal_m = lst_moves[min_index], min(lst_utils)

        # Populate the caching dictionary for easier access
        if caching:
            dict_minimax[board] = ideal_m
        return ideal_m


def minimax_max_node(board, color, limit, caching=0):  # returns highest possible utility
    # IMPLEMENT (and replace the line below)
    if board in dict_minimax and caching:
        return dict_minimax[board]

    # No need to worry about opponent_color here since we're focused on max
    lst_moves = get_possible_moves(board, color)

    # Base case: just return the utility if it exists
    if limit == 0 or len(lst_moves) == 0:
        return None, compute_utility(board, color)
    else:
        lst_utils = []
        # Loop through every move and append the options from here
        for m in lst_moves:
            lst_utils.append(minimax_min_node(
                play_move(board, color, m[0], m[1]), color, limit - 1)[1])

        # Max node computation
        maximum = max(lst_utils)
        max_index = lst_utils.index(maximum)
        ideal_m = lst_moves[max_index], max(lst_utils)

        # Populate the caching dictionary for easier access
        if caching:
            dict_minimax[board] = ideal_m
        return ideal_m


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
    lst_utils, lst_moves = [], get_possible_moves(board, color)

    # Loop through every move and append the options from here
    for m in lst_moves:
        lst_utils.append(minimax_min_node(
            play_move(board, color, m[0], m[1]), color, limit, caching)[1])

    # Max node computation
    maximum = max(lst_utils)
    max_index = lst_utils.index(maximum)
    return lst_moves[max_index]


############ ALPHA-BETA PRUNING #####################


def alphabeta_min_node(board, color, alpha, beta, limit, caching=0, ordering=0):
    # IMPLEMENT (and replace the line below)
    if board in dict_minimax and caching:
        return dict_minimax[board]

    # Need to check opponent's move
    if color == 1:
        opponent_color = 2
    else:
        opponent_color = 1

    lst_moves, ideal_m = get_possible_moves(board, opponent_color), None

    if limit == 0 or len(lst_moves) == 0:
        return None, compute_utility(board, color)

    elif ordering:
        lst_moves, lst_moves_ordered = [], []
        # Loop through every move and append the options from here
        for m in lst_moves:
            move_tuple = compute_utility(
                play_move(board, opponent_color, m[0], m[1]), opponent_color), m
            lst_moves_ordered.append(move_tuple)

        for m_o in lst_moves_ordered:
            lst_moves.append(m_o[1])
        # Simplest node ordering 
        lst_moves_ordered.sort(reverse=1)

    # Loop through every move and append the options from here
    for m in lst_moves:
        curr_a = alphabeta_max_node(
            play_move(board, opponent_color, m[0], m[1]), color, alpha, beta, limit - 1, caching, ordering)[1]
        if curr_a < beta:
            beta, ideal_m = curr_a, m
        if beta <= alpha:
            break

    # Populate the caching dictionary for easier access
    if caching:
        dict_minimax[board] = ideal_m, beta  # cache minimax value

    return ideal_m, beta


def alphabeta_max_node(board, color, alpha, beta, limit, caching=0, ordering=0):
    # IMPLEMENT (and replace the line below)
    if board in dict_minimax and caching:
        return dict_minimax[board]

    # No need to worry about opponent_color here since we're focused on max
    lst_moves, ideal_m = get_possible_moves(board, color), None

    if limit == 0 or len(lst_moves) == 0:
        return None, compute_utility(board, color)

    elif ordering:
        lst_moves, lst_moves_ordered = [], []
        # Loop through every move and append the options from here
        for m in lst_moves:
            move_tuple = compute_utility(
                play_move(board, color, m[0], m[1]), color), m
            lst_moves_ordered.append(move_tuple)

        for m_o in lst_moves_ordered:
            lst_moves.append(m_o[1])
        lst_moves_ordered.sort(reverse=1)

    # Loop through every move and append the options from here
    for m in lst_moves:
        curr_b = alphabeta_min_node(
            play_move(board, color, m[0], m[1]), color, alpha, beta, limit - 1, caching, ordering)[1]
        if alpha < curr_b:
            alpha, ideal_m = curr_b, m
        if beta <= alpha:
            break

    # Populate the caching dictionary for easier access
    if caching:
        dict_minimax[board] = ideal_m, alpha  # cache minimax value

    return ideal_m, alpha


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
    ideal_m, lst_moves, alpha, beta   = None, get_possible_moves(board, color), float("-inf"), float("inf")
    begin = time.time()

    if limit <= 0:
        limit = sys.maxsize

    for _ in range(1, limit):
        # Set a 10 second limit to follow the time constraints
        if (time.time() - begin) > 10:
            break

        # Loop through every move and append the options from here
        for m in lst_moves:
            curr_b = alphabeta_min_node(
                play_move(board, color, m[0], m[1]), color, alpha, beta, limit, caching, ordering)[1]
            if alpha < curr_b:
                alpha, ideal_m = curr_b, m
    return ideal_m

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
