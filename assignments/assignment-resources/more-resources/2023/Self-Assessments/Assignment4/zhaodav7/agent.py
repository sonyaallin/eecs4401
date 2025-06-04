"""
An AI player for Othello. 


##################### HEURISTIC DESCRIPTION #########################
Keep in mind my heuristics is a bit slow since I thought we would want to prioritize winning.
I decided to split the stage into two parts, before and after reaching the 3rd most outter edge of the board.
This is checked through is_endgame() with edge width of 3
The compute utility value of the current state acts as a basis value for this heuristic

Before endgame:
    I apply a mobility heuristic, were we compare the number of moves with the 
    number of potential moves that the opponent could have after our moves and maximize an instance of the distance
    Then I add compute utility value of the current state with it, and return

After reaching endgame:
    I apply a corner/edge detection heuristic, where moves that can cover corners/edges will be rewarded
    and moves that will allow opponent to cover corners/edges will be penalized
    Corners are given double the value of edges
    Maximize a difference between a move with the most corner/edge points and gives away the least corner/edge points
        ** However, if no corners or edges were passed through, mobility heuristic is reapplied.
    Then I add compute utility value of the current state with it, and return

Note that game ending ret values are incredibly enlarged to encourage ending the game when they see an opportunity to win.
"""

import random
import sys
import time

# You can use the functions in othello_shared to write your AI
from othello_shared import find_lines, get_possible_moves, get_score, play_move

min_cache = {}
max_cache = {}

def swap_color(color):
    # switches to other player
    if color == 2:
        return 1
    elif color == 1:
        return 2
    return None

def clear_caches():
    # reset caches
    global min_cache, max_cache
    min_cache = {} 
    max_cache = {}

def order_moves(board, color, moves, reverse):
    # put moves in order of potential
    if reverse:
        ret = sorted(moves, key = lambda x: compute_utility(board, color) + 2*sum(len(l) for l in find_lines(board, x[0], x[1], color)) + 1, reverse=reverse)
    else:
        ret = sorted(moves, key = lambda x: compute_utility(board, color) - 2*sum(len(l) for l in find_lines(board, x[0], x[1], swap_color(color))) - 1, reverse=reverse)
    return ret

def eprint(*args, **kwargs): #you can use this for debugging, as it will print to sterr and not stdout
    print(*args, file=sys.stderr, **kwargs)
    
# Method to compute utility value of terminal state
def compute_utility(board, color):
    # color 1 -> dark, 2 -> light
    dark, light = get_score(board)
    if color == 2:
        return light - dark
    elif color == 1:
        return dark - light
    return None

def is_endgame(board, edge_width):
    # checks if pieces are reaching the edge, 
    # x is the width of edge boundary
    ind = list(range(len(board)))
    edge_ind = list(set(ind[:edge_width] + ind[-edge_width:]))
    for i in edge_ind:
        for j in ind:
            if board[i][j] != 0 or board[j][i] != 0:
                return True
    return False

def whos_turn(board):
    # gives player who's turn it is depending on board
    # as a rule black always start the game therefore goes on evens
    n1, n2 = get_score(board)
    count = n1+n2
    if count % 2 == 0:
        return 1
    else:
        return 2

def is_corner(move, n):
    return (move[0] == 0 or move[0] == n-1) and (move[1] == 0 or move[1] == n-1)

def is_edge(move, n):
    return move[0] == 0 or move[0] == n-1 or move[1] == 0 or move[1] == n-1

# Better heuristic value of board
def compute_heuristic(board, color): # description at the top of file
    c_color = whos_turn(board)
    moves = get_possible_moves(board, c_color)
    ret = compute_utility(board, color)
    n = len(board) # assume >= 4
    
    if moves == []:
        # empathizes winning and losing on last moves since we want to win more
        return ret*n
    
    if is_endgame(board, 3):
        # corner heuristics
        nc = n//2
        ne = n//4
        ret_x = float("-Inf")
        for move in moves:
            total_count = 0
            temp_x = 0
            if is_corner(move, n):
                total_count += 1
                temp_x += nc
            elif is_edge(move, n):
                total_count += 1
                temp_x += ne
            nboard = play_move(board, c_color, move[0], move[1])
            nmoves = get_possible_moves(nboard, swap_color(c_color))
            if nmoves == []:
                ret = compute_utility(nboard, color)
                return ret*n
            nx = float("Inf")
            for nmove in nmoves:
                temp_nx = 0
                if is_corner(nmove, n):
                    total_count += 1
                    temp_nx -= nc
                elif is_edge(nmove, n):
                    total_count += 1
                    temp_nx -= ne
                nx = min(nx, temp_nx)
            temp_x += nx
            if color != c_color:
                temp_x = -temp_x
            ret_x = max(ret_x, temp_x)

            if total_count == 0:
                break

            return ret + ret_x
    
    # not in end_game
    # mobility heuristics
    ret_x = float("-Inf")
    a = len(moves)
    for move in moves:
        omoves = get_possible_moves(play_move(board, color, move[0], move[1]), swap_color(color))
        b = len(omoves)
        temp_x = a-b

        if color != c_color:
            temp_x = -temp_x
        ret_x = max(ret_x, temp_x)
    return ret + ret_x

