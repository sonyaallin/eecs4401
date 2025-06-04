"""
An AI player for Othello. 
"""

# Heuristic Description in compute_heuristic function docstrings

import random
import sys
import time

# Cache of Board State to Minimax Value
CACHE = dict()

# You can use the functions in othello_shared to write your AI
from othello_shared import find_lines, get_possible_moves, get_score, play_move

def eprint(*args, **kwargs): #you can use this for debugging, as it will print to sterr and not stdout
    print(*args, file=sys.stderr, **kwargs)
    
# Method to compute utility value of terminal state
def compute_utility(board, color):
    # utility = player ammount - opponent ammount
    dark, light = get_score(board)
    return dark - light if color == 1 else light - dark

# Better heuristic value of board
def compute_heuristic(board, color):
    '''
    Return heuristic value of game board state.

    Description: calculate heuristic based on the following heuristic factors:

    score: ammount of tiles
    mobility: ability to make many choices
    corner: stability of tiles
    beside corner: instability of tiles
    side: tiles on the edge less likely to change
    inner square: inner square so opponent cant take edges
    lining: instability of tiles

    HEURISTIC GOAL: play inner square all the time and never lining unless we can play
    side or corner excluding beside corners in the first half. the second half will emphasize
    score more since the game is coming to an end.
    '''
    opponent = opponent_color(color)
    dimensions = len(board)
    end = dimensions - 1

    # Count total number tiles for each player
    player, other = 0, 0
    for i in range(dimensions):
        for j in range(dimensions):
            if board[i][j] == color:
                player += 1
            elif board[i][j] == opponent:
                other += 1
    
    # score heuristic
    score = player - opponent
    tiles = player + opponent

    # game strategy
    first_half = (tiles) <= (dimensions - 3) ** 2

    utility = 0
    for i in range(dimensions):
        for j in range(dimensions):

            mine = board[i][j] == color
            yours = board[i][j] == opponent
            empty = board[i][j] == 0

            # mobility heuristic
            if empty:
                if find_lines(board, i, j, color):
                    utility += 1
                elif find_lines(board, i, j, opponent):
                    utility -= 1

            # corner heuristic
            if (i, j) in [(0, 0), (0, end), (end, 0), (end, end)]:
                utility += 3 if mine else -3 if yours else 0

            # beside corner heuristic
            if ((i, j) in [(0, 1), (1, 0), (1, 1)] and board[0][0] == 0 or
                (i, j) in [(0, end - 1), (1, end), (1, end - 1)] and board[0][end] == 0 or
                (i, j) in [(end - 1, 0), (end, 1), (end - 1, 1)] and board[end][0] == 0 or
                (i, j) in [(end - 1, end), (end, end - 1), (end - 1, end - 1)] and board[end][end] == 0):
                utility += -2 if mine else 2 if yours else 0

            # side heuristic
            elif i == 0 or i == end or j == 0 or j == end:
                utility += 1 if mine else -1 if yours else 0

            # opening to midgame strategy
            if first_half:
                # inner square heuristic
                if (1 < i < end - 1) and (1 < j < end - 1):
                    utility += 1 if mine else -1 if yours else 0

                # lining heuristic
                if i == 1 or i == end - 1 or j == 1 or j == end - 1:
                    utility += -2 if mine else -2 if yours else 0

    return score + utility if first_half else 2 * score + utility

# Return color's opponent color
def opponent_color(color):
    return color % 2 + 1

############ MINIMAX ###############################
def minimax_min_node(board, color, limit, caching = 0):
    
    # Check Cache for state
    value = CACHE.get((str(board), color))
    if caching and value:
        return value

    opponent = opponent_color(color)
    moves = get_possible_moves(board, opponent)
    # Terminal Node return utility
    if limit == 0 or not moves:
        return None, compute_utility(board, color)
    
    best_move, min_utility = None, float('inf')

    # Find minimum utility from max over state successors
    for move in moves:
        utility = minimax_max_node(play_move(board, opponent, *move), color, limit - 1, caching)[1]
        if utility < min_utility:
            best_move = move
            min_utility = utility

    # Cache result if possible
    if caching:
        CACHE[(str(board), color)] = best_move, min_utility

    return best_move, min_utility

def minimax_max_node(board, color, limit, caching = 0):

    # Check Cache for state
    value = CACHE.get((str(board), color))
    if caching and value:
        return value
    
    # Terminal Node return utility
    moves = get_possible_moves(board, color)
    if limit == 0 or not moves:
        return None, compute_utility(board, color)
    
    best_move, max_utility = None, - float('inf')

    # Find maximum utility from min over state successors
    for move in moves:
        utility = minimax_min_node(play_move(board, color, *move), color, limit - 1, caching)[1]
        if utility > max_utility:
            best_move = move
            max_utility = utility

    # Cache result if possible
    if caching:
        CACHE[(str(board), color)] = best_move, max_utility

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
    return minimax_max_node(board, color, limit, caching)[0]

############ ALPHA-BETA PRUNING #####################
def alphabeta_min_node(board, color, alpha, beta, limit, caching = 0, ordering = 0):
    
    # Check Cache for state
    value = CACHE.get((str(board), color))
    if caching and value:
        return value

    opponent = opponent_color(color)
    # Terminal Node return utility
    moves = get_possible_moves(board, opponent)
    if limit == 0 or not moves:
        # return None, compute_heuristic(board, color)
        return None, compute_utility(board, color)
    
    best_move, min_utility = None, float('inf')

    # State successors with move taken
    children = [(move, play_move(board, opponent, *move)) for move in moves]

    # Order successors by utility in ascending order for possible faster pruning
    if ordering:
        # children.sort(key=lambda x: compute_heuristic(x[1], color))
        children.sort(key=lambda x: compute_utility(x[1], color))

    # Find minimum utility from max over state successors
    for move, child in children:
        utility = alphabeta_max_node(child, color, alpha, beta, limit - 1, caching, ordering)[1]
        if utility < min_utility:
            best_move = move
            min_utility = utility
        
        # Prune if possible
        beta = min(beta, min_utility)
        if beta <= alpha:
            break
    
    # Cache result if possible
    if caching:
            CACHE[(str(board), color)] = best_move, min_utility

    return best_move, min_utility


def alphabeta_max_node(board, color, alpha, beta, limit, caching = 0, ordering = 0):
    
    # Check Cache for state
    value = CACHE.get((str(board), color))
    if caching and value:
        return value

    # Terminal Node return utility
    moves = get_possible_moves(board, color)
    if limit == 0 or not moves:
        # return None, compute_heuristic(board, color)
        return None, compute_utility(board, color)
    
    best_move, max_utility = None, - float('inf')

    # State successors with move taken
    children = [(move, play_move(board, color, *move)) for move in moves]

    # Order successors by utility in descending order for possible faster pruning
    if ordering:
        # children.sort(key=lambda x: compute_heuristic(x[1], color), reverse=True)
        children.sort(key=lambda x: compute_utility(x[1], color), reverse=True)

    # Find maximum utility from min over state successors
    for move, child in children:
        utility = alphabeta_min_node(child, color, alpha, beta, limit - 1, caching, ordering)[1]
        if utility > max_utility:
            best_move = move
            max_utility = utility
        
        # Prune if possible
        alpha = max(alpha, max_utility)
        if alpha >= beta:
            break
    
    # Cache result if possible
    if caching:
        CACHE[(str(board), color)] = best_move, max_utility

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
    return alphabeta_max_node(board, color, -float('inf'), float('inf'), limit, caching, ordering)[0]

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
