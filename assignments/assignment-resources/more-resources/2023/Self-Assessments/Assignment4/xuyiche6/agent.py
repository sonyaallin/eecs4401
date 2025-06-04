"""
An AI player for Othello. 
"""

import random
import sys
import time

# You can use the functions in othello_shared to write your AI
from othello_shared import find_lines, get_possible_moves, get_score, play_move

caches = {}

def eprint(*args, **kwargs): #you can use this for debugging, as it will print to sterr and not stdout
    print(*args, file=sys.stderr, **kwargs)
    
# Method to compute utility value of terminal state
def compute_utility(board, color):
    #IMPLEMENT
    p1_counter, p2_counter = get_score(board)
    if color == 1:
        return p1_counter - p2_counter
    if color == 2:
        return p2_counter - p1_counter

# Better heuristic value of board
def compute_heuristic(board, color): #not implemented, optional
    #IMPLEMENT
    '''
    This function just returns the compute_utility function.
    '''
    return compute_utility(board, color)

############ MINIMAX ###############################
def minimax_min_node(board, color, limit, caching = 0):
    #IMPLEMENT (and replace the line below)
    min_utility = float('inf')
    min_move = None

    if color == 1:
        turn = 2
    else:
        turn = 1
    
    cached = False
    if caching:
        bd = tuple(board)
        if bd in caches:
            if color in caches[bd]:
                min_move, min_utility = caches[bd][color]
                cached = True
    if not cached:
        all_moves = get_possible_moves(board, turn)
        found = False
        if all_moves != []:
            for move in all_moves:
                next_i, next_j = move[0], move[1]
                new_board = play_move(board, turn, next_i, next_j)
                # base case
                if limit <= 1:
                    new_utility = -compute_utility(new_board, turn)
                # recursively call max node
                else:
                    new_move, new_utility = minimax_max_node(new_board, color, limit-1, caching)
                if new_utility < min_utility:
                    min_utility = new_utility
                    min_move = move
                    found = True
            if not found:
                min_utility = -compute_utility(board, turn)
            else:
                bd = tuple(board)
                if bd not in caches:
                    caches[bd] = {}
                caches[bd][color] = (min_move, min_utility)
        else:
            min_utility = -compute_utility(board, turn)
    return (min_move, min_utility)

def minimax_max_node(board, color, limit, caching = 0): #returns highest possible utility
    #IMPLEMENT (and replace the line below)
    max_utility = -float('inf')
    max_move = None

    cached = False
    if caching:
        bd = tuple(board)
        if bd in caches:
            if color in caches[bd]:
                max_move, max_utility = caches[bd][color]
                cached = True
    if not cached:
        all_moves = get_possible_moves(board, color)
        found = False
        if all_moves != []:
            for move in all_moves:
                next_i, next_j = move[0], move[1]
                new_board = play_move(board, color, next_i, next_j)
                # base case
                if limit <= 1:
                    new_utility = compute_utility(new_board, color)
                # recursively call min node
                else:
                    new_move, new_utility = minimax_min_node(new_board, color, limit-1, caching)
                if new_utility > max_utility:
                    max_utility = new_utility
                    max_move = move
                    found = True
            if not found:
                max_utility = compute_utility(board, color)
            else:
                bd = tuple(board)
                if bd not in caches:
                    caches[bd] = {}
                caches[bd][color] = (max_move, max_utility)
        else:
            max_utility = compute_utility(board, color)
    return (max_move, max_utility)
    
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
    next_move, next_utility = minimax_max_node(board, color, limit, caching)
    return next_move #change this!

############ ALPHA-BETA PRUNING #####################
def node_order(board, color, all_moves):
    utility_values = []
    boards = []
    for move in all_moves:
        next_i, next_j = move[0], move[1]
        new_board = play_move(board, color, next_i, next_j)
        utility_values.append(compute_utility(new_board, color))
        boards.append(new_board)
    result = []
    while utility_values != []:
        to_pop = max(utility_values)
        pop_ind = utility_values.index(to_pop)
        to_append = [all_moves[pop_ind], boards[pop_ind], utility_values[pop_ind]]
        utility_values.pop(pop_ind)
        all_moves.pop(pop_ind)
        boards.pop(pop_ind)
        result.append(to_append)
    return result

def alphabeta_min_node(board, color, alpha, beta, limit, caching = 0, ordering = 0):
    #IMPLEMENT (and replace the line below)
    min_utility = float('inf')
    min_move = None

    if color == 1:
        turn = 2
    else:
        turn = 1

    cached = False
    if caching:
        bd = tuple(board)
        if bd in caches:
            if color in caches[bd]:
                min_move, min_utility = caches[bd][color]
                cached = True
    if not cached:
        temp = get_possible_moves(board, turn)
        found = False
        if ordering:
            all_moves = node_order(board, turn, temp)
        else:
            all_moves = temp
        if all_moves != []:
            for move in all_moves:
                if not ordering:
                    next_i, next_j = move[0], move[1]
                    new_board = play_move(board, turn, next_i, next_j)
                else:
                    new_board = move[1]
                # base case
                if limit <= 1:
                    if ordering:
                        new_utility = -move[2]
                    else:
                        new_utility = -compute_utility(new_board, turn)
                # recursively call max node
                else:
                    new_move, new_utility = alphabeta_max_node(new_board, color, alpha, beta, limit-1, caching, ordering)
                if new_utility < min_utility:
                    min_utility = new_utility
                    if ordering:
                        min_move = move[0]
                    else:
                        min_move = move
                    found = True
                    if beta > min_utility:
                        beta = min_utility
                        if beta <= alpha:
                            break
            if not found:
                min_utility = -compute_utility(board, turn)
            else:
                bd = tuple(board)
                if bd not in caches:
                    caches[bd] = {}
                caches[bd][color] = (min_move, min_utility)
        else:
            min_utility = -compute_utility(board, turn)
    return (min_move, min_utility)

def alphabeta_max_node(board, color, alpha, beta, limit, caching = 0, ordering = 0):
    #IMPLEMENT (and replace the line below)
    max_utility = -float('inf')
    max_move = None

    cached = False
    if caching:
        bd = tuple(board)
        if bd in caches:
            if color in caches[bd]:
                max_move, max_utility = caches[bd][color]
                cached = True
    if not cached:
        temp = get_possible_moves(board, color)
        found = False
        if ordering:
            all_moves = node_order(board, color, temp)
        else:
            all_moves = temp
        if all_moves != []:
            for move in all_moves:
                if not ordering:
                    next_i, next_j = move[0], move[1]
                    new_board = play_move(board, color, next_i, next_j)
                else:
                    new_board = move[1]
                # base case
                if limit <= 1:
                    if ordering:
                        new_utility = move[2]
                    else:
                        new_utility = compute_utility(new_board, color)
                # recursively call min node
                else:
                    new_move, new_utility = alphabeta_min_node(new_board, color, alpha, beta, limit-1, caching, ordering)
                if new_utility > max_utility:
                    max_utility = new_utility
                    if ordering:
                        max_move = move[0]
                    else:
                        max_move = move
                    found = True
                    if alpha < max_utility:
                        alpha = max_utility
                        if beta <= alpha:
                            break
            if not found:
                max_utility = compute_utility(board, color)
            else:
                bd = tuple(board)
                if bd not in caches:
                    caches[bd] = {}
                caches[bd][color] = (max_move, max_utility)
        else:
            max_utility = compute_utility(board, color)
    return (max_move, max_utility)

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
    next_move, next_utility = alphabeta_max_node(board, color, -float('inf'), float('inf'), limit, caching, ordering)
    return next_move #change this!

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
