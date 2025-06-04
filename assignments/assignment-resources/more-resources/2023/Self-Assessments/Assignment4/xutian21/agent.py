"""
An AI player for Othello. 
"""

import random
import sys
import time

# You can use the functions in othello_shared to write your AI
from othello_shared import find_lines, get_possible_moves, get_score, play_move

cache = {}

def eprint(*args, **kwargs): #you can use this for debugging, as it will print to sterr and not stdout
    print(*args, file=sys.stderr, **kwargs)
    
# Method to compute utility value of terminal state
def compute_utility(board, color):
    p1, p2 = get_score(board)
    if color == 1:
        return p1 - p2
    else:
        return p2 - p1

def coins(board, color):
    p1, p2 = get_score(board)
    if color == 1:
        return (p1 - p2)/(p1 + p2)
    else:
        return (p2 - p1)/(p1 + p2)


def mobility(board, color):
    my_moves = len(get_possible_moves(board, color))
    enemy_moves = len(get_possible_moves(board, 3 - color))
    return (my_moves - enemy_moves)/(my_moves + enemy_moves)

def corner(board, color):
    length = len(board[0])
    height = len(board[1])
    corners = [(0, 0), (0, length-1), (height-1, 0), (length-1, height-1)]
    my_count = 0
    ene_count = 0
    for corner in corners:
        if board[corner[0]][corner[1]] == color:
            my_count += 1
        elif board[corner[0]][corner[1]] == 3-color:
            ene_count += 1
    if my_count+ene_count == 0:
        return 0
    else:
        return (my_count-ene_count)/(my_count+ene_count)


# Better heuristic value of board
def compute_heuristic(board, color):
    '''
    This heuristics takes 3 things into account
    the base score of the board,
    The number of moves that AI can choose vs the opponent(more the better)
    The number of corners captured(It cannot be flipped)
    I calculated every value as a ratio so that the size of the board doesnt affect the heuristics.
    I decrease the heuristic of the base score so that the algorithm will prioritize moves that have better results long term.
    '''
    base_heur = compute_utility(board, color)
    mobility_heur = mobility(board, color)
    corner_heur = corner(board, color)
    return base_heur*0.5 + mobility_heur + corner_heur


############ MINIMAX ###############################
def minimax_min_node(board, color, limit, caching = 0):
    enemy = 3 - color

    if caching:
        if board in cache.keys():
            return cache[board]

    all_moves = get_possible_moves(board, enemy)
    min_util = float('inf')
    min_move = None

    if (not all_moves) or (limit == 0):
        return None, compute_utility(board, color)
    else:
        for move in all_moves:
            new_board = play_move(board, enemy, move[0], move[1])
            _, move_util = minimax_max_node(new_board, color, limit - 1, caching)
            if move_util < min_util:
                min_util, min_move = move_util, move
            if caching:
                cache[new_board] = (move, move_util)
        return min_move, min_util

def minimax_max_node(board, color, limit, caching = 0): #returns highest possible utility
    if caching:
        if board in cache.keys():
            return cache[board]

    all_moves = get_possible_moves(board, color)
    max_util = -float('inf')
    max_move = None

    if (not all_moves) or (limit == 0):
        return None, compute_utility(board, color)
    else:
        for move in all_moves:
            new_board = play_move(board, color, move[0], move[1])
            _, move_util = minimax_min_node(new_board, color, limit - 1, caching)
            if move_util > max_util:
                max_util, max_move = move_util, move
            if caching:
                cache[new_board] = (move, move_util)
        return max_move, max_util

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
    cache.clear()
    move, _ = minimax_max_node(board, color, limit, caching)
    return move

############ ALPHA-BETA PRUNING #####################
def alphabeta_min_node(board, color, alpha, beta, limit, caching = 0, ordering = 0):
    enemy = 3 - color

    if caching:
        if board in cache.keys():
            return cache[board]

    all_moves = get_possible_moves(board, enemy)
    min_util = float('inf')
    min_move = None

    if (not all_moves) or (limit == 0):
        return None, compute_utility(board, color)
    else:
        move_list = []
        for move in all_moves:
            new_board = play_move(board, enemy, move[0], move[1])
            board_util = compute_utility(new_board, color)
            move_list.append((board_util, move, new_board))
        if ordering:
            move_list = sorted(move_list, key=lambda x: x[0])
        for item in move_list:
            val, move, new_board = item
            _, move_util = alphabeta_max_node(new_board, color, alpha, beta, limit - 1, caching, ordering)
            if move_util < min_util:
                min_util, min_move = move_util, move
            if beta > min_util:
                beta = min_util
            if caching:
                cache[new_board] = (move, move_util)
            if beta <= alpha:
                break
        return min_move, min_util

def alphabeta_max_node(board, color, alpha, beta, limit, caching = 0, ordering = 0):
    if caching:
        if board in cache.keys():
            return cache[board]

    all_moves = get_possible_moves(board, color)
    max_util = -float('inf')
    max_move = None

    if (not all_moves) or (limit == 0):
        return None, compute_utility(board, color)
    else:
        move_list = []
        for move in all_moves:
            new_board = play_move(board, color, move[0], move[1])
            board_util = compute_utility(new_board, color)
            move_list.append((board_util, move, new_board))
        if ordering:
            move_list = sorted(move_list, key=lambda x: x[0], reverse=True)
        for item in move_list:
            _, move, new_board = item
            _, move_util = alphabeta_min_node(new_board, color, alpha, beta, limit - 1, caching, ordering)
            if move_util > max_util:
                max_util, max_move = move_util, move
            if alpha < max_util:
                alpha = max_util
            if caching:
                cache[new_board] = (move, move_util)
            if beta <= alpha:
                break
        return max_move, max_util

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
    cache.clear()
    move, _ = alphabeta_max_node(board, color, float("-inf"), float("inf"), limit, caching, ordering)
    return move

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
