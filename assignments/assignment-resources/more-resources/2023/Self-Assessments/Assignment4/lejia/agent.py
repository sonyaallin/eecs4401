"""
An AI player for Othello.
"""

import random
import sys
import time

# You can use the functions in othello_shared to write your AI
from othello_shared import find_lines, get_possible_moves, get_score, play_move

OPPONENT = {
    1:2,
    2:1
}

CACHE = {} # Global Cache Dictionary for when caching is enabled

def reset_cache():
    CACHE = {}

def eprint(*args, **kwargs): #you can use this for debugging, as it will print to sterr and not stdout
    print(*args, file=sys.stderr, **kwargs)

# Method to compute utility value of terminal state
def compute_utility(board, color):
    #IMPLEMENT
    p1_count, p2_count = get_score(board)

    # player color (1 is dark (goes first), 2 is light)
    if color == 1:
        return p1_count - p2_count

    # otherwise
    return p2_count - p1_count

# Better heuristic value of board
def compute_heuristic(board, color): #not implemented, optional
    #IMPLEMENT

    #swamped with other work :(
    return 0 #change this!

def get_ordered_boards(board, pos_moves, color, reversed=True):
    new_boards = [(play_move(board, color, i, j), (i, j)) for i, j in pos_moves]

    board_utils = [(board, compute_utility(board, color)) for board in new_boards]

    return sorted(board_utils, key=lambda tup: tup[1], reverse=reversed)

############ MINIMAX ###############################
def minimax_min_node(board, color, limit, caching = 0):
    """ Min plays a move to change state to lowest valued max child
    """
    # If state is already cached, do NOT explore it again
    if caching and board in CACHE:
        return CACHE[board]

    pos_moves = get_possible_moves(board, OPPONENT[color])

    # base case, maxdepth reached or no possible moves remaining
    # we generate utility for any non-terminal state using compute_utility
    if not (len(pos_moves) and limit):
        util = compute_utility(board, color)
        return None, util

    best_move, min_util = None, float("inf")

    for i, j in pos_moves:
        # opponent should make move in min node
        new_board = play_move(board, OPPONENT[color], i, j)

        # Find max now with limit-1 (one layer closer to limit)
        curr_util = minimax_max_node(new_board, color, limit - 1, caching)[1]
        if curr_util < min_util: best_move, min_util = (i, j), curr_util

        if caching: CACHE[new_board] = ((i, j), curr_util)

    return best_move, min_util

def minimax_max_node(board, color, limit, caching = 0): #returns highest possible utility
    """ Max plays a move to change state to highest valued min child
    """
    # If state is already cached, do NOT explore it again
    if caching and board in CACHE:
        return CACHE[board]

    pos_moves = get_possible_moves(board, color)

    # base case, maxdepth reached or no possible moves remaining
    # we generate utility for any non-terminal state using compute_utility
    if not (len(pos_moves) and limit):
        util = compute_utility(board, color)
        return None, util

    best_move, max_util = None, -float("inf")

    for i, j in pos_moves:
        # we should make move in max node
        new_board = play_move(board, color, i, j)

        curr_util = minimax_min_node(new_board, color, limit - 1, caching)[1]
        if curr_util > max_util: best_move, max_util = (i, j), curr_util

        if caching: CACHE[new_board] = ((i, j), curr_util)

    return best_move, max_util

def select_move_minimax(board, color, limit, caching = 0):
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
    #IMPLEMENT (and replace the line below)

    # NOTE: Assume other player will always play their best move
    # - play a move that MINIMIZES payoff gained by other player
    # - by minimizing payoff of opponent, you maximize your own payoff

    reset_cache()

    # Start of with max recursive call to maximize payoff of player with color
    return minimax_max_node(board, color, limit, caching)[0]

############ ALPHA-BETA PRUNING #####################
def alphabeta_min_node(board, color, alpha, beta, limit, caching = 0, ordering = 0):
    """ Min plays a move to change state to lowest valued max child (with pruning)
    """
    # If state is already cached, do NOT explore it again
    if caching and board in CACHE:
        return CACHE[board]

    pos_moves = get_possible_moves(board, OPPONENT[color])

    # base case, maxdepth reached or no possible moves remaining
    # we generate utility for any non-terminal state using compute_utility
    if not (len(pos_moves) and limit):
        util = compute_utility(board, color)
        return None, util

    best_move, min_util = None, float("inf")

    if ordering:
        ordered_boards = get_ordered_boards(board, pos_moves, color)

        for board_and_move, board_util in ordered_boards:
            new_board, move = board_and_move

            curr_util = alphabeta_max_node(new_board, color, alpha, beta, limit - 1, caching, ordering)[1]
            if curr_util < min_util: best_move, min_util = move, curr_util

            if caching: CACHE[new_board] = (move, curr_util)

            beta= min(beta, curr_util)
            if beta <= alpha: break

        return best_move, min_util

    for i, j in pos_moves:
        # opponent should make move in min node
        new_board = play_move(board, OPPONENT[color], i, j)

        # Find max now with limit-1 (one layer closer to limit)
        curr_util = alphabeta_max_node(new_board, color, alpha, beta, limit - 1, caching, ordering)[1]
        if curr_util < min_util: best_move, min_util = (i, j), curr_util

        if caching: CACHE[new_board] = ((i, j), curr_util)

        # Perform BETA-cut (slides 44-45)
        # NOTE: best pruning occurs if best move for MIN (child yielding lowest value) is explored first
        # at max node n, alpha is the highest value of n's siblings explored so far
        # let beta be the lowest value of n's children explored so far (changes as children are examined)
        # if beta <= alpha, we stop exploring children of n
        beta = min(beta, curr_util)
        if beta <= alpha: break

    return best_move, min_util

