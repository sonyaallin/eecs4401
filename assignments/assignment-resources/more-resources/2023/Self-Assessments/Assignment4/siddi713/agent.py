"""
An AI player for Othello. 

compute_heuristic description: 
To compute the heuristic value of a given board state I do the following:
1. Count the number of corner spots on the board. The reason I do this is because having a corner is disk = to having a stable disc. 
which means it can no longer be flipped and it is a safe spot. I ideally want my AI to aim for a corner spot and build up a stable discs.
This is why I multuply the corner count by 10.
2. I count the number of moves that can be made by me and the number of moves that can be made by the opponent. This is because its ideal 
for me to have multiple options to move, so I always want to have more places to move then my opponent so I cannot be forced into a bad position.
This is why I multiply the number of moves by 5 so the chance of ending up with a low move count is lower but I still value corners more.
3. I count the number of captures that can be made by me and the number of captures that can be made by the opponent. This is because I want to be 
able to capture more discs than my opponent so I can maximize my points.
"""

import random
import sys
import time

minimax_cache, alphabeta_cache = {}, {}

# You can use the functions in othello_shared to write your AI
from othello_shared import find_lines, get_possible_moves, get_score, play_move

def eprint(*args, **kwargs): #you can use this for debugging, as it will print to sterr and not stdout
    print(*args, file=sys.stderr, **kwargs)
    
# Method to compute utility value of terminal state
def compute_utility(board, color):
    number_of_dark_pieces, number_of_light_pieces = get_score(board)
    return number_of_dark_pieces - number_of_light_pieces if color == 1 else number_of_light_pieces - number_of_dark_pieces

# Better heuristic value of board
def compute_heuristic(board, color): #not implemented, optional
    #IMPLEMENT
    board_height = len(board)
    board_width = len(board[0])
    opponent_color = 1 if color == 2 else 2

    def count_corners(board):
        corners = [(0,0), (0,board_width - 1), (board_height - 1, 0), (board_height - 1, board_width - 1)]
        light_count, dark_count = 0, 0
        for corner in corners:
            if board[corner[0]][corner[1]] == 1:
                dark_count += 1
            elif board[corner[0]][corner[1]] == 2:
                light_count += 1
        return dark_count, light_count
    
    def get_current_mobility(board, color):
        possible_moves = get_possible_moves(board, color)
        return len(possible_moves)

    def maximize_captures(board, color):
        num_captures = 0
        possible_moves = get_possible_moves(board, color)
        for move in possible_moves:
            num_captures += len(find_lines(board, color, move[0], move[1]))
        return num_captures

    total_corner_count = count_corners(board)
    my_corner_count, opponent_corner_count = total_corner_count[0 if color == 1 else 1]*10, total_corner_count[0 if opponent_color == 1 else 1]*10
    my_current_mobility, opponent_current_mobility = get_current_mobility(board, color)*5, get_current_mobility(board, opponent_color)*5
    my_captures, opponent_captures = maximize_captures(board, color), maximize_captures(board, opponent_color)

    return (my_corner_count + my_current_mobility + my_captures) - (opponent_corner_count + opponent_current_mobility + opponent_captures)

############ MINIMAX ###############################
def minimax_min_node(board, color, limit, caching = 0):
    #IMPLEMENT (and replace the line below)
    opponent_color = 1 if color == 2 else 2
    opponent_possible_moves = get_possible_moves(board, opponent_color)
    return_move, return_utility = None, float('inf')

    # Base Case: We reached the depth limit of the search
    if limit == 0 or len(opponent_possible_moves) == 0:
        util = compute_utility(board, color)
        if caching:
            minimax_cache[board] = util
        return (return_move, util)
    
    # Recursive Case: Opponent has moves to make, play their next move and see how we can maximize our next move
    for move in opponent_possible_moves:
        succesor = play_move(board, opponent_color, move[0], move[1])
        utility = None

        if caching and succesor in minimax_cache:
            utility = minimax_cache[succesor]
        else:
            opponents_move, utility = minimax_max_node(succesor, color, limit - 1, caching)

        if caching and succesor not in minimax_cache:
            minimax_cache[succesor] = utility

        if utility < return_utility:
            return_move = move
            return_utility = utility
    
    return (return_move, return_utility)

