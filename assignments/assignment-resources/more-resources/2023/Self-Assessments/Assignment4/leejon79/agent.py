"""
An AI player for Othello. 
"""

"""
NOTE: I did not make a heuristic beyond just computing compute_utility. Mostly due to personal time constraints.
"""

import random
import sys
import time

# You can use the functions in othello_shared to write your AI
from othello_shared import find_lines, get_possible_moves, get_score, play_move

prev_boards = {}

def eprint(*args, **kwargs): #you can use this for debugging, as it will print to sterr and not stdout
    print(*args, file=sys.stderr, **kwargs)
    
# Method to compute utility value of terminal state
def compute_utility(board, color):
    #IMPLEMENT
    if color == 1:
        return get_score(board)[0] - get_score(board)[1]
    return get_score(board)[1]- get_score(board)[0]

# Better heuristic value of board
def compute_heuristic(board, color): #not implemented, optional
    #IMPLEMENT
    return compute_utility(board, color)

############ MINIMAX ###############################
def minimax_min_node(board, color, limit, caching = 0):
    #IMPLEMENT (and replace the line below)
    if caching == 1 and board in prev_boards.keys():
        return prev_boards[board]
    moves = get_possible_moves(board, color)
    if moves == []:
        util = compute_utility(board, color)
        if caching == 1:
            prev_boards[board] = util
        return (None, compute_utility(board, color))
    else:
        if limit == 0:
            return compute_heuristic(board, color)
        abs_min = 999999999999
        obs_color = 0
        if color == 0:
            obs_color = 1
        col = 0
        row = 0
        for move in get_possible_moves(board, color):
            curr_board = play_move(board, color, move[0], move[1])
            curr = minimax_max_node(curr_board, obs_color, limit - 1, caching)
            if curr[1] < abs_min:
                abs_min = curr[1]
                col = move[0]
                row = move[1]
        if caching == 1:
            prev_board[board] = abs_min
        return ((col,row),abs_min)

def minimax_max_node(board, color, limit, caching = 0): #returns highest possible utility
    #IMPLEMENT (and replace the line below)
    if caching == 1 and board in prev_boards.keys():
        return prev_boards[board]
    moves = get_possible_moves(board, color)
    if moves == []:
        util = compute_utility(board, color)
        if caching == 1:
            prev_boards[board] = util
        return (None, compute_utility(board, color))
    else:
        if limit == 0:
            return compute_heuristic(board, color)
        abs_max = -999999999999
        obs_color = 0
        if color == 0:
            obs_color = 1
        col = 0
        row = 0
        for move in get_possible_moves(board, color):
            curr_board = play_move(board, color, move[0], move[1])
            curr = minimax_min_node(curr_board, obs_color, limit - 1, caching)
            if curr[1] > abs_max:
                abs_max = curr[1]
                col = move[0]
                row = move[1]
        if caching == 1:
            prev_boards[board] = abs_max
        return ((col,row),abs_max)

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
    #IMPLEMENT (and replace the line below)
    curr = 9999999999
    if caching == 1 and board in prev_boards.keys():
        return prev_boards[board]
    moves = get_possible_moves(board, color)
    if moves == []:
        util = compute_utility(board, color)
        if caching == 1:
            prev_boards[board] = util
        return (None, compute_utility(board, color))
    else:
        if limit == 0:
            return compute_heuristic(board, color)
        obs_color = 0
        if color == 0:
            obs_color = 1
        col = 0
        row = 0
        b = beta
        if ordering == 0:
            for move in get_possible_moves(board, color):
                curr_board = play_move(board, color, move[0], move[1])
                curr = alphabeta_max_node(curr_board, obs_color, alpha, b, limit - 1, caching, ordering)[1]
                if b > curr:
                    b = curr
                    col = move[0]
                    row = move[1]
                    if b <= alpha:
                        if caching == 1:
                            prev_boards[board] = curr
                        return ((col,row), curr)
        else:
            order = []
            for move in get_possible_moves(board, color):
                curr_board = play_move(board, color, move[0], move[1])
                curr_ut = compute_utility(curr_board, color)
                inserted = False
                for i in range(len(order)):
                    if curr_ut > order[i][1]:
                        inserted = True
                        order.insert(i, (curr_board, curr_ut))
                        break
                if order == False:
                    order.append((curr_board, curr_ut))

            for curr_b in order:
                curr = alphabeta_max_node(curr_b, obs_color, alpha, b, limit - 1, caching, ordering)[1]
                if b > curr:
                    b = curr
                    col = move[0]
                    row = move[1]
                    if b <= alpha:
                        if caching == 1:
                            prev_boards[board] = curr
                        return ((col,row), curr)
        if caching == 1:
            prev_boards[board] = curr
        return ((col,row),curr)

def alphabeta_max_node(board, color, alpha, beta, limit, caching = 0, ordering = 0):
    #IMPLEMENT (and replace the line below)
    curr = -9999999999
    if caching == 1 and board in prev_boards.keys():
        return prev_boards[board]
    moves = get_possible_moves(board, color)
    if moves == []:
        util = compute_utility(board, color)
        if caching == 1:
            prev_boards[board] = util
        return (None, compute_utility(board, color))
    else:
        if limit == 0:
            return compute_heuristic(board, color)
        obs_color = 0
        if color == 0:
            obs_color = 1
        col = 0
        row = 0
        a = alpha
        if ordering == 0:
            for move in get_possible_moves(board, color):
                curr_board = play_move(board, color, move[0], move[1])
                curr = alphabeta_min_node(curr_board, obs_color, a, beta, limit - 1, caching, ordering)[1]
                if a < curr:
                    a = curr
                    col = move[0]
                    row = move[1]
                    if beta <= a:
                        if caching == 1:
                            prev_boards[board] = curr
                        return ((col,row), curr)
        else:
            order = []
            for move in get_possible_moves(board, color):
                curr_board = play_move(board, color, move[0], move[1])
                curr_ut = compute_utility(curr_board, color)
                inserted = False
                for i in range(len(order)):
                    if curr_ut > order[i][1]:
                        inserted = True
                        order.insert(i, (curr_board, curr_ut))
                        break
                if order == False:
                    order.append((curr_board, curr_ut))
            for move in get_possible_moves(board, color):
                curr_board = play_move(board, color, move[0], move[1])
                curr = alphabeta_min_node(curr_board, obs_color, a, beta, limit - 1, caching, ordering)[1]
                if a < curr:
                    a = curr
                    col = move[0]
                    row = move[1]
                    if beta <= a:
                        if caching == 1:
                            prev_boards[board] = curr
                        return ((col,row), curr)
        if caching == 1:
            prev_boards[board] = curr
        return ((col,row),curr)

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
    return alphabeta_max_node(board, color, -99999999999, 99999999999, limit, caching, ordering)[0]

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
