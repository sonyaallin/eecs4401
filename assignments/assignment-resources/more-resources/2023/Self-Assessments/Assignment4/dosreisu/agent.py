"""
An AI player for Othello. 
"""

import random
import sys
import time
import numpy as np

cache = {}

# You can use the functions in othello_shared to write your AI
from othello_shared import find_lines, get_possible_moves, get_score, play_move

def eprint(*args, **kwargs): #you can use this for debugging, as it will print to sterr and not stdout
    print(*args, file=sys.stderr, **kwargs)
    
# Method to compute utility value of terminal state
def compute_utility(board, color):
    dark, light = get_score(board)
    return dark - light if color == 1 else light - dark

# Better heuristic value of board
def compute_heuristic(board, color): 
    # Takeaways from article in instructions:
    # Find number of stable discs
    # Middle is eh
    # Want to increase your number of moves while reducing oponents
    # Want discs inside and avoid flipping outside discs
    # Successfully taking edge is quite good but failing is horrible

    # Encourage corner pieces with a big bonus
    # Penalize putting on X-pieces
    # Penalize putting on C-pieces
    # Encourage edge pieces

    # I tested multiple things like encouraging corner pieces, discouraging X and C pieces, as well as encouraging edge pieces.
    # I found that the edge pieces worked better ons smaller maps so I sset a threshold so that edges pieces would only have an impact
    # on certain map sizes. I also had to tune the impact of each of the parts so that the agent would make better decisions.
    total_pieces = 0
    pieces_color = 0
    corner_pieces = 1
    x_pieces = 5
    c_pieces = 9
    edge_pieces = 0
    for i in range(len(board)):
        for j in range(len(board)):
            total_pieces += 1 if board[i][j] else 0
            if board[i][j] == color: 
                pieces_color += 1
                if i in [0,-1] and j in [0,-1]: corner_pieces += 1
                if i in [-2,1] and j in [-2,1]: x_pieces -= 1
                if (i,j) in [(0, 1), (1, 0), (0, -2), (1,-2), (-2, 0), (-2,1), (-2, -1), (-1,-2)]: c_pieces -= 1
                if i in [0,-1] or j in [0,-1]: edge_pieces += 1
            # if board[i][j] == color % 2 + 1 and i in [0,-1] and j in [0,-1]: corner_pieces -= 0.5
    x_pieces /= 4
    c_pieces /= 8 # C piece is 1/2 of the penalty of a x_piece
    edge_pieces /= len(board)**2 # Don't want edge bonus to be too large
    
    if len(board) <= 7:
        return (pieces_color) * corner_pieces * x_pieces * c_pieces * edge_pieces
    # if total_pieces < (len(board)**2)/2:
    #     return (total_pieces - pieces_color) * corner_pieces * x_pieces * c_pieces * edge_pieces
    return (pieces_color) * corner_pieces * x_pieces * c_pieces

############ MINIMAX ###############################
def minimax_min_node(board, color, limit, caching = 0):
    if caching and (board, color % 2 + 1) in cache:
        return cache[(board, color % 2 + 1)]

    moves = get_possible_moves(board, color % 2 + 1)
    if not moves or not limit:
        return None, compute_utility(board, color)
    
    best_move = moves[0], float('inf')
    for move in moves:
        new_board = play_move(board, color % 2 + 1, *move)
        utility = minimax_max_node(new_board, color, limit-1, caching)[1]
        if best_move[1] > utility:
            best_move = (move, utility)

    if caching:
        cache[(board, color % 2 + 1)] = best_move
        # lr = np.fliplr(board)
        # cache[(tuple(map(tuple,lr)), color % 2 + 1)] = (-(best_move[0][0] + 1) % len(board), best_move[0][1]), best_move[1]
        # cache[(tuple(map(tuple,np.flipud(board))), color % 2 + 1)] = (best_move[0][0], -(best_move[0][1] + 1) % len(board)), best_move[1]
        # cache[(tuple(map(tuple,np.flipud(lr))), color % 2 + 1)] = (-(best_move[0][0] + 1) % len(board), -(best_move[0][1] + 1) % len(board)), best_move[1]
    return best_move

