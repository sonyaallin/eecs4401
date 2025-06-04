"""
An AI player for Othello. 
"""

"""
My Heuristic Function (Also written as the doctest of the function)

This heuristics uses multiple different values to compute an heuristic. It uses percentage of coins, 
percentage of legal moves, percentage of corner controlled, and percentage of adjacent corners that 
are captured. Note that these 4 values all have a weight signifying their importance in computing their 
heuristic. All the weights are a educated estimate of their true value.

If you have more coins than your opponent than you would win the game signifying that the amount of coins 
are very important. But the amount of coins only matters towards the end of the game. It is usually good 
to have a better position. Hence percentage of coins only has a weight of 1.

If you have more moves available than your opponent than it means you are restricting your opponent from 
making moves. Hence percentage of legal moves are valued at 10.

If you control the corners that allows you to set a base of tokens that will never be captured. This is 
because a token in the corner can never be captured (since no coin can go on the other side of the corner 
coin). Hence the weight is set to 20. 

Note that percentage of adjacent corners has a negative value since in othello you want to 
capture the corners meaning if you capture the adjacent corners it helps the opponent capture the corners. 
Hence it has a weight of -10.
"""

import random
import sys
import time

# You can use the functions in othello_shared to write your AI
from othello_shared import find_lines, get_possible_moves, get_score, play_move

CACHING_STATES_MIN = {}
CACHING_STATES_MAX = {}

def eprint(*args, **kwargs): #you can use this for debugging, as it will print to sterr and not stdout
    print(*args, file=sys.stderr, **kwargs)
    
# Method to compute utility value of terminal state
def compute_utility(board, color):

    p1_count, p2_count = get_score(board)
    if color == 1:
        return p1_count - p2_count
    else:
        return p2_count - p1_count

# Better heuristic value of board
def compute_heuristic(board, color):
    """
    This heuristics uses multiple different values to compute an heuristic. It uses percentage of coins, 
    percentage of legal moves, percentage of corner controlled, and percentage of adjacent corners that 
    are captured. Note that these 4 values all have a weight signifying their importance in computing their 
    heuristic. All the weights are a educated estimate of their true value.
    
    If you have more coins than your opponent than you would win the game signifying that the amount of coins 
    are very important. But the amount of coins only matters towards the end of the game. It is usually good 
    to have a better position. Hence percentage of coins only has a weight of 1.

    If you have more moves available than your opponent than it means you are restricting your opponent from 
    making moves. Hence percentage of legal moves are valued at 10.

    If you control the corners that allows you to set a base of tokens that will never be captured. This is 
    because a token in the corner can never be captured (since no coin can go on the other side of the corner 
    coin). Hence the weight is set to 20. 

    Note that percentage of adjacent corners has a negative value since in othello you want to 
    capture the corners meaning if you capture the adjacent corners it helps the opponent capture the corners. 
    Hence it has a weight of -10.
    """
    opp_color = [0, 2, 1][color]

    # Percentage of Coins you have compared to your opponent
    p1_count, p2_count = get_score(board)
    if p1_count == color:
        coin_parity = (p1_count - p2_count)/(p1_count + p2_count)
    else:
        coin_parity = (p2_count - p1_count)/(p2_count + p1_count)
    
    # Percentage of legal moves you have compared to your opponent
    p1_moves, p2_moves = len(get_possible_moves(board, color)), len(get_possible_moves(board, opp_color))
    if p1_moves + p2_moves != 0:
        mobility = (p1_moves - p2_moves)/(p1_moves + p2_moves)
    else:
        mobility = 0

    # Percentage of corners that are captured by you
    p1_corners = (board[0][0] == color) + (board[0][-1] == color) + (board[-1][0] == color) + (board[-1][-1] == color)
    p2_corners = (board[0][0] == opp_color) + (board[0][-1] == opp_color) + (board[-1][0] == opp_color) + (board[-1][-1] == opp_color)

    if p1_corners + p2_corners != 0:
        corners = (p1_corners - p2_corners)/(p1_corners + p2_corners)
    else:
        corners = 0

    # Percentage of adjacent corners that are captured by you
    p1_corners_closeness = (board[0][1] == color) + (board[1][0] == color) + (board[1][1] == color) + \
                            (board[0][-2] == color) + (board[1][-1] == color) + (board[1][-2] == color) + \
                            (board[-2][0] == color) + (board[-1][1] == color) + (board[-2][1] == color) + \
                            (board[-1][-2] == color) + (board[-2][-1] == color) + (board[-2][-2] == color)

    p2_corners_closeness = (board[0][1] == opp_color) + (board[1][0] == opp_color) + (board[1][1] == opp_color) + \
                            (board[0][-2] == opp_color) + (board[1][-1] == opp_color) + (board[1][-2] == opp_color) + \
                            (board[-2][0] == opp_color) + (board[-1][1] == opp_color) + (board[-2][1] == opp_color) + \
                            (board[-1][-2] == opp_color) + (board[-2][-1] == opp_color) + (board[-2][-2] == opp_color)

    if p1_corners_closeness + p2_corners_closeness != 0:
        corners_closeness = (p1_corners_closeness - p2_corners_closeness)/(p1_corners_closeness + p2_corners_closeness)
    else:
        corners_closeness = 0

    return (1 * coin_parity) + (20 * corners) + (-10 * corners_closeness) + (10 * mobility)

