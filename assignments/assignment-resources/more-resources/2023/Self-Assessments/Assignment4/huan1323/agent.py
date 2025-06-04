"""
An AI player for Othello.
"""
import math
import random
import sys
import time

# You can use the functions in othello_shared to write your AI
from othello_shared import find_lines, get_possible_moves, get_score, play_move


states = {}

def eprint(*args,
           **kwargs):  # you can use this for debugging, as it will print to sterr and not stdout
    print(*args, file=sys.stderr, **kwargs)


# Method to compute utility value of terminal state
def compute_utility(board, color):
    # IMPLEMENT
    score = get_score(board)
    if color == 1:
        return score[0] - score[1]
    else:
        return score[1] - score[0]


# Better heuristic value of board
def compute_heuristic(board, color):  # not implemented, optional
    # IMPLEMENT
    """
    In my heuristic, I estimate the given in 4 directions.
    1. The coin that can not be fliped.
    2. The current score of the players
    3. The number of possible moves
    4. The corners each player have.
    Since these directions are equally important, so I assign a 100 maximum for
    each direction. Then, I calculate the score by divides how much the player
    win to how much they have in total. For instance, I esitmate the score by
    100 * (player_score - opponent_score) / (player_score + opponent_score).
    Therefore, we have a sense of how are the player doing compare to the other
    player. This helps the estimation better than just focus on one player, since
    there are only two players in this game.
    """
    h = 0.0
    if color == 1:
        opponent = 2
        player_score, opponent_score = get_score(board)
    else:
        opponent = 1
        opponent_score, player_score = get_score(board)
    player_unflipable, opponent_unflipable = 0, 0
    player_corner, opponent_corner = 0, 0

    if board[0][0] == color:
        player_corner += 1
    elif board[0][0] == opponent:
        opponent_corner += 1
    if board[0][-1] == color:
        player_corner += 1
    elif board[0][-1] == opponent:
        opponent_corner += 1
    if board[-1][0] == color:
        player_corner += 1
    elif board[-1][0] == opponent:
        opponent_corner += 1
    if board[-1][-1] == color:
        player_corner += 1
    elif board[-1][-1] == opponent:
        opponent_corner += 1

    if player_corner + opponent_corner != 0:
        h += 100 * (player_corner - opponent_corner) / (player_corner + opponent_corner)

    for j in range(len(board)):
        for i in range(len(board)):
            if board[j][i] == color:
                lines = find_lines(board, i, j, opponent)
                unflipable = True
                for line in lines:
                    if len(line) != 0:
                        unflipable = False
                        break
                if unflipable:
                    player_unflipable += 1
            if board[j][i] == opponent:
                lines = find_lines(board, i, j, color)
                unflipable = True
                for line in lines:
                    if len(line) != 0:
                        unflipable = False
                        break
                if unflipable:
                    opponent_unflipable += 1
    if player_unflipable + opponent_unflipable != 0:
        h += 100 * (player_unflipable - opponent_unflipable) / (player_unflipable + opponent_unflipable)

    opponent_moves = len(get_possible_moves(board, opponent))
    player_moves = len(get_possible_moves(board, color))
    if opponent_moves + player_moves != 0:
        h += 100 * (player_moves - opponent_moves) / (player_moves + opponent_moves)

    h += 100 * (player_score - opponent_score) / (player_score + opponent_score)
    return h


############ MINIMAX ###############################
def minimax_min_node(board, color, limit, caching=0):
    # IMPLEMENT (and replace the line below)
    if limit <= 0:
        return None, compute_utility(board, color)
    if color == 1:
        player = 2
    else:
        player = 1
    global states
    if caching and (board, player) in states:
        return states[(board, player)]
    moves = get_possible_moves(board, player)
    if not moves:  # terminal states
        return None, compute_utility(board, color)

    minimax_value = (moves[0], math.inf)
    for move in moves:
        b = play_move(board, player, move[0], move[1])
        new_minimax_value = minimax_max_node(b, color, limit-1, caching)[1]
        if new_minimax_value < minimax_value[1]:
            minimax_value = (move, new_minimax_value)
    if caching:
        states[(board, player)] = minimax_value
    return minimax_value


def minimax_max_node(board, color, limit,
                     caching=0):  # returns highest possible utility
    # IMPLEMENT (and replace the line below)
    if limit <= 0:
        return None, compute_utility(board, color)
    global states
    if caching and (board, color) in states:
        return states[(board, color)]
    moves = get_possible_moves(board, color)
    if not moves:  # terminal states
        return None, compute_utility(board, color)
    minimax_value = (None, -math.inf)
    for move in moves:
        b = play_move(board, color, move[0], move[1])
        new_minimax_value = minimax_min_node(b, color, limit-1, caching)[1]
        if new_minimax_value > minimax_value[1]:
            minimax_value = (move, new_minimax_value)
    if caching:
        states[(board, color)] = minimax_value
    return minimax_value


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
    return minimax_max_node(board, color, limit, caching)[0]


############ ALPHA-BETA PRUNING #####################
def order_moves(board, moves, color):
    def move_utvaue(move):
        return compute_utility(play_move(board, color, move[0], move[1]), color)
    moves.sort(key=move_utvaue, reverse=True)
    return moves


def alphabeta_min_node(board, color, alpha, beta, limit, caching=0, ordering=0):
    # IMPLEMENT (and replace the line below)
    if limit <= 0:
        return None, compute_utility(board, color)
    if color == 1:
        player = 2
    else:
        player = 1
    global states
    if caching and (board, player) in states:
        return states[(board, player)]
    moves = get_possible_moves(board, player)
    if not moves:  # terminal states
        return None, compute_utility(board, color)
    if ordering:
        moves = order_moves(board, moves, player)
    best_move = (moves[0], math.inf)
    for move in moves:
        b = play_move(board, player, move[0], move[1])
        ut_value = alphabeta_max_node(b, color, alpha, beta, limit-1, caching)[1]
        if best_move[1] > ut_value:
            best_move = move, ut_value
        if beta > ut_value:
            beta = ut_value
            if beta <= alpha:
                break
    if caching:
        states[(board, player)] = best_move
    return best_move


def alphabeta_max_node(board, color, alpha, beta, limit, caching=0, ordering=0):
    # IMPLEMENT (and replace the line below)
    if limit <= 0:
        return None, compute_utility(board, color)
    global states
    if caching and (board, color) in states:
        return states[(board, color)]
    moves = get_possible_moves(board, color)
    if not moves:  # terminal states
        return None, compute_utility(board, color)
    if ordering:
        moves = order_moves(board, moves, color)
    best_move = (moves[0], -math.inf)
    for move in moves:
        b = play_move(board, color, move[0], move[1])
        ut_value = alphabeta_min_node(b, color, alpha, beta, limit-1, caching)[1]
        if best_move[1] < ut_value:
            best_move = (move, ut_value)
        if alpha < ut_value:
            alpha = ut_value
            if beta <= alpha:
                break
    if caching:
        states[(board, color)] = best_move
    return best_move


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