def minimax_max_node(board, color, limit, caching = 0):
    if caching and (board, color) in cache:
        return cache[(board, color)]

    moves = get_possible_moves(board, color)
    if not moves or not limit:
        return None, compute_utility(board, color)

    best_move = moves[0], float('-inf')
    for move in moves:
        new_board = play_move(board, color, *move)
        utility = minimax_min_node(new_board, color, limit-1, caching)[1]
        if best_move[1] < utility:
            best_move = move, utility

    if caching: 
        cache[(board, color)] = best_move
        # lr = np.fliplr(board)
        # cache[(tuple(map(tuple,lr)), color)] = (-(best_move[0][0] + 1) % len(board), best_move[0][1]), best_move[1]
        # cache[(tuple(map(tuple,np.flipud(board))), color)] = (best_move[0][0], -(best_move[0][1] + 1) % len(board)), best_move[1]
        # cache[(tuple(map(tuple,np.flipud(lr))), color)] = (-(best_move[0][0] + 1) % len(board), -(best_move[0][1] + 1) % len(board)), best_move[1]
    return best_move

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
    if caching and (board, color % 2 + 1) in cache:
        return cache[(board, color % 2 + 1)]

    moves = get_possible_moves(board, color % 2 + 1)
    if not moves or not limit:
        return None, compute_utility(board, color)

    if ordering:
        moves.sort(key=lambda move : compute_utility(play_move(board, color, *move), color))
    
    best_move = moves[0], beta
    for move in moves:
        new_board = play_move(board, color % 2 + 1, *move)
        utility = alphabeta_max_node(new_board, color, alpha, best_move[1], limit-1, caching)[1]
        if best_move[1] > utility:
            best_move = (move, utility)
            if alpha >= best_move[1]: break

    if caching:
        cache[(board, color % 2 + 1)] = best_move
        # lr = np.fliplr(board)
        # cache[(tuple(map(tuple,lr)), color % 2 + 1)] = (-(best_move[0][0] + 1) % len(board), best_move[0][1]), best_move[1]
        # cache[(tuple(map(tuple,np.flipud(board))), color % 2 + 1)] = (best_move[0][0], -(best_move[0][1] + 1) % len(board)), best_move[1]
        # cache[(tuple(map(tuple,np.flipud(lr))), color % 2 + 1)] = (-(best_move[0][0] + 1) % len(board), -(best_move[0][1] + 1) % len(board)), best_move[1]
    return best_move

def alphabeta_max_node(board, color, alpha, beta, limit, caching = 0, ordering = 0):
    if caching and (board, color) in cache:
            return cache[(board, color)]

    moves = get_possible_moves(board, color)
    if not moves or not limit:
        return None, compute_utility(board, color)

    if ordering:
        moves.sort(key=lambda move : compute_utility(play_move(board, color, *move), color))

    best_move = moves[0], alpha
    for move in moves:
        new_board = play_move(board, color, *move)
        utility = alphabeta_min_node(new_board, color, best_move[1], beta, limit-1, caching)[1]
        if best_move[1] < utility:
            best_move = (move, utility)
            if best_move[1] >= beta: break

    if caching:
        cache[(board, color)] = best_move
        # lr = np.fliplr(board)
        # cache[(tuple(map(tuple,lr)), color)] = (-(best_move[0][0] + 1) % len(board), best_move[0][1]), best_move[1]
        # cache[(tuple(map(tuple,np.flipud(board))), color)] = (best_move[0][0], -(best_move[0][1] + 1) % len(board)), best_move[1]
        # cache[(tuple(map(tuple,np.flipud(lr))), color)] = (-(best_move[0][0] + 1) % len(board), -(best_move[0][1] + 1) % len(board)), best_move[1]
    return best_move

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
    return alphabeta_max_node(board, color, float('-inf'), float('inf'), limit, caching)[0]

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