############ MINIMAX ###############################
def minimax_min_node(board, color, limit, caching = 0):

    board_key = tuple(map(tuple, board))
    if caching == 1 and (board_key, color) in CACHING_STATES_MIN:
        return CACHING_STATES_MIN[(board_key, color)]

    opp_color = [0, 2, 1][color]
    result = get_possible_moves(board, opp_color)

    if not result:
        return ((-1, -1), compute_utility(board, color))
    elif limit == 0:
        return ((-1, -1), compute_utility(board, color))
    else:
        all_scores = []
        
        for move_x, move_y in result:
            new_board = play_move(board, opp_color, move_x, move_y)
            _, score = minimax_max_node(new_board, color, limit-1, caching)
            all_scores.append(score)
        
        if caching == 1:
            CACHING_STATES_MIN[(board_key, color)] = (result[all_scores.index(min(all_scores))], min(all_scores))
            return CACHING_STATES_MIN[(board_key, color)]
        else:
            return result[all_scores.index(min(all_scores))], min(all_scores)

def minimax_max_node(board, color, limit, caching = 0): #returns highest possible utility

    board_key = tuple(map(tuple, board))
    if caching == 1 and (board_key, color) in CACHING_STATES_MAX:
        return CACHING_STATES_MAX[(board_key, color)]

    result = get_possible_moves(board, color)

    if not result:
        return ((-1, -1), compute_utility(board, color))
    elif limit == 0:
        return ((-1, -1), compute_utility(board, color))
    else:
        all_scores = []
        
        for move_x, move_y in result:
            new_board = play_move(board, color, move_x, move_y)
            _, score = minimax_min_node(new_board, color, limit-1, caching)
            all_scores.append(score)

        if caching == 1:
            CACHING_STATES_MAX[(board_key, color)] = (result[all_scores.index(max(all_scores))], max(all_scores))
            return CACHING_STATES_MAX[(board_key, color)]
        else:
            return result[all_scores.index(max(all_scores))], max(all_scores)

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
    move, _ = minimax_max_node(board, color, limit, caching)
    return move

############ ALPHA-BETA PRUNING #####################
def alphabeta_min_node(board, color, alpha, beta, limit, caching = 0, ordering = 0):

    board_key = tuple(map(tuple, board))
    if caching == 1 and (board_key, color) in CACHING_STATES_MIN:
        return CACHING_STATES_MIN[(board_key, color)]

    opp_color = [0, 2, 1][color]
    result = get_possible_moves(board, opp_color)

    if not result:
        return ((-1, -1), compute_utility(board, color))
    elif limit == 0:
        return ((-1, -1), compute_utility(board, color))
    else:
        opt_move = (-1, -1)

        if ordering == 1:
            ord_heuristic = []

            for move_x, move_y in result:
                new_board = play_move(board, color, move_x, move_y)
                ord_heuristic.append(compute_utility(new_board, color))

            temp_results = result.copy()
            result = []
            for _ in range(len(temp_results)):
                index = ord_heuristic.index(min(ord_heuristic))
                result.append(temp_results[index])
                ord_heuristic[index] = float("inf")


        for move_x, move_y in result:
            new_board = play_move(board, opp_color, move_x, move_y)
            _, score = alphabeta_max_node(new_board, color, alpha, beta, limit-1, caching, ordering)

            if score < beta:
                beta = score
                opt_move = (move_x, move_y)

            if beta <= alpha:
                if caching == 1:
                    CACHING_STATES_MIN[(board_key, color)] = (opt_move, beta)
                    return CACHING_STATES_MIN[(board_key, color)]
                else:
                    return opt_move, beta
        
        if caching == 1:
            CACHING_STATES_MIN[(board_key, color)] = (opt_move, beta)
            return CACHING_STATES_MIN[(board_key, color)]
        else:
            return opt_move, beta

def alphabeta_max_node(board, color, alpha, beta, limit, caching = 0, ordering = 0):

    board_key = tuple(map(tuple, board))
    if caching == 1 and (board_key, color) in CACHING_STATES_MAX:
        return CACHING_STATES_MAX[(board_key, color)]

    result = get_possible_moves(board, color)

    if not result:
        return ((-1, -1), compute_utility(board, color))
    elif limit == 0:
        return ((-1, -1), compute_utility(board, color))
    else:
        opt_move = (-1, -1)
        
        if ordering == 1:
            ord_heuristic = []

            for move_x, move_y in result:
                new_board = play_move(board, color, move_x, move_y)
                ord_heuristic.append(compute_utility(new_board, color))

            temp_results = result.copy()
            result = []
            for _ in range(len(temp_results)):
                index = ord_heuristic.index(max(ord_heuristic))
                result.append(temp_results[index])
                ord_heuristic[index] = -float("inf")

        
        for move_x, move_y in result:
            new_board = play_move(board, color, move_x, move_y)
            _, score = alphabeta_min_node(new_board, color, alpha, beta, limit-1, caching, ordering)

            if score > alpha:
                alpha = score
                opt_move = (move_x, move_y)
            
            if beta <= alpha:
                if caching == 1:
                    CACHING_STATES_MAX[(board_key, color)] = (opt_move, alpha)
                    return CACHING_STATES_MAX[(board_key, color)]
                else:
                    return opt_move, alpha

        if caching == 1:
            CACHING_STATES_MAX[(board_key, color)] = (opt_move, alpha)
            return CACHING_STATES_MAX[(board_key, color)]
        else:
            return opt_move, alpha

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
    #IMPLEMENT (and replace the line below)
    move, _ = alphabeta_max_node(board, color, -float("inf"), float("inf"), limit, caching, ordering)
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