############ MINIMAX ###############################
def minimax_min_node(board, color, limit, caching = 0):
    global min_cache, max_cache
    key = hash(board)
    if caching and key in min_cache:
        return min_cache[key]
    if limit <= 0:
        return (None, compute_utility(board, color))
    moves = get_possible_moves(board, swap_color(color))
    if moves:
        best_move = None
        min_val = float("Inf")
        for move in moves:
            temp_board = play_move(board, swap_color(color), move[0], move[1])
            prev_move, temp_val = minimax_max_node(temp_board, color, limit-1, caching)
            if temp_val < min_val:
                min_val = temp_val
                best_move = move
        if caching:
            min_cache[key] = (best_move, min_val)
        return (best_move, min_val)
    else:
        ret = (None, compute_utility(board, color))
        if caching:
            min_cache[key] = ret
            max_cache[key] = ret
        return ret

def minimax_max_node(board, color, limit, caching = 0): #returns highest possible utility
    global max_cache, min_cache
    key = hash(board)
    if caching and key in max_cache:
        return max_cache[key]
    if limit <= 0:
        return (None, compute_utility(board, color))
    moves = get_possible_moves(board, color)
    if moves:
        best_move = None
        max_val = float("-Inf")
        for move in moves:
            temp_board = play_move(board, color, move[0], move[1])
            prev_move, temp_val = minimax_min_node(temp_board, color, limit-1, caching)
            if temp_val > max_val:
                max_val = temp_val
                best_move = move
        if caching:
            max_cache[key] = (best_move, max_val)
        return (best_move, max_val)
    else:
        ret = (None, compute_utility(board, color))
        if caching:
            max_cache[key] = ret
            min_cache[key] = ret
        return ret


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
    if caching:
        clear_caches()
    move, val = minimax_max_node(board, color, limit, caching)
    return move

############ ALPHA-BETA PRUNING #####################
def alphabeta_min_node(board, color, alpha, beta, limit, caching = 0, ordering = 0):
    global min_cache, max_cache
    key = hash(board)
    if caching and key in min_cache:
        return min_cache[key]
    if limit <= 0:
        return (None, compute_utility(board, color))
    moves = get_possible_moves(board, swap_color(color))
    if moves:
        if ordering:
            moves = order_moves(board, color, moves, reverse=False)
        best_move = None
        min_val = float("Inf")
        for move in moves:
            temp_board = play_move(board, swap_color(color), move[0], move[1])
            prev_move, temp_val = alphabeta_max_node(temp_board, color, alpha, beta, limit-1, caching, ordering)
            if temp_val < min_val:
                min_val = temp_val
                best_move = move
            # a-b portion
            if min_val < beta:
                beta = min_val
                if beta <= alpha:
                    break
        if caching: 
            min_cache[key] = (best_move, min_val)
        return (best_move, min_val)
    else:
        ret = (None, compute_utility(board, color))
        if caching: 
            min_cache[key] = max_cache[key] = ret
        return ret

def alphabeta_max_node(board, color, alpha, beta, limit, caching = 0, ordering = 0):
    global max_cache, min_cache
    key = hash(board)
    if caching and key in max_cache:
        return max_cache[key]
    if limit <= 0:
        return (None, compute_utility(board, color))
    moves = get_possible_moves(board, color)
    if moves:
        if ordering:
            moves = order_moves(board, color, moves, reverse=True)
        best_move = None
        max_val = float("-Inf")
        for move in moves:
            temp_board = play_move(board, color, move[0], move[1])
            prev_move, temp_val = alphabeta_min_node(temp_board, color, alpha, beta, limit-1, caching, ordering)
            if temp_val > max_val:
                max_val = temp_val
                best_move = move
            # a-b portion
            if max_val > alpha:
                alpha = max_val
                if beta <= alpha:
                    break
        if caching: 
            max_cache[key] = (best_move, max_val)
        return (best_move, max_val)
    else:
        ret = (None, compute_utility(board, color))
        if caching: 
            max_cache[key] = min_cache[key] = ret
        return ret

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
    if caching:
        clear_caches()
    move, val = alphabeta_max_node(board, color, float("-Inf"), float("Inf"), limit, caching, ordering)
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
