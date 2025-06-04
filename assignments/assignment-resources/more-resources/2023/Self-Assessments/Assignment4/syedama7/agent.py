"""
An AI player for Othello. 
"""
# Heuristic function will check all the following conditions for a good board
# 1. number of corners playable (+) good
# 2. number of edges playable (+) good
# 3. number of positions adjacent to a corner playable (-) bad
# 4. difference of number of your pieces and opponents (+) good

import random
import sys
import time

# You can use the functions in othello_shared to write your AI
from othello_shared import find_lines, get_possible_moves, get_score, play_move

states = {}

def eprint(*args, **kwargs): #you can use this for debugging, as it will print to sterr and not stdout
    print(*args, file=sys.stderr, **kwargs)


# Method to compute utility value of terminal state
def compute_utility(board, color):
    #  number of disks of the player's colour minus the number of disks of the opponent
    dark, light = get_score(board)
    if color == 1:
        return dark - light
    return light - dark


# Better heuristic value of board
def compute_heuristic(board, color):
    num_edges = 0
    num_corner = 0
    num_corner_adj = 0
    size = len(board) - 1
    for i in range(size + 1):
        for edge in [board[0][i], board[i][0], board[size][i], board[i][size]]:
            if color == edge:
                num_edges += 1

    for adj_corner in [board[1][0], board[0][1], board[1][1], board[size - 1][size], board[size][size - 1],
                       board[size - 1][size - 1]]:
        if color == adj_corner:
            num_corner_adj += 1

    if board[0][0] == color:
        num_corner += 1
    if board[size][size] == color:
        num_corner += 1
    if board[0][size] == color:
        num_corner += 1
    if board[size][0] == color:
        num_corner += 1

    dark, light = get_score(board)
    diff = light - dark
    if color == 1:
        diff = dark - light

    return 4 * len(board) * num_corner - num_corner_adj + 2 * num_edges + diff


############ MINIMAX ###############################
def minimax_min_node(board, color, limit, caching = 0):
    if board in states and caching == 1:
        return states[board]
    other_color = 1
    if color == 1:
        other_color = 2
    moves = get_possible_moves(board, other_color)
    if not moves or limit == 0:
        return (None, None), compute_utility(board, color)

    successors = [play_move(board, other_color, i, j) for (i, j) in moves]
    scores = []
    for i in range(len(successors)):
        val = minimax_max_node(successors[i], color, limit-1, caching)
        states[successors[i]] = (moves[i], val[1])
        scores.append(val[1])
    best = min(scores)
    min_move = moves[scores.index(best)]
    return min_move, best


def minimax_max_node(board, color, limit, caching = 0): #returns highest possible utility
    if board in states and caching == 1:
        return states[board]
    moves = get_possible_moves(board, color)
    if not moves or limit == 0:
        val = (None, None), compute_utility(board, color)
        return val
    successors = [play_move(board, color, i, j) for (i, j) in moves]
    scores = []
    for i in range(len(successors)):
        val = minimax_min_node(successors[i], color, limit - 1, caching)
        states[successors[i]] = (moves[i], val[1])
        scores.append(val[1])
    best = max(scores)
    max_move = moves[scores.index(best)]
    return max_move, best


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
    states.clear()
    move, score = minimax_max_node(board, color, limit, caching)
    return move

############ ALPHA-BETA PRUNING #####################
def alphabeta_min_node(board, color, alpha, beta, limit, caching = 0, ordering = 0):
    if board in states and caching == 1:
        return states[board]
    other_color = 1
    if color == 1:
        other_color = 2
    moves = get_possible_moves(board, other_color)
    if not moves or limit == 0:
        val = (None, None), compute_utility(board, color)
        return val
    move_suc = [(move, play_move(board, other_color, move[0], move[1])) for move in moves]
    # if ordering == 1:
    #     move_suc.sort(key=lambda x: compute_utility(get_second(x), board), reverse=True)
    scores = []
    for move, successor in move_suc:
        m, val = alphabeta_max_node(successor, color, alpha, beta, limit - 1, caching, ordering)
        states[board] = move, val
        scores.append(val)
        beta = min(beta, val)
        if beta <= alpha:
            break
    best_score = min(scores)
    best_move = move_suc[scores.index(best_score)][0]
    return best_move, best_score


def alphabeta_max_node(board, color, alpha, beta, limit, caching = 0, ordering = 0):
    if board in states and caching == 1:
        return states[board]
    moves = get_possible_moves(board, color)
    if not moves or limit == 0:
        val = (None, None), compute_utility(board, color)
        return val

    move_suc = [(move, play_move(board, color, move[0], move[1])) for move in moves]
    if ordering == 1:
        move_suc.sort(key=lambda x: compute_utility(get_second(x), board))
    scores = []
    for move, successor in move_suc:
        m, val = alphabeta_min_node(successor, color, alpha, beta, limit-1, caching, ordering)
        states[board] = move, val
        scores.append(val)
        alpha = max(alpha, val)
        if beta <= alpha:
            break
    best_score = max(scores)
    best_move = move_suc[scores.index(best_score)][0]
    return best_move, best_score


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
    states.clear()
    move, score = alphabeta_max_node(board, color, -float('inf'), float('inf'), limit, caching, ordering)
    return move


# helpers
def get_second(elem):
    return elem[1]


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