def alphabeta_max_node(board, color, alpha, beta, limit, caching = 0, ordering = 0):
    """ Max plays a move to change state to highest valued min child (with pruning)
    """
    # If state is already cached, do NOT explore it again
    if caching and board in CACHE:
        return CACHE[board]

    pos_moves = get_possible_moves(board, color)

    # base case, maxdepth reached or no possible moves remaining
    # we generate utility for any non-terminal state using compute_utility
    if not (len(pos_moves) and limit):
        util = compute_utility(board, color)
        return None, util

    best_move, max_util = None, -float("inf")

    if ordering:
        ordered_boards = get_ordered_boards(board, pos_moves, color)

        for board_and_move, board_util in ordered_boards:
            new_board, move = board_and_move

            curr_util = alphabeta_min_node(new_board, color, alpha, beta, limit - 1, caching, ordering)[1]
            if curr_util > max_util: best_move, max_util = move, curr_util

            if caching: CACHE[new_board] = (move, curr_util)

            alpha = max(alpha, curr_util)
            if alpha >= beta: break

        return best_move, max_util

    for i, j in pos_moves:
        # we should make move in max node
        new_board = play_move(board, color, i, j)

        # Find max now with limit-1 (one layer closer to limit)
        curr_util = alphabeta_min_node(new_board, color, alpha, beta, limit - 1, caching, ordering)[1]
        if curr_util > max_util: best_move, max_util = (i, j), curr_util

        if caching: CACHE[new_board] = ((i, j), curr_util)

        # Perform ALPHA-cut (slides 42-43)
        # NOTE: best pruning occurs if best move for MAX (child yielding highest value) is explored first
        # At max node n, beta is the lowest value of n's siblings explored so far
        # let alpha be highest value of n's children explored so far (changes as children are examined)
        # if alpha >= beta, we stop exploring children of n
        alpha = max(alpha, curr_util)
        if alpha >= beta: break

    return best_move, max_util

def select_move_alphabeta(board, color, limit, caching = 0, ordering = 0):
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
    reset_cache()

    return alphabeta_max_node(board, color, -float("inf"), float("inf"), limit, caching, ordering)[0]

####################################################
def run_ai():
    """
    This function establishes communication with the game manager.
    It first introduces itself and receives its color.
    Then it repeatedly receives the current score and current board state
    until the game is over.
    """
    print("Othello AI") # First line is the name of this AI
    arguments = input().split(",")

    color = int(arguments[0]) #Player color: 1 for dark (goes first), 2 for light.
    limit = int(arguments[1]) #Depth limit
    minimax = int(arguments[2]) #Minimax or alpha beta
    caching = int(arguments[3]) #Caching
    ordering = int(arguments[4]) #Node-ordering (for alpha-beta only)

    if (minimax == 1): eprint("Running MINIMAX")
    else: eprint("Running ALPHA-BETA")

    if (caching == 1): eprint("State Caching is ON")
    else: eprint("State Caching is OFF")

    if (ordering == 1): eprint("Node Ordering is ON")
    else: eprint("Node Ordering is OFF")

    if (limit == -1): eprint("Depth Limit is OFF")
    else: eprint("Depth Limit is ", limit)

    if (minimax == 1 and ordering == 1): eprint("Node Ordering should have no impact on Minimax")

    while True: # This is the main loop
        # Read in the current game status, for example:
        # "SCORE 2 2" or "FINAL 33 31" if the game is over.
        # The first number is the score for player 1 (dark), the second for player 2 (light)
        next_input = input()
        status, dark_score_s, light_score_s = next_input.strip().split()
        dark_score = int(dark_score_s)
        light_score = int(light_score_s)

        if status == "FINAL": # Game is over.
            print
        else:
            board = eval(input()) # Read in the input and turn it into a Python
                                  # object. The format is a list of rows. The
                                  # squares in each row are represented by
                                  # 0 : empty square
                                  # 1 : dark disk (player 1)
                                  # 2 : light disk (player 2)

            # Select the move and send it to the manager
            if (minimax == 1): #run this if the minimax flag is given
                movei, movej = select_move_minimax(board, color, limit, caching)
            else: #else run alphabeta
                movei, movej = select_move_alphabeta(board, color, limit, caching, ordering)

            print("{} {}".format(movei, movej))

if __name__ == "__main__":
    run_ai()