def minimax_max_node(board, color, limit, caching = 0): #returns highest possible utility
    #IMPLEMENT (and replace the line below)
    possible_moves = get_possible_moves(board, color)
    return_move, return_utility = None, float('-inf')

    if limit == 0 or len(possible_moves) == 0:
        util = compute_utility(board, color)
        if caching:
            minimax_cache[board] = util
        return (return_move, util)
    
    for move in possible_moves:
        succesor = play_move(board, color, move[0], move[1])
        utility = None

        if caching and succesor in minimax_cache:
            utility = minimax_cache[succesor]
        else:
            opponents_move, utility = minimax_min_node(succesor, color, limit - 1, caching)

        if caching and succesor not in minimax_cache:
            minimax_cache[succesor] = utility

        if utility > return_utility:
            return_move = move
            return_utility = utility

    return (return_move, return_utility)


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
    move, utility = minimax_max_node(board, color, limit, caching)
    return move

############ ALPHA-BETA PRUNING #####################
def alphabeta_min_node(board, color, alpha, beta, limit, caching = 0, ordering = 0):
    #IMPLEMENT (and replace the line below)
    opponent_color = 1 if color == 2 else 2
    opponent_possible_moves = get_possible_moves(board, opponent_color)
    return_move, return_utility = None, float('inf')

    # Base Case: We reached the depth limit of the search
    if limit == 0 or len(opponent_possible_moves) == 0:
        util = compute_utility(board, color)
        if caching:
            alphabeta_cache[board] = util
        return (return_move, util)

    if ordering:
        opponent_possible_moves.sort(key = lambda x: compute_utility(play_move(board, opponent_color, x[0], x[1]), opponent_color), reverse = True)
    
    # Recursive Case: Opponent has moves to make, play their next move and see how we can maximize our next move
    for move in opponent_possible_moves:
        succesor = play_move(board, opponent_color, move[0], move[1])
        utility = None

        if caching and succesor in alphabeta_cache:
            utility = alphabeta_cache[succesor]
        else:
            opponents_move, utility = alphabeta_max_node(succesor, color, alpha, beta, limit - 1, caching, ordering)

        if caching and succesor not in alphabeta_cache:
            alphabeta_cache[succesor] = utility

        if utility < return_utility:
            return_move = move
            return_utility = utility

        if beta > return_utility:
            beta = return_utility
            if beta <= alpha:
                break
    
    return (return_move, return_utility)

def alphabeta_max_node(board, color, alpha, beta, limit, caching = 0, ordering = 0):
    #IMPLEMENT (and replace the line below)
    possible_moves = get_possible_moves(board, color)
    possible_boards = []
    return_move, return_utility = None, float('-inf')

    if limit == 0 or len(possible_moves) == 0:
        util = compute_utility(board, color)
        if caching:
            alphabeta_cache[board] = util
        return (return_move, util)
    
    if ordering:
        possible_moves.sort(key = lambda x: compute_utility(play_move(board, color, x[0], x[1]), color), reverse = True)

    for move in possible_moves:
        succesor = play_move(board, color, move[0], move[1])
        utility = None

        if caching and succesor in alphabeta_cache:
            utility = alphabeta_cache[succesor]
        else:
            opponents_move, utility = alphabeta_min_node(succesor, color, alpha, beta, limit - 1, caching, ordering)

        if caching and succesor not in alphabeta_cache:
            alphabeta_cache[succesor] = utility

        if utility > return_utility:
            return_move = move
            return_utility = utility
        
        if alpha < return_utility:
            alpha = return_utility
            if beta <= alpha:
                break

    return (return_move, return_utility)

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
    move, utility = alphabeta_max_node(board, color, float('-inf'), float('inf'), limit, caching, ordering)
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
