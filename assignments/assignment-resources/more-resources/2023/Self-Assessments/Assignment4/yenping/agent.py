"""
An AI player for Othello. 
"""

import random
import sys
import time

# You can use the functions in othello_shared to write your AI
from othello_shared import find_lines, get_possible_moves, get_score, play_move

board_cache = {}

def eprint(*args, **kwargs): #you can use this for debugging, as it will print to sterr and not stdout
    print(*args, file=sys.stderr, **kwargs)
    
# Method to compute utility value of terminal state
def compute_utility(board, color):
    dark, light = get_score(board)
    if color == 1: # player 1 - dark
        return dark - light
    else: # player 2 - light
        return light - dark

# Better heuristic value of board
def compute_heuristic(board, color): #not implemented, optional
    """
    I am considering 3 things in my heuristic implementation
    1. Utility score
       This is the original heuristic we have, and it is able to provide us a good AI player. Therefore, extending from this
       heuristic should be able to construct a better heuristic.
    2. Number of possible moves
       After playing a few Othello games, I discover that when I have more move choices, the greater the change of winning.
       I also discover that the number of possible moves has a much stronger effect on whether I am winning or not, hence, I
       will assign this value a larger weight than the utility score.
    3. Corner choice of next move
       Pieces that are placed in the corner will never be flipped during the game, hence the more coner you take, the higher
       chance of winning. Therefore, I am assignin corner moves with the highest weight to establish this observation.

    Weighting strategy
        Utility score - 1
        Number of possible moves - 5
        Corner moves - 10
    """
    w = len(board)
    corners = [(0,0), (0, w-1), (w-1, 0), (w-1,w-1)]
    
    # Utility score
    score = compute_utility(board, color)

    moves = get_possible_moves(board, color)

    # Corner moves
    corner_count = 0
    for corner in corners:
        if corner in moves:
            corner_count += 1

    # Number of possble moves - Don't re-count the corner moves
    num_move = len(moves) - corner_count
    return score + 5 * num_move + 10 * corner_count



############ MINIMAX ###############################
def minimax_min_node(board, color, limit, caching = 0):
    # "color" is the MAX player --> make move with the other player (MIN player)
    # Compute utility with respect to the MAX player i.e., color

    # Check caching
    if caching == 1 and board in board_cache:
        return board_cache[board]
    
    # Check depth limit
    if limit == 0:
        return None, compute_utility(board, color)
        # return None, compute_heuristic(board, color)
    
    # Check remaining moves
    other_player = 2 if color == 1 else 1
    moves = get_possible_moves(board, other_player)
    if len(moves) == 0:
        return None, compute_utility(board, color)
        # return None, compute_heuristic(board, color)
    
    # Find best move
    min_move = None
    min_score = float('inf')
    for move in moves:
        # Get utility score
        x, y = move
        next_board = play_move(board, other_player, x, y)
        _, score = minimax_max_node(next_board, color, limit-1, caching)

        #Check minimum
        if score < min_score:
            min_score = score
            min_move = move
    
    # Cache the found minimum move and utility score
    if caching == 1:
        board_cache[board] = (min_move, min_score)

    return min_move, min_score

def minimax_max_node(board, color, limit, caching = 0): #returns highest possible utility
    # Check caching
    if caching == 1 and board in board_cache:
        return board_cache[board]
    
    # Check depth limit
    if limit == 0:
        return None, compute_utility(board, color)
        # return None, compute_heuristic(board, color)
    
    # Check remaining moves
    moves = get_possible_moves(board, color)
    if len(moves) == 0:
        return None, compute_utility(board, color)
        # return None, compute_heuristic(board, color)
        
    
    # Find best move
    max_move = None
    max_score = -float('inf')
    for move in moves:
        # Get utility score
        x, y = move
        next_board = play_move(board, color, x, y)
        _, score = minimax_min_node(next_board, color, limit-1, caching)
        
        # Check maximum
        if score > max_score:
            max_score = score
            max_move = move
    
    # Cache the found maximum move and utility score
    if caching == 1:
        board_cache[board] = (max_move, max_score)

    return max_move, max_score

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
    board_cache.clear()
    move, _ = minimax_max_node(board, color, limit, caching)
    return move

############ ALPHA-BETA PRUNING #####################
def alphabeta_min_node(board, color, alpha, beta, limit, caching = 0, ordering = 0):
    # "color" is the MAX player --> make move with the other player (MIN player)
    # Compute utility with respect to the MAX player i.e., color
    # No ordering in this function since the given ordering only apply to MAX player

    # Check caching
    if caching == 1 and board in board_cache:
        return board_cache[board]

    # Check depth limit
    if limit == 0:
        return None, compute_utility(board, color)
    
    # Check remaining moves
    other_player = 1 if color == 2 else 2
    moves = get_possible_moves(board, other_player)
    if len(moves) == 0:
        return None, compute_utility(board, color)

    min_move = None
    min_score = float('inf')
    for move in moves:
        # Get utility score
        x, y = move
        next_board = play_move(board, other_player, x, y)
        _, score = alphabeta_max_node(next_board, color, alpha, beta, limit-1, caching, ordering)

        if score < min_score:
            min_score = score
            min_move = move
        
        # Update beta
        beta = min(beta, score)
        if beta <= alpha:
            break
    
    if caching == 1:
        board_cache[board] = (min_move, min_score)
    return min_move, min_score

def alphabeta_max_node(board, color, alpha, beta, limit, caching = 0, ordering = 0):
    # Check caching
    if caching == 1 and board in board_cache:
        return board_cache[board]

    # Check depth limit
    if limit == 0:
        return None, compute_utility(board, color)
    
    # Check remaining moves
    moves = get_possible_moves(board, color)
    if len(moves) == 0:
        return None, compute_utility(board, color)
    
    # ordering - largest utility score first
    scores = {}
    for move in moves:
        x, y = move
        next_board = play_move(board, color, x, y)
        score = compute_utility(next_board, color)
        if score not in scores:
            scores[score] = [move]
        else:
            scores[score].append(move)
    order = sorted(list(scores.keys()))[::-1]
    ordered_moves = []
    for i in order:
        ordered_moves += scores[i]
    moves = ordered_moves

    max_move = None
    max_score = -float('inf')
    for move in moves:
        # Get utility score
        x, y = move
        next_board = play_move(board, color, x, y)
        _, score = alphabeta_min_node(next_board, color, alpha, beta, limit-1, caching, ordering)

        if score > max_score:
            max_score = score
            max_move = move
        
        # Update alpha
        alpha = max(alpha, score)
        if beta <= alpha:
            break
    
    if caching == 1:
        board_cache[board] = (max_move, max_score)
    return max_move, max_score


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
    board_cache.clear()
    move, _ = alphabeta_max_node(board, color, -float('inf'), float('inf'), limit, caching, ordering)
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
