"""
An AI player for Othello. 
"""

"""
Heuristic explanation:
- Use difference in tiles as base value; same as utility function.
- Corners are worth double, because they can't be flipped.
- Having tiles around the corners is -1 each, since they provide the opponent access to the corner.
  This goes for both the player and the opponent.
- Having more move options than your opponent is ideal. Add the difference in number of legal moves.
"""

import random
import sys
import time

# You can use the functions in othello_shared to write your AI
from othello_shared import find_lines, get_possible_moves, get_score, play_move

def eprint(*args, **kwargs): #you can use this for debugging, as it will print to sterr and not stdout
    print(*args, file=sys.stderr, **kwargs)
    
def other_color(color):
    return (color % 2) + 1

# Method to compute utility value of terminal state
def compute_utility(board, color):
    dark, light = get_score(board)
    return dark - light if color == 1 else light - dark

# Better heuristic value of board
def compute_heuristic(board, color):
    diff = compute_utility(board, color)
    other = other_color(color)
    n = len(board)
    corners = [(0, 0), (0, n-1), (n-1, 0), (n-1, n-1)]
    near_corners = [
        (1,0),(1,1),(0,1),
        (1,n-1),(1,n-2),(0,n-2),
        (n-1,1),(n-2,1),(n-2,0),
        (n-2,n-1),(n-2,n-2),(n-1,n-2)
    ]

    for x,y in corners:
        if board[y][x] == color:
            diff += 1
        elif board[y][x] == other:
            diff -= 1
    
    for x,y in near_corners:
        if board[y][x] == color:
            diff -= 1
        elif board[y][x] == other:
            diff += 1

    our_moves = get_possible_moves(board, color)
    their_moves = get_possible_moves(board, other)
    diff += len(our_moves) - len(their_moves)

    return diff

state_cache = dict()

############ MINIMAX ###############################
MOVE = 0
UTILITY = 1

def minimax_min_node(board, color, limit, caching = 0):  # returns lowest possible utility for color
    # color is the antagonist
    next_color = other_color(color)
    legal_moves = get_possible_moves(board, next_color)
    if len(legal_moves) == 0:
        temp = (None, compute_utility(board, color))
        if caching == 1:
            state_cache[board] = temp
        return temp

    if limit == 0:
        return (None, compute_utility(board, color))

    best_move = None
    best_utility = float('inf')
    for move in legal_moves:
        successor_board = play_move(board, next_color, *move)
        next_turn = state_cache.get(successor_board)
        if next_turn is None:
            next_turn = minimax_max_node(successor_board, color, limit-1, caching)
        if next_turn[UTILITY] < best_utility:
            best_utility = next_turn[UTILITY]
            best_move = move

    if caching == 1:
        state_cache[board] = (best_move, best_utility)
    
    return (best_move, best_utility)


def minimax_max_node(board, color, limit, caching = 0): #returns highest possible utility
    # color is the protagonist
    legal_moves = get_possible_moves(board, color)
    if len(legal_moves) == 0:
        temp = (None, compute_utility(board, color))
        if caching == 1:
            state_cache[board] = temp
        return temp

    if limit == 0:
        return (None, compute_utility(board, color))

    best_move = None
    best_utility = float('-inf')
    for move in legal_moves:
        successor_board = play_move(board, color, *move)
        next_turn = state_cache.get(successor_board)
        if next_turn is None:
            next_turn = minimax_min_node(successor_board, color, limit-1, caching)
        if next_turn[UTILITY] > best_utility:
            best_utility = next_turn[UTILITY]
            best_move = move

    if caching == 1:
        state_cache[board] = (best_move, best_utility)
    
    return (best_move, best_utility)


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
    global state_cache
    state_cache = dict()

    best_move = minimax_max_node(board, color, limit, caching)
    return best_move[0]


############ ALPHA-BETA PRUNING #####################
def alphabeta_min_node(board, color, alpha, beta, limit, caching = 0, ordering = 0):
    next_color = other_color(color)
    legal_moves = get_possible_moves(board, next_color)
    if len(legal_moves) == 0:
        temp = (None, compute_utility(board, color))
        if caching == 1:
            state_cache[board] = temp
        return temp

    if limit == 0:
        return (None, compute_utility(board, color))

    best_move = None
    best_utility = float('inf')
    if ordering == 1:
        legal_moves.sort(key=lambda move: compute_utility(play_move(board, next_color, *move), color))

    for move in legal_moves:
        successor_board = play_move(board, next_color, *move)
        next_turn = state_cache.get(successor_board)
        if next_turn is None:
            next_turn = alphabeta_max_node(successor_board, color, alpha, beta, limit-1, caching, ordering)
        if next_turn[UTILITY] < best_utility:
            best_utility = next_turn[UTILITY]
            best_move = move

        if beta > best_utility:
            beta = best_utility

            if alpha >= beta:
                break

    if caching == 1:
        state_cache[board] = (best_move, best_utility)

    return (best_move, best_utility)


def alphabeta_max_node(board, color, alpha, beta, limit, caching = 0, ordering = 0):
    legal_moves = get_possible_moves(board, color)
    if len(legal_moves) == 0:
        temp = (None, compute_utility(board, color))
        if caching == 1:
            state_cache[board] = temp
        return temp

    if limit == 0:
        return (None, compute_utility(board, color))

    best_move = None
    best_utility = float('-inf')
    if ordering == 1:
        legal_moves.sort(key=lambda move: compute_utility(play_move(board, color, *move), color))

    for move in legal_moves:
        successor_board = play_move(board, color, *move)
        next_turn = state_cache.get(successor_board)
        if next_turn is None:
            next_turn = alphabeta_min_node(successor_board, color, alpha, beta, limit-1, caching, ordering)
        if next_turn[UTILITY] > best_utility:
            best_utility = next_turn[UTILITY]
            best_move = move
        
        if best_utility > alpha:
            alpha = best_utility
        
            if alpha >= beta:
                break

    if caching == 1:
        state_cache[board] = (best_move, best_utility)

    return (best_move, best_utility)


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
    global state_cache
    state_cache = dict()
    alpha, beta = float('-inf'), float('inf')

    best_move = alphabeta_max_node(board, color, alpha, beta, limit, caching, ordering)
    return best_move[0]

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
