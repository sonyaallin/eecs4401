"""
An AI player for Othello.
"""
"""
My heuristic calculates 3 values, the first is the naive heuristic we used in compute_utility
then I calculated the values suggested in the handout consider stable board locations, for this
I found locations where the piece is on a corner tile, if so award a point to the player it belongs to.
The final value found was that of how many moves each player can make at a given board state, so I found
the num of moves each player can make, found the difference between these and divided it by the total num 
of moves and * 100 to get a % of sorts to represent how many options a player has.
"""
import random
import sys
import time

# You can use the functions in othello_shared to write your AI
from othello_shared import find_lines, get_possible_moves, get_score, play_move

board_states_minimax = {}
board_states_alphabeta = {}

def eprint(*args, **kwargs): #you can use this for debugging, as it will print to sterr and not stdout
    print(*args, file=sys.stderr, **kwargs)


# Method to compute utility value of terminal state
def compute_utility(board, color):
    # IMPLEMENT
    state = get_score(board)
    if color == 1:  # dark player utility
        utility = state[0] - state[1]
    else:           # light player utility
        utility = state[1] - state[0]
    return utility


# Better heuristic value of board
def compute_heuristic(board, color): #not implemented, optional
    if color == 1:
        opponent = 2
    else:
        opponent = 1

    dimension = len(board) - 1
    # ----------------------------------------------------------------
    # naive heuristic from compute_utility
    state = get_score(board)
    naive_score = 0
    if color == 1:  # dark player utility
        naive_score = state[0] - state[1]
    else:           # light player utility
        naive_score = state[1] - state[0]

    # ----------------------------------------------------------------
    # Stable board locations i.e where they cannot be flipped (corners)
    player_corner_tiles = 0
    opponent_corner_tiles = 0
    if board[0][0] == color: # checked top left corner
        player_corner_tiles += 1
    else:
        opponent_corner_tiles += 1

    if board[0][dimension] == color: # checked top right corner
        player_corner_tiles += 1
    else:
        opponent_corner_tiles += 1

    if board[dimension][dimension] == color: # check bottom right corner
        player_corner_tiles += 1
    else:
        opponent_corner_tiles += 1

    if board[dimension][0] == color: # check bottom left corner
        player_corner_tiles += 1
    else:
        opponent_corner_tiles += 1

    corner_score = player_corner_tiles - opponent_corner_tiles

    # -----------------------------------------------------------------
    # Consider the number of moves you and your opponent can make given the current config
    player_available_moves = len(get_possible_moves(board, color))
    opponent_available_moves = len(get_possible_moves(board, opponent))
    moves_score = (player_available_moves - opponent_available_moves) / (player_available_moves + opponent_available_moves)
    moves_score = moves_score * 100
    # --------------------------------------------------------------------
    # total value of heuristic
    return naive_score + corner_score + moves_score


############ MINIMAX ###############################
def minimax_min_node(board, color, limit, caching=0):

    if caching == 1:
        if (board, color) in board_states_minimax:
            return board_states_minimax[(board, color)]

    #  assign color of player and opponent
    if color == 1:
        opponent = 2
    else:
        opponent = 1

    legal_moves = get_possible_moves(board, opponent)
    if legal_moves == [] or limit == 0:  # game end condition or max depth/limit
        utility = compute_utility(board, color)
        if caching == 1:
            board_states_minimax[(board, color)] = None, utility
        return None, utility

    else: # moves can be made + not max depth (so want to find best move for min)
        min_utility = float('inf')
        best_move = None
        for move in legal_moves:
            next_board_state = play_move(board, opponent, move[0], move[1])
            potential_utility = minimax_max_node(next_board_state, color, limit - 1, caching)[1]
            if potential_utility < min_utility:
                min_utility = potential_utility
                best_move = move
            if caching:
                board_states_minimax[(board, color)] = (move, potential_utility)
    return best_move, min_utility


