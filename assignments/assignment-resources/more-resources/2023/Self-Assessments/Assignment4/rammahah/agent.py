"""
An AI player for Othello.
"""

"""
Heuristic Description: Calculates the score of the board but weights the 
value of stable pieces as double those of non-stable pieces. Returns the 
difference between the player's score and the opponents score.
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
    #IMPLEMENT
    dark, light = get_score(board)
    if color == 1:
        return dark - light
    else:
        return light - dark

# Better heuristic value of board
def compute_heuristic(board, color): 
    #IMPLEMENT
    p1_count = 0
    p2_count = 0
    for i in range(len(board)):
        for j in range(len(board)):
            stable = is_stable(board, i, j)
            if board[i][j] == 1:
                if stable == 1:
                    p1_count += 2
                else:
                    p1_count += 1
            elif board[i][j] == 2:
                if stable == 2:
                    p2_count += 2
                else:
                    p2_count += 1
    if color == 1:
        return p1_count - p2_count
    else:
        return p2_count - p1_count

############ MINIMAX ###############################
def minimax_min_node(board, color, limit, caching = 0):
    #IMPLEMENT (and replace the line below)

    if limit == 0:
        return None, compute_utility(board, color)

    moves = get_possible_moves(board, 3 - color)
    if moves == []:
        return None, compute_utility(board, color)
    min_val = float("Inf")
    min_move = (0,0)
    for x in moves:
        if caching:
            val = cache.get(x)
        if caching == 0 or not val:
            new_board = play_move(board, 3 - color, x[0], x[1])
            move, val = minimax_max_node(new_board, color, limit - 1)
            if caching:
                cache[x] = val
        if val < min_val:
            min_val = val
            min_move = x

    return (min_move, min_val)


def minimax_max_node(board, color, limit, caching = 0): #returns highest possible utility
    #IMPLEMENT (and replace the line below)
    if limit == 0:
        return None, compute_utility(board, color)

    moves = get_possible_moves(board, color)
    if moves == []:
        return None, compute_utility(board, color)
    max_val = float("-Inf")
    max_move = (0, 0)
    for x in moves:
        if caching:
            val = cache.get(x)
        if caching == 0 or not val:
            new_board = play_move(board, color, x[0], x[1])
            move, val = minimax_min_node(new_board, color, limit - 1)
            if caching:
                cache[x] = val
        if val > max_val:
            max_val = val
            max_move = x

    return (max_move, max_val)

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
    if limit == 0:
        limit = -1
    move, val = minimax_max_node(board, color, limit, caching)
    return move

############ ALPHA-BETA PRUNING #####################
def alphabeta_min_node(board, color, alpha, beta, limit, caching = 0, ordering = 0):
    #IMPLEMENT (and replace the line below)
    if limit == 0:
        return None, compute_utility(board, color)
    moves = get_possible_moves(board, 3 - color)
    if not moves:
        return None, compute_utility(board, color)
    ut_val = float("Inf")
    min_move = (0,0)

    successors = get_successors(board, moves, color, 3 - color)

    curr = 0

    next = next_successor(successors, curr)
    curr += 1

    while next:
        x = next[2]
        b = next[1]
        if caching:
            val = cache.get(x)
        if caching == 0 or not val:
            move, val = alphabeta_max_node(b, color, alpha, beta, limit - 1, caching, ordering)
            if caching:
                cache[x] = val
        if val < ut_val:
            ut_val = val
            min_move = x
            if beta > ut_val:
                beta = ut_val
                if beta <= alpha:
                    break
        next = next_successor(successors, curr)
        curr += 1

    return (min_move,ut_val)

def alphabeta_max_node(board, color, alpha, beta, limit, caching = 0, ordering = 0):
    #IMPLEMENT (and replace the line below)
    if limit == 0:
        return None, compute_utility(board, color)
    moves = get_possible_moves(board, color)
    if not moves:
        return None, compute_utility(board, color)
    ut_val = float("-Inf")
    max_move = (0, 0)

    successors = get_successors(board, moves, color, color)

    curr = 0

    next = next_successor(successors, curr)
    curr += 1

    while next:
        x = next[2]
        b = next[1]
        if caching:
            val = cache.get(x)
        if caching == 0 or not val:
            move, val = alphabeta_min_node(b, color, alpha, beta, limit - 1,
                                     caching, ordering)
            if caching:
                cache[x] = val
        if val > ut_val:
            ut_val = val
            max_move = x
            if alpha < ut_val:
                alpha = ut_val
                if beta <= alpha:
                    break
        next = next_successor(successors, curr)
        curr += 1

    return (max_move, ut_val)

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
    if limit == 0:
        limit = -1
    move, val = alphabeta_max_node(board, color, float("-Inf"), float("Inf"), limit, caching)
    return move

def get_successors(board, moves, color, player):
    new = []
    for x in moves:
        new_board = new_board = play_move(board, player, x[0], x[1])
        ut = compute_utility(new_board, color)
        new.append((ut,new_board,x))
    return new

def next_successor(successors, curr):
    n = len(successors)
    if curr == n:
        return None
    largest = None
    ut_val = float("-Inf")
    for i in range(curr, n):
        val = successors[i][0]
        if (val > ut_val):
            largest = i
            ut_val = val

    successors[largest], successors[curr] = successors[curr], successors[largest]
    return successors[curr]

def is_stable(board, i, j):
    color = board[i][j]
    if color == 0:
        return 0
    for xdir, ydir in [[0, 1], [1, 1], [1, 0], [1, -1]]:
        u = i
        v = j
        line = []

        u += xdir
        v += ydir
        found = check_line(board, (3-color), u, v, xdir, ydir)
        u = i
        v = j
        xdir2 = -xdir
        ydir2 = -ydir
        u += xdir2
        v += ydir2
        if found == 0:
            check = check_line(board, (3-color), u, v, xdir2, ydir2)
            if check != color:
                return 0
        elif found == (3-color):
            check = check_line(board, (3 - color), u, v, xdir2, ydir2)
            if check == 0:
                return 0
    return color

def check_line(board, target, u, v, xdir, ydir):
    while u >= 0 and u < len(board) and v >= 0 and v < len(board):
        if board[v][u] == 0:
            return 0
        elif board[v][u] == target:
            return target
        u += xdir
        v += ydir
    return (3 - target)


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
        #print("input:", next_input)
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