def minimax_max_node(board, color, limit, caching = 0): #returns highest possible utility
    #  assign color of player and opponent
    if color == 1:
        opponent = 2
    else:
        opponent = 1

    if caching == 1:
        if (board, color) in board_states_minimax:
            return board_states_minimax[(board, color)]

    legal_moves = get_possible_moves(board, color)
    if legal_moves == [] or limit == 0:  # game end condition or max depth/limit
        utility = compute_utility(board, color)
        if caching:
            board_states_minimax[(board, color)] = None, utility
        return None, utility

    else: # moves can be made + not max depth (so want to find best move for min)
        max_utility = float('-inf')
        best_move = None
        for move in legal_moves:
            next_board_state = play_move(board, color, move[0], move[1])
            potential_utility = minimax_min_node(next_board_state, color, limit - 1, caching)[1]
            if potential_utility > max_utility:
                max_utility = potential_utility
                best_move = move
            if caching:
                board_states_minimax[(board, color)] = (move, potential_utility)
    return best_move, max_utility


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
    return minimax_max_node(board, color, limit, caching)[0]


############ ALPHA-BETA PRUNING #####################
def alphabeta_min_node(board, color, alpha, beta, limit, caching = 0, ordering = 0):
    #  assign color of player and opponent
    if color == 1:
        opponent = 2
    else:
        opponent = 1

    if caching == 1:
        if (board, color) in board_states_alphabeta:
            return board_states_alphabeta[(board, color)]

    legal_moves = get_possible_moves(board, opponent)
    if legal_moves == [] or limit == 0:  # game end condition or max depth/limit
        utility = compute_utility(board, color)
        if caching:
            board_states_alphabeta[(board, color)] = None, utility
        return None, utility
    else:
        best_move = None
        found_states = []
        for move in legal_moves: # find the utility for branches before exploring further
            next_board_state = play_move(board, opponent, move[0], move[1])
            utility = compute_utility(next_board_state, opponent)
            found_states.append((next_board_state, utility, move))

        if ordering == 1:
            found_states = sorted(found_states, key=lambda item: (item[1])) # sort the states by utility

        for next_board_state, _, move in found_states:
            potential_utility = alphabeta_max_node(next_board_state, color, alpha, beta, limit-1, caching, ordering)[1]

            if caching == 1:
                board_states_alphabeta[(board, color)] = move, potential_utility

            if potential_utility < beta:
                beta = potential_utility
                best_move = move

            if alpha >= beta:
                break

        return best_move, beta



def alphabeta_max_node(board, color, alpha, beta, limit, caching = 0, ordering = 0):
    #  assign color of player and opponent
    if color == 1:
        opponent = 2
    else:
        opponent = 1

    if caching == 1:
        if (board, color) in board_states_alphabeta:
            return board_states_alphabeta[(board, color)]

    legal_moves = get_possible_moves(board, color)
    if legal_moves == [] or limit == 0:  # game end condition or max depth/limit
        utility = compute_utility(board, color)
        if caching:
            board_states_alphabeta[(board, color)] = None, utility
        return None, utility
    else:
        max_utility = float('-inf')
        best_move = None
        found_states = []
        for move in legal_moves: # find the utility for branches before exploring further
            next_board_state = play_move(board, color, move[0], move[1])
            utility = compute_utility(next_board_state, color)
            found_states.append((next_board_state, utility, move))

        if ordering == 1:
            found_states = sorted(found_states, key=lambda item: (item[1]), reverse=True) # sort the states by utility

        for next_board_state, _, move in found_states:
            potential_utility = alphabeta_min_node(next_board_state, color, alpha, beta, limit-1, caching, ordering)[1]

            if caching == 1:
                board_states_alphabeta[next_board_state] = (move, potential_utility)

            if potential_utility > max_utility:
                max_utility = potential_utility
                best_move = move
            alpha = max(alpha, max_utility)

            if alpha >= beta:
                return best_move, max_utility

        return best_move, max_utility

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
    return alphabeta_max_node(board, color, float("-inf"), float("inf"), limit, caching, ordering)[0]




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
